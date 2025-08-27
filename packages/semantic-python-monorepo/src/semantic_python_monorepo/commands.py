import inspect
import traceback
from dataclasses import dataclass
from typing import Any, Callable

from .changelog import update_changelogs
from .logging import console, log
from .package_registry import (
    PackageRegistry,
    build_package_registry,
    calculate_version_bumps_to_apply,
)
from .release import create_gh_release
from .types import Commit, Package
from .utils import (
    LOCK_FILE,
    apply_version_bump,
    build,
    create_version_bump_commit,
    fail_fast,
    format_git_tag,
    get_commits,
    git_tag,
    log_run,
    publish,
    push_version_commit_with_tags,
    update_lockfile_with_latest_commit,
    version_bump,
)


@dataclass
class CommandWithRollback:
    apply: Callable

    name: str

    rollback: Callable | None = None
    validate: Callable | None = None

    def __repr__(self):
        return f"Command({self.name})"


# NOTE: New Type
CommandResult = Any


class CommandQueue:
    _stack: list[tuple[CommandWithRollback, Any]]

    def __init__(self):
        self._stack = []

    def execute(self, cmd: CommandWithRollback) -> CommandResult:
        log.info(f"Applying: {cmd.name}")
        result = None
        try:
            log.info(f"[red][bold]<({len(self._stack)})>[/bold] Running {cmd.name}")

            console.print(f"Running: {cmd.name}")
            result = cmd.apply()
            log.debug(f"result: {result}")
            if not self.call_with_var_args(cmd.validate, result):
                raise Exception(f"Invalid Result {result}")

        except Exception as e:
            self._stack.append((cmd, result))
            self.rollback(e)
        self._stack.append((cmd, result))
        # log.debug(f"{self._stack}, {result}")
        return result

    def rollback(self, exception):
        log.debug(exception)
        log.debug(traceback.format_exc())
        self._stack.reverse()
        for index, item in enumerate(self._stack):
            log.info(f"[red][bold]<({len(self._stack) - index})>[/bold] Rolling Back {item[0].name}")
            self.call_with_var_args(item[0].rollback, item[1])
        fail_fast()

    def call_with_var_args(self, fn, *args, **kwargs):
        if callable(fn):
            spec = inspect.getfullargspec(fn)

            has_args = len(spec.args) > 0 or spec.varargs
            has_kwargs = len(spec.kwonlyargs) > 0 or spec.varkw

            if has_args and has_kwargs:
                return fn(*args, **kwargs)
            elif has_args:
                return fn(*args)
            elif has_kwargs:
                return fn(**kwargs)
            else:  # has no arguments
                return fn()
        return True


class CommandLibrary:
    @staticmethod
    def get_commits() -> CommandWithRollback:
        return CommandWithRollback(
            name="Get Commits",
            apply=get_commits,
            rollback=lambda: None,
            validate=lambda result: isinstance(result, list) and len(result) > 0,
        )

    @staticmethod
    def build_package_registry() -> CommandWithRollback:
        return CommandWithRollback(
            name="Build Package Registry",
            apply=build_package_registry,
            rollback=lambda: None,
            validate=lambda result: isinstance(result, PackageRegistry),
        )

    @staticmethod
    def calculate_version_bumps(pr: PackageRegistry, commits: list[Commit]) -> CommandWithRollback:
        return CommandWithRollback(
            name="Calculate Version Bumps",
            apply=lambda: calculate_version_bumps_to_apply(pr, commits),
            rollback=None,
            validate=lambda: len(pr.sorted_packages_with_bumps) > 0,
        )

    @staticmethod
    def apply_version_bumps(packages_with_bumps: list[Package]) -> CommandWithRollback:
        return CommandWithRollback(
            name="Apply Version Bumps",
            apply=lambda: [apply_version_bump(package) for package in packages_with_bumps],
            rollback=lambda: log_run(["git", "restore", "packages/**/pyproject.toml"]),
            validate=lambda result: all(r.returncode == 0 for r in result),
        )

    @staticmethod
    def update_package_lock_files(
        packages_with_bumps: list[Package],
    ) -> CommandWithRollback:
        return CommandWithRollback(
            name="Update Package Lock Files",
            apply=lambda: [
                log_run(
                    ["poetry", "lock", "--no-update"],
                    cwd=f"packages/{package.package}",
                )
                for package in packages_with_bumps
            ],
            rollback=lambda: log_run(["git", "restore", "packages/**/poetry.lock"]),
            validate=lambda result: all(r.returncode == 0 for r in result),
        )

    @staticmethod
    def update_changelogs(package_with_bumps: list[Package]) -> CommandWithRollback:
        return CommandWithRollback(
            name="Update CHANGELOG.md",
            apply=lambda: update_changelogs(package_with_bumps),
            rollback=None,
            validate=lambda _: True,
        )

    @staticmethod
    def update_lockfile_with_latest_commit() -> CommandWithRollback:
        return CommandWithRollback(
            name="Update Lockfile with latest commit",
            apply=update_lockfile_with_latest_commit,
            rollback=None,
            validate=lambda latest_commit: isinstance(latest_commit, str),
        )

    @staticmethod
    def create_bump_versions_commit() -> CommandWithRollback:
        files = [
            LOCK_FILE,
            "packages/**/pyproject.toml",
            "packages/**/poetry.toml",
            "packages/**/poetry.lock",
            "packages/**/CHANGELOG.md",
        ]
        return CommandWithRollback(
            name="Bump Versions",
            apply=lambda: create_version_bump_commit(files),
            rollback=lambda results: (
                (
                    log_run(["git", "reset", "HEAD^1"]),
                    log_run(["git", "restore", *files]),
                )
                if any((r.returncode != 0 and "commit" in r.args) for r in results)
                else log_run(["git", "restore", *files]),
            ),
            validate=lambda results: all(r.returncode == 0 for r in results),
        )

    @staticmethod
    def git_tag_package(package: Package) -> CommandWithRollback:
        tag = format_git_tag(
            package_name=package.package,
            version=version_bump(version=package.version, _type=package.bump),
        )
        return CommandWithRollback(
            name=f"Tagging Package: {package.package} ({tag})",
            apply=lambda: git_tag(tag),
            rollback=lambda: log_run(["git", "tag", "--delete", tag]),
            validate=lambda result: result.returncode == 0,
        )

    @staticmethod
    def build_package(package: Package) -> CommandWithRollback:
        return CommandWithRollback(
            name=f"Building Package: {package.package}",
            apply=lambda: build(package),
            rollback=None,
            validate=lambda result: result.returncode == 0,
        )

    @staticmethod
    def publish_package(package: Package) -> CommandWithRollback:
        return CommandWithRollback(
            name=f"Publishing Package: {package.package}",
            apply=lambda: publish(package),
            rollback=None,
            validate=lambda result: result.returncode == 0,
        )

    @staticmethod
    def push_changes_and_tags() -> CommandWithRollback:
        return CommandWithRollback(
            name="Push VERSION BUMP commit to origin",
            apply=push_version_commit_with_tags,
            rollback=None,
            validate=lambda results: all(r.returncode == 0 for r in results),
        )

    @staticmethod
    def create_gh_releases(packages_with_bumps) -> CommandWithRollback:
        return CommandWithRollback(
            name="Create GH releases",
            apply=lambda: create_gh_release(packages_with_bumps),
            rollback=None,
            validate=lambda _: True,
        )

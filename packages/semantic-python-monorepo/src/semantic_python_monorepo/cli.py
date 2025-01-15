import inspect
import re
import pathlib
import graphlib
import os
import shutil
import subprocess
from dataclasses import dataclass
import sys
import argparse
import tomllib
import logging
import traceback
from typing import Any, Callable
from rich.console import Console
from rich.logging import RichHandler
from rich.padding import Padding
from rich.rule import Rule
from rich.tree import Tree


parser = argparse.ArgumentParser()
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Increase verbosity level (use -v for verbose, -vv for very verbose)",
)
parser.add_argument(
    "-n",
    "--dry-run",
    action="store_true",
    help="A flag whether to check if Rehab Optima is refreshed",
)

args = parser.parse_args()
if args.verbose == 0:
    LOGGING_LEVEL = logging.ERROR
elif args.verbose == 1:
    LOGGING_LEVEL = logging.INFO
elif args.verbose == 2:
    LOGGING_LEVEL = logging.DEBUG

# NOTE: OPTIONS
DRY_RUN = args.dry_run
FAIL_FAST = True
LOCK_FILE = "semantic-python-monorepo.lock"

logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=True,
        )
    ],
)

log = logging.getLogger(
    "rich",
)

console = Console(force_terminal=True)


def li(li: str | list[str], padding: int = 0) -> None:
    if isinstance(li, str):
        console.print(Padding(f"• {li}", (0, padding)))
    else:
        for item in li:
            li(item, padding=padding)


def fail_fast():
    if FAIL_FAST:
        sys.exit()


@dataclass
class CommandWithRollback:
    apply: Callable

    name: str

    rollback: Callable = None
    validate: Callable = None

    def __repr__(self):
        return f"Command({self.name})"


# NOTE: New Type
CommandResult = Any

h1 = lambda msg: console.print(Padding(Rule(msg), (0, 0)))
h2 = lambda msg: console.print(Padding(Rule(msg), (0, 4)))
h3 = lambda msg: console.print(Padding(Rule(msg), (0, 8)))


class CommandQueue:
    _stack: list[tuple[CommandWithRollback, Any]]

    def __init__(self):
        self._stack = []

    def execute(self, cmd: CommandWithRollback) -> CommandResult:
        log.info(f"Applying: {cmd.name}")
        result = None
        try:
            log.info(f"[red][bold]<({len(self._stack)})>[/bold] Running {cmd.name}")
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
            log.info(
                f"[red][bold]<({len(self._stack) - index})>[/bold] Rolling Back {item[0].name}"
            )
            self.call_with_var_args(item[0].rollback, item[1])
        fail_fast()

    def call_with_var_args(self, fn, *args, **kwargs):
        if callable(fn):
            spec = inspect.getfullargspec(fn)
            # log.debug(f"{spec} {(*args,)} {{**kwargs,}}")
            if len(spec.args) > 0 and spec.varargs and len(list(spec.varargs.items())):
                return fn(*args, **kwargs)
            elif len(spec.args) > 0:
                return fn(*args)
            elif spec.varargs and len(list(spec.varargs.items())):
                return fn(**args)
            else:
                return fn()
        return True


def log_run(
    cmd: str | list, msg: str = None, *args, **kwargs
) -> subprocess.CompletedProcess:
    log.debug(f"{msg if msg else 'Calling cmd'}")
    log.debug(cmd)
    result = subprocess.run(
        cmd,
        *args,
        capture_output=True,
        encoding="utf-8",
        **kwargs,
    )
    log.info(result.stdout)
    log.info(result.stderr)
    return result


# TODO: Finish implementing dry run (incomplete)
# TODO: add a cli build / publish
# TODO: add a cli dry run
# TODO: add a bump cli
# TODO: add tests

"""
NOTE:

state:
    Lives in "deploy" commits. (sum of changes per package)

alg:
    for each commit since last commit (not including):
        get affected packages
        get current version
        get bump type
        get dependency graph
        starting with packages in sorted dependencies:
            update version of packages
            build package
            publish package
    make new commit with version bumps "version bumping":
        tag commit with package-version for each package bump made


cases:
    packages A < B
special cases:
    dependency has breaking change, breaking change for upstream

    should patch bump anything that has a downstream that was bumped
"""


@dataclass()
class Commit:
    sha: str
    msg: str
    files: list[str]
    packages: set[str]


@dataclass()
class Package:
    version: str
    package: str
    relevant_commits: list[Commit]  # for release notes
    dependencies: list = None
    bump: str = None  # patch/minor/major
    index: int = 0


class PackageRegistry:
    registry_path: str
    sorted_packages: list[Package]
    _g: dict
    _packages: dict[str, Package]

    def __init__(self, registry_path):
        self.registry_path = registry_path
        self._packages = {}
        self._g = {}
        self.sorted_packages = []
        self.collect_packages()

    def collect_packages(self) -> None:
        for d in pathlib.Path(self.registry_path).iterdir():
            self.parse_package(d)
        log.info(f"{len(self._packages.keys())} packages found")

    def parse_package(self, package_dir: pathlib.Path) -> None:
        _, package_name = str(package_dir).split("/")
        package_version = get_package_version(package_name)
        deps = get_package_dependencies(package_name)
        self._g.update(deps)
        self._packages[package_name] = Package(
            package=package_name,
            version=package_version,
            dependencies=list(deps.values())[0],
            relevant_commits=[],
        )
        self.sort_packages_and_update_indexes()

    def sort_packages_and_update_indexes(self) -> None:
        graph = graphlib.TopologicalSorter(graph=self._g)
        sorted_deps = tuple(graph.static_order())
        for package_name in self._packages.keys():
            # Update index to sort later by
            index = sorted_deps.index(package_name)
            if index >= 0:
                self._packages[package_name].index = index

            # update bump type if dependency has a bump

        self.sorted_packages: list[Package] = sorted(
            list(self._packages.values()), key=lambda package: package.index
        )

    def get_tree(self):
        tree = Tree(f"Package Registry ({self.registry_path})")
        for pname, p in self._packages.items():
            ptree = tree.add(f"[bold blue]{pname}")
            for name in p.dependencies:
                ptree.add(f"[blue]{name}")
        return tree

    @property
    def packages_with_bumps(self) -> dict[str, Package]:
        return {k: v for k, v in self._packages.items() if v.bump}

    @property
    def sorted_packages_with_bumps(self) -> list[Package]:
        return [package for package in self._packages.values() if package.bump]

    @property
    def has_changes(self) -> bool:
        return any(self.sorted_packages_with_bumps)


def read_lock_file() -> str:
    """Get last commit that was managed"""
    with open(f"./{LOCK_FILE}", "r" if os.path.exists(LOCK_FILE) else "a+") as f:
        return f.readline().rstrip()


def format_git_tag(package_name: str, version: str) -> str:
    return f"{package_name}-v{version}"


def git_tag(tag: str) -> None:
    return log_run(
        ["git", "tag", tag],
        "Creating Git Tags",
    )


def get_commits() -> list[Commit]:
    """return list of all commits that haven't been built"""
    last_managed_commit = read_lock_file()
    log.info(f"Latest processed commit: {last_managed_commit}")
    commit_format = ">>%H<++>%B"
    output = []
    commits = []
    if last_managed_commit:
        output = log_run(
            [
                "git",
                "log",
                "--name-only",
                "--oneline",
                f'--format="{commit_format}"',
                f"{last_managed_commit}..HEAD",
            ],
            "Getting log since last process",
        )
    else:
        output = log_run(
            ["git", "log", "--name-only", "--oneline", f'--format="{commit_format}"'],
            "Initial Run",
        )
    files = []
    packages = set()
    sha = msg = ""
    lines = output.stdout.replace('"', "").splitlines()
    log.info("Parsing commit log")
    log.info(f"Number of Files affected by recent commits: {len(files)}")
    log.debug(f"Files affected by recent commits: {files}")
    for index, line in enumerate(lines):
        if line == "":
            continue
        if line.find(">>") == -1:
            # A commit line
            if sha and msg:
                # finish old commit
                commits.append(Commit(sha=sha, msg=msg, files=files, packages=packages))
                files = []
                packages = set()
            sha, msg = line.replace(">>", "").split("<++>")
        else:
            # file line
            file = line
            files.append(file)
            if len(file.split("/")) >= 2:
                # part of a package
                packages.add(file.split("/")[1])
            if len(lines) - 1 == index:
                commits.append(Commit(sha=sha, msg=msg, files=files, packages=packages))

    commits.reverse()
    return [commit for commit in commits if "VERSION BUMP" not in commit.msg]


def version_bump(version: str, _type: str = "patch") -> str:
    """A semver version bumper where _type is (patch|minor|major)"""
    major, minor, patch = version.split(".")
    major = int(major)
    minor = int(minor)
    patch = int(patch)
    if _type == "patch":
        patch += 1
    if _type == "minor":
        patch = 0
        minor += 1
    if _type == "major":
        patch = 0
        minor = 0
        major += 1
    return f"{major}.{minor}.{patch}"


def get_package_version(package: str) -> str:
    with open(f"packages/{package}/pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        version = data["tool"]["poetry"]["version"]
        return version


def get_package_repository(package: str) -> str:
    try:
        with open(f"packages/{package}/poetry.toml", "rb") as f:
            data = tomllib.load(f)
            repositories = data["repositories"]
            return list(repositories.keys())[0]
    except FileNotFoundError as e:
        console.print(
            f"You need to define a repositories key in poetry.toml for package {package}"
        )
        raise e


def get_package_dependencies(package: str) -> dict:
    with open(f"packages/{package}/pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        deps = data["tool"]["poetry"]["dependencies"]
        result = []
        for pkg, info in deps.items():
            if type(info) == dict:
                if "../" in info["path"] and info["develop"] == True:
                    result.append(pkg)

        return {package: set(result)}


def apply_version_bump(package: Package):
    return log_run(
        ["poetry", "-C", f"packages/{package.package}", "version", package.bump],
        f"Applying Change: {package.package} ({package.version} -> {version_bump(package.version, _type=package.bump)})",
    )


def build(package: Package):
    path = f"./packages/{package.package}/dist"
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)

    return log_run(
        ["poetry", "build"],
        cwd=f"packages/{package.package}",
    )


def publish(package: Package):
    repository = get_package_repository(package.package)
    return log_run(
        ["poetry", "publish", "--skip-existing", f"--repository={repository}"],
        "Publishing Package",
        cwd=f"packages/{package.package}",
    )


def build_package_registry(commits: list[Commit]) -> PackageRegistry:
    pr = PackageRegistry("packages")
    return pr


def calculate_version_bumps_to_apply(
    pr: PackageRegistry, commits: list[Commit]
) -> None:
    """Updates the pr passed in to have the correct version bumps.
    This propogates upstream changes to packages that use them as dependencies."""
    for commit in commits:
        if "VERSION BUMP" in commit.msg:
            log.info("Skipping VERSION BUMP COMMIT")
            continue
        log.info(f"Processing commit: {commit.msg}, ({commit.sha[:5]})")
        for package_name in commit.packages:
            pr._packages[package_name].relevant_commits.append(commit)
            if "BREAKING" in commit.msg or re.search("^(\w|[)(])+!:", commit.msg):
                pr._packages[package_name].bump = "major"
            elif (
                re.search("^(feat|perf):", commit.msg)
                and pr._packages[package_name].bump != "major"
            ):
                pr._packages[package_name].bump = "minor"
            elif (
                re.search("^(bug|fix|regression|test):", commit.msg)
                and pr._packages[package_name].bump != "major"
                and pr._packages[package_name].bump != "minor"
            ):
                pr._packages[package_name].bump = "patch"

    # version bumps based on downstream dependencies (Even without commits)
    for package_name, package in pr._packages.items():
        if package.bump:
            for pname, p in pr._packages.items():
                if pname == package_name:
                    continue
                if package_name in p.dependencies:
                    if package.bump == "major":
                        pr._packages[pname].bump = "major"
                    elif package.bump:
                        if package.bump in {"minor", "patch"} and not p.bump:
                            pr._packages[pname].bump = package.bump

                    log.info(
                        f"Found downstream depency of {package_name} ({package.bump}): {pname} ({p.bump})"
                    )


def update_lockfile_with_latest_commit() -> str:
    """Returns the commit logged"""
    log.info("Changes detected")
    output = log_run(
        ["git", "rev-parse", "HEAD"],
        "Getting most recent commit",
    ).stdout.rstrip()
    with open(LOCK_FILE, "w") as f:
        f.seek(0)
        f.write(output)
        f.truncate()
    return output


def create_version_bump_commit() -> list[subprocess.CompletedProcess]:
    return [
        log_run(["git", "add", LOCK_FILE], "Adding lockfile"),
        log_run(
            ["git", "add", "packages/**/pyproject.toml"],
            "Adding pyproject.toml files",
        ),
        log_run(
            ["git", "add", "packages/**/poetry.lock"],
            "Adding poetry.lock files",
        ),
        log_run(
            ["git", "commit", "-m", "VERSION BUMP", "--no-verify"],
            "Adding VERSION BUMP commit",
        ),
    ]


def push_version_commit_with_tags():
    return [
        log_run(["git", "push", "--no-verify"], "Pushing commit to origin"),
        log_run(["git", "push", "--no-verify", "--follow-tags"], "Pushing Git Tags"),
        log_run(
            ["git", "push", "--no-verify", "--tags"], "Pushing unAnnotated Git Tags)"
        ),
    ]


def main():
    if DRY_RUN:
        console.print("[bold yellow]This is a Dry Run")

    cq = CommandQueue()
    h1("Collect Meta Data")
    li("Get Commits")
    commits = cq.execute(
        CommandWithRollback(
            name="Get Commits",
            apply=get_commits,
            rollback=lambda: None,
            validate=lambda result: isinstance(result, list) and len(result) > 0,
        )
    )

    li("Build Package Registry")
    pr = cq.execute(
        CommandWithRollback(
            name="Build Package Registry",
            apply=lambda: build_package_registry(commits),
            rollback=lambda: None,
            validate=lambda result: isinstance(result, PackageRegistry),
        )
    )
    console.print(Padding(pr.get_tree(), (0, 4)))

    log.debug("Package Registry:")
    for p in pr._packages.values():
        log.debug(f"\t - {p.package} ({','.join(p.dependencies)})")

    li("Calculate Version Bumps")
    packages_with_bumps = None
    cq.execute(
        CommandWithRollback(
            name="Calculate Version Bumps",
            apply=lambda: calculate_version_bumps_to_apply(pr, commits),
            rollback=None,
            validate=lambda: len(pr.sorted_packages_with_bumps) > 0,
        )
    )
    packages_with_bumps = pr.sorted_packages_with_bumps
    log.debug(packages_with_bumps)
    h1("Apply Changes")
    li("Apply Version Bumps")
    cq.execute(
        CommandWithRollback(
            name="Apply Version Bumps",
            apply=lambda: [
                apply_version_bump(package) for package in packages_with_bumps
            ],
            rollback=lambda: log_run(["git", "restore", "packages/**/pyproject.toml"]),
            validate=lambda result: all(r.returncode == 0 for r in result),
        )
    )
    li("Update Package Lock Files")
    cq.execute(
        CommandWithRollback(
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
    )

    li("Update Lockfile with latest commit")
    latest_commit = None
    if not DRY_RUN:
        latest_commit = cq.execute(
            CommandWithRollback(
                name="Update Lockfile with latest commit",
                apply=update_lockfile_with_latest_commit,
                rollback=None,
                validate=lambda latest_commit: isinstance(latest_commit, str),
            )
        )
    log.debug(latest_commit)

    li("Bump Versions")
    files = [
        LOCK_FILE,
        "packages/**/pyproject.toml",
        "packages/**/poetry.toml",
        "packages/**/poetry.lock",
    ]
    if not DRY_RUN:
        cq.execute(
            CommandWithRollback(
                name="Bump Versions",
                apply=create_version_bump_commit,
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
        )

    h1(
        f"Build and Publish Packages ({', '.join(p.package for p in packages_with_bumps)})"
    )
    for package in packages_with_bumps:
        package_slug = f"{package.package} ({version_bump(version=package.version, _type=package.bump)})"
        li(f"{package_slug}")
        tag = format_git_tag(
            package_name=package.package,
            version=version_bump(version=package.version, _type=package.bump),
        )
        li(f"Tagging with {tag}", padding=4)
        if not DRY_RUN:
            cq.execute(
                CommandWithRollback(
                    name=f"Tagging Package: {package.package}",
                    apply=lambda: git_tag(tag),
                    rollback=lambda: log_run(["git", "tag", "--delete", tag]),
                    validate=lambda result: result.returncode == 0,
                )
            )
        li("Building", padding=4)
        if not DRY_RUN:
            cq.execute(
                CommandWithRollback(
                    name=f"Building Package: {package.package}",
                    apply=lambda: build(package),
                    rollback=None,
                    validate=lambda result: result.returncode == 0,
                )
            )
        li("Publishing", padding=4)
        if not DRY_RUN:
            cq.execute(
                CommandWithRollback(
                    name=f"Publishing Package: {package.package}",
                    apply=lambda: publish(package),
                    rollback=None,
                    validate=lambda result: result.returncode == 0,
                )
            )

    h1("Push VERSION BUMP commit to origin")
    if not DRY_RUN:
        cq.execute(
            CommandWithRollback(
                name="Push VERSION BUMP commit to origin",
                apply=push_version_commit_with_tags,
                rollback=None,
                validate=lambda results: all(r.returncode == 0 for r in results),
            )
        )

    if DRY_RUN:
        console.print("[bold yellow]This was a Dry Run")


if __name__ == "__main__":
    main()

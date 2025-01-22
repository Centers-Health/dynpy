import os
import shutil
import subprocess
import sys

import tomllib

from .logging import console, log
from .types import Commit, Package

LOCK_FILE = "semantic-python-monorepo.lock"


def log_run(cmd: str | list, msg: str | None = None, *args, **kwargs) -> subprocess.CompletedProcess:
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


def fail_fast():
    sys.exit()


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
                f"--format={commit_format}",
                f"{last_managed_commit}..HEAD",
            ],
            "Getting log since last process",
        )
    else:
        output = log_run(
            ["git", "log", "--name-only", "--oneline", f"--format={commit_format}"],
            "Initial Run",
        )
    files = []
    packages = set()
    sha = msg = ""
    lines = output.stdout.splitlines()
    log.info("Parsing commit log")
    log.info(f"Number of Files affected by recent commits: {len(files)}")
    log.debug(f"Files affected by recent commits: {files}")
    for index, line in enumerate(lines):
        if line == "":
            continue
        if line.find(">>") != -1:
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
            split_path = file.split("/")
            if len(split_path) >= 2 and split_path[0] == "packages":
                # part of a package
                packages.add(split_path[1])
            if len(lines) - 1 == index:
                commits.append(Commit(sha=sha, msg=msg, files=files, packages=packages))

    commits.reverse()
    return [commit for commit in commits if "VERSION BUMP" not in commit.msg]


def read_lock_file() -> str:
    """Get last commit that was managed"""
    with open(f"./{LOCK_FILE}", "r" if os.path.exists(LOCK_FILE) else "a+") as f:
        return f.readline().rstrip()


def version_bump(version: str, _type: str | None = "patch") -> str:
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
        console.print(f"You need to define a repositories key in poetry.toml for package {package}")
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
        env=os.environ.copy(),
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
        log_run(["git", "push", "--no-verify", "--tags"], "Pushing unAnnotated Git Tags)"),
    ]


def format_git_tag(package_name: str, version: str) -> str:
    return f"{package_name}-v{version}"


def git_tag(tag: str) -> subprocess.CompletedProcess:
    return log_run(
        ["git", "tag", tag],
        "Creating Git Tags",
    )

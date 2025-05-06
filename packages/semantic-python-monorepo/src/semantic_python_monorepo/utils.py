import os
import re
import shutil
import subprocess
import sys
from io import TextIOWrapper

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


def fail_fast(status_code: int = 1):
    sys.exit(status_code)


def get_commit_history(last_managed_commit: str) -> list[str]:
    """
    Grab the recent commits from git log.

    Two variants:
        1. no last_managed_commit (we are in initial state) parse from the begining of repo history
        2. from last_managed_commit to current HEAD.
    """
    output = []
    commit_format = ">>%H<++>%B"
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
    return output.stdout.splitlines()


def parse_commit_history(commit_history: list[str]) -> list[Commit]:
    commits = []
    files = []
    packages = set()
    sha = msg = ""
    for index, line in enumerate(commit_history):
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
            if len(commit_history) - 1 == index:
                commits.append(Commit(sha=sha, msg=msg, files=files, packages=packages))

    log.info("Parsing commit log")
    log.info(f"Number of Files affected by recent commits: {len(files)}")
    log.debug(f"Files affected by recent commits: {files}")
    commits.reverse()
    return commits


def filter_out_version_bump_commits(commits: list[Commit]) -> list[Commit]:
    return [commit for commit in commits if "VERSION BUMP" not in commit.msg]


def get_commits() -> list[Commit]:
    """return list of all commits that haven't been built"""
    last_managed_commit = read_lock_file()
    commit_history = get_commit_history(last_managed_commit)
    commits = parse_commit_history(commit_history)
    commits = filter_out_version_bump_commits(commits)

    return commits


def create_or_open(file: str) -> TextIOWrapper:
    return open(file, "r" if os.path.exists(file) else "a+")


def read_lock_file() -> str:
    console.log(f"Reading Lockfile {LOCK_FILE}")
    """Get last commit that was managed"""
    with create_or_open(f"./{LOCK_FILE}") as f:
        last_managed_commit = f.readline().rstrip()
        log.info(f"Latest processed commit: {last_managed_commit}")
        return last_managed_commit


def categorize_commit(commit: Commit) -> dict[str, str]:
    """Categorize a commit based on its message and return the appropriate section"""
    bump_type = get_bump_from_commit_msg(commit.msg)
    commit_link = f"([`{commit.sha[:7]}`](https://github.com/Centers-health/dynpy/commit/{commit.sha}))"

    if bump_type == "major":  # noqa: SIM116
        return {"Breaking": f"{commit.msg} {commit_link}"}
    elif bump_type == "minor":
        return {"Feature": f"{commit.msg} {commit_link}"}
    elif bump_type == "patch":
        return {"Fix": f"{commit.msg} {commit_link}"}
    else:
        return {"Other": f"{commit.msg} {commit_link}"}


def version_bump(version: str, _type: str | None = "patch") -> str:
    """A semver version bumper where _type is (patch|minor|major)"""
    assert isinstance(version, str)
    assert isinstance(_type, str | None)

    split = version.split(".")
    if len(split) == 3:
        major, minor, patch = split
    elif len(split) == 2:
        major, minor = split
        patch = "0"
    elif len(split) == 1 and split[0] != "":
        major = split[0]
        minor = "0"
        patch = "0"
    else:
        raise ValueError(f"Version invalid -- {version}; Needs to be major.minor.patch.")

    major = int(major)
    minor = int(minor)
    patch = int(patch)
    match _type:
        case "patch":
            patch += 1
        case "minor":
            patch = 0
            minor += 1
        case "major":
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
        for info in deps.values():
            # NOTE: Must have both path and develop set to these values for the poetry monorepo plugin to manage them correctly.
            if isinstance(info, dict) and "../" in info["path"] and info["develop"]:
                result.append(os.path.basename(info["path"]))

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


def create_version_bump_commit(files: list[str]) -> list[subprocess.CompletedProcess]:
    return [log_run(["git", "add", file]) for file in files] + [
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


def max_bump(bump1: str | None, bump2: str | None) -> str | None:
    """A max function that returns the more significant of two bumps."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    assert isinstance(bump1, str | None)
    assert isinstance(bump2, str | None)

    if bump1 == bump2:
        return bump1
    elif bump1 == MAJOR or bump2 == MAJOR:
        return MAJOR
    elif {bump1, bump2} == {MINOR, PATCH}:
        return MINOR
    elif not bump1:
        return bump2
    elif not bump2:
        return bump1


def git_tag(tag: str) -> subprocess.CompletedProcess:
    return log_run(
        ["git", "tag", tag],
        "Creating Git Tags",
    )


def get_bump_from_commit_msg(
    msg: str,
) -> str | None:
    """get a new bump type (major, minor, patch) based on the current bump as well as the commit message, using conventional commit standards. The objective here is not to superscede the current bump. So highest bump value wins. So if we run this on a 'feat' commit, but current bump is 'major' we leave at major."""
    new_bump = None
    if "BREAKING CHANGES" in msg or re.search(r"^(\w|[)(])+!:", msg):
        new_bump = "major"
    elif re.search(r"^(feat|perf)(\(\w+\))?:", msg):
        new_bump = "minor"
    elif re.search(r"^(bug|fix|refactor|test|revert)(\(\w+\))?:", msg):
        new_bump = "patch"

    return new_bump


def verify_poetry_plugins_are_installed() -> bool:
    result = subprocess.run(
        ["poetry", "self", "show", "plugins"], capture_output=True, check=True, encoding="utf-8"
    )
    log.debug(result.stdout)
    return "poetry-plugin-mono-repo-deps" in result.stdout and "poetry-bumpversion" in result.stdout

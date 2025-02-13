import datetime
import re

from .types import Commit, Package
from .utils import create_or_open, get_bump_from_commit_msg


def format_commit_msg(msg: str) -> str:
    return re.sub(r"^[^:]+:\s", "", msg).capitalize()


def categorize_commit(commit: Commit) -> tuple[str, str]:
    """Categorize a commit based on its message and return the appropriate section"""
    bump_type = get_bump_from_commit_msg(commit.msg)
    commit_link = f"([`{commit.sha[:7]}`](https://github.com/Centers-health/dynpy/commit/{commit.sha}))"
    msg = format_commit_msg(commit.msg)

    if bump_type == "major":  # noqa: SIM116
        return "Breaking", f"{commit.msg} {commit_link}"
    elif bump_type == "minor":
        return "Feature", f"{commit.msg} {commit_link}"
    elif bump_type == "patch":
        return "Fix", f"{commit.msg} {commit_link}"
    else:
        return "Other", f"{commit.msg} {commit_link}"


def update_changelog(package: Package) -> None:
    commits_by_type = {
        "Breaking": [],
        "Feature": [],
        "Fix": [],
        "Other": [],
    }
    version = package.new_version
    current_date = datetime.datetime.today().strftime("%Y-%m-%d")
    name = package.package

    if len(package.relevant_commits) == 0:
        return

    for commit in package.relevant_commits:
        _type, text = categorize_commit(commit)
        commits_by_type[_type].append(text)

    filename = f"packages/{name}/CHANGELOG.md"
    lines = []
    with create_or_open(filename) as f:
        lines = f.readlines()

    if len(lines) > 3:
        header = lines[0:4]
        tail = lines[4:]
    else:
        header = [
            "# Changelog",
            "",
            "<!--next-version-placeholder-->",
            "",
        ]
        tail = []

    new_log = []
    new_log.append(f"## v{version} ({current_date})")
    for key, val in commits_by_type.items():
        if len(val) == 0:
            # NOTE: no commits for this category, so skip
            continue
        new_log.append(f"### {key}")
        for line in val:
            new_log.append(f"- {line}")

    new_lines = header + new_log + tail
    with open(filename, "w") as f:
        f.writelines([f"{line}\n" for line in new_lines[:-1]] + [new_lines[-1]])


def update_changelogs(packages_with_bumps: list[Package]) -> None:
    for package in packages_with_bumps:
        update_changelog(package)

from dataclasses import dataclass


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
    dependencies: list | None = None
    bump: str | None = None  # patch/minor/major
    index: int = 0

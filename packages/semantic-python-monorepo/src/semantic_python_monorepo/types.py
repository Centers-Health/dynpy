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

    @property
    def new_version(self) -> str:
        from .utils import version_bump

        return f"{version_bump(version=self.version, _type=self.bump)}"

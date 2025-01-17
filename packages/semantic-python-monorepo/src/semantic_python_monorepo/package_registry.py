import re
import graphlib
import pathlib

from rich.tree import Tree

from .types import Package, Commit
from .logging import log
from .utils import get_package_dependencies, get_package_version


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

        self.sorted_packages = sorted(
            list(self._packages.values()), key=lambda package: package.index
        )

    def get_tree(self):
        tree = Tree(f"Package Registry ({self.registry_path})")
        for pname, p in self._packages.items():
            ptree = tree.add(f"[bold blue]{pname}")
            if p.dependencies:
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


def build_package_registry() -> PackageRegistry:
    pr = PackageRegistry("packages")
    return pr


def calculate_version_bumps_to_apply(
    pr: PackageRegistry, commits: list[Commit]
) -> None:
    """Updates the PackageRegistry passed in to have the correct version bumps.
    This propogates upstream changes to packages that use them as dependencies."""
    for commit in commits:
        if "VERSION BUMP" in commit.msg:
            log.info("Skipping VERSION BUMP COMMIT")
            continue
        log.info(f"Processing commit: {commit.msg}, ({commit.sha[:5]})")
        for package_name in commit.packages:
            pr._packages[package_name].relevant_commits.append(commit)
            if "BREAKING" in commit.msg or re.search(r"^(\w|[)(])+!:", commit.msg):
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
                if p.dependencies and package_name in p.dependencies:
                    if package.bump == "major":
                        pr._packages[pname].bump = "major"
                    elif package.bump:
                        if package.bump in {"minor", "patch"} and not p.bump:
                            pr._packages[pname].bump = package.bump

                    log.info(
                        f"Found downstream depency of {package_name} ({package.bump}): {pname} ({p.bump})"
                    )

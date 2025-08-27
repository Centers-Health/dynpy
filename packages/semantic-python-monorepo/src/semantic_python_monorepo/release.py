import subprocess

from .types import Package
from .utils import format_git_tag


def create_gh_release(package: Package):
    tag = format_git_tag(package_name=package.package, version=package.new_version)
    command = f"gh release create {tag} --generate-notes"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Release {tag} created successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create release {tag}: {e}")


def create_gh_releases(packages_with_bumps: list[Package]) -> None:
    for package in packages_with_bumps:
        create_gh_release(package)

import logging
from rich.padding import Padding

from .arg_parser import parser
from .commands import CommandLibrary as CL, CommandQueue
from .logging import console, h1, li, log, logger_setup
from .utils import version_bump

# TODO: Finish implementing dry run (incomplete)
# NOTE: Do we need rich?
# TODO: add a cli build / publish
# TODO: add a bump cli
# TODO: add tests
# FIXME: fix broken imports from refactor
# FIXME: dry run needs to be build into the runner
# FIXME: printouts can be in CL instead of from the CommandQueue, this would allow more formatting options. But may scrap the formatter from rich and do a simpler linear one, though the tree is nice


LOGGING_LEVEL = logging.ERROR
args = parser.parse_args()
if args.verbose == 0:
    LOGGING_LEVEL = logging.ERROR
elif args.verbose == 1:
    LOGGING_LEVEL = logging.INFO
elif args.verbose == 2:
    LOGGING_LEVEL = logging.DEBUG


logger_setup(LOGGING_LEVEL)
# NOTE: OPTIONS
DRY_RUN = args.dry_run


def main():
    if DRY_RUN:
        console.print("[bold yellow]This is a Dry Run")

    cq = CommandQueue()

    h1("Collect Meta Data")
    commits = cq.execute(CL.get_commits())

    pr = cq.execute(CL.build_package_registry())
    console.print(Padding(pr.get_tree(), (0, 4)))

    log.debug("Package Registry:")
    for p in pr._packages.values():
        log.debug(f"\t - {p.package} ({','.join(p.dependencies)})")

    packages_with_bumps = None
    cq.execute(CL.calculate_version_bumps(pr, commits))

    packages_with_bumps = pr.sorted_packages_with_bumps
    log.debug(packages_with_bumps)

    h1("Apply Changes")
    cq.execute(CL.apply_version_bumps(packages_with_bumps))

    cq.execute(CL.update_package_lock_files(packages_with_bumps))

    latest_commit = None
    if not DRY_RUN:
        latest_commit = cq.execute(CL.update_lockfile_with_latest_commit())
    log.debug(latest_commit)

    if not DRY_RUN:
        cq.execute(CL.create_bump_versions_commit())

    h1(
        f"Build and Publish Packages ({', '.join(p.package for p in packages_with_bumps)})"
    )
    for package in packages_with_bumps:
        package_slug = f"{package.package} ({version_bump(version=package.version, _type=package.bump)})"
        li(f"{package_slug}")
        if not DRY_RUN:
            cq.execute(CL.git_tag_package(package))

        if not DRY_RUN:
            cq.execute(CL.build_package(package))

        if not DRY_RUN:
            cq.execute(CL.publish_package(package))

    if not DRY_RUN:
        cq.execute(CL.push_changes_and_tags())

    if DRY_RUN:
        console.print("[bold yellow]This was a Dry Run")


if __name__ == "__main__":
    main()

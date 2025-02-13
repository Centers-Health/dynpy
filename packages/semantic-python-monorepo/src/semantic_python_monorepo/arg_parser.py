import argparse

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
parser.add_argument(
    "--registry",
    action="store_true",
    help="View the current package registry as is",
)
parser.add_argument(
    "--analyze",
    action="store_true",
    help="Show what version bumps would occur if run now",
)

parser.add_argument(
    "--generate-changelogs",
    action="store_true",
    help="Generate and update CHANGELOGS.md",
)

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

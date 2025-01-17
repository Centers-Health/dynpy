import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.padding import Padding
from rich.rule import Rule


def logger_setup(level: int):
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_time=True,
            )
        ],
    )


log = logging.getLogger(
    "rich",
)

console = Console(force_terminal=True)


def li(item: str | list[str], padding: int = 0) -> None:
    if isinstance(item, str):
        console.print(Padding(f"• {item}", (0, padding)))
    else:
        for item in item:
            li(item, padding=padding)


h1 = lambda msg: console.print(Padding(Rule(msg), (0, 0)))
h2 = lambda msg: console.print(Padding(Rule(msg), (0, 4)))
h3 = lambda msg: console.print(Padding(Rule(msg), (0, 8)))

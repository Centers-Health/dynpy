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
        for it in item:
            li(it, padding=padding)


def h1(msg: str) -> None:
    console.print(Padding(Rule(msg), (0, 0)))


def h2(msg: str) -> None:
    console.print(Padding(Rule(msg), (0, 4)))


def h3(msg: str) -> None:
    console.print(Padding(Rule(msg), (0, 8)))

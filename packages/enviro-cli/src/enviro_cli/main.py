import typer
from rich.console import Console

from enviro_cli.commands.qa import qa_app

console = Console()
app = typer.Typer()
app.add_typer(qa_app, name="qa")


if __name__ == "__main__":
    app()

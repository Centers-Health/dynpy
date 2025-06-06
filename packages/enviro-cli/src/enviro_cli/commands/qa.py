import subprocess
from time import sleep
from typing import Annotated

import requests
import typer
from enviro_cli.utils import GH, get_list_of_envs
from rich import print
from rich.console import Console
from rich.progress import Progress, TextColumn

console = Console()
qa_app = typer.Typer()


@qa_app.command(
    "list",
    help="List current QA environments. NOTE - this means they are on disk, it does NOT indicate anything about their state.",
)
def qa_list(status: Annotated[bool, typer.Argument] = False):
    result = get_list_of_envs()
    with Progress(TextColumn("[progress.description]{task.description}"), transient=False) as progress:
        for name in result.json()["qa_envs"]:
            if status:
                task = progress.add_task(f"Checking {name}", total=None)
                code = requests.get(result.json()["qa_envs"][name])
                if code.status_code != 200:
                    progress.update(
                        task,
                        description=f"[black on red]{name} [bold]{code.status_code}[/bold] [bold]![/bold]",
                    )
                else:
                    progress.update(
                        task, description=f"{name} [blue]{code.status_code}[/blue] [green]✓[/green]"
                    )
                progress.stop_task(task)
            else:
                print(name)


@qa_app.command(
    "new",
    help="Spin up a new QA environment.",
)
def qa_new(branch: str, wait_for_it: Annotated[bool, typer.Argument] = False):
    result = get_list_of_envs()
    existing = result.json()["qa_envs"]
    if any(name == branch.lower().strip() for name in existing):
        print("[yellow]A QA environment for that branch already exists. Doing nothing.")
        raise typer.Exit()
    GH.new_environment(branch=branch)

    if wait_for_it:
        while True:
            print("Waiting for environment...")
            try:
                response = requests.get(f"https://{branch.lower()}-cas.qa.centershealthcare.org")
                if response.status_code == 200:
                    subprocess.run(["notify-send", f"QA Environment for {branch} is ready."])
                    typer.launch(f"https://{branch.lower()}-cas.qa.centershealthcare.org")
                    break
            except Exception as e:
                print(e)
            sleep(30)


@qa_app.command(
    "remove",
    help="Remove an existing QA environment.",
)
def qa_remove(branch: str):
    result = get_list_of_envs()
    existing = result.json()["qa_envs"]
    if not any(name == branch.lower().strip() for name in existing):
        print(f"[yellow]No QA environment exists by that name '{branch}'. Doing nothing.")
        raise typer.Exit()
    GH.remove_environment(branch=branch)

import subprocess

import requests
import typer
from rich import print


def get_list_of_envs():
    try:
        return requests.get("https://qa.centershealthcare.org/api/list")
    except requests.RequestException:
        print("[yellow]Unable to reach qa.centershealthcare.org. Are you on the VPN?")
        raise typer.Exit()


def _dispatch_qa_manage_action(action: str, branch: str) -> None:
    subprocess.run(
        [
            "gh",
            "workflow",
            "run",
            "Manage QA Environments (QA Core)",
            "--repo",
            "Centers-health/enviro",
            "-f",
            f"branch={branch}",
            "-f",
            f"action={action}",
        ]
    )


class GH:
    """A wrapper for the github client 'gh'"""

    @staticmethod
    def new_environment(branch: str) -> None:
        _dispatch_qa_manage_action(action="new", branch=branch)

    @staticmethod
    def refresh_environment(branch: str) -> None:
        _dispatch_qa_manage_action(action="refresh", branch=branch)

    @staticmethod
    def renew_environment(branch: str) -> None:
        _dispatch_qa_manage_action(action="renew", branch=branch)

    @staticmethod
    def remove_environment(branch: str) -> None:
        _dispatch_qa_manage_action(action="remove", branch=branch)

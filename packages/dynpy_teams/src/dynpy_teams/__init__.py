import json
import os

import requests

from . import blocks

WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def post_to_teams_channel(
    title: str,
    body_elements: list,
    actions: list | None = None,
    url: str | None = None,
    request_kwargs: dict | None = None,
) -> None:
    """
    Posts an adaptive card message to Microsoft Teams

    :param title: Title of the card
    :param body_elements: List of text elements (strings or pre-formatted elements)
    :param actions: List of action dictionaries (buttons)
    :param url: The msteams webhook url
    """
    _url = url or WEBHOOK_URL
    if not _url:
        raise ValueError(
            "No webhook URL provided. Pass 'url' parameter or set WEBHOOK_URL environment variable."
        )
    # Construct body
    body = [blocks.title(title)]
    for element in body_elements:
        if isinstance(element, str):
            body.append(blocks.title(element))
        else:
            body.append(element)

    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": body,
                    "actions": actions or [],
                },
            }
        ],
    }

    # Send request
    kwargs = {"headers": {"Content-Type": "application/json"}, "data": json.dumps(payload)}
    if isinstance(request_kwargs, dict):
        kwargs.update(request_kwargs)
    response = requests.post(_url, **kwargs)
    response.raise_for_status()

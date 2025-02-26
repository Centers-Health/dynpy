import json
import os

import requests
from django.conf import settings

from . import blocks

WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def post_to_teams_channel(
    title: str, body_elements: list, actions: list | None = None, url: str | None = None
) -> None:
    """
    Posts an adaptive card message to Microsoft Teams

    :param title: Title of the card
    :param body_elements: List of text elements (strings or pre-formatted elements)
    :param actions: List of action dictionaries (buttons)
    :param url: The msteams webhook url
    """
    _url = WEBHOOK_URL or url or settings.DJANGO_ERRONEOUS_TEAMS_CONNECTOR_URL
    # Construct body
    body = [blocks.title(title)]
    for element in body_elements:
        if isinstance(element, str):
            body.append(blocks.title(element))
        else:
            body.append(element)

    # Build adaptive card payload
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
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
    headers = {"Content-Type": "application/json"}
    response = requests.post(_url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()

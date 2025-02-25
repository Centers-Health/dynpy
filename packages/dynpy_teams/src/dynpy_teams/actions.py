def openurl_action(title: str, url: str) -> dict:
    return {"type": "Action.OpenUrl", "title": title, "url": url}

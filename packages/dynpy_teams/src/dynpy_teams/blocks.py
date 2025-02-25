def raw_text(text: str, **kwargs) -> dict:
    return {"type": "TextBlock", "text": text, **kwargs}


def title(title: str) -> dict:
    return {"type": "TextBlock", "text": title, "weight": "bolder", "size": "large", "wrap": True}


def text(text: str) -> dict:
    return {"type": "TextBlock", "text": text, "wrap": True}

from typing import Any


def deep_get(dictionary: dict, keys: str | list, default=None) -> Any:
    """
    Retrieve a value from a nested dictionary or list using a dotted path string or a list of keys/indices.
    Returns the default value if any key or index is not found.

    Args:
        dictionary (dict): The dictionary (or dictionary-list mix) to retrieve the value from.
        keys (str | list): A dotted string or list of keys/indices to navigate the nested structure.
        default (Any): The value to return if the key or index is not found. Defaults to None.

    Returns:
        Any: The value found at the specified path, or the default value if not found.

    Examples:
        >>> deep_get({"a": {"b": {"c": 1}}}, "a.b.c")
        1
        >>> deep_get({"a": {"b": {"c": 1}}}, ["a", "b", "c"])
        1
        >>> deep_get({"a": [{"b": 2}]}, "a.0.b")
        2
        >>> deep_get({"a": {"b": None}}, "a.b.d", "default")
        'default'
    """
    keys = keys.split(".") if isinstance(keys, str) else keys

    for key in keys:
        if isinstance(dictionary, dict):
            dictionary = dictionary.get(key, default)
        elif isinstance(dictionary, list):
            try:
                key = int(key)
                dictionary = dictionary[key]
            except (ValueError, IndexError, TypeError):
                return default
        else:
            return default

    return dictionary

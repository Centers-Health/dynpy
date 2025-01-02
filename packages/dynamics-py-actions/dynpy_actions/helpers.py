from typing import Dict, List

from django.apps import apps
from django.db.models.base import Model

from dynpy_actions.exceptions import ActionNotFoundException


def serialize(item):
    if isinstance(item, Model):
        return f"model_instance___{item._meta.app_label}___{item._meta.model_name}___{item.pk}"
    else:
        return str(item)


def serialize_kwargs(_prefix="", **kwargs) -> Dict:
    """
    Serializes kwargs that are passed into template.
    An Object becomes model_instance_{app_label}_{model}_{PK}
    """
    serialized_kwargs = {}
    for key, value in kwargs.items():
        value = serialize(value)
        serialized_kwargs[_prefix + str(key)] = value
    return serialized_kwargs


def serialize_args(*args) -> List:
    """
    Serializes kwargs that are passed into template.
    An Object becomes model_instance_{app_label}_{model}_{PK}
    """
    serialized_args = []
    for item in args:
        item = serialize(item)
        serialized_args.append(item)
    return serialized_args


def deserialize_kwargs(_prefix="", **kwargs):
    """
    Deserializes kwargs that were serialized.
    Goes from model_instance_{app_label}_{model}_{PK} to Object.
    """
    deserialized_kwargs = {}
    for key, value in kwargs.items():
        key = key.removeprefix(_prefix)
        if isinstance(value, str):
            if value.startswith("model_instance___"):
                _, app_label, model, pk = value.split("___")
                model = apps.get_model(app_label, model)
                model_instance = model.objects.get(pk=pk)
                deserialized_kwargs[(key.replace("action_", "", 1))] = model_instance
            else:
                value = False if value == "False" else True if value == "True" else value
                deserialized_kwargs[(key.replace("action_", "", 1))] = value
        else:
            deserialized_kwargs[key] = value
    return deserialized_kwargs


def flatten_kwargs(**kwargs) -> dict:
    """
    Takes a dict of lists and flattens it.
    i.e. k:[v] becomes k:v
    """
    return {k: v[0] for k, v in kwargs.items()}


def validate_action(context, action):
    if not context.get("actions"):
        raise ActionNotFoundException(
            """Actions missing from the context. Did you forget
            to add ViewActionsMixin to the view's inheritance?""",
        )
    if not hasattr(action, "name") or not context.get("actions").get(action.name):
        actions = "\n" + "\n".join(sorted(context["actions"].keys()))
        raise ActionNotFoundException(
            f"{action} is not a valid action. Must be one of these: {actions}",
        )

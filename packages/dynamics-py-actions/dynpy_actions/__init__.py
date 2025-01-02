"""
The Actions module enables update / create behavior (form behavior) to
be be added to any view and not be coupled with that view. The behavior
is handled by the action and does not need to be implemented in the view.

i.e. A modal form can be easily implemented as an action by setting embed_type
on the action to MODAL. The post will be handled by the action's handle method.
None of this needs to be handled by the view.

To install in a project:
    1. Load actions.js the base.html of the project
    2. Add dynpy_actions to the list of installed apps
"""
from .generic_actions import DeleteAction, GenericCreateUpdateAction

__all__ = ["DeleteAction", "GenericCreateUpdateAction"]

__version__ = "6.0.0"

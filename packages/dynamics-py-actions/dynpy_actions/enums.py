from enum import Enum


class EmbedType(Enum):
    """
    Used to set embed types for GenericFilterList actions
    """

    INLINE = "Inline"
    MODAL = "Modal"
    TARGET = "Target"
    BASE = "Base"


class ModalSize(Enum):
    SMALL = "modal-sm"
    DEFAULT = ""
    LARGE = "modal-lg"
    EXTRA_LARGE = "modal-xl"

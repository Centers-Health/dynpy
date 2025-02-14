import enum
from enum import Enum

from django.db import models
from django.db.models.enums import Choices, TextChoices
from django.utils.functional import Promise


class ChoicesWithKwargsMeta(models.enums.ChoicesMeta):
    """
    A metaclass for creating enum choices that also have extra kwargs.

    The class extends from Django's meta class but overrides the __new__ function
    which adds all the keywords as properties of the class members.

    To use this class you can add a dict as the THIRD value of each enum member.
    For example: ENUM_MEMBER = "a value", "a label", {"kwarg1": "value1", "kwarg2": "value2"}
    Each enum member must have all the same keyword arguments.
    """

    def __new__(metacls, classname, bases, classdict, **kwds):
        list_of_kwargs = []
        labels = []
        for key in classdict._member_names:
            value = classdict[key]
            kwargs = None
            if (
                isinstance(value, (list, tuple))
                and len(value) > 2
                and isinstance(value[1], (Promise, str))
                and isinstance(value[2], dict)
            ):
                *value, label, kwargs = value
                value = tuple(value)
            elif (
                isinstance(value, (list, tuple))
                and len(value) == 2
                and isinstance(value[-1], (Promise, str))
            ):
                *value, label = value
                value = tuple(value)
            else:
                label = key.replace("_", " ").title()
            labels.append(label)
            if kwargs:
                list_of_kwargs.append(kwargs)
            # Use dict.__setitem__() to suppress defenses against double
            # assignment in enum's classdict.
            dict.__setitem__(classdict, key, value)
        # call super to create cls
        cls = super().__new__(metacls, classname, bases, classdict, **kwds)
        # add labels to class members
        cls._value2label_map_ = dict(zip(cls._value2member_map_, labels))
        # Add a label property to instances of enum which uses the enum member
        # that is passed in as "self" as the value to use when looking up the
        # label in the choices.
        cls.label = property(lambda self: cls._value2label_map_.get(self.value))
        # add kwargs to members
        if list_of_kwargs:
            if not all(element.keys() == list_of_kwargs[0].keys() for element in list_of_kwargs):
                raise KeyError(
                    "Keywords do not match. "
                    + "When using kwargs all members of the Enum must have the same kwargs"
                )
            for kwarg in list_of_kwargs[0]:

                def set_value2kwargvaluelist_map_(kwarg, _value2kwargvaluelist_map_):
                    # Has to be a function to avoid late binding (otherwise it binds kwarg to the last
                    # value of the loop due to how python handles closure with late binding)
                    # https://stackoverflow.com/questions/62414299/python-lambda-functions-defined-in-a-loop-end-up-pointing-to-the-same-operation
                    setattr(
                        cls,
                        kwarg,
                        property(lambda self: _value2kwargvaluelist_map_.get(self.value)),
                    )

                kwarg_value_list = [kwargs[kwarg] for kwargs in list_of_kwargs]
                cls._value2kwargvaluelist_map_ = dict(zip(cls._value2member_map_, kwarg_value_list))

                # See comment above for why this is a function
                set_value2kwargvaluelist_map_(kwarg, cls._value2kwargvaluelist_map_)

        cls.do_not_call_in_templates = True
        return enum.unique(cls)


class ChoicesWithKwargs(Choices, metaclass=ChoicesWithKwargsMeta):
    """
    Class for creating enumerated choices with keyword arguments.
    """

    pass


class TextChoicesWithKwargs(ChoicesWithKwargs, TextChoices):
    """
    Class for creating enumerated string choices with keyword arguments.
    """

    pass


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"


class RoundingDirection(models.TextChoices):
    UP = "Up"
    DOWN = "Down"

import pytest
from dynpy.enums import TextChoicesWithKwargs


def test_kwargs_are_converted_to_properties():
    class DummyTextEnumWithKwargs(TextChoicesWithKwargs):
        CHOICE_A = "a", "A", {"kwargKey1": "kwargValA"}

    assert DummyTextEnumWithKwargs.CHOICE_A.kwargKey1 == "kwargValA"


def test_inherited_enum_properties_work_when_enum_has_kwargs():
    class DummyTextEnumWithKwargs(TextChoicesWithKwargs):
        CHOICE_A = "a", "A", {"kwargKey1": "kwargValA"}

    choice_a = DummyTextEnumWithKwargs.CHOICE_A

    assert choice_a.label == "A"
    assert choice_a.value == "a"
    assert choice_a.name == "CHOICE_A"


def test_inherited_enum_properties_work_when_enum_does_not_have_kwargs():
    class DummyTextEnumWithKwargs(TextChoicesWithKwargs):
        CHOICE_A = "a", "A"

    choice_a = DummyTextEnumWithKwargs.CHOICE_A

    assert choice_a.label == "A"
    assert choice_a.value == "a"
    assert choice_a.name == "CHOICE_A"


def test_raises_error_if_kwargs_keys_for_choices_do_not_match():
    with pytest.raises(KeyError) as e:

        class DummyTextEnumWithKwargs(TextChoicesWithKwargs):
            CHOICE_A = "a", "A", {"kwargKey1": "kwargValA"}
            CHOICE_B = "b", "B", {"kwargKey2": "kwargValB"}

    assert "Keywords do not match" in str(e.value)


def test_does_not_raise_error_if_kwargs_keys_for_choices_do_match():
    class DummyTextEnumWithKwargs(TextChoicesWithKwargs):
        CHOICE_A = "a", "A", {"kwargKey1": "kwargValA"}
        CHOICE_B = "b", "B", {"kwargKey1": "kwargValB"}

from datetime import date, datetime, timezone

import pytest
from dynpy import masking
from dynpy.masking import (
    STRATEGIES,
    MaskingCommandMixin,
    mask_cin,
    mask_date_keep_year,
    mask_dict,
    mask_digits,
    mask_email,
    mask_first_name,
    mask_medicare,
    mask_phone,
    mask_row,
    mask_rows,
    mask_ssn,
    mask_zip_keep3,
    masking_enabled,
)


@pytest.fixture
def _dev_env(settings):
    """Masking is active: dev environment, not testing."""
    settings.DJANGO_ENV = "dev"
    settings.TESTING = False


class Row:
    """Stand-in for a mutable pyodbc row."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def describe_masking_enabled():
    def is_off_under_tests(settings):
        settings.DJANGO_ENV = "dev"
        settings.TESTING = True
        assert not masking_enabled()

    @pytest.mark.parametrize("env", ["prod", "qa", "testing", ""])
    def is_off_outside_dev(settings, env):
        settings.DJANGO_ENV = env
        settings.TESTING = False
        assert not masking_enabled()

    def is_on_in_dev(_dev_env):
        assert masking_enabled()


def describe_strategies():
    def nulls_stay_null():
        for strategy in STRATEGIES.values():
            assert strategy(None) is None
            assert strategy("") == ""

    def is_deterministic():
        assert mask_first_name("John") == mask_first_name("John")
        assert mask_cin("AB12345C") == mask_cin("AB12345C")
        assert mask_first_name("John") != mask_first_name("Paul")

    def never_returns_the_original():
        for value in ("John", "jdoe@example.org", "123-45-6789", "POL123"):
            assert mask_first_name(value) != value
            assert mask_email(value) != value
            assert mask_ssn(value) != value
            assert mask_digits(value) != value

    def id_strategies_are_pure_hash_arithmetic():
        """
        Identifier-shaped fakes never depend on Faker — matching logic
        (CIN <-> medicaid_number, medicare/medicaid fallbacks) relies on
        them being stable across processes and library versions.
        """
        assert mask_cin("AB12345C") == "TA44122E"
        assert mask_digits("POL123") == "764846772"
        assert mask_email("jdoe@centershealthcare.org") == "user56bc52c322@example.com"

    def ssn_uses_never_issued_area_and_keeps_dashes():
        dashed = mask_ssn("123-45-6789")
        assert len(dashed) == 11
        assert dashed.count("-") == 2
        assert 900 <= int(dashed[:3]) <= 999
        plain = mask_ssn("123456789")
        assert len(plain) == 9
        assert plain.isdigit()
        assert 900 <= int(plain[:3]) <= 999

    def phone_uses_fictional_exchange():
        assert mask_phone("9171234567").startswith("212-555-")

    def zip_keeps_first_three_digits():
        assert mask_zip_keep3("11230") == "11200"
        assert mask_zip_keep3("11230-1234") == "11200"

    def medicare_is_mbi_shaped():
        assert len(mask_medicare("1EG4-TE5-MK73")) == 11

    def dob_keeps_year_only():
        assert mask_date_keep_year(date(1990, 5, 14)) == date(1990, 1, 1)
        assert mask_date_keep_year("1990-05-14") == "1990-01-01"
        masked_dt = mask_date_keep_year(datetime(1990, 5, 14, 8, 30, tzinfo=timezone.utc))
        assert masked_dt == datetime(1990, 1, 1, tzinfo=timezone.utc)

    def dob_aggregates_ages_90_and_above():
        today = date.today()
        masked = mask_date_keep_year(date(today.year - 95, 6, 1))
        assert masked == date(today.year - 90, 1, 1)


def describe_mask_rows():
    RULES = {"FirstName": "first_name", "SSN": "ssn", "DOB": "dob"}

    def masks_in_place_when_enabled(_dev_env):
        rows = [Row(FirstName="John", SSN="123-45-6789", DOB=date(1990, 5, 14), Other="keep")]
        result = mask_rows(rows, RULES)
        assert result[0] is rows[0]
        assert result[0].FirstName != "John"
        assert result[0].SSN != "123-45-6789"
        assert date(1990, 1, 1) == result[0].DOB
        assert result[0].Other == "keep"

    def passes_through_outside_dev(settings):
        settings.DJANGO_ENV = "prod"
        settings.TESTING = False
        rows = [Row(FirstName="John")]
        assert mask_rows(rows, RULES)[0].FirstName == "John"

    def skips_fields_missing_from_the_row(_dev_env):
        row = Row(FirstName="John")  # no SSN / DOB attributes
        assert mask_row(row, RULES).FirstName != "John"

    def rejects_unknown_strategy_names(_dev_env):
        with pytest.raises(ValueError, match="Unknown masking strategy"):
            mask_rows([Row(FirstName="John")], {"FirstName": "nope"})

    def accepts_callables(_dev_env):
        rows = mask_rows([Row(FirstName="John")], {"FirstName": lambda v: "X"})
        assert rows[0].FirstName == "X"


def describe_mask_dict():
    def masks_matching_keys_when_enabled(_dev_env):
        data = {"firstName": "John", "ssn": "123456789", "gender": "M"}
        masked = mask_dict(data, {"firstName": "first_name", "ssn": "ssn"})
        assert masked["firstName"] != "John"
        assert masked["ssn"] != "123456789"
        assert masked["gender"] == "M"

    def passes_through_outside_dev(settings):
        settings.DJANGO_ENV = "qa"
        settings.TESTING = False
        data = {"firstName": "John"}
        assert mask_dict(data, {"firstName": "first_name"})["firstName"] == "John"


def describe_masking_command_mixin():
    class FakeCommand(MaskingCommandMixin):
        mask_fields = {"FirstName": "first_name", "LastName": "last_name"}

    def applies_declared_mask_fields(_dev_env):
        rows = FakeCommand().apply_masking([Row(FirstName="John", LastName="Smith")])
        assert rows[0].FirstName != "John"
        assert rows[0].LastName != "Smith"

    def no_mask_fields_is_a_noop(_dev_env):
        class Bare(MaskingCommandMixin):
            pass

        rows = Bare().apply_masking([Row(FirstName="John")])
        assert rows[0].FirstName == "John"

    def respects_custom_salt(_dev_env, settings):
        h_default = masking._h("John")
        settings.MASKING_SALT = "another-salt"
        assert masking._h("John") != h_default
        settings.MASKING_SALT = "chc-mask-v1"
        assert masking._h("John") == h_default

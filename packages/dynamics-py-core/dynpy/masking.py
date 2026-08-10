"""
HIPAA PHI masking for data imported from external systems in dev environments.

When a developer machine runs an import command (stored procedures, external
APIs), real PHI must not land in the local database. This module provides:

- ``masking_enabled()`` — masking is active only when ``settings.DJANGO_ENV``
  is ``"dev"`` and tests are not running. Prod/qa are untouched.
- Deterministic field strategies (``mask_first_name``, ``mask_ssn``, ...) —
  the same real value always maps to the same fake value across commands,
  runs, and repos, so cross-command matching (e.g. residents matched by
  name/DOB) keeps working.
- ``MaskingCommandMixin`` — management commands declare which row fields to
  mask via a ``mask_fields`` mapping and call ``apply_masking()`` on fetched
  rows.

Determinism contract: these strategies intentionally replicate the SQL
masking used by the chc-cli seed command: same salt, same 48-bit md5 hash,
and the same frozen value pools (dynpy.masking_pools). A database seeded
from a masked dump and rows masked here therefore produce IDENTICAL fakes
for the same real value — resident matching by name/DOB keeps working
against seeded data. Do not change the salt, the hash, or the pools without
changing them everywhere.

All strategies preserve ``None`` and empty strings.
"""

import hashlib
from collections.abc import Callable, Iterable
from datetime import date, datetime, time
from typing import Any

from django.conf import settings

from dynpy import masking_pools

MASKING_SALT_SETTING = "MASKING_SALT"
DEFAULT_MASKING_SALT = "chc-mask-v1"


def masking_enabled() -> bool:
    """
    PHI masking is active only on dev environments, never in prod/qa/tests.
    """
    return getattr(settings, "DJANGO_ENV", "") == "dev" and not getattr(settings, "TESTING", False)


def _salt() -> str:
    return getattr(settings, MASKING_SALT_SETTING, DEFAULT_MASKING_SALT)


def _h(value: Any) -> int:
    """
    Deterministic 48-bit hash of the salted value.

    Matches the SQL implementation used at seed time:
    ('x' || substr(md5(salt || ':' || val), 1, 12))::bit(48)::bigint
    """
    digest = hashlib.md5(f"{_salt()}:{value}".encode()).hexdigest()  # noqa: S324
    return int(digest[:12], 16)


def _hex(value: Any, length: int) -> str:
    return hashlib.md5(f"{_salt()}:{value}".encode()).hexdigest()[:length]  # noqa: S324


def _letter(n: int) -> str:
    return chr(65 + (n % 26))


_POOLS: dict[str, tuple[str, ...]] = {
    "first_names": masking_pools.FIRST_NAMES,
    "last_names": masking_pools.LAST_NAMES,
    "streets": masking_pools.STREETS,
    "cities": masking_pools.CITIES,
    "counties": masking_pools.COUNTIES,
}


def _skip(value: Any) -> bool:
    """Masking never touches NULLs or empty strings."""
    return value is None or value == ""


def _pick(value: Any, pool_name: str) -> str:
    pool = _POOLS[pool_name]
    return pool[_h(value) % len(pool)]


def mask_first_name(value: Any) -> Any:
    return value if _skip(value) else _pick(value, "first_names")


def mask_last_name(value: Any) -> Any:
    return value if _skip(value) else _pick(value, "last_names")


def mask_full_name(value: Any) -> Any:
    if _skip(value):
        return value
    return f"{mask_first_name(value)} {mask_last_name(value)}"


def mask_email(value: Any) -> Any:
    if _skip(value):
        return value
    return f"user{_hex(value, 10)}@example.com"


def mask_phone(value: Any) -> Any:
    """212-555-XXXX — the 555 exchange is reserved for fictional use."""
    if _skip(value):
        return value
    return f"212-555-{_h(value) % 10_000:04d}"


def mask_ssn(value: Any) -> Any:
    """
    9 digits in the never-issued 900+ area. Keeps dashes if the input had them.
    """
    if _skip(value):
        return value
    h = _h(value)
    area = 900 + h % 100
    group = (h >> 8) % 100
    serial = (h >> 16) % 10_000
    if isinstance(value, str) and "-" in value:
        return f"{area:03d}-{group:02d}-{serial:04d}"
    return f"{area:03d}{group:02d}{serial:04d}"


def mask_zip_keep3(value: Any) -> Any:
    """Safe Harbor: keep only the first 3 digits of a ZIP code."""
    if _skip(value):
        return value
    return f"{str(value)[:3]}00"


def mask_street(value: Any) -> Any:
    return value if _skip(value) else _pick(value, "streets")


def mask_address(value: Any) -> Any:
    if _skip(value):
        return value
    return f"{_h(value) % 9899 + 100} {mask_street(value)}"


def mask_city(value: Any) -> Any:
    return value if _skip(value) else _pick(value, "cities")


def mask_county(value: Any) -> Any:
    return value if _skip(value) else _pick(value, "counties")


def mask_date_keep_year(value: Any) -> Any:
    """
    Safe Harbor for dates of birth: keep the year only (Jan 1), and collapse
    ages 90+ into a single bucket. Accepts date/datetime/ISO strings.
    """
    if _skip(value):
        return value
    original = value
    if isinstance(value, str):
        value = datetime.strptime(value[:10], "%Y-%m-%d").date()
    elif isinstance(value, datetime):
        value = value.date()
    today = date.today()
    try:
        cutoff = today.replace(year=today.year - 89)
    except ValueError:  # Feb 29
        cutoff = today.replace(year=today.year - 89, day=28)
    masked = date(today.year - 90, 1, 1) if value < cutoff else date(value.year, 1, 1)
    if isinstance(original, str):
        return masked.isoformat()
    if isinstance(original, datetime):
        return datetime.combine(masked, time.min, tzinfo=original.tzinfo)
    return masked


def mask_cin(value: Any) -> Any:
    """NY Medicaid CIN shape: two letters, five digits, one letter."""
    if _skip(value):
        return value
    h = _h(value)
    return f"{_letter(h)}{_letter(h >> 5)}{(h >> 10) % 100_000:05d}{_letter(h >> 27)}"


def mask_medicare(value: Any) -> Any:
    """Medicare MBI-shaped identifier (11 characters)."""
    if _skip(value):
        return value
    h = _h(value)
    return (
        f"{h % 9 + 1}{_letter(h >> 4)}{_letter(h >> 9)}{(h >> 14) % 100:02d}"
        f"{_letter(h >> 21)}{(h >> 26) % 100:02d}{_letter(h >> 33)}"
        f"{_letter(h >> 38)}{(h >> 43) % 10}"
    )


def mask_digits(value: Any, length: int = 9) -> Any:
    """Fixed-length digit string (policy/auth numbers, MRNs, EEIDs, ...)."""
    if _skip(value):
        return value
    return f"{_h(value) % 10**length:0{length}d}"


def mask_id(value: Any) -> Any:
    return mask_digits(value, 9)


def mask_text(value: Any) -> Any:
    """Free text (notes, messages) is replaced with a placeholder."""
    return value if _skip(value) else "[masked]"


STRATEGIES: dict[str, Callable[[Any], Any]] = {
    "first_name": mask_first_name,
    "last_name": mask_last_name,
    "full_name": mask_full_name,
    "email": mask_email,
    "phone": mask_phone,
    "ssn": mask_ssn,
    "zip": mask_zip_keep3,
    "street": mask_street,
    "address": mask_address,
    "city": mask_city,
    "county": mask_county,
    "dob": mask_date_keep_year,
    "cin": mask_cin,
    "medicare": mask_medicare,
    "id": mask_id,
    "mrn": lambda value: mask_digits(value, 6),
    "room": lambda value: mask_digits(value, 3),
    "text": mask_text,
}

MaskRules = dict[str, "Callable[[Any], Any] | str"]


def _resolve(strategy: "Callable[[Any], Any] | str") -> Callable[[Any], Any]:
    if callable(strategy):
        return strategy
    try:
        return STRATEGIES[strategy]
    except KeyError:
        raise ValueError(f"Unknown masking strategy {strategy!r}. Known: {sorted(STRATEGIES)}") from None


def mask_row(row: Any, rules: MaskRules) -> Any:
    """
    Mask a single row IN PLACE (pyodbc rows are mutable) and return it.

    Fields missing from the row are skipped, so shared rules survive minor
    SP shape differences.
    """
    for field, strategy in rules.items():
        if hasattr(row, field):
            setattr(row, field, _resolve(strategy)(getattr(row, field)))
    return row


def mask_rows(rows: Iterable[Any], rules: MaskRules) -> list[Any]:
    """Mask an iterable of rows in place; always returns a list."""
    rows = list(rows)
    if not rules or not masking_enabled():
        return rows
    for row in rows:
        mask_row(row, rules)
    return rows


def mask_dict(data: dict, rules: MaskRules) -> dict:
    """Mask a dict (e.g. a GraphQL/REST payload) in place and return it."""
    if not rules or not masking_enabled():
        return data
    for field, strategy in rules.items():
        if field in data:
            data[field] = _resolve(strategy)(data[field])
    return data


class MaskingCommandMixin:
    """
    Adds dev-environment PHI masking to a management command.

    Usage::

        class Command(MaskingCommandMixin, LoggingCommand):
            mask_fields = {
                "FirstName": "first_name",
                "LastName": "last_name",
                "SSN": "ssn",
                "DOB": "dob",
            }

            def run(self, *args, **options):
                rows = self.apply_masking(cursor.fetchall())

    ``mask_fields`` maps row attribute names to a strategy name from
    ``STRATEGIES`` (or any callable). Masking only runs when
    ``masking_enabled()`` is true — prod/qa/tests see the rows unchanged.
    """

    mask_fields: MaskRules = {}

    def apply_masking(self, rows: Iterable[Any]) -> list[Any]:
        return mask_rows(rows, self.mask_fields)

    def apply_dict_masking(self, data: dict, rules: MaskRules | None = None) -> dict:
        return mask_dict(data, self.mask_fields if rules is None else rules)

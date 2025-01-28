import pytest
from semantic_python_monorepo import utils


@pytest.mark.parametrize(
    ("version", "_type", "expected"),
    [
        ("1.0.0", "major", "2.0.0"),
        ("1.1.0", "major", "2.0.0"),
        ("0.1.0", "major", "1.0.0"),
        ("0.1.0", "minor", "0.2.0"),
        ("0.1.1", "minor", "0.2.0"),
        ("0.1.1", "patch", "0.1.2"),
        ("0.1.1", None, "0.1.2"),
        # Handle cases with short value
        ("0", "minor", "0.1.0"),
        ("0", "patch", "0.0.1"),
        ("0.1", "minor", "0.2.0"),
        ("0.1", "major", "1.0.0"),
        # Invalid cases
        ("0.1.0.0", "major", (ValueError, "Version invalid")),
        ("", "major", (ValueError, "Version invalid")),
        (0, "major", (AssertionError, None)),
        (False, "major", (AssertionError, None)),
    ],
)
def test_version_bump_should_bump_the_appropriate_version_based_on_semver_convention(
    version,
    _type,  # noqa: PT019
    expected,
):
    """Test version bump should bump the appropriate version based on semver convention"""
    if isinstance(expected, tuple):
        with pytest.raises(expected[0], match=expected[1]):
            assert utils.version_bump(version, _type) == expected
    else:
        assert utils.version_bump(version, _type) == expected

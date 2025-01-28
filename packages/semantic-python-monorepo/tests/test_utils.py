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


@pytest.mark.parametrize(
    ("bump1", "bump2", "expected"),
    [
        # same cases
        ("major", "major", "major"),
        ("minor", "minor", "minor"),
        ("patch", "patch", "patch"),
        # major cases
        ("major", "patch", "major"),
        ("major", "minor", "major"),
        ("minor", "major", "major"),
        ("patch", "major", "major"),
        # minor cases
        ("minor", "patch", "minor"),
        ("patch", "minor", "minor"),
        # none cases
        (None, "major", "major"),
        (None, "minor", "minor"),
        (None, "patch", "patch"),
        ("major", None, "major"),
        ("minor", None, "minor"),
        ("patch", None, "patch"),
    ],
)
def test_max_bump(
    bump1,
    bump2,  # noqa: PT019
    expected,
):
    """Test version bump should bump the appropriate version based on semver convention"""
    if isinstance(expected, tuple):
        with pytest.raises(expected[0], match=expected[1]):
            assert utils.max_bump(bump1, bump2) == expected
    else:
        assert utils.max_bump(bump1, bump2) == expected


@pytest.mark.parametrize(
    ("msg", "expected"),
    [
        ("feat: a feature", "minor"),
        ("perf: a feature", "minor"),
        ("feat:a feature", "minor"),
        ("bug:a feature", "patch"),
        ("fix:a feature", "patch"),
        ("fix!: a feature", "major"),
        ("fix: a fea!ture", "patch"),
        ("regression: a fea!ture", "patch"),
        ("test: a fea!ture", "patch"),
        ("fix: a fea!ture\n\nBREAKING CHANGES", "major"),
        ("docs: something", None),
        ("chore: something", None),
        ("build: something", None),
        ("ci: something", None),
        ("feat(package): sjomething", "minor"),
        ("bug(package): sjomething", "patch"),
        ("bug(package)!: sjomething", "major"),
        ("this is not conventional commit", None),
    ],
)
def test_get_bump_from_commit_msg(msg, expected):
    assert utils.get_bump_from_commit_msg(msg=msg) == expected


def test_format_git_tag():
    assert utils.format_git_tag("package-name", "1.0.1") == "package-name-v1.0.1"

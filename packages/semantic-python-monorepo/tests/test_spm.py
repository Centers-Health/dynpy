import pytest

# NOTE: This testfile is like a smoketest / integration test of the whole suite


@pytest.mark.skip(reason="Fixtures don't seem to work on CI environment")
@pytest.mark.usefixtures("with_packages")
def test_can_find_registry(spm):
    result = spm.registry()
    assert "3 packages found" in result
    assert "app1 (0.1.0)" in result
    assert "app2 (0.1.0)" in result


@pytest.mark.skip(reason="Fixtures don't seem to work on CI environment")
@pytest.mark.usefixtures("with_packages")
def test_can_analyze(spm):
    result = spm.analyze()
    assert "app2 (0.1.0 -> 0.2.0)" in result
    assert "feat: add app2" in result
    assert "app1 (0.1.0 -> 0.2.0)" in result
    assert "feat: add app1" in result


@pytest.mark.skip(reason="Fixtures don't seem to work on CI environment")
@pytest.mark.usefixtures("with_packages")
def test_full_run_through_dry(spm):
    result = spm.run(["--dry-run"])
    assert "app2 (0.1.0 -> 0.2.0)" in result
    assert "feat: add app2" in result
    assert "app1 (0.1.0 -> 0.2.0)" in result
    assert "feat: add app1" in result
    assert "Publish Packages (app2, app1)" in result


# TODO: add one more integration test that tests that all things are done
# - New commit is made
# - Tags are made and pushed to origin
# - Don't assert on the output, assert on the directory state
# - (would need a demo registry setup, can make a session fixture that runs a docker container with the registry on it. maybe https://pypi.org/project/pytest-mock-server/ instead. CI would be complicated to do docker.)

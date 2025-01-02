from dynpy import enums


def test_that_status_has_the_right_values() -> None:
    assert enums.Status.PASS.value == "PASS"
    assert enums.Status.FAIL.value == "FAIL"
    assert enums.Status.WARN.value == "WARN"

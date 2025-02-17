from dynpy_cas.apps import DynpyConfig


def test_it_should_have_the_correct_information():
    """It should have the correct information"""
    assert DynpyConfig.name == "dynpy_cas"
    assert DynpyConfig.verbose_name == "Dynamics-Py-Cas"

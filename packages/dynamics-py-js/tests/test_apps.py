from dynpy_js.apps import DynpyJSConfig


def test_it_has_correct_name():
    """It should have the correct information"""
    assert DynpyJSConfig.name == "dynpy_js"
    assert DynpyJSConfig.verbose_name == "Dynamics Py JS"

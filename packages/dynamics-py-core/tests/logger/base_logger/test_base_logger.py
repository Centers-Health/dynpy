from dynpy.logger.base import BaseLogger


def test_that_properties_are_set():
    logger = BaseLogger(app_name="dynpy.logger")
    assert logger.app_name == "dynpy.logger"

import pytest
from dynpy.dw import DWConnector

facilities_sp = "{CALL p_PayrollFacilityGetList}"
aging_sp = "{CALL usp_Refresh_NamiPrivate_Aging_4}"
namis_sp = "{CALL p_GetNamiAmountsByFacilityResidentMonth(?,?)}"


@pytest.fixture(autouse=True)
def add_settings_for_DWConnector(settings):
    settings.DW_SERVER = "server"
    settings.DW_DRIVER = "driver"
    settings.DW_USERNAME = "test"
    settings.DW_PASSWORD = "0"
    settings.DW_DATABASE = "database"


def test_can_mock_single_SP_that_does_not_take_additional_args(mock_sp):
    mock_facility_data = ["mock facility"]
    mock_sp(sp=facilities_sp, data=mock_facility_data)
    facilities = DWConnector.run_sp(facilities_sp).fetchall()
    assert facilities == mock_facility_data


def test_can_mock_multiple_SPs_that_do_not_take_additional_args(mock_sp):
    mock_facility_data = ["mock facility"]
    mock_aging_data = ["mock aging"]

    mock_sp(sp=facilities_sp, data=mock_facility_data)
    mock_sp(sp=aging_sp, data=mock_aging_data)

    facilities = DWConnector.run_sp(facilities_sp).fetchall()
    aging = DWConnector.run_sp(aging_sp).fetchall()

    assert facilities == mock_facility_data
    assert aging == mock_aging_data


def test_can_do_global_mock_of_SP_that_takes_additional_args(mock_sp):
    """
    Test that a global mock can be made for an SP that takes additional arguments, regardless of what
    arguments are passed to that SP
    """
    mock_nami_data = ["mock nami"]
    mock_sp(sp=namis_sp, data=mock_nami_data)
    namis = DWConnector.run_sp(namis_sp).fetchall()
    assert namis == mock_nami_data

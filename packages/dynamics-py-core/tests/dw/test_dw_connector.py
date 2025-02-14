import contextlib

import pyodbc
import pytest
from django.db import models
from dynpy.dw import DWConnector
from dynpy.erroneous.models import Error


class SP(models.TextChoices):
    FACILITIES = "{CALL p_PayrollFacilityGetList}"
    NAMIS = "{CALL p_GetNamiAmountsByFacilityResidentMonth(?,?)}"


def test_runs_sp_without_args(mock_sp):
    mock_sp(sp=SP.FACILITIES, data=[])
    dw = DWConnector()
    facilities = dw.run_sp(SP.FACILITIES).fetchall()
    assert type(facilities) == list


def test_runs_sp_with_args(mock_sp):
    mock_sp(sp=SP.NAMIS, data=[])
    dw = DWConnector()
    namis = dw.run_sp(SP.NAMIS, (1, 1)).fetchall()
    assert type(namis) == list


@pytest.mark.django_db
def test_run_sp_raises_connection_errors(mocker):
    mocker.patch("pyodbc.connect", side_effect=pyodbc.Error("1234", "Error 1234"))
    with pytest.raises(pyodbc.Error):
        DWConnector().run_sp(SP.NAMIS, (1, 1))


@pytest.mark.django_db
def test_run_sp_logs_connection_errors(mocker):
    mocker.patch("pyodbc.connect", side_effect=pyodbc.Error("1234", "Error 1234"))
    with contextlib.suppress(pyodbc.Error):
        DWConnector().run_sp(SP.NAMIS, (1, 1))
    log = Error.objects.last()
    assert "Error 1234" in log.data


@pytest.mark.django_db
def test_run_sp_raises_execute_errors(mocker):
    mocker.patch("pyodbc.connect", side_effect=pyodbc.Error("1234", "Error 1234"))
    with pytest.raises(pyodbc.Error):
        DWConnector().run_sp(SP.NAMIS, (1))


@pytest.mark.django_db
def test_run_sp_logs_execute_errors(mocker):
    mocker.patch("pyodbc.connect", side_effect=pyodbc.Error("1234", "Error 1234"))
    with contextlib.suppress(pyodbc.Error):
        DWConnector().run_sp(SP.NAMIS, (1))
    log = Error.objects.last()

    assert "Error 1234" in log.data

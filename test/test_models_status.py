"""Tests of the status model on a real response of the machine."""

import dataclasses
from typing import Any

import pytest

from fixture_loader import load_fixture
from gaggiuino_api.enums import OperationMode
from gaggiuino_api.exceptions import GaggiuinoResponseFormatError
from gaggiuino_api.models.status import Status

FIELDS = dataclasses.fields(Status)
OPTIONAL = [f.metadata["alias"] for f in FIELDS if f.default is not dataclasses.MISSING]
REQUIRED = [f.metadata["alias"] for f in FIELDS if f.default is dataclasses.MISSING]


def _raw(**changes: object) -> dict[str, Any]:
    data: dict[str, Any] = load_fixture("status")[0]
    data.update(changes)
    return data


def test_fixture_is_parsed():
    raw = _raw()
    status = Status.from_api(raw)
    assert type(status.up_time) is int
    assert status.up_time == int(raw["upTime"])
    assert status.temperature == pytest.approx(20.786776)
    assert type(status.pump_flow) is float
    assert status.profile_name == "_OFF"
    assert status.operation_mode is OperationMode.HOME
    assert status.startup_init_finished is True
    assert status.brew_switch_state is False
    assert status.thermocouple_fault_reason == ""
    assert status.energy_watt_hours == pytest.approx(515.2248)
    assert status.readiness_state == 3


def test_each_fixture_key_is_one_field():
    aliases = [f.metadata["alias"] for f in FIELDS]
    assert len(aliases) == len(set(aliases)) == 46
    assert set(aliases) == set(_raw())


def test_optional_aliases():
    assert set(OPTIONAL) == {
        "boilerTemperature",
        "brewSwitchActive",
        "steamForgottenOn",
        "pcbV2",
        "debugLoggingEnabled",
        "readinessState",
        "warmupElapsedSeconds",
        "warmupRemainingSeconds",
    }


@pytest.mark.parametrize("alias", OPTIONAL)
def test_optional_key_can_be_missing(alias: str):
    raw = _raw()
    del raw[alias]
    status = Status.from_api(raw)
    name = next(f.name for f in FIELDS if f.metadata["alias"] == alias)
    assert getattr(status, name) is None


@pytest.mark.parametrize("alias", REQUIRED)
def test_required_key_cannot_be_missing(alias: str):
    raw = _raw()
    del raw[alias]
    with pytest.raises(GaggiuinoResponseFormatError):
        Status.from_api(raw)


def test_unknown_operation_mode():
    status = Status.from_api(_raw(operationMode="NEW_MODE"))
    assert status.operation_mode is OperationMode.UNKNOWN


def test_unknown_key_is_ignored():
    assert Status.from_api(_raw(newFirmwareKey=1)) == Status.from_api(_raw())


def test_false_string_in_bool_field():
    status = Status.from_api(_raw(startupInitFinished="false"))
    assert status.startup_init_finished is False


def test_repr_hides_the_machine_name():
    status = Status.from_api(_raw(machineName="Kitchen of Alex"))
    assert "Kitchen of Alex" not in repr(status)
    assert "profile_name='_OFF'" in repr(status)
    assert status.machine_name == "Kitchen of Alex"
    assert status.to_api()["machineName"] == "Kitchen of Alex"


def test_model_is_frozen():
    status = Status.from_api(_raw())
    name = "up_time"
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(status, name, 1)

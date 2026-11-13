"""Tests of the maintenance, firmware progress and health models on real responses."""

import dataclasses
from typing import Any

import pytest

from fixture_loader import load_fixture
from gaggiuino_api.enums import FirmwareStatus, FirmwareType
from gaggiuino_api.exceptions import GaggiuinoResponseFormatError
from gaggiuino_api.models.base import Model
from gaggiuino_api.models.firmware import FirmwareProgress
from gaggiuino_api.models.health import Health
from gaggiuino_api.models.maintenance import Maintenance


def _aliases(cls: Any) -> set[str]:
    return {field.metadata["alias"] for field in dataclasses.fields(cls)}


def test_maintenance_fixture_parses():
    raw = load_fixture("maintenance")
    maintenance = Maintenance.from_api(raw)
    assert maintenance.last_descale_timestamp == 0
    assert maintenance.shots_since_descale == 11
    assert maintenance.last_backflush_timestamp == 0
    assert maintenance.shots_since_backflush == 11
    assert _aliases(Maintenance) == set(raw)


@pytest.mark.parametrize("alias", sorted(_aliases(Maintenance)))
def test_maintenance_missing_key_is_a_format_error(alias: str):
    raw = load_fixture("maintenance")
    del raw[alias]
    with pytest.raises(GaggiuinoResponseFormatError):
        Maintenance.from_api(raw)


def test_firmware_progress_fixture_parses():
    raw = load_fixture("firmware_progress")
    progress = FirmwareProgress.from_api(raw)
    assert progress.progress == 0
    assert progress.status is FirmwareStatus.IDLE
    assert progress.type is FirmwareType.C_FW
    assert _aliases(FirmwareProgress) | {"migration"} == set(raw)


def test_firmware_progress_unknown_status_and_type_give_unknown():
    raw = load_fixture("firmware_progress") | {"status": "NEW", "type": "NEW"}
    progress = FirmwareProgress.from_api(raw)
    assert progress.status is FirmwareStatus.UNKNOWN
    assert progress.type is FirmwareType.UNKNOWN


def test_firmware_progress_missing_status_is_a_format_error():
    raw = load_fixture("firmware_progress")
    del raw["status"]
    with pytest.raises(GaggiuinoResponseFormatError):
        FirmwareProgress.from_api(raw)


def test_health_fixture_parses():
    assert Health.from_api(load_fixture("health")).ok is True


def test_health_other_status_is_not_ok():
    assert Health.from_api({"status": "down"}).ok is False


def test_health_missing_status_is_a_format_error():
    with pytest.raises(GaggiuinoResponseFormatError):
        Health.from_api({})


@pytest.mark.parametrize(
    ("cls", "fixture", "name"),
    [
        (Maintenance, "maintenance", "shots_since_descale"),
        (FirmwareProgress, "firmware_progress", "progress"),
        (Health, "health", "status"),
    ],
)
def test_models_are_frozen(cls: type[Model], fixture: str, name: str):
    model = cls.from_api(load_fixture(fixture))
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(model, name, None)

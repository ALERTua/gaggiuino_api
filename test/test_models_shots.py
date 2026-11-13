"""Tests of the shot models on real responses of the machine."""

import dataclasses
from typing import Any

import pytest

from fixture_loader import load_fixture
from gaggiuino_api.enums import PhaseType
from gaggiuino_api.exceptions import GaggiuinoResponseFormatError
from gaggiuino_api.models.shots import LatestShot, Shot, ShotDatapoints


def _aliases(cls: type[Any]) -> set[str]:
    return {f.metadata["alias"] for f in dataclasses.fields(cls)}


_REQUIRED_DATAPOINTS = sorted(_aliases(ShotDatapoints) - {"phaseIndex"})


def test_shot_fixture_values():
    raw = load_fixture("shot")
    shot = Shot.from_api(raw)
    assert shot.id == raw["id"]
    assert shot.timestamp == raw["timestamp"]
    assert shot.duration == raw["duration"]
    for value in (shot.id, shot.timestamp, shot.duration):
        assert type(value) is int
    arrays = [
        getattr(shot.datapoints, f.name) for f in dataclasses.fields(ShotDatapoints)
    ]
    assert len(arrays) == 11
    for array in arrays:
        assert array is not None
        assert len(array) == 20
        assert all(type(item) is int for item in array)
    assert shot.profile.id == raw["profile"]["id"]
    assert isinstance(shot.profile.phases[0].type, PhaseType)


def test_each_fixture_key_has_a_field():
    raw = load_fixture("shot")
    assert _aliases(ShotDatapoints) == set(raw["datapoints"])
    assert _aliases(Shot) == set(raw)


def test_missing_phase_index_is_none():
    raw = load_fixture("shot")
    del raw["datapoints"]["phaseIndex"]
    assert Shot.from_api(raw).datapoints.phase_index is None


@pytest.mark.parametrize("missing", _REQUIRED_DATAPOINTS)
def test_datapoints_without_required_key_is_a_format_error(missing: str):
    raw = load_fixture("shot")
    del raw["datapoints"][missing]
    with pytest.raises(GaggiuinoResponseFormatError):
        Shot.from_api(raw)


def test_shot_without_profile_is_a_format_error():
    raw = load_fixture("shot")
    del raw["profile"]
    with pytest.raises(GaggiuinoResponseFormatError):
        Shot.from_api(raw)


def test_latest_shot_parses_the_one_object_of_the_list():
    raw = load_fixture("shots_latest")
    latest = LatestShot.from_api(raw[0])
    assert latest.last_shot_id == raw[0]["lastShotId"]
    assert type(latest.last_shot_id) is int
    assert LatestShot.from_api({"lastShotId": "580"}).last_shot_id == 580


def test_models_are_frozen():
    latest = LatestShot(last_shot_id=1)
    name = "last_shot_id"
    value: Any = 2
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(latest, name, value)

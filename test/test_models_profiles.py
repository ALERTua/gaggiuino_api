"""Tests of the profile models on real responses of the machine."""

import dataclasses
import types
import typing
from typing import Any

import pytest

from fixture_loader import load_fixture
from gaggiuino_api.enums import CurveType, PhaseType
from gaggiuino_api.exceptions import GaggiuinoResponseFormatError
from gaggiuino_api.models.base import Model
from gaggiuino_api.models.profiles import (
    Phase,
    PhaseTarget,
    Profile,
    ProfileCreated,
    ProfileSummary,
)


def _profile_fixtures() -> list[dict[str, Any]]:
    return [load_fixture("profile"), load_fixture("shot")["profile"]]


def test_profiles_all_parses_selected_as_bool():
    summaries = [ProfileSummary.from_api(item) for item in load_fixture("profiles_all")]
    assert summaries[0] == ProfileSummary(id=7, name="_Long", selected=False)
    assert summaries[0].selected is False
    assert summaries[1].selected is True


def test_profile_fixture_values():
    profile = Profile.from_api(load_fixture("profile"))
    assert profile.id is None
    assert profile.name == "_Long"
    phase = profile.phases[0]
    assert phase.type is PhaseType.FLOW
    assert phase.target is not None
    assert phase.target.curve is CurveType.INSTANT
    assert phase.stop_conditions is not None
    assert phase.stop_conditions.time == 8000
    assert type(phase.stop_conditions.time) is int
    assert profile.water_temperature == 92.0


@pytest.mark.parametrize("raw", _profile_fixtures(), ids=["profile", "shot"])
def test_profile_round_trip(raw: dict[str, Any]):
    assert Profile.from_api(raw).to_api() == raw


def _model_of(hint: object) -> type[Model] | None:
    """Return the model class inside a field type such as `list[Phase]` or `Recipe | None`."""
    if isinstance(hint, type) and issubclass(hint, Model):
        return hint
    if typing.get_origin(hint) in (list, typing.Union, types.UnionType):
        for arg in typing.get_args(hint):
            if (found := _model_of(arg)) is not None:
                return found
    return None


def _assert_known_keys(cls: type[Any], data: dict[str, Any], where: str) -> None:
    hints = typing.get_type_hints(cls)
    by_alias = {f.metadata["alias"]: f for f in dataclasses.fields(cls)}
    for key, value in data.items():
        assert key in by_alias, f"{where}: {cls.__name__} has no field for {key!r}"
        nested = _model_of(hints[by_alias[key].name])
        if nested is None:
            continue
        items = value if isinstance(value, list) else [value]
        for index, item in enumerate(items):
            _assert_known_keys(nested, item, f"{where}.{key}[{index}]")


@pytest.mark.parametrize("raw", _profile_fixtures(), ids=["profile", "shot"])
def test_each_fixture_key_has_a_field(raw: dict[str, Any]):
    _assert_known_keys(Profile, raw, "profile")


def test_unknown_phase_type_and_curve_go_back_unchanged():
    raw = {"type": "NEW_TYPE", "target": {"curve": "NEW_CURVE"}}
    phase = Phase.from_api(raw)
    assert phase.type == "NEW_TYPE"
    assert type(phase.type) is str
    assert phase.target is not None
    assert type(phase.target.curve) is str
    assert phase.to_api() == raw


def test_minimal_profile_writes_only_name_and_phase_type():
    profile = Profile(name="Test", phases=[Phase(type=PhaseType.PRESSURE)])
    assert profile.to_api() == {"name": "Test", "phases": [{"type": "PRESSURE"}]}


@pytest.mark.parametrize("missing", ["name", "phases"])
def test_profile_without_required_key_is_a_format_error(missing: str):
    raw = load_fixture("profile")
    del raw[missing]
    with pytest.raises(GaggiuinoResponseFormatError):
        Profile.from_api(raw)


def test_profile_created_parses():
    created = ProfileCreated.from_api({"id": 4, "name": "18g Double"})
    assert created == ProfileCreated(id=4, name="18g Double")


def test_models_are_frozen():
    target = PhaseTarget(end=1.0)
    name = "end"
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(target, name, 2.0)

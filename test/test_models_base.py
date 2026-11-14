"""Tests of the model base: the field helper, the parse and the write back."""

import dataclasses
from dataclasses import dataclass

import pytest

from gaggiuino_api.enums import OperationMode, PhaseType, ReleaseChannel
from gaggiuino_api.exceptions import GaggiuinoResponseFormatError
from gaggiuino_api.models import Model, api


@dataclass(frozen=True, kw_only=True)
class Point(Model):
    value: float = api("pointValue")


@dataclass(frozen=True, kw_only=True)
class Sample(Model):
    note: str | None = api("noteText", default=None)
    up_time: int = api("upTime")
    temperature: float = api("temperature")
    selected: bool = api("selected")
    mode: OperationMode = api("operationMode")
    phase_type: PhaseType | str = api("type")
    channel: ReleaseChannel | int = api("releaseChannel")
    point: Point = api("point")
    points: list[Point] = api("points")


def _raw(**changes: object) -> dict[str, object]:
    data: dict[str, object] = {
        "upTime": 150,
        "temperature": 88.5,
        "selected": True,
        "operationMode": "BREW_AUTO",
        "type": "FLOW",
        "releaseChannel": 0,
        "point": {"pointValue": 1.5},
        "points": [],
    }
    data.update(changes)
    return data


def test_alias_is_read_and_written_back():
    raw = _raw(noteText="hi", points=[{"pointValue": 2.5}])
    assert Sample.from_api(raw).to_api() == raw


def test_unknown_key_is_ignored():
    assert Sample.from_api(_raw(newFirmwareKey=1)) == Sample.from_api(_raw())


def test_none_is_left_out_on_write():
    sample = Sample.from_api(_raw())
    assert sample.note is None
    assert "noteText" not in sample.to_api()


def test_required_field_after_optional_field_takes_keywords():
    sample = Sample(
        up_time=1,
        temperature=2.0,
        selected=False,
        mode=OperationMode.HOME,
        phase_type=PhaseType.FLOW,
        channel=ReleaseChannel.STABLE,
        point=Point(value=0.0),
        points=[],
    )
    assert sample.to_api()["upTime"] == 1


def test_missing_required_key_is_a_format_error():
    raw = _raw()
    del raw["upTime"]
    with pytest.raises(GaggiuinoResponseFormatError) as info:
        Sample.from_api(raw)
    assert info.value.__cause__ is not None


@pytest.mark.parametrize("data", [[], "text", None, 5])
def test_value_that_is_not_an_object_is_a_format_error(data: object):
    with pytest.raises(GaggiuinoResponseFormatError) as info:
        Sample.from_api(data)
    assert isinstance(info.value.__cause__, TypeError)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("false", False),
        ("true", True),
        ("FALSE", False),
        (True, True),
        (False, False),
        (0, False),
        (1, True),
    ],
)
def test_bool_reads_booleans_strings_and_zero_or_one(value: object, expected: bool):
    sample = Sample.from_api(_raw(selected=value))
    assert sample.selected is expected
    assert sample.to_api()["selected"] is expected


@pytest.mark.parametrize("value", [2, "yes", "", None, 1.0])
def test_bool_refuses_other_values(value: object):
    with pytest.raises(GaggiuinoResponseFormatError):
        Sample.from_api(_raw(selected=value))


def test_numbers_in_strings_are_parsed():
    sample = Sample.from_api(_raw(upTime="150", temperature="88.839622"))
    assert sample.up_time == 150
    assert sample.temperature == 88.839622


def test_json_integer_in_float_field_becomes_float():
    sample = Sample.from_api(_raw(temperature=0))
    assert type(sample.temperature) is float


@pytest.mark.parametrize("value", [True, "92.000000", 92.5, None])
def test_int_refuses_bool_float_and_float_string(value: object):
    with pytest.raises(GaggiuinoResponseFormatError):
        Sample.from_api(_raw(upTime=value))


@pytest.mark.parametrize("value", [True, "warm", None])
def test_float_refuses_bool_and_text(value: object):
    with pytest.raises(GaggiuinoResponseFormatError):
        Sample.from_api(_raw(temperature=value))


@pytest.mark.parametrize("value", [5, 1.5, False])
def test_str_refuses_other_json_types(value: object):
    with pytest.raises(GaggiuinoResponseFormatError):
        Sample.from_api(_raw(noteText=value))


def test_nested_model_and_list_of_models():
    sample = Sample.from_api(
        _raw(point={"pointValue": "3"}, points=[{"pointValue": 1}, {"pointValue": 2.5}])
    )
    assert sample.point == Point(value=3.0)
    assert sample.points == [Point(value=1.0), Point(value=2.5)]


def test_bad_nested_model_is_a_format_error():
    with pytest.raises(GaggiuinoResponseFormatError):
        Sample.from_api(_raw(points=[{"otherKey": 1}]))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("PRESSURE", PhaseType.PRESSURE), ("NEW_TYPE", "NEW_TYPE")],
)
def test_enum_or_str_keeps_unknown_value(raw: str, expected: PhaseType | str):
    sample = Sample.from_api(_raw(type=raw))
    assert sample.phase_type == expected
    assert type(sample.phase_type) is type(expected)
    assert sample.to_api()["type"] == raw
    assert type(sample.to_api()["type"]) is str


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(2, ReleaseChannel.DEBUG), (7, 7)],
)
def test_enum_or_int_keeps_unknown_value(raw: object, expected: ReleaseChannel | int):
    sample = Sample.from_api(_raw(releaseChannel=raw))
    assert sample.channel == expected
    assert type(sample.channel) is type(expected)
    written = sample.to_api()["releaseChannel"]
    assert written == int(expected)
    assert type(written) is int


def test_enum_or_str_refuses_a_number():
    with pytest.raises(GaggiuinoResponseFormatError):
        Sample.from_api(_raw(type=5))


def test_read_only_enum_field_gives_unknown():
    assert Sample.from_api(_raw(operationMode="NEW_MODE")).mode is OperationMode.UNKNOWN


def test_enum_after_its_raw_type_in_a_union_is_refused():
    with pytest.raises(TypeError, match="enum first"):

        @dataclass(frozen=True, kw_only=True)
        class WrongOrder(Model):
            phase_type: list[str | PhaseType] = api("type")


def test_model_is_frozen():
    sample = Sample.from_api(_raw())
    name = "up_time"
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(sample, name, 1)

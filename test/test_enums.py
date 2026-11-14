"""Tests of the enums: an enum that is only read gives UNKNOWN, an enum that goes back does not."""

from enum import Enum

import pytest

from gaggiuino_api.enums import (
    CurveType,
    FirmwareStatus,
    FirmwareType,
    OperationMode,
    PhaseType,
    ReleaseChannel,
)


@pytest.mark.parametrize("enum", [OperationMode, FirmwareStatus, FirmwareType])
def test_read_only_enum_gives_unknown_for_unknown_value(enum: type[Enum]):
    assert enum("SOMETHING_NEW") is enum["UNKNOWN"]


@pytest.mark.parametrize(
    "enum", [OperationMode, FirmwareStatus, FirmwareType, PhaseType, CurveType]
)
def test_str_enum_value_is_its_name(enum: type[Enum]):
    for member in enum:
        assert member.value == member.name


@pytest.mark.parametrize(
    ("enum", "unknown"), [(PhaseType, "NEW"), (CurveType, "NEW"), (ReleaseChannel, 9)]
)
def test_enum_that_goes_back_has_no_unknown(enum: type[Enum], unknown: object):
    assert "UNKNOWN" not in enum.__members__
    with pytest.raises(ValueError):
        enum(unknown)


def test_release_channel_values():
    assert [int(member) for member in ReleaseChannel] == [0, 1, 2]

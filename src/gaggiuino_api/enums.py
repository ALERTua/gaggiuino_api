"""Enums of the API.

A read-only enum maps an unknown value to `UNKNOWN`. A writable enum has no `UNKNOWN`: its
field is `TheEnum | str` or `TheEnum | int` and keeps the raw value.
"""

from enum import IntEnum, StrEnum
from typing import Self


class _ReadOnlyStrEnum(StrEnum):
    """A string enum that gives `UNKNOWN` for each value that it does not know."""

    @classmethod
    def _missing_(cls, value: object) -> Self:
        return cls["UNKNOWN"]


class OperationMode(_ReadOnlyStrEnum):
    """The operation mode of the machine."""

    BREW_AUTO = "BREW_AUTO"
    BREW_MANUAL = "BREW_MANUAL"
    FLUSH = "FLUSH"
    DESCALE = "DESCALE"
    STEAM = "STEAM"
    FLUSH_AUTO = "FLUSH_AUTO"
    HOT_WATER = "HOT_WATER"
    HOME = "HOME"
    PUMP_CALIBRATION = "PUMP_CALIBRATION"
    POWER_OFF = "POWER_OFF"
    UNKNOWN = "UNKNOWN"


class FirmwareStatus(_ReadOnlyStrEnum):
    """The state of a firmware update."""

    IDLE = "IDLE"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class FirmwareType(_ReadOnlyStrEnum):
    """The part of the firmware that an update writes.

    `C_FW` is the core firmware, `F_FW` is the frontend firmware, and `F_FS` is the frontend
    filesystem image.
    """

    C_FW = "C_FW"
    F_FW = "F_FW"
    F_FS = "F_FS"
    UNKNOWN = "UNKNOWN"


class PhaseType(StrEnum):
    """What a phase of a profile controls."""

    FLOW = "FLOW"
    PRESSURE = "PRESSURE"
    MANUAL = "MANUAL"


class CurveType(StrEnum):
    """The curve of the transition from the start value to the end value of a phase."""

    EASE_IN_OUT = "EASE_IN_OUT"
    EASE_IN = "EASE_IN"
    EASE_OUT = "EASE_OUT"
    LINEAR = "LINEAR"
    INSTANT = "INSTANT"


class ReleaseChannel(IntEnum):
    """The release channel of the firmware updates."""

    STABLE = 0
    TEST = 1
    DEBUG = 2

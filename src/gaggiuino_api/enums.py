"""Enums of the values that the firmware sends and takes.

An enum that the library only reads has the member `UNKNOWN`: a value that the library
does not know becomes `UNKNOWN`, so a newer firmware does not stop the parse.

An enum that also goes back to the machine has no `UNKNOWN` member. Its model field has the
type `TheEnum | str` or `TheEnum | int`: a known value becomes the member, and an unknown value
stays as the raw value, so the model writes it back unchanged.
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

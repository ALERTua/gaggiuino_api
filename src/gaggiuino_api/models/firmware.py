"""The progress of a firmware update: the answer of `GET /api/firmware/progress`."""

from dataclasses import dataclass

from ..enums import FirmwareStatus, FirmwareType
from .base import Model, api


@dataclass(frozen=True, kw_only=True)
class FirmwareProgress(Model):
    """The progress of an update that is in flight, or the idle state when none runs.

    Some firmware versions add an object `migration` to the answer. The model does not read
    it: an unknown key is ignored.

    `progress` is a number that the machine reports for the update. The documentation shows
    the value 42 next to the status `IN_PROGRESS` and gives no unit.
    """

    progress: int = api("progress")
    status: FirmwareStatus = api("status")
    type: FirmwareType = api("type")

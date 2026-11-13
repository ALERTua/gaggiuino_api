"""The firmware of the machine: start an update and read its progress."""

from .._transport import Transport
from ..models.firmware import FirmwareProgress


class Firmware:
    """The firmware update of the machine."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def update(self) -> None:
        """Start an update of both firmware parts: `POST /api/firmware/update-all`.

        The call only starts the update and does not wait for it. `progress()`
        gives its state. The machine restarts during the update, so it does not
        answer for a while.
        Raise `GaggiuinoCommandError` when the machine cannot start the update.
        """
        await self._transport.command('POST', 'firmware/update-all')

    async def progress(self) -> FirmwareProgress:
        """Return the progress of the firmware update: `GET /api/firmware/progress`."""
        data = await self._transport.get_json('firmware/progress')
        return FirmwareProgress.from_api(data)

"""The client of the REST API of a Gaggiuino espresso machine."""

from types import TracebackType
from typing import Self

import aiohttp

from ._transport import Transport
from .const import DEFAULT_BASE_URL
from .exceptions import GaggiuinoResponseFormatError
from .models.health import Health
from .models.maintenance import Maintenance
from .models.status import Status
from .resources import Firmware, Profiles, SettingsResource, Shots


class GaggiuinoClient:
    """Async client of one machine. It keeps no state: each call asks the machine.

    A session that the caller gives stays open after `close()`.

    ```python
    async with GaggiuinoClient("http://gaggiuino.local") as machine:
        status = await machine.status()
        profiles = await machine.profiles.list()
        shot_id = await machine.shots.latest_id()
        await machine.settings.boiler.update(steam_set_point=130)
    ```
    """

    profiles: Profiles
    """The saved profiles of the machine."""
    shots: Shots
    """The saved shots of the machine."""
    settings: SettingsResource
    """The settings of the machine."""
    firmware: Firmware
    """The firmware update of the machine."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        session: aiohttp.ClientSession | None = None,
        timeout: float | aiohttp.ClientTimeout | None = None,
    ) -> None:
        self._transport = Transport(base_url, session=session, timeout=timeout)
        self.profiles = Profiles(self._transport)
        self.shots = Shots(self._transport)
        self.settings = SettingsResource(self._transport)
        self.firmware = Firmware(self._transport)

    async def connect(self) -> None:
        """Open the HTTP session when the client owns it."""
        await self._transport.open()

    async def close(self) -> None:
        """Close the HTTP session when the client owns it."""
        await self._transport.close()

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def status(self) -> Status:
        """Return the live status of the machine: `GET /api/system/status`.

        Raise `GaggiuinoResponseFormatError` when the answer is not a JSON list
        with at least one status object.
        """
        data = await self._transport.get_json('system/status')
        if not isinstance(data, list) or not data:
            raise GaggiuinoResponseFormatError(
                'Expected a non-empty JSON list with the status'
            )
        return Status.from_api(data[0])

    async def maintenance(self) -> Maintenance:
        """Return the service history of the machine: `GET /api/maintenance`."""
        data = await self._transport.get_json('maintenance')
        return Maintenance.from_api(data)

    async def healthy(self) -> bool:
        """Return True when `GET /api/health` says ok.

        During a restart of the machine it raises `GaggiuinoConnectionError` or
        `GaggiuinoConnectionTimeoutError`.
        """
        data = await self._transport.get_json('health')
        return Health.from_api(data).ok

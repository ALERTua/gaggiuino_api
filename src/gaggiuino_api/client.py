"""The client of the REST API of a Gaggiuino espresso machine."""

from types import TracebackType
from typing import Self

import aiohttp

from ._transport import Transport
from .const import DEFAULT_BASE_URL


class GaggiuinoClient:
    """Async client of one Gaggiuino machine.

    Use it as an async context manager, or call `connect()` and `close()`.
    A session that the caller gives stays open after `close()`.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        session: aiohttp.ClientSession | None = None,
        timeout: float | aiohttp.ClientTimeout | None = None,
    ) -> None:
        self._transport = Transport(base_url, session=session, timeout=timeout)

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

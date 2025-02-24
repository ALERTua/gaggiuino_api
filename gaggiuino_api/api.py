"""Gaggiuino API Wrapper."""

from __future__ import annotations

import asyncio
import logging
from typing import Type, Any
from urllib import parse as urllib_parse

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectionError

from gaggiuino_api.const import DEFAULT_BASE_URL
from gaggiuino_api.exceptions import (
    GaggiuinoError,
    GaggiuinoConnectionError,
    GaggiuinoEndpointNotFoundError,
)
from gaggiuino_api.models import GaggiuinoProfile, GaggiuinoShot

_LOGGER = logging.getLogger(__name__)


class GaggiuinoClient:
    """Initialise a client to receive Server Sent Events (SSE)"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, session: ClientSession = None):
        self.session = session
        self.base_url = base_url
        self.headers = {}
        self.post_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.close_session = False

    async def __aenter__(self) -> "GaggiuinoClient":
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        """Open the session"""
        if self.session is None:
            self.close_session = True
            self.session = ClientSession(headers=self.headers)

    async def disconnect(self) -> None:
        """Close the session if it was created internally"""
        if self.session is not None and self.close_session:
            await self.session.close()
            self.session = None
            self.close_session = False

    async def post(self, url: str, params: dict = None) -> bool:
        assert self.session is not None, "Session not created"

        data = urllib_parse.urlencode(params) if params is not None else None

        try:
            async with self.session.post(
                url,
                data=data,
                headers=self.post_headers,
            ) as response:
                if response.status == 404:
                    raise GaggiuinoEndpointNotFoundError("endpoint not found")
                await response.text(encoding="utf-8")
                return response.status == 200
        except ClientConnectionError as err:
            raise GaggiuinoConnectionError("Connection failed") from err
        except Exception as err:
            raise GaggiuinoError("Unhandled exception") from err

    async def get(
        self,
        url: str | None = None,
        params: dict[str, Any] = None,
    ) -> Any:
        assert self.session is not None, "Session not created"

        params = params or {}
        url = url or self.base_url

        try:
            async with self.session.get(
                url,
                headers=self.headers,
                params=params,
            ) as response:
                if response.status == 404:
                    raise GaggiuinoEndpointNotFoundError("endpoint not found")

                return await response.json()
        except ClientConnectionError as err:
            raise GaggiuinoConnectionError("Connection failed") from err
        except Exception as err:
            raise GaggiuinoError("Unhandled exception") from err


class GaggiuinoAPI(GaggiuinoClient):
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        session: ClientSession | None = None,
    ) -> None:
        super().__init__(base_url=base_url, session=session)
        self.api_base = f"{self.base_url}/api"

    async def get_profiles(self) -> list[GaggiuinoProfile]:
        url = f"{self.api_base}/profiles/all"
        profiles: list[dict[str, Any]] = await self.get(url)
        output = [GaggiuinoProfile(**_) for _ in profiles]
        return output

    async def _select_profile(self, profile_id: int) -> bool:
        url = f"{self.api_base}/profile-select/{profile_id}"
        return await self.post(url)

    async def select_profile(self, profile: GaggiuinoProfile | int) -> bool:
        profile_id = profile
        if isinstance(profile, GaggiuinoProfile):
            profile_id = profile.id

        return await self._select_profile(profile_id=profile_id)

    async def get_shot(self, shot_id: int):
        url = f"{self.api_base}/shots/{shot_id}"
        shot = await self.get(url)
        return GaggiuinoShot(**shot)


async def _main():
    async with GaggiuinoAPI() as gapi:
        _profiles = await gapi.get_profiles()
        _shot = await gapi.get_shot(1)
    pass


if __name__ == '__main__':
    asyncio.run(_main())

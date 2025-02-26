"""Gaggiuino API Wrapper."""

from __future__ import annotations
import sys

import asyncio
import logging
from typing import Type, Any, Literal
from urllib import parse as urllib_parse

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectionError

from gaggiuino_api.const import DEFAULT_BASE_URL
from gaggiuino_api.exceptions import (
    GaggiuinoError,
    GaggiuinoConnectionError,
    GaggiuinoEndpointNotFoundError,
)
from gaggiuino_api.models import (
    GaggiuinoProfile,
    GaggiuinoShot,
    GaggiuinoStatus,
    GaggiuinoLatestShotResult,
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_LOGGER = logging.getLogger(__name__)


class GaggiuinoClient:
    """Initialise a client to receive Server Sent Events (SSE)"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, session: ClientSession = None):
        self.session = session
        self.base_url = base_url
        self.headers = {}
        self.post_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.close_session = False
        self.timeout = 15

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
        except GaggiuinoEndpointNotFoundError as err:
            raise GaggiuinoEndpointNotFoundError from err
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
                timeout=self.timeout,
            ) as response:
                if response.status == 404:
                    raise GaggiuinoEndpointNotFoundError("endpoint not found")

                return await response.json()
        except ClientConnectionError as err:
            raise GaggiuinoConnectionError("Connection failed") from err
        except GaggiuinoEndpointNotFoundError as err:
            raise GaggiuinoEndpointNotFoundError from err
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
        self._profile: GaggiuinoProfile | None = None
        self._profiles: list[GaggiuinoProfile] | None = None
        self._status: GaggiuinoStatus | None = None

    @property
    def profile(self):
        if self._status is None:
            _LOGGER.debug(
                "Cannot get the currently selected profile. Use get_status() first."
            )
            return None

        self._profile = GaggiuinoProfile(
            id=self._status.profileId, name=self._status.profileName
        )
        if self._profiles:
            for profile in self._profiles:
                if profile.id == self._status.profileId:
                    self._profile = profile
                    break

        _LOGGER.debug("Current profile: %s", self._profile)
        return self._profile

    @profile.setter
    async def profile(self, profile: GaggiuinoProfile | int):
        if await self._select_profile(profile):
            self._profile = profile

    async def get_profiles(self) -> list[GaggiuinoProfile] | None:
        url = f"{self.api_base}/profiles/all"
        try:
            profiles: list[dict[str, Any]] = await self.get(url)
        except GaggiuinoEndpointNotFoundError as err:
            raise GaggiuinoEndpointNotFoundError("Profile not found") from err
        except Exception as err:
            raise GaggiuinoError("Unhandled exception") from err
        if profiles is None:
            return None

        self._profiles = [GaggiuinoProfile(**_) for _ in profiles]
        return self._profiles

    async def _select_profile(self, profile_id: int) -> bool:
        url = f"{self.api_base}/profile-select/{profile_id}"
        try:
            return await self.post(url)
        except GaggiuinoEndpointNotFoundError as err:
            raise GaggiuinoEndpointNotFoundError("Profile not found") from err
        except Exception as err:
            raise GaggiuinoError("Unhandled exception") from err

    async def select_profile(self, profile: GaggiuinoProfile | int) -> bool:
        profile_id = profile
        if isinstance(profile, GaggiuinoProfile):
            profile_id = profile.id

        return await self._select_profile(profile_id=profile_id)

    async def _get_shot(self, shot_id: int | Literal["latest"]) -> dict:
        url = f"{self.api_base}/shots/{shot_id}"
        try:
            shot = await self.get(url)
        except GaggiuinoEndpointNotFoundError as err:
            raise GaggiuinoEndpointNotFoundError("Shot not found") from err
        except Exception as err:
            raise GaggiuinoError("Unhandled exception") from err

        return shot

    async def get_shot(self, shot_id: int) -> GaggiuinoShot | None:
        shot = await self._get_shot(shot_id)
        if shot is None:
            _LOGGER.debug("Couldn't retrieve shot %s", shot_id)
            return None

        return GaggiuinoShot(**shot)

    async def get_status(self) -> GaggiuinoStatus | None:
        url = f"{self.api_base}/system/status"
        try:
            status: list[dict[str, Any]] = await self.get(url)
        except GaggiuinoEndpointNotFoundError as err:
            raise GaggiuinoEndpointNotFoundError("Shot not found") from err
        except Exception as err:
            raise GaggiuinoError("Unhandled exception") from err

        if status:
            self._status = GaggiuinoStatus(**status[0])
            return self._status

    async def get_latest_shot_id(self):
        latest_shots = await self._get_shot("latest")
        if latest_shots is None:
            _LOGGER.debug("Couldn't retrieve the latest shot")
            return None

        return GaggiuinoLatestShotResult(**latest_shots[0])


async def _main():
    async with GaggiuinoAPI() as gapi:
        _status = await gapi.get_status()
        _profiles = await gapi.get_profiles()
        _latest_shot_id_result = await gapi.get_latest_shot_id()
        _latest_shot_id = _latest_shot_id_result.lastShotId
        _shot = await gapi.get_shot(_latest_shot_id)
    pass


if __name__ == '__main__':
    asyncio.run(_main())

"""Gaggiuino API Wrapper."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Type, Any, Literal
from urllib import parse as urllib_parse

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientConnectionError

from gaggiuino_api.const import DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from gaggiuino_api.exceptions import (
    GaggiuinoError,
    GaggiuinoConnectionError,
    GaggiuinoEndpointNotFoundError,
    GaggiuinoConnectionTimeoutError,
)
from gaggiuino_api.models import (
    GaggiuinoProfile,
    GaggiuinoShot,
    GaggiuinoStatus,
    GaggiuinoLatestShotResult,
)
from gaggiuino_api.tools import strtobool

if sys.platform == 'win32' and strtobool(
    os.getenv('GAGGIUINO_DISABLE_WIN_SELECTOR', 'False')
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_LOGGER = logging.getLogger(__name__)


class GaggiuinoClient:
    """Initialise a client to receive Server Sent Events (SSE)"""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        session: ClientSession | None = None,
        *,
        timeout: float | ClientTimeout | None = None,
    ):
        self.session = session
        # Normalize base_url to avoid trailing slash duplication
        self.base_url = base_url.rstrip("/")
        self.headers = {}
        self.post_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.close_session = False
        if isinstance(timeout, ClientTimeout):
            self._client_timeout = timeout
            self.timeout = float(timeout.total or DEFAULT_TIMEOUT)
        else:
            self.timeout = (
                float(timeout) if isinstance(timeout, (int, float)) else DEFAULT_TIMEOUT
            )
            self._client_timeout = ClientTimeout(total=self.timeout)

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
        """Open the session."""
        if self.session is None:
            self.close_session = True
            self.session = ClientSession(
                headers=self.headers, timeout=self._client_timeout
            )

    async def disconnect(self) -> None:
        """Close the session if it was created internally."""
        if self.session is not None and self.close_session:
            await self.session.close()
            self.session = None
            self.close_session = False

    async def _request(
        self,
        method: Literal["GET", "POST", "DELETE"],
        url: str,
        params: dict = None,
        *,
        json_response: bool = False,
    ) -> bool | dict[str, Any]:
        """Shared request handler.

        Args:
            method: HTTP method to use
            url: Target URL
            params: Request parameters
            json_response: Whether to parse response as JSON

        Returns:
            JSON data if json_response=True, otherwise bool indicating success
        """
        assert self.session is not None, "Session not created"

        # Prepare request args
        is_get = method == "GET"
        data = None
        if not is_get and params is not None:
            data = urllib_parse.urlencode(params)
        headers = self.post_headers if method in ["POST", "DELETE"] else self.headers

        try:
            async with self.session.request(
                method,
                url,
                params=params if is_get else None,
                data=data,
                headers=headers,
                timeout=self.timeout,
            ) as response:
                _LOGGER.debug("%s %s -> %s", method, url, response.status)
                if response.status == 404:
                    raise GaggiuinoEndpointNotFoundError("endpoint not found")

                if not json_response:
                    return response.status == 200
                return await response.json()

        except ClientConnectionError as err:
            raise GaggiuinoConnectionError("Connection failed") from err
        except asyncio.TimeoutError as err:
            raise GaggiuinoConnectionTimeoutError from err
        except GaggiuinoEndpointNotFoundError as err:
            raise err
        except Exception as err:
            raise GaggiuinoError(
                f"Unhandled exception: {type(err)}: {str(err)}"
            ) from err

    async def post(self, url: str, params: dict = None) -> bool:
        """Send POST request.

        Args:
            url: Target URL
            params: POST parameters

        Returns:
            True if successful
        """
        return await self._request("POST", url, params)

    async def delete(self, url: str, params: dict = None) -> bool:
        """Send DELETE request.

        Args:
            url: Target URL
            params: DELETE parameters

        Returns:
            True if successful
        """
        return await self._request("DELETE", url, params)

    async def get(
        self,
        url: str | None = None,
        params: dict[str, Any] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Send GET request.

        Args:
            url: Target URL (defaults to base_url)
            params: Query parameters

        Returns:
            JSON response data
        """
        url = url or self.base_url
        return await self._request("GET", url, params, json_response=True)


class GaggiuinoAPI(GaggiuinoClient):
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        session: ClientSession | None = None,
        timeout: float | ClientTimeout | None = None,
    ) -> None:
        super().__init__(base_url=base_url, session=session, timeout=timeout)
        self.api_base = f"{self.base_url}/api"
        self._profile: GaggiuinoProfile | None = None
        self._profiles: list[GaggiuinoProfile] | None = None
        self._status: GaggiuinoStatus | None = None

    @property
    def profile(self) -> GaggiuinoProfile | None:
        """Get currently selected profile.

        Returns:
            Currently selected profile or None
        """
        self._profile = None
        if self._status is not None:
            self._profile = GaggiuinoProfile(
                id=self._status.profileId,
                name=self._status.profileName,
                selected=True,
            )
        elif self._profiles is not None:
            self._profile = next(
                (profile for profile in self._profiles if profile.selected),
                None,
            )
        _LOGGER.debug("Current profile: %s", self._profile)
        if self._profile is None:
            _LOGGER.debug(
                "Cannot get the currently selected profile. Use get_status() or get_profiles() first."
            )
        return self._profile

    async def get_profiles(self) -> list[GaggiuinoProfile] | None:
        """Retrieve all available profiles.

        Returns:
            List of profiles or None
        """
        url = f"{self.api_base}/profiles/all"
        profiles: list[dict[str, Any]] = await self.get(url)
        if profiles is None:
            return None

        self._profiles = [GaggiuinoProfile(**_) for _ in profiles]
        return self._profiles

    async def _select_profile(self, profile_id: int) -> bool:
        """Select profile by ID.

        Args:
            profile_id: Profile ID to select

        Returns:
            True if successful
        """
        url = f"{self.api_base}/profile-select/{profile_id}"
        return await self.post(url)

    async def select_profile(self, profile: GaggiuinoProfile | int) -> bool:
        """Select a profile.

        Args:
            profile: Profile object or profile ID

        Returns:
            True if successful
        """
        profile_id = profile
        if isinstance(profile, GaggiuinoProfile):
            profile_id = profile.id

        return await self._select_profile(profile_id=profile_id)

    async def _delete_profile(self, profile_id: int) -> bool:
        """Delete profile by ID.

        Args:
            profile_id: Profile ID to delete

        Returns:
            True if successful
        """
        url = f"{self.api_base}/profile-select/{profile_id}"
        return await self.delete(url)

    async def delete_profile(self, profile: GaggiuinoProfile | int) -> bool:
        """Delete a profile.

        Args:
            profile: Profile object or profile ID

        Returns:
            True if successful
        """
        profile_id = profile
        if isinstance(profile, GaggiuinoProfile):
            profile_id = profile.id

        return await self._delete_profile(profile_id=profile_id)

    async def _get_shot(self, shot_id: int | Literal["latest"]) -> dict:
        """Get shot data by ID.

        Args:
            shot_id: Shot ID or 'latest'

        Returns:
            Raw shot data
        """
        url = f"{self.api_base}/shots/{shot_id}"
        return await self.get(url)

    async def get_shot(self, shot_id: int) -> GaggiuinoShot | None:
        """Retrieve shot data.

        Args:
            shot_id: Shot ID to retrieve

        Returns:
            Shot data or None
        """
        shot = await self._get_shot(shot_id)
        if shot is None:
            _LOGGER.debug("Couldn't retrieve shot %s", shot_id)
            return None

        return GaggiuinoShot(**shot)

    async def get_status(self) -> GaggiuinoStatus | None:
        """Retrieve system status.

        Returns:
            System status or None
        """
        url = f"{self.api_base}/system/status"
        status: list[dict[str, Any]] = await self.get(url)

        if status:
            self._status = GaggiuinoStatus.from_dict(status[0])
            return self._status

        return None

    async def get_latest_shot_id(self) -> GaggiuinoLatestShotResult | None:
        """Retrieve latest shot ID.

        Returns:
            Latest shot result or None
        """
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
        _test_profile = next((_ for _ in _profiles if _.name == 'test (copy)'), None)
        _deletion = await gapi.delete_profile(_test_profile)
    pass


if __name__ == '__main__':
    asyncio.run(_main())

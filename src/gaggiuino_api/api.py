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
    GaggiuinoBoilerSettings,
    GaggiuinoSystemSettings,
    GaggiuinoLedSettings,
    GaggiuinoScalesSettings,
    GaggiuinoDisplaySettings,
    GaggiuinoThemeSettings,
    GaggiuinoVersions,
    GaggiuinoSettings,
)
from gaggiuino_api.tools import strtobool

if sys.platform == "win32" and strtobool(
    os.getenv("GAGGIUINO_DISABLE_WIN_SELECTOR", "False")
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_LOGGER = logging.getLogger(__name__)


class GaggiuinoClient:
    """Initialize a client to receive Server Sent Events (SSE)"""

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
        params: dict | None = None,
        *,
        json_response: bool = False,
        json_data: dict[str, Any] | None = None,
    ) -> bool | dict[str, Any]:
        """Shared request handler.

        Args:
            method: HTTP method to use
            url: Target URL
            params: Request parameters
            json_response: Whether to parse response as JSON
            json_data: JSON payload to send in POST/DELETE requests

        Returns:
            JSON data if json_response=True, otherwise bool indicating success
        """
        assert self.session is not None, "Session not created"

        # Prepare request args
        is_get = method == "GET"
        data = None
        json_body = None
        if not is_get:
            if json_data is not None:
                json_body = json_data
            elif params is not None:
                data = urllib_parse.urlencode(params)
        headers = (
            self.post_headers
            if method in ["POST", "DELETE"] and json_data is None
            else self.headers
        )

        try:
            async with self.session.request(
                method,
                url,
                params=params if is_get else None,
                data=data,
                headers=headers,
                json=json_body,
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

    async def post(self, url: str, params: dict | None = None, **kwargs) -> bool:
        """Send POST request.

        Args:
            url: Target URL
            params: POST parameters

        Returns:
            True if successful
        """
        return await self._request("POST", url, params, **kwargs)

    async def delete(self, url: str, params: dict | None = None) -> bool:
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
        params: dict | None = None,
        json_response: bool = True,
        **kwargs,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Send GET request.

        Args:
            url: Target URL (defaults to base_url)
            params: Query parameters
            json_response: Whether to parse response as JSON

        Returns:
            JSON response data
        """
        url = url or self.base_url
        return await self._request(
            "GET", url, params, json_response=json_response, **kwargs
        )


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

        return GaggiuinoLatestShotResult.from_dict(latest_shots[0])

    async def update_firmware(self, version: str = "latest") -> bool:
        """Update firmware for all components.

        Args:
            version: Firmware version to update to

        Returns:
            True if update initiated successfully
        """
        url = f"{self.api_base}/firmware/update-all"
        return await self.post(url, json_data={"version": version})

    async def get_firmware_progress(self) -> dict[str, Any]:
        """Get firmware update progress status.

        Returns:
            Firmware progress dictionary
            {"progress":0,"status":"IDLE","type":"F_FW"}
            {"progress":0,"status":"ERROR","type":"F_FS"}
            {"progress":0,"status":"IN_PROGRESS","type":"C_FW"}
            {"progress":0,"status":"ERROR","type":"C_FW"}
        """
        url = f"{self.api_base}/firmware/progress"
        return await self.get(url, json_response=True)

    async def get_health(self) -> dict[str, Any]:
        """Get health status of the API.

        Returns:
            Health status dictionary
        """
        url = f"{self.api_base}/health"
        return await self.get(url)

    async def healthy(self) -> bool:
        health = await self.get_health()
        try:
            return health.get("status") == "ok"
        except Exception as e:
            _LOGGER.debug("Healthy check failed: %s", e)
            return False

    # Settings API Methods

    async def get_settings(self) -> GaggiuinoSettings | None:
        """Retrieve all settings in a single response.

        Returns:
            GaggiuinoSettings object containing all settings categories or None
        """
        url = f"{self.api_base}/settings"
        data: dict[str, Any] = await self.get(url)
        if data is None:
            return None
        return GaggiuinoSettings.from_dict(data)

    async def get_boiler_settings(self) -> GaggiuinoBoilerSettings | None:
        """Retrieve boiler-related settings.

        Includes steam set point, temperature offset, heating power, dividers,
        and operational states.

        Returns:
            GaggiuinoBoilerSettings object or None
        """
        url = f"{self.api_base}/settings/boiler"
        data: dict[str, Any] = await self.get(url)
        if data is None:
            return None
        return GaggiuinoBoilerSettings.from_dict(data)

    async def update_boiler_settings(
        self, settings: GaggiuinoBoilerSettings | dict[str, Any]
    ) -> bool:
        """Update boiler settings.

        Args:
            settings: GaggiuinoBoilerSettings object or dict with settings

        Returns:
            True if successful
        """
        url = f"{self.api_base}/settings/boiler"
        if isinstance(settings, GaggiuinoBoilerSettings):
            data = settings.to_api_dict()
        else:
            data = settings
        return await self.post(url, json_data=data)

    async def get_system_settings(self) -> GaggiuinoSystemSettings | None:
        """Retrieve system-level settings.

        Includes pump calibration, timezone, API tokens, services state,
        WiFi, and release channel.

        Returns:
            GaggiuinoSystemSettings object or None
        """
        url = f"{self.api_base}/settings/system"
        data: dict[str, Any] = await self.get(url)
        if data is None:
            return None
        return GaggiuinoSystemSettings.from_dict(data)

    async def update_system_settings(
        self, settings: GaggiuinoSystemSettings | dict[str, Any]
    ) -> bool:
        """Update system settings.

        Args:
            settings: GaggiuinoSystemSettings object or dict with settings

        Returns:
            True if successful
        """
        url = f"{self.api_base}/settings/system"
        if isinstance(settings, GaggiuinoSystemSettings):
            data = settings.to_api_dict()
        else:
            data = settings
        return await self.post(url, json_data=data)

    async def get_theme_settings(self) -> GaggiuinoThemeSettings | None:
        """Retrieve theme color settings.

        Colors are in RGB565 format.

        Returns:
            GaggiuinoThemeSettings object or None
        """
        url = f"{self.api_base}/settings/theme"
        data: dict[str, Any] = await self.get(url)
        if data is None:
            return None
        return GaggiuinoThemeSettings.from_dict(data)

    async def update_theme_settings(
        self, settings: GaggiuinoThemeSettings | dict[str, Any]
    ) -> bool:
        """Update theme color settings.

        Colors should be provided in RGB565 format.

        Args:
            settings: GaggiuinoThemeSettings object or dict with settings

        Returns:
            True if successful
        """
        url = f"{self.api_base}/settings/theme"
        if isinstance(settings, GaggiuinoThemeSettings):
            data = settings.to_api_dict()
        else:
            data = settings
        return await self.post(url, json_data=data)

    async def get_display_settings(self) -> GaggiuinoDisplaySettings | None:
        """Retrieve display-related settings.

        Includes brightness, dark mode, sleep timeout, and auto-home timeout.

        Returns:
            GaggiuinoDisplaySettings object or None
        """
        url = f"{self.api_base}/settings/display"
        data: dict[str, Any] = await self.get(url)
        if data is None:
            return None
        return GaggiuinoDisplaySettings.from_dict(data)

    async def update_display_settings(
        self, settings: GaggiuinoDisplaySettings | dict[str, Any]
    ) -> bool:
        """Update display settings.

        Args:
            settings: GaggiuinoDisplaySettings object or dict with settings

        Returns:
            True if successful
        """
        url = f"{self.api_base}/settings/display"
        if isinstance(settings, GaggiuinoDisplaySettings):
            data = settings.to_api_dict()
        else:
            data = settings
        return await self.post(url, json_data=data)

    async def get_scales_settings(self) -> GaggiuinoScalesSettings | None:
        """Retrieve scales-related settings.

        Includes hardware scales, Bluetooth scales, and calibration factors.

        Returns:
            GaggiuinoScalesSettings object or None
        """
        url = f"{self.api_base}/settings/scales"
        data: dict[str, Any] = await self.get(url)
        if data is None:
            return None
        return GaggiuinoScalesSettings.from_dict(data)

    async def update_scales_settings(
        self, settings: GaggiuinoScalesSettings | dict[str, Any]
    ) -> bool:
        """Update scales settings.

        Args:
            settings: GaggiuinoScalesSettings object or dict with settings

        Returns:
            True if successful
        """
        url = f"{self.api_base}/settings/scales"
        if isinstance(settings, GaggiuinoScalesSettings):
            data = settings.to_api_dict()
        else:
            data = settings
        return await self.post(url, json_data=data)

    async def get_led_settings(self) -> GaggiuinoLedSettings | None:
        """Retrieve LED-related settings.

        Includes RGB color, state, disco mode, and time-of-flight sensor config.

        Returns:
            GaggiuinoLedSettings object or None
        """
        url = f"{self.api_base}/settings/led"
        data: dict[str, Any] = await self.get(url)
        if data is None:
            return None
        return GaggiuinoLedSettings.from_dict(data)

    async def update_led_settings(
        self, settings: GaggiuinoLedSettings | dict[str, Any]
    ) -> bool:
        """Update LED settings.

        Args:
            settings: GaggiuinoLedSettings object or dict with settings

        Returns:
            True if successful
        """
        url = f"{self.api_base}/settings/led"
        if isinstance(settings, GaggiuinoLedSettings):
            data = settings.to_api_dict()
        else:
            data = settings
        return await self.post(url, json_data=data)

    async def get_versions(self) -> GaggiuinoVersions | None:
        """Retrieve version information for all system components.

        This endpoint is read-only (no POST method available).

        Returns:
            GaggiuinoVersions object or None
        """
        url = f"{self.api_base}/settings/versions"
        data: dict[str, Any] = await self.get(url)
        if data is None:
            return None
        return GaggiuinoVersions.from_dict(data)


async def _main():
    async with GaggiuinoAPI() as gapi:
        _status = await gapi.get_status()
        _profiles = await gapi.get_profiles()
        _latest_shot_id_result = await gapi.get_latest_shot_id()
        _latest_shot_id = _latest_shot_id_result.lastShotId
        _shot = await gapi.get_shot(_latest_shot_id)
        _fw = await gapi.update_firmware()
        _test_profile = next((_ for _ in _profiles if _.name == 'test (copy)'), None)
        _deletion = await gapi.delete_profile(_test_profile)
    pass


if __name__ == '__main__':
    asyncio.run(_main())

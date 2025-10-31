"""End-to-end tests for Gaggiuino API."""

import os
import pytest
import pytest_asyncio
from gaggiuino_api import (
    GaggiuinoAPI,
    GaggiuinoEndpointNotFoundError,
    GaggiuinoProfile,
    GaggiuinoShot,
    GaggiuinoStatus,
)
from gaggiuino_api.models import GaggiuinoLatestShotResult
from gaggiuino_api.const import DEFAULT_BASE_URL

pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture(loop_scope="session", name="api_client")
async def _api_client():
    """Fixture to provide an API client."""
    async with GaggiuinoAPI(base_url=DEFAULT_BASE_URL) as gapi:
        yield gapi


@pytest.mark.asyncio(loop_scope="session")
async def test_api_connection(api_client):
    """Test basic API connection."""
    assert api_client is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profiles(api_client):
    """Test getting profiles from the API."""
    profiles = await api_client.get_profiles()
    assert isinstance(profiles, list)
    if profiles:  # If there are any profiles
        assert isinstance(profiles[0], GaggiuinoProfile)
        assert all(isinstance(profile, GaggiuinoProfile) for profile in profiles)
        assert all(hasattr(profile, 'id') for profile in profiles)
        assert all(getattr(profile, 'id', None) is not None for profile in profiles)
        assert all(hasattr(profile, 'name') for profile in profiles)
        assert all(hasattr(profile, 'phases') for profile in profiles)


@pytest.mark.asyncio(loop_scope="session")
async def test_select_profile(api_client):
    """Test selecting a profile."""
    profiles = await api_client.get_profiles()
    if not profiles:
        pytest.skip("No profiles available for testing")

    profile_off_name = os.getenv('GAGGIUINO_PROFILE_OFF', 'OFF')
    profile_test_name = os.getenv('GAGGIUINO_PROFILE_TEST', 'test')

    profile_off = next((_ for _ in profiles if _.name == profile_off_name), None)
    assert profile_off, "Cannot check withoout an OFF profile"
    profile_test = next((_ for _ in profiles if _.name == profile_test_name), None)
    assert profile_test, "Cannot check withoout a test profile"

    # Test with profile object
    result = await api_client.select_profile(profile_test)
    assert result is True

    # Test with profile ID
    result = await api_client.select_profile(profile_off.id)
    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_invalid_profile_selection(api_client):
    """Test selecting an invalid profile ID."""
    assert (
        await api_client.select_profile(99999) is False
    )  # Using an arbitrary large ID


@pytest.mark.asyncio(loop_scope="session")
async def test_invalid_shot_request(api_client):
    """Test requesting an invalid shot ID."""
    with pytest.raises(GaggiuinoEndpointNotFoundError):
        await api_client.get_shot(99999)  # Using an arbitrary large ID


@pytest.mark.asyncio(loop_scope="session")
async def test_get_status(api_client):
    """Test getting profiles from the API."""
    status = await api_client.get_status()
    assert isinstance(status, GaggiuinoStatus)
    assert isinstance(status.brewSwitchState, bool)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_shot(api_client):
    """Test getting the latst shot id."""
    latest_shot_id = await api_client.get_latest_shot_id()
    assert isinstance(latest_shot_id, GaggiuinoLatestShotResult)
    latest_shot_id = latest_shot_id.lastShotId

    shot_data = await api_client.get_shot(latest_shot_id)
    if shot_data is None:
        pytest.skip("No shot data available for testing")

    assert isinstance(shot_data, GaggiuinoShot)


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_profile_mock(api_client, monkeypatch):
    """Mock profile deletion endpoint and verify behavior.

    - Success when deleting a specific profile id via object and id.
    - Failure for a non-existing/invalid id.
    """
    # Use a fake profile id; we won't hit the real network.
    profile_id = 12345
    profile = GaggiuinoProfile(id=profile_id, name="test")

    async def _fake_delete(url: str, params: dict | None = None) -> bool:  # type: ignore[override]
        # Ensure we call the expected endpoint
        assert url.startswith(f"{api_client.api_base}/profile-select/")
        # Simulate success only for the chosen profile id
        return url.endswith(f"/{profile_id}")

    # Patch the low-level delete used by delete_profile()
    monkeypatch.setattr(api_client, "delete", _fake_delete)

    # Deleting by profile object should succeed
    assert await api_client.delete_profile(profile) is True

    # Deleting by invalid id should fail
    assert await api_client.delete_profile(99999) is False


@pytest.mark.asyncio(loop_scope="session")
async def test_get_health(api_client, monkeypatch):
    """Test getting health status."""
    expected_health = {"status": "ok"}

    async def _fake_get(url: str | None = None, params: dict | None = None):
        # Ensure we call the expected endpoint
        assert url == f"{api_client.api_base}/health"
        return expected_health

    # Patch the get method used by get_health()
    monkeypatch.setattr(api_client, "get", _fake_get)

    # Get health status
    health = await api_client.get_health()
    assert health == expected_health
    assert health["status"] == "ok"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_firmware_all(api_client, monkeypatch):
    """Test updating firmware for all components."""
    call_count = 0

    async def _fake_request(
        method, url, params=None, json_response=False, json_data=None
    ):
        nonlocal call_count
        # Ensure we call the expected endpoint with correct method
        assert method == "POST"
        assert url == f"{api_client.api_base}/firmware/update-all"

        call_count += 1
        if call_count == 1:
            assert json_data == {"version": "latest"}
        elif call_count == 2:
            assert json_data == {"version": "1.0.0"}

        return True  # Simulate success

    # Patch the _request method used by update_firmware_all()
    monkeypatch.setattr(api_client, "_request", _fake_request)

    # Test update firmware with default version
    result = await api_client.update_firmware()
    assert result is True

    # Test update firmware with specific version
    result = await api_client.update_firmware("1.0.0")
    assert result is True

"""End-to-end tests for Gaggiuino API."""

import os
import pytest
import pytest_asyncio
from gaggiuino_api import (
    GaggiuinoAPI,
    GaggiuinoEndpointNotFoundError,
    GaggiuinoProfile,
    GaggiuinoShot,
)
from gaggiuino_api.const import DEFAULT_BASE_URL

pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture(loop_scope="session")
async def api_client():
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
    assert profile_off, "Cannot check withoout a test profile"

    # Test with profile object
    result = await api_client.select_profile(profile_test)
    assert result is True

    # Test with profile ID
    result = await api_client.select_profile(profile_off.id)
    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_get_shot(api_client):
    """Test getting shot data."""
    # Try to get the most recent shot (ID 1)
    shot_data = await api_client.get_shot(1)
    if shot_data is None:
        pytest.skip("No shot data available for testing")

    assert isinstance(shot_data, GaggiuinoShot)


@pytest.mark.asyncio(loop_scope="session")
async def test_invalid_profile_selection(api_client):
    """Test selecting an invalid profile ID."""
    with pytest.raises(
        GaggiuinoEndpointNotFoundError
    ):  # Will raise when profile not found
        await api_client.select_profile(99999)  # Using an arbitrary large ID


@pytest.mark.asyncio(loop_scope="session")
async def test_invalid_shot_request(api_client):
    """Test requesting an invalid shot ID."""
    with pytest.raises(GaggiuinoEndpointNotFoundError):
        await api_client.get_shot(99999)  # Using an arbitrary large ID

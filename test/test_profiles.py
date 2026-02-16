"""Tests for Profiles API endpoints."""

import pytest
from gaggiuino_api import GaggiuinoProfile


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profiles(api_client, mock_profiles_data, monkeypatch):
    """Test retrieving all profiles."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/profiles/all" in url:
            return mock_profiles_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    profiles = await api_client.get_profiles()

    assert profiles is not None
    assert isinstance(profiles, list)
    assert len(profiles) == 2
    assert all(isinstance(p, GaggiuinoProfile) for p in profiles)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profiles_attributes(api_client, mock_profiles_data, monkeypatch):
    """Test that profile attributes are properly parsed."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/profiles/all" in url:
            return mock_profiles_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    profiles = await api_client.get_profiles()

    assert profiles is not None
    # Check first profile
    profile = profiles[0]
    assert profile.id == 1
    assert profile.name == "Espresso"
    assert profile.selected is True
    assert profile.waterTemperature == 90


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profiles_empty(api_client, monkeypatch):
    """Test retrieving profiles when none exist."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/profiles/all" in url:
            return None
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    profiles = await api_client.get_profiles()

    assert profiles is None


@pytest.mark.asyncio(loop_scope="session")
async def test_select_profile_by_id(api_client, monkeypatch):
    """Test selecting a profile by ID."""
    profile_id = 1

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if f"/profile-select/{profile_id}" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    result = await api_client.select_profile(profile_id)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_select_profile_by_object(api_client, monkeypatch):
    """Test selecting a profile by GaggiuinoProfile object."""
    profile = GaggiuinoProfile(id=1, name="Espresso")

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if f"/profile-select/{profile.id}" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    result = await api_client.select_profile(profile)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_select_profile_invalid(api_client, monkeypatch):
    """Test selecting an invalid profile ID."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    result = await api_client.select_profile(99999)

    assert result is False


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_profile_by_id(api_client, monkeypatch):
    """Test deleting a profile by ID."""
    profile_id = 1

    async def _mock_delete(url, params=None):
        if f"/profile-select/{profile_id}" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "delete", _mock_delete)

    result = await api_client.delete_profile(profile_id)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_profile_by_object(api_client, monkeypatch):
    """Test deleting a profile by GaggiuinoProfile object."""
    profile = GaggiuinoProfile(id=1, name="test")

    async def _mock_delete(url, params=None):
        if f"/profile-select/{profile.id}" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "delete", _mock_delete)

    result = await api_client.delete_profile(profile)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_profile_invalid(api_client, monkeypatch):
    """Test deleting an invalid profile ID."""

    async def _mock_delete(url, params=None):
        return False

    monkeypatch.setattr(api_client, "delete", _mock_delete)

    result = await api_client.delete_profile(99999)

    assert result is False


@pytest.mark.asyncio(loop_scope="session")
async def test_profile_property_from_status(api_client, mock_status_data, monkeypatch):
    """Test profile property derived from status."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/system/status" in url:
            return mock_status_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    await api_client.get_status()
    profile = api_client.profile

    assert profile is not None
    assert profile.id == 7
    assert profile.name == "OFF"


@pytest.mark.asyncio(loop_scope="session")
async def test_profile_property_from_profiles(
    api_client, mock_profiles_data, monkeypatch
):
    """Test profile property derived from profiles list."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/profiles/all" in url:
            return mock_profiles_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    await api_client.get_profiles()
    profile = api_client.profile

    assert profile is not None
    assert profile.selected is True


@pytest.mark.asyncio(loop_scope="session")
async def test_profile_phases_parsing(api_client, mock_profiles_data, monkeypatch):
    """Test that profile phases are available as dicts (not parsed into model objects)."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/profiles/all" in url:
            return mock_profiles_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    profiles = await api_client.get_profiles()

    assert profiles is not None
    profile = profiles[0]
    assert profile.phases is not None
    assert len(profile.phases) == 1
    # Phases are passed through as dicts, not parsed into GaggiuinoProfilePhase objects
    phase = profile.phases[0]
    assert isinstance(phase, dict)
    assert phase["restriction"] == 2
    assert phase["skip"] is False
    assert phase["type"] == "FLOW"

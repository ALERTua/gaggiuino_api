"""Tests for Profiles API endpoints."""

import pytest

from gaggiuino_api import (
    GaggiuinoProfile,
    GaggiuinoProfilePhase,
    GaggiuinoProfilePhaseStopCondition,
    GaggiuinoProfilePhaseTarget,
)


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
            return
        return

    monkeypatch.setattr(api_client, "get", _mock_get)

    profiles = await api_client.get_profiles()

    assert profiles is None


@pytest.mark.asyncio(loop_scope="session")
async def test_select_profile_by_id(api_client, monkeypatch):
    """Test selecting a profile by ID."""
    profile_id = 1

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        return f"/profile-select/{profile_id}" in url

    monkeypatch.setattr(api_client, "post", _mock_post)

    result = await api_client.select_profile(profile_id)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_select_profile_by_object(api_client, monkeypatch):
    """Test selecting a profile by GaggiuinoProfile object."""
    profile = GaggiuinoProfile(id=1, name="Espresso")

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        return f"/profile-select/{profile.id}" in url

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
        return f"/profile-select/{profile_id}" in url

    monkeypatch.setattr(api_client, "delete", _mock_delete)

    result = await api_client.delete_profile(profile_id)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_profile_by_object(api_client, monkeypatch):
    """Test deleting a profile by GaggiuinoProfile object."""
    profile = GaggiuinoProfile(id=1, name="test")

    async def _mock_delete(url, params=None):
        return f"/profile-select/{profile.id}" in url

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
async def test_get_profile_by_id(api_client, mock_profile_export_data, monkeypatch):
    """Test retrieving a full profile definition by ID."""
    profile_id = 4

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if f"/profile/{profile_id}" in url:
            return dict(mock_profile_export_data)
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    profile = await api_client.get_profile(profile_id)

    assert profile is not None
    assert isinstance(profile, GaggiuinoProfile)
    # The API omits 'id'; the wrapper restores the requested one
    assert profile.id == profile_id
    assert profile.name == "18g Double"
    assert profile.waterTemperature == 93
    assert profile.recipe == {"coffeeIn": 18, "coffeeOut": 36, "ratio": 2}
    assert len(profile.phases) == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profile_by_object(api_client, mock_profile_export_data, monkeypatch):
    """Test retrieving a full profile definition by GaggiuinoProfile object."""
    stub = GaggiuinoProfile(id=4, name="18g Double")

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if f"/profile/{stub.id}" in url:
            return dict(mock_profile_export_data)
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    profile = await api_client.get_profile(stub)

    assert profile is not None
    assert profile.id == stub.id
    assert profile.name == "18g Double"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_profile_not_found(api_client, monkeypatch):
    """Test retrieving a non-existent profile returns None."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    profile = await api_client.get_profile(99999)

    assert profile is None


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
    """Test that profile phases are parsed into nested model objects."""

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
    phase = profile.phases[0]
    assert isinstance(phase, GaggiuinoProfilePhase)
    assert phase.restriction == 2
    assert phase.skip is False
    assert phase.type == "FLOW"
    assert isinstance(phase.target, GaggiuinoProfilePhaseTarget)
    assert phase.target.curve == "INSTANT"
    assert phase.target.end == 2
    assert phase.target.time == 10000
    assert isinstance(phase.stopConditions, GaggiuinoProfilePhaseStopCondition)
    assert phase.stopConditions.pressureAbove == 2
    assert phase.stopConditions.time == 15000
    assert phase.stopConditions.weight == 0.1


@pytest.mark.asyncio(loop_scope="session")
async def test_profile_phases_unknown_keys(api_client, mock_profiles_data, monkeypatch):
    """Test that unknown keys from newer firmware don't break phase parsing."""
    mock_profiles_data[0]["phases"][0]["someFutureKey"] = 42
    mock_profiles_data[0]["phases"][0]["target"]["anotherFutureKey"] = "x"

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/profiles/all" in url:
            return mock_profiles_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    profiles = await api_client.get_profiles()

    assert profiles is not None
    phase = profiles[0].phases[0]
    assert phase.type == "FLOW"
    assert phase.target.curve == "INSTANT"

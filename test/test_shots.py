"""Tests for Shots API endpoints."""

import pytest

from gaggiuino_api import (
    GaggiuinoEndpointNotFoundError,
    GaggiuinoProfile,
    GaggiuinoShot,
    GaggiuinoShotDataPoints,
)
from gaggiuino_api.models import GaggiuinoLatestShotResult


@pytest.mark.asyncio(loop_scope="session")
async def test_get_shot(api_client, mock_shot_data, monkeypatch):
    """Test retrieving a shot by ID."""
    shot_id = 1

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if f"/shots/{shot_id}" in url:
            return mock_shot_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    shot = await api_client.get_shot(shot_id)

    assert shot is not None
    assert isinstance(shot, GaggiuinoShot)
    assert shot.id == shot_id
    assert shot.duration == mock_shot_data["duration"]
    assert shot.timestamp == mock_shot_data["timestamp"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_shot_not_found(api_client, monkeypatch):
    """Test retrieving a non-existent shot raises error."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        raise GaggiuinoEndpointNotFoundError("endpoint not found")

    monkeypatch.setattr(api_client, "get", _mock_get)

    with pytest.raises(GaggiuinoEndpointNotFoundError):
        await api_client.get_shot(99999)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_latest_shot_id(api_client, mock_latest_shot_data, monkeypatch):
    """Test retrieving the latest shot ID."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/shots/latest" in url:
            return mock_latest_shot_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    result = await api_client.get_latest_shot_id()

    assert result is not None
    assert isinstance(result, GaggiuinoLatestShotResult)
    # lastShotId is returned as string from API but converted to int by from_dict
    assert result.lastShotId == 100
    assert isinstance(result.lastShotId, int)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_latest_shot_id_empty(api_client, monkeypatch):
    """Test retrieving latest shot ID when no shots exist."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/shots/latest" in url:
            return
        return

    monkeypatch.setattr(api_client, "get", _mock_get)

    result = await api_client.get_latest_shot_id()

    assert result is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_shot_by_id(api_client, monkeypatch):
    """Test deleting a shot by ID."""
    shot_id = 1

    async def _mock_delete(url, params=None):
        return f"/shots/{shot_id}" in url

    monkeypatch.setattr(api_client, "delete", _mock_delete)

    result = await api_client.delete_shot(shot_id)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_shot_by_object(api_client, mock_shot_data, monkeypatch):
    """Test deleting a shot by GaggiuinoShot object."""
    shot = GaggiuinoShot.from_dict(mock_shot_data)

    async def _mock_delete(url, params=None):
        return f"/shots/{shot.id}" in url

    monkeypatch.setattr(api_client, "delete", _mock_delete)

    result = await api_client.delete_shot(shot)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_shot_failure(api_client, monkeypatch):
    """Test deleting a shot when the machine has no SD card."""

    async def _mock_delete(url, params=None):
        return False

    monkeypatch.setattr(api_client, "delete", _mock_delete)

    result = await api_client.delete_shot(99999)

    assert result is False


@pytest.mark.asyncio(loop_scope="session")
async def test_shot_datapoints(api_client, mock_shot_data, monkeypatch):
    """Test that shot datapoints are properly parsed."""
    shot_id = 1

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if f"/shots/{shot_id}" in url:
            return mock_shot_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    shot = await api_client.get_shot(shot_id)

    assert shot is not None
    assert isinstance(shot.datapoints, GaggiuinoShotDataPoints)
    assert shot.datapoints.pressure == mock_shot_data["datapoints"]["pressure"]
    assert shot.datapoints.pumpFlow == mock_shot_data["datapoints"]["pumpFlow"]
    assert shot.datapoints.shotWeight == mock_shot_data["datapoints"]["shotWeight"]
    assert shot.datapoints.temperature == mock_shot_data["datapoints"]["temperature"]


@pytest.mark.asyncio(loop_scope="session")
async def test_shot_profile(api_client, mock_shot_data, monkeypatch):
    """Test that shot profile is properly parsed."""
    shot_id = 1

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if f"/shots/{shot_id}" in url:
            return mock_shot_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    shot = await api_client.get_shot(shot_id)

    assert shot is not None
    assert isinstance(shot.profile, GaggiuinoProfile)
    assert shot.profile.id == mock_shot_data["profile"]["id"]
    assert shot.profile.name == mock_shot_data["profile"]["name"]
    assert (
        shot.profile.waterTemperature == mock_shot_data["profile"]["waterTemperature"]
    )

"""Tests for Maintenance API endpoint."""

import pytest

from gaggiuino_api import GaggiuinoEndpointNotFoundError, GaggiuinoMaintenance


@pytest.mark.asyncio(loop_scope="session")
async def test_get_maintenance(api_client, mock_maintenance_data, monkeypatch):
    """Test retrieving maintenance history."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/maintenance" in url:
            return mock_maintenance_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    maintenance = await api_client.get_maintenance()

    assert maintenance is not None
    assert isinstance(maintenance, GaggiuinoMaintenance)
    assert maintenance.lastDescaleTimestamp == 1753900000
    assert maintenance.shotsSinceDescale == 42
    assert maintenance.lastBackflushTimestamp == 1753000000
    assert maintenance.shotsSinceBackflush == 10


@pytest.mark.asyncio(loop_scope="session")
async def test_get_maintenance_never_recorded(api_client, monkeypatch):
    """Test maintenance response with zero timestamps (never recorded)."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/maintenance" in url:
            return {
                "lastDescaleTimestamp": 0,
                "shotsSinceDescale": 0,
                "lastBackflushTimestamp": 0,
                "shotsSinceBackflush": 0,
            }
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    maintenance = await api_client.get_maintenance()

    assert maintenance is not None
    assert maintenance.lastDescaleTimestamp == 0
    assert maintenance.lastBackflushTimestamp == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_maintenance_empty(api_client, monkeypatch):
    """Test maintenance endpoint returning no data."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    maintenance = await api_client.get_maintenance()

    assert maintenance is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_maintenance_not_found(api_client, monkeypatch):
    """Test maintenance endpoint missing on older firmware (404)."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        raise GaggiuinoEndpointNotFoundError("endpoint not found")

    monkeypatch.setattr(api_client, "get", _mock_get)

    with pytest.raises(GaggiuinoEndpointNotFoundError):
        await api_client.get_maintenance()

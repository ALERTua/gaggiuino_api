"""Tests for System API endpoints."""

import pytest
from gaggiuino_api import GaggiuinoStatus


@pytest.mark.asyncio(loop_scope="session")
async def test_get_status(api_client, mock_status_data, monkeypatch):
    """Test retrieving system status."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/system/status" in url:
            return mock_status_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    status = await api_client.get_status()

    assert status is not None
    assert isinstance(status, GaggiuinoStatus)


@pytest.mark.asyncio(loop_scope="session")
async def test_status_attributes(api_client, mock_status_data, monkeypatch):
    """Test that status attributes are properly parsed."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/system/status" in url:
            return mock_status_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    status = await api_client.get_status()

    assert status is not None
    assert status.upTime == 89107
    assert status.profileId == 7
    assert status.profileName == "OFF"
    assert status.targetTemperature == 15.0
    assert status.temperature == 22.5
    assert status.pressure == -0.028054
    assert status.waterLevel == 100
    assert status.weight == 0.0
    assert status.brewSwitchState is False
    assert status.steamSwitchState is False


@pytest.mark.asyncio(loop_scope="session")
async def test_status_boolean_parsing(api_client, monkeypatch):
    """Test that boolean string values are properly parsed."""
    status_data = [
        {
            "upTime": "100",
            "profileId": "1",
            "profileName": "Test",
            "targetTemperature": "90.0",
            "temperature": "92.5",
            "pressure": "9.5",
            "waterLevel": "50",
            "weight": "25.0",
            "brewSwitchState": "true",
            "steamSwitchState": "true",
        }
    ]

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/system/status" in url:
            return status_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    status = await api_client.get_status()

    assert status is not None
    assert status.brewSwitchState is True
    assert status.steamSwitchState is True


@pytest.mark.asyncio(loop_scope="session")
async def test_status_empty(api_client, monkeypatch):
    """Test retrieving status when no data is available."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/system/status" in url:
            return []
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    status = await api_client.get_status()

    assert status is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_health(api_client, mock_health_data, monkeypatch):
    """Test retrieving health status."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/health" in url:
            return mock_health_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    health = await api_client.get_health()

    assert health is not None
    assert health["status"] == "ok"


@pytest.mark.asyncio(loop_scope="session")
async def test_healthy(api_client, mock_health_data, monkeypatch):
    """Test healthy check returns True when status is ok."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/health" in url:
            return mock_health_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    is_healthy = await api_client.healthy()

    assert is_healthy is True


@pytest.mark.asyncio(loop_scope="session")
async def test_healthy_failure(api_client, monkeypatch):
    """Test healthy check returns False when status is not ok."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/health" in url:
            return {"status": "error"}
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    is_healthy = await api_client.healthy()

    assert is_healthy is False


@pytest.mark.asyncio(loop_scope="session")
async def test_get_firmware_progress(
    api_client, mock_firmware_progress_data, monkeypatch
):
    """Test retrieving firmware update progress."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/firmware/progress" in url:
            return mock_firmware_progress_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    progress = await api_client.get_firmware_progress()

    assert progress is not None
    assert progress["progress"] == 0
    assert progress["status"] == "IDLE"
    assert progress["type"] == "F_FW"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_firmware(api_client, monkeypatch):
    """Test initiating firmware update."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/firmware/update-all" in url:
            assert json_data == {"version": "latest"}
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    result = await api_client.update_firmware()

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_update_firmware_specific_version(api_client, monkeypatch):
    """Test initiating firmware update with specific version."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/firmware/update-all" in url:
            assert json_data == {"version": "1.0.0"}
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    result = await api_client.update_firmware("1.0.0")

    assert result is True

"""Tests for the low-level request handling."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from gaggiuino_api import (
    GaggiuinoEndpointNotFoundError,
    GaggiuinoResponseError,
)


def _mock_request(mock_session, status, json_data=None, text_data=""):
    """Set up mock_session.request to return a response context manager."""
    response = MagicMock()
    response.status = status
    response.json = AsyncMock(return_value=json_data)
    response.text = AsyncMock(return_value=text_data)

    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    mock_session.request = MagicMock(return_value=ctx)


@pytest.mark.asyncio(loop_scope="session")
async def test_request_json_response_ok(api_client, mock_session):
    """Test that a 200 JSON response is returned as data."""
    _mock_request(mock_session, 200, json_data={"status": "ok"})

    result = await api_client.get(f"{api_client.api_base}/health")

    assert result == {"status": "ok"}


@pytest.mark.asyncio(loop_scope="session")
async def test_request_json_response_error_status(api_client, mock_session):
    """Test that a 4xx/5xx JSON response raises GaggiuinoResponseError."""
    _mock_request(mock_session, 422, text_data="malformed JSON")

    with pytest.raises(GaggiuinoResponseError) as exc_info:
        await api_client.get(f"{api_client.api_base}/profile")

    assert exc_info.value.status == 422
    assert exc_info.value.body == "malformed JSON"


@pytest.mark.asyncio(loop_scope="session")
async def test_request_404_raises_not_found(api_client, mock_session):
    """Test that a 404 raises GaggiuinoEndpointNotFoundError."""
    _mock_request(mock_session, 404)

    with pytest.raises(GaggiuinoEndpointNotFoundError):
        await api_client.get(f"{api_client.api_base}/nonexistent")


@pytest.mark.asyncio(loop_scope="session")
async def test_request_bool_response_error_status(api_client, mock_session):
    """Test that a non-JSON request returns False on error status."""
    _mock_request(mock_session, 500)

    result = await api_client.post(f"{api_client.api_base}/profile-select/1")

    assert result is False

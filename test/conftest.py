"""Shared fixtures for Gaggiuino API tests."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from aiohttp import ClientSession

from gaggiuino_api import GaggiuinoAPI
from gaggiuino_api.const import DEFAULT_BASE_URL

pytest_plugins = ("pytest_asyncio",)

# Mock data fixtures


@pytest.fixture
def mock_status_data():
    """Mock status response data."""
    return [
        {
            "upTime": "89107",
            "profileId": "7",
            "profileName": "OFF",
            "targetTemperature": "15.000000",
            "temperature": "22.500000",
            "pressure": "-0.028054",
            "waterLevel": "100",
            "weight": "0.000000",
            "brewSwitchState": "false",
            "steamSwitchState": "false",
        }
    ]


@pytest.fixture
def mock_profiles_data():
    """Mock profiles response data."""
    return [
        {
            "id": 1,
            "name": "Espresso",
            "selected": True,
            "globalStopConditions": {"weight": 50},
            "phases": [
                {
                    "restriction": 2,
                    "skip": False,
                    "stopConditions": {
                        "pressureAbove": 2,
                        "time": 15000,
                        "weight": 0.1,
                    },
                    "target": {"curve": "INSTANT", "end": 2, "time": 10000},
                    "type": "FLOW",
                }
            ],
            "recipe": {},
            "waterTemperature": 90,
        },
        {
            "id": 2,
            "name": "_OFF",
            "selected": False,
            "globalStopConditions": {},
            "phases": [],
            "recipe": {},
            "waterTemperature": 0,
        },
    ]


@pytest.fixture
def mock_shot_data():
    """Mock shot response data."""
    return {
        "datapoints": {
            "pressure": [3, 3, 3],
            "pumpFlow": [0, 6, 12],
            "shotWeight": [0, 0, 0],
            "targetPressure": [20, 20, 20],
            "targetPumpFlow": [20, 20, 20],
            "targetTemperature": [900, 900, 900],
            "temperature": [898, 898, 898],
            "timeInShot": [2, 3, 5],
            "waterPumped": [0, 2, 4],
            "weightFlow": [0, 0, 0],
        },
        "duration": 648,
        "id": 1,
        "profile": {
            "id": 1,
            "name": "Espresso",
            "globalStopConditions": {"weight": 50},
            "phases": [],
            "recipe": {},
            "waterTemperature": 90,
        },
        "timestamp": 1731316192,
    }


@pytest.fixture
def mock_latest_shot_data():
    """Mock latest shot ID response data."""
    return [{"lastShotId": "100"}]


@pytest.fixture
def mock_boiler_settings_data():
    """Mock boiler settings response data."""
    return {
        "steamSetPoint": 145,
        "offsetTemp": 5,
        "hpwr": 1200,
        "mainDivider": 2,
        "brewDivider": 4,
        "brewDeltaState": "true",
        "dreamSteamState": "false",
        "startupHeatDelta": 10,
    }


@pytest.fixture
def mock_system_settings_data():
    """Mock system settings response data."""
    return {
        "pumpFlowAtZero": 0.5,
        "timezoneOffsetMinutes": -300,
        "sprofilerToken": "abc123xyz",
        "visualizerToken": "def456uvw",
        "servicesState": True,
        "wifiEnabled": True,
        "releaseChannel": 0,
    }


@pytest.fixture
def mock_theme_settings_data():
    """Mock theme settings response data."""
    return {"colourPrimary": 31, "colourSecondary": 63488}


@pytest.fixture
def mock_display_settings_data():
    """Mock display settings response data."""
    return {
        "lcdBrightness": 80,
        "lcdDarkMode": "false",
        "lcdSleep": 10,
        "lcdGoHome": 5,
    }


@pytest.fixture
def mock_scales_settings_data():
    """Mock scales settings response data."""
    return {
        "forcePredictive": "false",
        "hwScalesEnabled": "true",
        "hwScalesF1": 1000,
        "hwScalesF2": 2000,
        "btScalesEnabled": "false",
        "btScalesAutoConnect": "false",
    }


@pytest.fixture
def mock_led_settings_data():
    """Mock LED settings response data."""
    return {
        "color": {"R": 255, "G": 128, "B": 0},
        "state": "true",
        "disco": "false",
        "tof": {"max": 100, "min": 10},
    }


@pytest.fixture
def mock_versions_data():
    """Mock versions response data."""
    return {
        "coreVersion": "a06f97fd",
        "frontVersion": "a06f97fd",
        "staticVersion": "a06f97fd",
    }


@pytest.fixture
def mock_settings_data(
    mock_boiler_settings_data,
    mock_system_settings_data,
    mock_led_settings_data,
    mock_scales_settings_data,
    mock_display_settings_data,
    mock_theme_settings_data,
    mock_versions_data,
):
    """Mock aggregate settings response data."""
    return {
        "boiler": mock_boiler_settings_data,
        "system": mock_system_settings_data,
        "led": mock_led_settings_data,
        "scales": mock_scales_settings_data,
        "display": mock_display_settings_data,
        "theme": mock_theme_settings_data,
        "versions": mock_versions_data,
    }


@pytest.fixture
def mock_health_data():
    """Mock health response data."""
    return {"status": "ok"}


@pytest.fixture
def mock_firmware_progress_data():
    """Mock firmware progress response data."""
    return {"progress": 0, "status": "IDLE", "type": "F_FW"}


# API Client fixtures


@pytest_asyncio.fixture(loop_scope="session", name="mock_session")
async def _mock_session():
    """Mock aiohttp session."""
    session = MagicMock(spec=ClientSession)
    yield session


@pytest_asyncio.fixture(loop_scope="session", name="api_client")
async def _api_client(mock_session):
    """API client with mocked session for unit tests."""
    async with GaggiuinoAPI(session=mock_session) as client:
        yield client


@pytest_asyncio.fixture(loop_scope="session", name="real_api_client")
async def _real_api_client():
    """Real API client for integration tests.

    This fixture creates a real connection to the Gaggiuino device.
    Should only be used in integration tests that are skipped by default.
    """
    async with GaggiuinoAPI(base_url=DEFAULT_BASE_URL) as client:
        yield client


# Helper fixtures for mocking responses


@pytest.fixture
def mock_response():
    """Factory fixture to create mock responses."""

    def _create_mock_response(data, status=200):
        response = AsyncMock()
        response.status = status
        response.json = AsyncMock(return_value=data)
        return response

    return _create_mock_response


@pytest.fixture
def mock_get_factory(mock_response):
    """Factory fixture to create mock GET responses."""

    def _create_mock_get(url_pattern, response_data, status=200):
        """Create a mock GET method that returns specific data for URL patterns."""

        async def _mock_get(url, params=None, json_response=True, **kwargs):
            if url_pattern in url:
                return response_data
            return None

        return _mock_get

    return _create_mock_get


@pytest.fixture
def mock_post_factory():
    """Factory fixture to create mock POST responses."""

    def _create_mock_post(success=True):
        """Create a mock POST method that returns success/failure."""

        async def _mock_post(url, params=None, json_data=None, **kwargs):
            return success

        return _mock_post

    return _create_mock_post

"""Tests for Settings API endpoints."""

import pytest
from gaggiuino_api.models import (
    GaggiuinoSettings,
    GaggiuinoBoilerSettings,
    GaggiuinoSystemSettings,
    GaggiuinoLedSettings,
    GaggiuinoLedColor,
    GaggiuinoTofSettings,
    GaggiuinoScalesSettings,
    GaggiuinoDisplaySettings,
    GaggiuinoThemeSettings,
    GaggiuinoVersions,
)


# Aggregate Settings Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_settings(api_client, mock_settings_data, monkeypatch):
    """Test retrieving all settings."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings" in url and "/settings/" not in url:
            return mock_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_settings()

    assert settings is not None
    assert isinstance(settings, GaggiuinoSettings)


@pytest.mark.asyncio(loop_scope="session")
async def test_settings_contains_all_categories(
    api_client, mock_settings_data, monkeypatch
):
    """Test that settings contains all expected categories."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings" in url and "/settings/" not in url:
            return mock_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_settings()

    assert settings is not None
    assert isinstance(settings.boiler, GaggiuinoBoilerSettings)
    assert isinstance(settings.system, GaggiuinoSystemSettings)
    assert isinstance(settings.led, GaggiuinoLedSettings)
    assert isinstance(settings.scales, GaggiuinoScalesSettings)
    assert isinstance(settings.display, GaggiuinoDisplaySettings)
    assert isinstance(settings.theme, GaggiuinoThemeSettings)
    assert isinstance(settings.versions, GaggiuinoVersions)


# Boiler Settings Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_boiler_settings(api_client, mock_boiler_settings_data, monkeypatch):
    """Test retrieving boiler settings."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/boiler" in url:
            return mock_boiler_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_boiler_settings()

    assert settings is not None
    assert isinstance(settings, GaggiuinoBoilerSettings)
    assert settings.steamSetPoint == 145
    assert settings.offsetTemp == 5
    assert settings.hpwr == 1200


@pytest.mark.asyncio(loop_scope="session")
async def test_update_boiler_settings_with_model(
    api_client, mock_boiler_settings_data, monkeypatch
):
    """Test updating boiler settings with model object."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/settings/boiler" in url:
            assert json_data is not None
            assert json_data["steamSetPoint"] == 145
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    settings = GaggiuinoBoilerSettings.from_dict(mock_boiler_settings_data)
    result = await api_client.update_boiler_settings(settings)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_update_boiler_settings_with_dict(
    api_client, mock_boiler_settings_data, monkeypatch
):
    """Test updating boiler settings with dict."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/settings/boiler" in url:
            assert json_data is not None
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    result = await api_client.update_boiler_settings(mock_boiler_settings_data)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_boiler_settings_to_api_dict(mock_boiler_settings_data):
    """Test that boiler settings can be serialized to API format."""
    settings = GaggiuinoBoilerSettings.from_dict(mock_boiler_settings_data)
    api_dict = settings.to_api_dict()

    assert api_dict["steamSetPoint"] == 145
    assert api_dict["offsetTemp"] == 5
    assert api_dict["hpwr"] == 1200
    assert api_dict["mainDivider"] == 2
    assert api_dict["brewDivider"] == 4
    assert api_dict["brewDeltaState"] == "true"
    assert api_dict["dreamSteamState"] == "false"
    assert api_dict["startupHeatDelta"] == 10


# System Settings Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_system_settings(api_client, mock_system_settings_data, monkeypatch):
    """Test retrieving system settings."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/system" in url:
            return mock_system_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_system_settings()

    assert settings is not None
    assert isinstance(settings, GaggiuinoSystemSettings)
    assert settings.pumpFlowAtZero == 0.5
    assert settings.timezoneOffsetMinutes == -300
    assert settings.servicesState is True
    assert settings.wifiEnabled is True
    assert settings.releaseChannel == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_update_system_settings(
    api_client, mock_system_settings_data, monkeypatch
):
    """Test updating system settings."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/settings/system" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    settings = GaggiuinoSystemSettings.from_dict(mock_system_settings_data)
    result = await api_client.update_system_settings(settings)

    assert result is True


# Theme Settings Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_theme_settings(api_client, mock_theme_settings_data, monkeypatch):
    """Test retrieving theme settings."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/theme" in url:
            return mock_theme_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_theme_settings()

    assert settings is not None
    assert isinstance(settings, GaggiuinoThemeSettings)
    assert settings.colourPrimary == 31
    assert settings.colourSecondary == 63488


@pytest.mark.asyncio(loop_scope="session")
async def test_update_theme_settings(api_client, mock_theme_settings_data, monkeypatch):
    """Test updating theme settings."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/settings/theme" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    settings = GaggiuinoThemeSettings.from_dict(mock_theme_settings_data)
    result = await api_client.update_theme_settings(settings)

    assert result is True


# Display Settings Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_display_settings(
    api_client, mock_display_settings_data, monkeypatch
):
    """Test retrieving display settings."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/display" in url:
            return mock_display_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_display_settings()

    assert settings is not None
    assert isinstance(settings, GaggiuinoDisplaySettings)
    assert settings.lcdBrightness == 80
    assert settings.lcdDarkMode == "false"
    assert settings.lcdSleep == 10
    assert settings.lcdGoHome == 5


@pytest.mark.asyncio(loop_scope="session")
async def test_update_display_settings(
    api_client, mock_display_settings_data, monkeypatch
):
    """Test updating display settings."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/settings/display" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    settings = GaggiuinoDisplaySettings.from_dict(mock_display_settings_data)
    result = await api_client.update_display_settings(settings)

    assert result is True


# Scales Settings Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_scales_settings(api_client, mock_scales_settings_data, monkeypatch):
    """Test retrieving scales settings."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/scales" in url:
            return mock_scales_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_scales_settings()

    assert settings is not None
    assert isinstance(settings, GaggiuinoScalesSettings)
    assert settings.forcePredictive is False
    assert settings.hwScalesEnabled is True
    assert settings.hwScalesF1 == 1000
    assert settings.hwScalesF2 == 2000


@pytest.mark.asyncio(loop_scope="session")
async def test_update_scales_settings(
    api_client, mock_scales_settings_data, monkeypatch
):
    """Test updating scales settings."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/settings/scales" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    settings = GaggiuinoScalesSettings.from_dict(mock_scales_settings_data)
    result = await api_client.update_scales_settings(settings)

    assert result is True


# LED Settings Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_led_settings(api_client, mock_led_settings_data, monkeypatch):
    """Test retrieving LED settings."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/led" in url:
            return mock_led_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_led_settings()

    assert settings is not None
    assert isinstance(settings, GaggiuinoLedSettings)
    assert settings.state is True
    assert settings.disco is False


@pytest.mark.asyncio(loop_scope="session")
async def test_led_settings_color(api_client, mock_led_settings_data, monkeypatch):
    """Test LED settings color parsing."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/led" in url:
            return mock_led_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_led_settings()

    assert settings is not None
    assert isinstance(settings.color, GaggiuinoLedColor)
    assert settings.color.R == 255
    assert settings.color.G == 128
    assert settings.color.B == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_led_settings_tof(api_client, mock_led_settings_data, monkeypatch):
    """Test LED settings time-of-flight sensor parsing."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/led" in url:
            return mock_led_settings_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_led_settings()

    assert settings is not None
    assert isinstance(settings.tof, GaggiuinoTofSettings)
    assert settings.tof.max == 100
    assert settings.tof.min == 10


@pytest.mark.asyncio(loop_scope="session")
async def test_update_led_settings(api_client, mock_led_settings_data, monkeypatch):
    """Test updating LED settings."""

    async def _mock_post(url, params=None, json_data=None, **kwargs):
        if "/settings/led" in url:
            return True
        return False

    monkeypatch.setattr(api_client, "post", _mock_post)

    settings = GaggiuinoLedSettings.from_dict(mock_led_settings_data)
    result = await api_client.update_led_settings(settings)

    assert result is True


@pytest.mark.asyncio(loop_scope="session")
async def test_led_settings_to_api_dict(mock_led_settings_data):
    """Test that LED settings can be serialized to API format."""
    settings = GaggiuinoLedSettings.from_dict(mock_led_settings_data)
    api_dict = settings.to_api_dict()

    assert "color" in api_dict
    assert api_dict["color"]["R"] == 255
    assert api_dict["color"]["G"] == 128
    assert api_dict["color"]["B"] == 0
    assert api_dict["state"] is True
    assert api_dict["disco"] is False
    assert "tof" in api_dict
    assert api_dict["tof"]["max"] == 100
    assert api_dict["tof"]["min"] == 10


# Versions Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_versions(api_client, mock_versions_data, monkeypatch):
    """Test retrieving version information."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        if "/settings/versions" in url:
            return mock_versions_data
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    versions = await api_client.get_versions()

    assert versions is not None
    assert isinstance(versions, GaggiuinoVersions)
    assert versions.coreVersion == "a06f97fd"
    assert versions.frontVersion == "a06f97fd"
    assert versions.staticVersion == "a06f97fd"


# Empty/None Response Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_get_settings_empty(api_client, monkeypatch):
    """Test retrieving settings when no data is available."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_settings()

    assert settings is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_boiler_settings_empty(api_client, monkeypatch):
    """Test retrieving boiler settings when no data is available."""

    async def _mock_get(url, params=None, json_response=True, **kwargs):
        return None

    monkeypatch.setattr(api_client, "get", _mock_get)

    settings = await api_client.get_boiler_settings()

    assert settings is None

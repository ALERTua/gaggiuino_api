"""End-to-end tests for Gaggiuino API.

These tests run against real hardware and are deselected by default
(see addopts in pyproject.toml).
To run these tests, ensure your Gaggiuino device is powered on and accessible.

Run with: pytest -v -m e2e test/e2e
"""

import os
import time
from dataclasses import replace

import pytest

from gaggiuino_api import (
    GaggiuinoMaintenance,
    GaggiuinoProfile,
    GaggiuinoSettings,
    GaggiuinoShot,
    GaggiuinoStatus,
)
from gaggiuino_api.models import GaggiuinoLatestShotResult

# Mark all tests in this module as end-to-end tests
pytestmark = pytest.mark.e2e


# Health Check Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_health(real_api_client):
    """Test real health endpoint."""
    is_healthy = await real_api_client.healthy()
    assert is_healthy is True, "Gaggiuino device is not healthy or not reachable"


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_health(real_api_client):
    """Test real health endpoint returns status."""
    health = await real_api_client.get_health()
    assert health is not None
    assert health.get("status") == "ok"


# System Status Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_status(real_api_client):
    """Test real system status endpoint."""
    status = await real_api_client.get_status()
    assert status is not None
    assert isinstance(status, GaggiuinoStatus)
    assert isinstance(status.brewSwitchState, bool)
    assert isinstance(status.steamSwitchState, bool)


# Profile Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_profiles(real_api_client):
    """Test real profiles endpoint."""
    profiles = await real_api_client.get_profiles()
    assert profiles is not None
    assert isinstance(profiles, list)
    assert len(profiles) > 0
    assert all(isinstance(p, GaggiuinoProfile) for p in profiles)


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_profile(real_api_client):
    """Test real single profile retrieval (full definition)."""
    profiles = await real_api_client.get_profiles()
    assert profiles

    profile = await real_api_client.get_profile(profiles[0])
    assert profile is not None
    assert isinstance(profile, GaggiuinoProfile)
    assert profile.id == profiles[0].id
    assert profile.name == profiles[0].name
    assert profile.phases is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_profile_selection(real_api_client):
    """Test profile selection with restoration.

    Pattern: Read -> Modify -> Verify -> Restore
    """
    # Get all profiles
    profiles = await real_api_client.get_profiles()
    assert profiles is not None

    # Find OFF and a test profile
    profile_off_name = os.getenv("GAGGIUINO_PROFILE_OFF", "_OFF")
    profile_test_name = os.getenv("GAGGIUINO_PROFILE_TEST", "test")

    profile_off = next((_ for _ in profiles if _.name == profile_off_name), None)
    profile_test = next((_ for _ in profiles if _.name == profile_test_name), None)
    if profile_off is None or profile_test is None:
        pytest.skip(
            f"Profiles '{profile_off_name}' and '{profile_test_name}' must exist"
        )

    # Get current status to know original profile
    original_status = await real_api_client.get_status()
    original_profile_id = original_status.profileId
    select_profile = (
        profile_test if original_profile_id == profile_off.id else profile_off
    )  # select opposite profile

    try:
        # Select test profile
        result = await real_api_client.select_profile(select_profile)
        assert result is True

        # Verify change
        status = await real_api_client.get_status()
        assert status.profileId == select_profile.id

    finally:
        # Restore original profile
        await real_api_client.select_profile(original_profile_id)


# Shot Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_latest_shot_id(real_api_client):
    """Test real latest shot ID endpoint."""
    result = await real_api_client.get_latest_shot_id()
    assert result is not None
    assert isinstance(result, GaggiuinoLatestShotResult)
    assert result.lastShotId >= 0


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_shot(real_api_client):
    """Test real shot retrieval."""
    # Get latest shot ID
    latest = await real_api_client.get_latest_shot_id()
    if latest is None or latest.lastShotId == 0:
        pytest.skip("No shots available for testing")

    # Get the shot
    shot = await real_api_client.get_shot(latest.lastShotId)
    assert shot is not None
    assert isinstance(shot, GaggiuinoShot)
    assert shot.id == latest.lastShotId


# Maintenance Tests


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_maintenance(real_api_client):
    """Test real maintenance history endpoint."""
    maintenance = await real_api_client.get_maintenance()
    assert maintenance is not None
    assert isinstance(maintenance, GaggiuinoMaintenance)
    assert maintenance.lastDescaleTimestamp >= 0
    assert maintenance.shotsSinceDescale >= 0
    assert maintenance.lastBackflushTimestamp >= 0
    assert maintenance.shotsSinceBackflush >= 0


# Settings Tests - Each follows the Read -> Modify -> Verify -> Restore pattern


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_settings(real_api_client):
    """Test real settings endpoint."""
    settings = await real_api_client.get_settings()
    assert settings is not None
    assert isinstance(settings, GaggiuinoSettings)


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_boiler_settings_roundtrip(real_api_client):
    """Test boiler settings GET/POST with restoration.

    Pattern: Read -> Modify -> Verify -> Restore
    """
    # 1. Read current settings
    original = await real_api_client.get_boiler_settings()
    assert original is not None

    # 2. Modify settings (increment steamSetPoint by 1)
    modified = replace(original, steamSetPoint=original.steamSetPoint + 1)
    result = await real_api_client.update_boiler_settings(modified)
    assert result is True

    # 3. Verify change
    current = await real_api_client.get_boiler_settings()
    assert current is not None
    assert current.steamSetPoint == modified.steamSetPoint

    # 4. Restore original
    await real_api_client.update_boiler_settings(original)
    restored = await real_api_client.get_boiler_settings()
    assert restored is not None
    assert restored.steamSetPoint == original.steamSetPoint


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_display_settings_roundtrip(real_api_client):
    """Test display settings GET/POST with restoration.

    Pattern: Read -> Modify -> Verify -> Restore
    """
    # 1. Read current settings
    original = await real_api_client.get_display_settings()
    assert original is not None

    # 2. Modify settings (increment lcdSleep by 1)
    modified = replace(original, lcdSleep=original.lcdSleep + 1)
    result = await real_api_client.update_display_settings(modified)
    assert result is True

    # 3. Verify change
    current = await real_api_client.get_display_settings()
    assert current is not None
    assert current.lcdSleep == modified.lcdSleep

    # 4. Restore original
    await real_api_client.update_display_settings(original)
    restored = await real_api_client.get_display_settings()
    assert restored is not None
    assert restored.lcdSleep == original.lcdSleep


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_theme_settings_roundtrip(real_api_client):
    """Test theme settings GET/POST with restoration.

    Pattern: Read -> Modify -> Verify -> Restore
    """
    # 1. Read current settings
    original = await real_api_client.get_theme_settings()
    assert original is not None

    # 2. Modify settings (increment primary color by 1)
    modified = replace(original, colourPrimary=original.colourPrimary + 1)
    result = await real_api_client.update_theme_settings(modified)
    assert result is True

    # 3. Verify change
    current = await real_api_client.get_theme_settings()
    assert current is not None
    assert current.colourPrimary == modified.colourPrimary

    # 4. Restore original
    await real_api_client.update_theme_settings(original)
    restored = await real_api_client.get_theme_settings()
    assert restored is not None
    assert restored.colourPrimary == original.colourPrimary


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_scales_settings_roundtrip(real_api_client):
    """Test scales settings GET/POST with restoration.

    Pattern: Read -> Modify -> Verify -> Restore
    """
    # 1. Read current settings
    original = await real_api_client.get_scales_settings()
    assert original is not None

    # 2. Modify settings (toggle forcePredictive boolean)
    modified = replace(original, forcePredictive=not original.forcePredictive)
    result = await real_api_client.update_scales_settings(modified)
    assert result is True

    # 3. Verify change
    current = await real_api_client.get_scales_settings()
    assert current is not None
    assert current.forcePredictive == modified.forcePredictive

    # 4. Restore original
    await real_api_client.update_scales_settings(original)
    restored = await real_api_client.get_scales_settings()
    assert restored is not None
    assert restored.forcePredictive == original.forcePredictive


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_led_settings_roundtrip(real_api_client):
    """Test LED settings GET/POST with restoration.

    Pattern: Read -> Modify -> Verify -> Restore
    """
    # 1. Read current settings
    original = await real_api_client.get_led_settings()
    assert original is not None

    # 2. Modify settings (toggle disco boolean)
    modified = replace(original, disco=not original.disco)
    result = await real_api_client.update_led_settings(modified)
    assert result is True

    # 3. Verify change
    current = await real_api_client.get_led_settings()
    assert current is not None
    assert current.disco == modified.disco

    # 4. Restore original
    await real_api_client.update_led_settings(original)
    restored = await real_api_client.get_led_settings()
    assert restored is not None
    assert restored.disco == original.disco


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_system_settings_roundtrip(real_api_client):
    """Test system settings GET/POST with restoration.

    Pattern: Read -> Modify -> Verify -> Restore
    Note: This test modifies sprofilerToken which is relatively safe.
    """
    # 1. Read current settings
    original = await real_api_client.get_system_settings()
    assert original is not None

    # 2. Modify settings (change sprofilerToken to unique value)
    fake_token = f"test_token_{int(time.time())}"
    modified = replace(original, sprofilerToken=fake_token)
    result = await real_api_client.update_system_settings(modified)
    assert result is True

    # 3. Verify change
    current = await real_api_client.get_system_settings()
    assert current is not None
    assert current.sprofilerToken == fake_token

    # 4. Restore original
    await real_api_client.update_system_settings(original)
    restored = await real_api_client.get_system_settings()
    assert restored is not None
    assert restored.sprofilerToken == original.sprofilerToken


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_versions(real_api_client):
    """Test versions endpoint (read-only)."""
    versions = await real_api_client.get_versions()
    assert versions is not None
    assert versions.coreVersion is not None
    assert versions.frontVersion is not None
    assert versions.staticVersion is not None


# Firmware Tests (Read-only - we don't want to actually trigger updates)


@pytest.mark.asyncio(loop_scope="session")
async def test_e2e_get_firmware_progress(real_api_client):
    """Test firmware progress endpoint."""
    progress = await real_api_client.get_firmware_progress()
    assert progress is not None
    assert "progress" in progress
    assert "status" in progress
    assert "type" in progress

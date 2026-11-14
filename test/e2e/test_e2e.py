"""End-to-end tests of the client against a real machine.

The tests are deselected by default. Run them with `uv run pytest -m e2e test/e2e`.
Each test that changes the machine reads the state first and restores it in a `finally`
block, also when an assert fails. A write goes only to the `led` or `display` settings
group and to the profiles. A test deletes only the profile that it created itself.
"""

import asyncio
import dataclasses
import json

import pytest

from e2e.e2e_support import is_selected, profile_rows, settings_equal, wait_until
from gaggiuino_api import (
    BoilerSettings,
    DisplaySettings,
    FirmwareProgress,
    GaggiuinoClient,
    GaggiuinoNotFoundError,
    GaggiuinoResponseError,
    LedSettings,
    Maintenance,
    Profile,
    ProfileSummary,
    ScalesSettings,
    Settings,
    Shot,
    SystemSettings,
    ThemeSettings,
    Versions,
)

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio(loop_scope='session')]

# An id of a shot or a profile that does not exist on the machine.
MISSING_ID = 999999

TEST_PROFILE_NAME = '_e2e_test'


async def selected_and_other(
    machine: GaggiuinoClient,
) -> tuple[ProfileSummary, ProfileSummary]:
    """Return the selected profile and another saved profile."""
    profiles = await machine.profiles.list()
    selected = [p for p in profiles if p.selected]
    assert len(selected) == 1
    others = [p for p in profiles if not p.selected]
    if not others:
        pytest.skip('The machine needs at least two saved profiles')
    return selected[0], others[0]


async def test_healthy(machine: GaggiuinoClient) -> None:
    assert await machine.healthy() is True


async def test_status(machine: GaggiuinoClient) -> None:
    status = await machine.status()
    selected, _ = await selected_and_other(machine)
    # Each value goes to a local name, so a failed assert never shows the whole status.
    profile_id = status.profile_id
    up_time = status.up_time
    temperature = status.temperature
    pressure = status.pressure
    brew_switch_state = status.brew_switch_state
    assert profile_id == selected.id
    assert isinstance(up_time, int)
    assert isinstance(temperature, float)
    assert isinstance(pressure, float)
    assert isinstance(brew_switch_state, bool)


async def test_maintenance(machine: GaggiuinoClient) -> None:
    maintenance = await machine.maintenance()
    assert isinstance(maintenance, Maintenance)
    assert maintenance.shots_since_descale >= 0


async def test_firmware_progress(machine: GaggiuinoClient) -> None:
    progress = await machine.firmware.progress()
    assert isinstance(progress, FirmwareProgress)
    assert 0 <= progress.progress <= 100


async def test_settings_get(machine: GaggiuinoClient) -> None:
    settings = await machine.settings.get()
    # The settings hold private values, so a failed assert shows only a flag.
    ok = isinstance(settings, Settings) and isinstance(settings.system, SystemSettings)
    assert ok


@pytest.mark.parametrize(
    ('group', 'model'),
    [
        ('boiler', BoilerSettings),
        ('system', SystemSettings),
        ('led', LedSettings),
        ('scales', ScalesSettings),
        ('display', DisplaySettings),
        ('theme', ThemeSettings),
    ],
)
async def test_settings_group_get(
    machine: GaggiuinoClient, group: str, model: type
) -> None:
    value = await getattr(machine.settings, group).get()
    # Some groups hold private values, so a failed assert shows only a flag.
    ok = isinstance(value, model)
    assert ok


async def test_settings_versions(machine: GaggiuinoClient) -> None:
    versions = await machine.settings.versions()
    assert isinstance(versions, Versions)
    assert versions.core_version


async def test_profiles_list_and_get(machine: GaggiuinoClient) -> None:
    profiles = await machine.profiles.list()
    assert profiles
    assert len([p for p in profiles if p.selected]) == 1
    for summary in profiles:
        profile = await machine.profiles.get(summary.id)
        assert isinstance(profile, Profile)
        assert profile.id == summary.id
        assert profile.name == summary.name
        assert profile.phases


async def test_profiles_get_missing(machine: GaggiuinoClient) -> None:
    with pytest.raises(GaggiuinoNotFoundError):
        await machine.profiles.get(MISSING_ID)


async def test_profiles_select_missing(machine: GaggiuinoClient) -> None:
    rows = await profile_rows(machine)
    with pytest.raises(GaggiuinoResponseError):
        await machine.profiles.select(MISSING_ID)
    assert await profile_rows(machine) == rows


async def test_shots_latest_and_get(machine: GaggiuinoClient) -> None:
    latest_id = await machine.shots.latest_id()
    assert latest_id > 0
    shot = await machine.shots.get(latest_id)
    assert isinstance(shot, Shot)
    assert shot.id == latest_id
    assert shot.datapoints.time_in_shot


async def test_shots_get_missing(machine: GaggiuinoClient) -> None:
    with pytest.raises(GaggiuinoNotFoundError):
        await machine.shots.get(MISSING_ID)


async def test_profiles_select(machine: GaggiuinoClient) -> None:
    selected, other = await selected_and_other(machine)
    try:
        await machine.profiles.select(other)
        assert await wait_until(lambda: is_selected(machine, other.id))
    finally:
        await machine.profiles.select(selected.id)
        assert await wait_until(lambda: is_selected(machine, selected.id))


async def test_profiles_create_and_delete(machine: GaggiuinoClient) -> None:
    rows_before = await profile_rows(machine)
    ids_before = {row[0] for row in rows_before}
    assert TEST_PROFILE_NAME not in {row[1] for row in rows_before}, (
        f'A profile {TEST_PROFILE_NAME!r} is left from an earlier run: remove it by hand'
    )
    # A copy of each saved profile, so that a lost profile can be created again by hand.
    backup = {
        pid: await machine._transport.get_json(f'profile/{pid}') for pid in ids_before
    }
    selected, source_summary = await selected_and_other(machine)
    source = await machine.profiles.get(source_summary.id)
    created_id: int | None = None
    try:
        created = await machine.profiles.create(
            dataclasses.replace(source, id=None, name=TEST_PROFILE_NAME)
        )
        created_id = created.id
        assert created.name == TEST_PROFILE_NAME
        assert created_id not in ids_before
        rows = await profile_rows(machine)
        assert (created_id, TEST_PROFILE_NAME, False) in rows
        copy = await machine.profiles.get(created_id)
        assert copy.phases == source.phases
        assert await is_selected(machine, selected.id)
    finally:
        # Delete only an id that this test created and that the list still holds: never
        # an id from before the test, and never an id that the machine does not have.
        leftovers = {
            p.id
            for p in await machine.profiles.list()
            if p.name == TEST_PROFILE_NAME and p.id not in ids_before
        }
        for pid in sorted(leftovers):
            await machine.profiles.delete(pid)
        rows_after = await profile_rows(machine)
        lost = {pid: backup[pid] for pid in ids_before - {row[0] for row in rows_after}}
        assert not lost, f'Saved profiles were lost: {json.dumps(lost)}'
        if not await is_selected(machine, selected.id):
            await machine.profiles.select(selected.id)
            pytest.fail(
                f'The selected profile changed and was restored to {selected.id}'
            )
        assert rows_after == rows_before


async def test_settings_update_changes(machine: GaggiuinoClient) -> None:
    # The raw group holds keys that the model does not know: they must survive the write.
    original = await machine._transport.get_json('settings/display')
    brightness = original['lcdBrightness']
    new_brightness = brightness - 1 if brightness > 0 else brightness + 1
    expected = {**original, 'lcdBrightness': new_brightness}
    try:
        await machine.settings.display.update(lcd_brightness=new_brightness)
        assert await wait_until(lambda: settings_equal(machine, 'display', expected))
        assert (await machine.settings.display.get()).lcd_brightness == new_brightness
    finally:
        await machine._transport.command('POST', 'settings/display', body=original)
        assert await wait_until(lambda: settings_equal(machine, 'display', original))


async def test_settings_update_from_model(machine: GaggiuinoClient) -> None:
    original = await machine._transport.get_json('settings/led')
    led = await machine.settings.led.get()
    red = led.color.r - 1 if led.color.r > 0 else led.color.r + 1
    changed = dataclasses.replace(led, color=dataclasses.replace(led.color, r=red))
    expected = {**original, 'color': {**original['color'], 'R': red}}
    try:
        await machine.settings.led.update_from(changed)
        assert await wait_until(lambda: settings_equal(machine, 'led', expected))
    finally:
        await machine._transport.command('POST', 'settings/led', body=original)
        assert await wait_until(lambda: settings_equal(machine, 'led', original))


async def test_settings_concurrent_updates_both_arrive(
    machine: GaggiuinoClient,
) -> None:
    # A smoke check only: it also passes without the lock; the unit test proves the lock.
    original = await machine._transport.get_json('settings/display')
    brightness = original['lcdBrightness']
    new_brightness = brightness - 1 if brightness > 0 else brightness + 1
    new_dark_mode = not original['lcdDarkMode']
    expected = {
        **original,
        'lcdBrightness': new_brightness,
        'lcdDarkMode': new_dark_mode,
    }
    try:
        # Wait for both updates to end, so the restore below runs after both posts.
        results = await asyncio.gather(
            machine.settings.display.update(lcd_brightness=new_brightness),
            machine.settings.display.update(lcd_dark_mode=new_dark_mode),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, BaseException):
                raise result
        assert await wait_until(lambda: settings_equal(machine, 'display', expected))
    finally:
        await machine._transport.command('POST', 'settings/display', body=original)
        assert await wait_until(lambda: settings_equal(machine, 'display', original))

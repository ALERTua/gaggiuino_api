"""Tests of the settings resource on the HTTP level."""

import asyncio
import dataclasses
from collections.abc import AsyncIterator
from typing import Any, assert_type

import pytest
import pytest_asyncio

from conftest import FakeMachine
from fixture_loader import load_fixture
from gaggiuino_api import GaggiuinoCommandError, GaggiuinoResponseFormatError
from gaggiuino_api._transport import Transport
from gaggiuino_api.enums import ReleaseChannel
from gaggiuino_api.models.base import Model
from gaggiuino_api.models.settings import (
    BoilerSettings,
    DisplaySettings,
    LedColor,
    LedSettings,
    ScalesSettings,
    Settings,
    SystemSettings,
    ThemeSettings,
    TofSettings,
    Versions,
)
from gaggiuino_api.resources import SettingsResource

GROUPS: dict[str, type[Model]] = {
    'boiler': BoilerSettings,
    'system': SystemSettings,
    'led': LedSettings,
    'scales': ScalesSettings,
    'display': DisplaySettings,
    'theme': ThemeSettings,
}


@pytest_asyncio.fixture(loop_scope='function')
async def settings(machine: FakeMachine) -> AsyncIterator[SettingsResource]:
    transport = Transport(machine.base_url, timeout=5)
    yield SettingsResource(transport)
    await transport.close()


def _serve(machine: FakeMachine, group: str, raw: Any) -> None:
    machine.answer('GET', f'settings/{group}', raw)
    machine.answer('POST', f'settings/{group}', {'success': True})


def _posted(machine: FakeMachine, group: str) -> Any:
    get, post = machine.requests
    path = f'/api/settings/{group}'
    assert (get.method, get.path) == ('GET', path)
    assert (post.method, post.path) == ('POST', path)
    return post.json


async def test_get_all(machine: FakeMachine, settings: SettingsResource) -> None:
    machine.answer('GET', 'settings', load_fixture('settings'))
    assert await settings.get() == Settings.from_api(load_fixture('settings'))
    (request,) = machine.requests
    assert request.path == '/api/settings'


async def test_versions(machine: FakeMachine, settings: SettingsResource) -> None:
    machine.answer('GET', 'settings/versions', load_fixture('settings_versions'))
    versions = await settings.versions()
    assert versions == Versions.from_api(load_fixture('settings_versions'))
    (request,) = machine.requests
    assert request.path == '/api/settings/versions'


@pytest.mark.parametrize('group', GROUPS)
async def test_group_get(
    machine: FakeMachine, settings: SettingsResource, group: str
) -> None:
    raw = load_fixture(f'settings_{group}')
    machine.answer('GET', f'settings/{group}', raw)
    assert await getattr(settings, group).get() == GROUPS[group].from_api(raw)
    (request,) = machine.requests
    assert (request.method, request.path) == ('GET', f'/api/settings/{group}')


async def test_group_get_type(machine: FakeMachine, settings: SettingsResource) -> None:
    machine.answer('GET', 'settings/boiler', load_fixture('settings_boiler'))
    assert_type(await settings.boiler.get(), BoilerSettings)


async def test_update_changes_one_key(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    raw = load_fixture('settings_boiler')
    _serve(machine, 'boiler', raw)
    assert await settings.boiler.update(steam_set_point=130) is None
    body = _posted(machine, 'boiler')
    assert body == raw | {'steamSetPoint': 130}
    assert body['dualBoilerStagger'] == raw['dualBoilerStagger']


async def test_update_keeps_a_key_of_a_newer_firmware(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    raw = load_fixture('settings_boiler') | {'futureKey': {'a': 1}}
    _serve(machine, 'boiler', raw)
    await settings.boiler.update(offset_temp=8)
    assert _posted(machine, 'boiler') == raw | {'offsetTemp': 8}


async def test_update_keeps_the_form_of_an_unchanged_key(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    raw = load_fixture('settings_boiler') | {'brewDeltaState': 'true'}
    _serve(machine, 'boiler', raw)
    await settings.boiler.update(steam_set_point=130)
    assert _posted(machine, 'boiler')['brewDeltaState'] == 'true'


@pytest.mark.parametrize(
    ('name', 'value', 'key', 'sent'),
    [
        ('steam_set_point', '131', 'steamSetPoint', 131),
        ('brew_delta_state', 'false', 'brewDeltaState', False),
    ],
)
async def test_update_sends_a_changed_key_in_normal_form(
    machine: FakeMachine,
    settings: SettingsResource,
    name: str,
    value: str,
    key: str,
    sent: object,
) -> None:
    _serve(machine, 'boiler', load_fixture('settings_boiler'))
    await settings.boiler.update(**{name: value})
    posted = _posted(machine, 'boiler')[key]
    assert (posted, type(posted)) == (sent, type(sent))


async def test_update_enum(machine: FakeMachine, settings: SettingsResource) -> None:
    raw = load_fixture('settings_system')
    _serve(machine, 'system', raw)
    await settings.system.update(release_channel=ReleaseChannel.TEST)
    assert _posted(machine, 'system') == raw | {'releaseChannel': 1}


@pytest.mark.parametrize('extra', [{}, {'W': 7}], ids=['plain', 'unknown-key'])
async def test_update_nested_model(
    machine: FakeMachine, settings: SettingsResource, extra: dict[str, int]
) -> None:
    raw = load_fixture('settings_led')
    raw['color'] |= extra
    _serve(machine, 'led', raw)
    await settings.led.update(color=LedColor(r=1, g=2, b=3))
    assert _posted(machine, 'led') == raw | {'color': {'R': 1, 'G': 2, 'B': 3} | extra}


@pytest.mark.parametrize(
    ('changes', 'error', 'match'),
    [
        ({'steam_point': 1}, TypeError, "boiler settings have no field 'steam_point'"),
        ({}, TypeError, 'boiler'),
        ({'steam_set_point': LedColor(r=1, g=2, b=3)}, TypeError, 'LedColor'),
        ({'steam_set_point': None}, ValueError, 'None'),
    ],
    ids=['unknown-name', 'no-change', 'nested-model', 'none'],
)
async def test_update_refuses_before_any_request(
    machine: FakeMachine,
    settings: SettingsResource,
    changes: dict[str, Any],
    error: type[Exception],
    match: str,
) -> None:
    with pytest.raises(error, match=match):
        await settings.boiler.update(**changes)
    assert machine.requests == []


@pytest.mark.parametrize(
    ('changes', 'match'),
    [
        ({'color': {'r': 255}}, 'LedColor.*dict'),
        ({'color': {'R': 255, 'G': 0, 'B': 0}}, 'LedColor.*dict'),
        ({'tof': {'max': 1, 'min': 2}}, 'TofSettings.*dict'),
        ({'color': TofSettings(max=1, min=2)}, 'LedColor.*TofSettings'),
        ({'color': 'red'}, 'LedColor.*str'),
    ],
    ids=['dict', 'dict-with-firmware-keys', 'tof-dict', 'other-model', 'str'],
)
async def test_update_of_a_nested_field_needs_its_model(
    machine: FakeMachine,
    settings: SettingsResource,
    changes: dict[str, Any],
    match: str,
) -> None:
    with pytest.raises(TypeError, match=match):
        await settings.led.update(**changes)
    assert machine.requests == []


async def test_update_bad_value_sends_no_post(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    _serve(machine, 'boiler', load_fixture('settings_boiler'))
    with pytest.raises(ValueError, match='steam_set_point') as exc_info:
        await settings.boiler.update(steam_set_point='hot')
    assert isinstance(exc_info.value.__cause__, GaggiuinoResponseFormatError)
    (request,) = machine.requests
    assert request.method == 'GET'


async def test_update_refused_by_the_machine(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    machine.answer('GET', 'settings/boiler', load_fixture('settings_boiler'))
    machine.answer(
        'POST', 'settings/boiler', {'success': False, 'error': 'Invalid value'}
    )
    with pytest.raises(GaggiuinoCommandError, match='Invalid value'):
        await settings.boiler.update(steam_set_point=130)


async def test_update_of_a_group_that_is_not_an_object(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    _serve(machine, 'boiler', [])
    with pytest.raises(GaggiuinoResponseFormatError):
        await settings.boiler.update(steam_set_point=130)
    (request,) = machine.requests
    assert request.method == 'GET'


async def test_update_of_a_group_that_the_model_cannot_read(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    raw = load_fixture('settings_boiler') | {'hpwr': 'much'}
    _serve(machine, 'boiler', raw)
    with pytest.raises(GaggiuinoResponseFormatError):
        await settings.boiler.update(steam_set_point=130)
    (request,) = machine.requests
    assert request.method == 'GET'


async def test_update_from(machine: FakeMachine, settings: SettingsResource) -> None:
    raw = load_fixture('settings_display')
    machine.answer('GET', 'settings/display', raw)
    current = await settings.display.get()
    machine.requests.clear()
    machine.answer('POST', 'settings/display', {'success': True})
    await settings.display.update_from(dataclasses.replace(current, lcd_brightness=50))
    body = _posted(machine, 'display')
    assert body == raw | {'lcdBrightness': 50}
    assert {'homeLayout', 'homeTileLeftTop', 'homeTileRightTopGroup'} <= body.keys()


async def test_update_from_another_model(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    theme = ThemeSettings(colour_primary=1, colour_secondary=2)
    with pytest.raises(TypeError, match='DisplaySettings'):
        await settings.display.update_from(theme)  # ty: ignore[invalid-argument-type]
    assert machine.requests == []


async def test_concurrent_updates_of_one_group_run_one_after_the_other(
    machine: FakeMachine, settings: SettingsResource
) -> None:
    raw = load_fixture('settings_led')
    assert raw['disco'] is True
    assert raw['state'] is False
    # The machine answers the second read with the state after the first post.
    machine.answer('GET', 'settings/led', raw, delay=0.05)
    machine.answer('GET', 'settings/led', raw | {'disco': False}, delay=0.05)
    machine.answer('POST', 'settings/led', {'success': True})
    await asyncio.gather(
        settings.led.update(disco=False), settings.led.update(state=True)
    )
    assert [request.method for request in machine.requests] == [
        'GET',
        'POST',
        'GET',
        'POST',
    ]
    assert machine.requests[-1].json == raw | {'disco': False, 'state': True}

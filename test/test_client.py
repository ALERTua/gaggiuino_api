"""Tests of the client: its session lifecycle, its direct methods and its resources."""

import os
import socket
import subprocess
import sys
from collections.abc import AsyncIterator
from pathlib import Path

import aiohttp
import pytest
import pytest_asyncio

import gaggiuino_api
from conftest import FakeMachine
from fixture_loader import load_fixture
from gaggiuino_api import (
    FirmwareProgress,
    GaggiuinoClient,
    GaggiuinoConnectionError,
    GaggiuinoResponseFormatError,
    Maintenance,
    OperationMode,
    ProfileSummary,
)
from gaggiuino_api.resources import Firmware, Profiles, Shots


@pytest_asyncio.fixture(loop_scope='function')
async def client(machine: FakeMachine) -> AsyncIterator[GaggiuinoClient]:
    async with GaggiuinoClient(machine.base_url, timeout=5) as c:
        yield c


async def test_async_with_closes_own_session(machine: FakeMachine) -> None:
    machine.answer('GET', 'health', {'ok': True})
    async with GaggiuinoClient(f'{machine.base_url}/', timeout=1) as client:
        assert isinstance(client, GaggiuinoClient)
        session = client._transport._session
        assert session is not None
        assert not session.closed
        assert await client._transport.get_json('health') == {'ok': True}
    assert session.closed
    assert [r.path for r in machine.requests] == ['/api/health']


async def test_caller_session_stays_open_after_close(machine: FakeMachine) -> None:
    machine.answer('GET', 'health', {})
    async with aiohttp.ClientSession() as session:
        client = GaggiuinoClient(machine.base_url, session=session)
        await client.connect()
        await client._transport.get_json('health')
        await client.close()
        assert not session.closed
        assert client._transport._session is session
    assert len(machine.requests) == 1


async def test_status(machine: FakeMachine, client: GaggiuinoClient) -> None:
    machine.answer('GET', 'system/status', load_fixture('status'))
    status = await client.status()
    assert status.profile_name == '_OFF'
    assert status.profile_id == 9
    assert status.operation_mode is OperationMode.HOME
    (request,) = machine.requests
    assert (request.method, request.path) == ('GET', '/api/system/status')


@pytest.mark.parametrize(
    'answer', [[], load_fixture('status')[0]], ids=['empty-list', 'object']
)
async def test_status_bad_shape(
    machine: FakeMachine, client: GaggiuinoClient, answer: object
) -> None:
    machine.answer('GET', 'system/status', answer)
    with pytest.raises(GaggiuinoResponseFormatError):
        await client.status()


async def test_status_of_a_list_with_two_objects_takes_the_first(
    machine: FakeMachine, client: GaggiuinoClient
) -> None:
    first = load_fixture('status')[0]
    second = first | {'profileId': '3', 'profileName': 'Other'}
    machine.answer('GET', 'system/status', [first, second])
    status = await client.status()
    assert (status.profile_id, status.profile_name) == (9, '_OFF')


async def test_maintenance(machine: FakeMachine, client: GaggiuinoClient) -> None:
    machine.answer('GET', 'maintenance', load_fixture('maintenance'))
    assert await client.maintenance() == Maintenance(
        last_descale_timestamp=0,
        shots_since_descale=11,
        last_backflush_timestamp=0,
        shots_since_backflush=11,
    )
    assert machine.requests[0].path == '/api/maintenance'


@pytest.mark.parametrize(('state', 'expected'), [('ok', True), ('down', False)])
async def test_healthy(
    machine: FakeMachine, client: GaggiuinoClient, state: str, expected: bool
) -> None:
    machine.answer('GET', 'health', {'status': state})
    assert await client.healthy() is expected
    assert machine.requests[0].path == '/api/health'


async def test_healthy_raises_when_nothing_listens() -> None:
    # Windows retries a refused connection for about 2 seconds, so the timeout is longer.
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    async with GaggiuinoClient(f'http://127.0.0.1:{port}', timeout=15) as client:
        with pytest.raises(GaggiuinoConnectionError):
            await client.healthy()


async def test_resources_work_through_client(
    machine: FakeMachine, client: GaggiuinoClient
) -> None:
    assert isinstance(client.profiles, Profiles)
    assert isinstance(client.shots, Shots)
    assert isinstance(client.firmware, Firmware)
    machine.answer('GET', 'profiles/all', load_fixture('profiles_all'))
    machine.answer('GET', 'shots/latest', load_fixture('shots_latest'))
    machine.answer('GET', 'firmware/progress', load_fixture('firmware_progress'))
    assert (await client.profiles.list())[1] == ProfileSummary(
        id=9, name='_OFF', selected=True
    )
    assert await client.shots.latest_id() == 580
    assert isinstance(await client.firmware.progress(), FirmwareProgress)
    assert [r.path for r in machine.requests] == [
        '/api/profiles/all',
        '/api/shots/latest',
        '/api/firmware/progress',
    ]


async def test_settings_work_through_client(
    machine: FakeMachine, client: GaggiuinoClient
) -> None:
    raw = load_fixture('settings_boiler')
    machine.answer('GET', 'settings/boiler', raw)
    machine.answer('POST', 'settings/boiler', {'success': True})
    await client.settings.boiler.update(steam_set_point=130)
    assert machine.requests[1].json == raw | {'steamSetPoint': 130}


async def test_resources_use_caller_session(machine: FakeMachine) -> None:
    machine.answer('GET', 'shots/latest', load_fixture('shots_latest'))
    async with aiohttp.ClientSession() as session:
        client = GaggiuinoClient(machine.base_url, session=session)
        assert await client.shots.latest_id() == 580
        assert client.shots._transport._session is session
        await client.close()
        assert not session.closed
    assert len(machine.requests) == 1


def test_import_sets_no_event_loop_policy() -> None:
    src = str(Path(gaggiuino_api.__file__).parents[1])
    code = (
        'import asyncio.events as e, gaggiuino_api; assert e._event_loop_policy is None'
    )
    subprocess.run(
        [sys.executable, '-c', code],
        check=True,
        timeout=30,
        env={**os.environ, 'PYTHONPATH': src},
    )

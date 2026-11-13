"""Tests of the HTTP transport: URLs, JSON parsing, error mapping and the session lifecycle."""

import logging
import socket
from collections.abc import AsyncIterator

import aiohttp
import pytest
import pytest_asyncio

from conftest import FakeMachine
from gaggiuino_api import (
    GaggiuinoCommandError,
    GaggiuinoConnectionError,
    GaggiuinoConnectionTimeoutError,
    GaggiuinoNotFoundError,
    GaggiuinoResponseError,
    GaggiuinoResponseFormatError,
)
from gaggiuino_api._transport import Transport


@pytest_asyncio.fixture(loop_scope='function')
async def transport(machine: FakeMachine) -> AsyncIterator[Transport]:
    t = Transport(machine.base_url, timeout=5)
    yield t
    await t.close()


@pytest.mark.parametrize('suffix', ['', '/'])
async def test_base_url_with_and_without_trailing_slash(
    machine: FakeMachine, suffix: str
) -> None:
    machine.answer('GET', 'health', {'ok': True})
    t = Transport(machine.base_url + suffix)
    try:
        assert await t.get_json('health') == {'ok': True}
    finally:
        await t.close()
    assert t.base_url == machine.base_url
    assert [r.path for r in machine.requests] == ['/api/health']


async def test_get_sends_accept_json_and_no_body(
    machine: FakeMachine, transport: Transport
) -> None:
    machine.answer('GET', 'health', {})
    await transport.get_json('health')
    (request,) = machine.requests
    assert request.method == 'GET'
    assert request.headers['Accept'] == 'application/json'
    assert request.raw == b''


async def test_get_json_of_attachment(
    machine: FakeMachine, transport: Transport
) -> None:
    machine.answer(
        'GET',
        'profile/4',
        {'name': '18g Double'},
        headers={'Content-Disposition': 'attachment; filename="profile.json"'},
    )
    assert await transport.get_json('profile/4') == {'name': '18g Double'}


async def test_get_json_with_wrong_content_type(
    machine: FakeMachine, transport: Transport
) -> None:
    machine.answer('GET', 'shots/latest', text='[{"id": 7}]')
    assert await transport.get_json('shots/latest') == [{'id': 7}]


async def test_get_json_invalid_json(
    machine: FakeMachine, transport: Transport
) -> None:
    machine.answer(
        'GET', 'health', text='not json', headers={'Content-Type': 'application/json'}
    )
    with pytest.raises(GaggiuinoResponseFormatError) as exc_info:
        await transport.get_json('health')
    assert isinstance(exc_info.value.__cause__, ValueError)


async def test_404_of_unknown_endpoint(
    machine: FakeMachine, transport: Transport
) -> None:
    with pytest.raises(GaggiuinoNotFoundError) as exc_info:
        await transport.get_json('shots/999')
    assert (exc_info.value.status, exc_info.value.body) == (404, 'Not found')


async def test_500_with_text_body(machine: FakeMachine, transport: Transport) -> None:
    machine.answer('POST', 'profile', text='Failed to save', status=500)
    with pytest.raises(GaggiuinoResponseError) as exc_info:
        await transport.command_json('POST', 'profile', body={'name': 'x'})
    assert type(exc_info.value) is GaggiuinoResponseError
    assert (exc_info.value.status, exc_info.value.body) == (500, 'Failed to save')


async def test_422(machine: FakeMachine, transport: Transport) -> None:
    machine.answer('POST', 'profile', text='Unprocessable', status=422)
    with pytest.raises(GaggiuinoResponseError) as exc_info:
        await transport.command_json('POST', 'profile', body={})
    assert type(exc_info.value) is GaggiuinoResponseError
    assert (exc_info.value.status, exc_info.value.body) == (422, 'Unprocessable')


@pytest.mark.parametrize('status', [200, 400])
@pytest.mark.parametrize(
    ('payload', 'message'),
    [
        (
            {'success': False, 'error': 'Description of the error'},
            'Description of the error',
        ),
        (
            {'success': False, 'message': 'Failed to start update'},
            'Failed to start update',
        ),
    ],
)
async def test_success_false_raises_command_error(
    machine: FakeMachine,
    transport: Transport,
    status: int,
    payload: dict,
    message: str,
) -> None:
    machine.answer('POST', 'settings/brew', payload, status=status)
    with pytest.raises(GaggiuinoCommandError) as exc_info:
        await transport.command('POST', 'settings/brew', body={'a': 1})
    assert exc_info.value.message == message


async def test_success_false_in_required_json(
    machine: FakeMachine, transport: Transport
) -> None:
    machine.answer(
        'POST', 'firmware/update-all', {'success': False, 'message': 'Failed'}
    )
    with pytest.raises(GaggiuinoCommandError, match='Failed'):
        await transport.command_json('POST', 'firmware/update-all')


async def test_command_returns_json_object(
    machine: FakeMachine, transport: Transport
) -> None:
    machine.answer('POST', 'settings/brew', {'success': True})
    assert await transport.command('POST', 'settings/brew', body={'a': 1}) == {
        'success': True
    }


@pytest.mark.parametrize('text', ['', 'OK', '[1]'])
async def test_command_returns_none_for_empty_or_non_object_body(
    machine: FakeMachine, transport: Transport, text: str
) -> None:
    machine.answer('DELETE', 'shots/7', text=text)
    assert await transport.command('DELETE', 'shots/7') is None
    (request,) = machine.requests
    assert request.method == 'DELETE'


async def test_command_json_requires_json(
    machine: FakeMachine, transport: Transport
) -> None:
    machine.answer('POST', 'profile', text='')
    with pytest.raises(GaggiuinoResponseFormatError):
        await transport.command_json('POST', 'profile', body={'name': 'x'})


async def test_post_sends_json_body(machine: FakeMachine, transport: Transport) -> None:
    machine.answer('POST', 'profile', {'id': 4, 'name': '18g Double'})
    assert await transport.command_json(
        'POST', 'profile', body={'name': '18g Double'}
    ) == {'id': 4, 'name': '18g Double'}
    (request,) = machine.requests
    assert (request.method, request.path) == ('POST', '/api/profile')
    assert request.json == {'name': '18g Double'}
    assert request.headers['Content-Type'] == 'application/json'
    assert request.headers['Accept'] == 'application/json'


async def test_post_without_body_declares_json(
    machine: FakeMachine, transport: Transport
) -> None:
    machine.answer('POST', 'profile-select/4', text='')
    await transport.command('POST', 'profile-select/4')
    (request,) = machine.requests
    assert request.raw == b''
    assert request.headers['Content-Type'] == 'application/json'
    assert request.headers['Accept'] == 'application/json'


@pytest.mark.parametrize(
    ('timeout', 'cause'),
    [
        # aiohttp raises a plain TimeoutError for the total time
        (0.2, TimeoutError),
        # and a TimeoutError that is also a ClientError for a read of the socket
        (aiohttp.ClientTimeout(sock_read=0.2), aiohttp.ServerTimeoutError),
    ],
)
async def test_timeout(
    machine: FakeMachine,
    timeout: float | aiohttp.ClientTimeout,
    cause: type[Exception],
) -> None:
    machine.answer('GET', 'health', {}, delay=5)
    t = Transport(machine.base_url, timeout=timeout)
    try:
        with pytest.raises(GaggiuinoConnectionTimeoutError) as exc_info:
            await t.get_json('health')
    finally:
        await t.close()
    assert isinstance(exc_info.value.__cause__, cause)


async def test_refused_connection() -> None:
    # Nothing listens on a port that was free a moment ago. Windows retries a refused
    # connection for about 2 seconds, so the timeout is much longer than that.
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    t = Transport(f'http://127.0.0.1:{port}', timeout=15)
    try:
        with pytest.raises(GaggiuinoConnectionError) as exc_info:
            await t.get_json('health')
    finally:
        await t.close()
    assert isinstance(exc_info.value.__cause__, aiohttp.ClientConnectorError)


async def test_debug_log_has_no_body(
    machine: FakeMachine, transport: Transport, caplog: pytest.LogCaptureFixture
) -> None:
    machine.answer('POST', 'settings/system', {'success': True})
    with caplog.at_level(logging.DEBUG, logger='gaggiuino_api'):
        await transport.command('POST', 'settings/system', body={'password': 'hunter2'})
    assert 'POST settings/system -> 200' in caplog.text
    assert 'hunter2' not in caplog.text
    assert 'success' not in caplog.text
    (request,) = machine.requests
    assert request.json == {'password': 'hunter2'}


async def test_request_opens_own_session(machine: FakeMachine) -> None:
    machine.answer('GET', 'health', {})
    t = Transport(machine.base_url)
    await t.get_json('health')
    session = t._session
    assert session is not None
    await t.close()
    assert session.closed


async def test_caller_session_stays_open(machine: FakeMachine) -> None:
    machine.answer('GET', 'health', {})
    async with aiohttp.ClientSession() as session:
        t = Transport(machine.base_url, session=session)
        await t.open()
        await t.get_json('health')
        await t.close()
        assert not session.closed
        assert t._session is session
    assert len(machine.requests) == 1

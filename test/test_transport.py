"""Tests of the HTTP transport: URLs, JSON parsing, error mapping and the session lifecycle."""

import logging
from collections.abc import AsyncIterator

import aiohttp
import pytest
from aioresponses import aioresponses
from yarl import URL

from gaggiuino_api import (
    GaggiuinoCommandError,
    GaggiuinoConnectionError,
    GaggiuinoConnectionTimeoutError,
    GaggiuinoNotFoundError,
    GaggiuinoResponseError,
    GaggiuinoResponseFormatError,
)
from gaggiuino_api._transport import Transport

BASE = 'http://gaggiuino.test'


@pytest.fixture
async def transport() -> AsyncIterator[Transport]:
    t = Transport(BASE)
    yield t
    await t.close()


@pytest.mark.parametrize('base_url', [BASE, f'{BASE}/'])
async def test_base_url_with_and_without_trailing_slash(
    mocked: aioresponses, base_url: str
) -> None:
    mocked.get(f'{BASE}/api/health', payload={'ok': True})
    t = Transport(base_url)
    try:
        assert await t.get_json('health') == {'ok': True}
    finally:
        await t.close()


async def test_get_json_of_attachment(
    mocked: aioresponses, transport: Transport
) -> None:
    mocked.get(
        f'{BASE}/api/profile/4',
        payload={'name': '18g Double'},
        headers={'Content-Disposition': 'attachment; filename="profile.json"'},
    )
    assert await transport.get_json('profile/4') == {'name': '18g Double'}


async def test_get_json_with_wrong_content_type(
    mocked: aioresponses, transport: Transport
) -> None:
    mocked.get(
        f'{BASE}/api/shots/latest', body='[{"id": 7}]', content_type='text/plain'
    )
    assert await transport.get_json('shots/latest') == [{'id': 7}]


async def test_get_json_invalid_json(
    mocked: aioresponses, transport: Transport
) -> None:
    mocked.get(f'{BASE}/api/health', body='not json', content_type='application/json')
    with pytest.raises(GaggiuinoResponseFormatError) as exc_info:
        await transport.get_json('health')
    assert isinstance(exc_info.value.__cause__, ValueError)


async def test_404_with_text_body(mocked: aioresponses, transport: Transport) -> None:
    mocked.get(
        f'{BASE}/api/shots/999', status=404, body='Not Found', content_type='text/plain'
    )
    with pytest.raises(GaggiuinoNotFoundError) as exc_info:
        await transport.get_json('shots/999')
    assert (exc_info.value.status, exc_info.value.body) == (404, 'Not Found')


async def test_500_with_text_body(mocked: aioresponses, transport: Transport) -> None:
    mocked.post(
        f'{BASE}/api/profile',
        status=500,
        body='Failed to save',
        content_type='text/plain',
    )
    with pytest.raises(GaggiuinoResponseError) as exc_info:
        await transport.command_json('POST', 'profile', body={'name': 'x'})
    assert type(exc_info.value) is GaggiuinoResponseError
    assert (exc_info.value.status, exc_info.value.body) == (500, 'Failed to save')


async def test_422(mocked: aioresponses, transport: Transport) -> None:
    mocked.post(
        f'{BASE}/api/profile',
        status=422,
        body='Unprocessable',
        content_type='text/plain',
    )
    with pytest.raises(GaggiuinoResponseError) as exc_info:
        await transport.command_json('POST', 'profile', body={})
    assert exc_info.value.status == 422


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
    mocked: aioresponses, transport: Transport, status: int, payload: dict, message: str
) -> None:
    mocked.post(f'{BASE}/api/settings/brew', status=status, payload=payload)
    with pytest.raises(GaggiuinoCommandError) as exc_info:
        await transport.command('POST', 'settings/brew', body={'a': 1})
    assert exc_info.value.message == message


async def test_success_false_in_required_json(
    mocked: aioresponses, transport: Transport
) -> None:
    mocked.post(
        f'{BASE}/api/firmware/update-all',
        payload={'success': False, 'message': 'Failed'},
    )
    with pytest.raises(GaggiuinoCommandError, match='Failed'):
        await transport.command_json('POST', 'firmware/update-all')


async def test_command_returns_json_object(
    mocked: aioresponses, transport: Transport
) -> None:
    mocked.post(f'{BASE}/api/settings/brew', payload={'success': True})
    assert await transport.command('POST', 'settings/brew', body={'a': 1}) == {
        'success': True
    }


@pytest.mark.parametrize('body', ['', 'OK', '[1]'])
async def test_command_returns_none_for_empty_or_non_object_body(
    mocked: aioresponses, transport: Transport, body: str
) -> None:
    mocked.delete(f'{BASE}/api/shots/7', body=body, content_type='text/plain')
    assert await transport.command('DELETE', 'shots/7') is None


async def test_command_json_requires_json(
    mocked: aioresponses, transport: Transport
) -> None:
    mocked.post(f'{BASE}/api/profile', body='', content_type='text/plain')
    with pytest.raises(GaggiuinoResponseFormatError):
        await transport.command_json('POST', 'profile', body={'name': 'x'})


async def test_post_sends_json_body(mocked: aioresponses, transport: Transport) -> None:
    url = f'{BASE}/api/profile'
    mocked.post(url, payload={'id': 4, 'name': '18g Double'})
    assert await transport.command_json(
        'POST', 'profile', body={'name': '18g Double'}
    ) == {
        'id': 4,
        'name': '18g Double',
    }
    (call,) = mocked.requests[('POST', URL(url))]
    assert call.kwargs['json'] == {'name': '18g Double'}
    assert call.kwargs.get('data') is None
    assert call.kwargs['headers']['Content-Type'] == 'application/json'


async def test_post_without_body_declares_json(
    mocked: aioresponses, transport: Transport
) -> None:
    url = f'{BASE}/api/profile-select/4'
    mocked.post(url, body='')
    await transport.command('POST', 'profile-select/4')
    (call,) = mocked.requests[('POST', URL(url))]
    assert call.kwargs['json'] is None
    assert call.kwargs.get('data') is None
    assert call.kwargs['headers']['Content-Type'] == 'application/json'


@pytest.mark.parametrize('exception', [TimeoutError(), aiohttp.ServerTimeoutError()])
async def test_timeout(
    mocked: aioresponses, transport: Transport, exception: Exception
) -> None:
    mocked.get(f'{BASE}/api/health', exception=exception)
    with pytest.raises(GaggiuinoConnectionTimeoutError) as exc_info:
        await transport.get_json('health')
    assert exc_info.value.__cause__ is exception


async def test_refused_connection(mocked: aioresponses, transport: Transport) -> None:
    err = aiohttp.ClientConnectionError('Connection refused')
    mocked.get(f'{BASE}/api/health', exception=err)
    with pytest.raises(GaggiuinoConnectionError) as exc_info:
        await transport.get_json('health')
    assert exc_info.value.__cause__ is err


async def test_debug_log_has_no_body(
    mocked: aioresponses, transport: Transport, caplog: pytest.LogCaptureFixture
) -> None:
    mocked.post(f'{BASE}/api/settings/system', payload={'success': True})
    with caplog.at_level(logging.DEBUG, logger='gaggiuino_api'):
        await transport.command('POST', 'settings/system', body={'password': 'hunter2'})
    assert 'POST settings/system -> 200' in caplog.text
    assert 'hunter2' not in caplog.text
    assert 'success' not in caplog.text


async def test_request_opens_own_session(mocked: aioresponses) -> None:
    mocked.get(f'{BASE}/api/health', payload={})
    t = Transport(BASE)
    await t.get_json('health')
    session = t._session
    assert session is not None
    await t.close()
    assert session.closed


async def test_caller_session_stays_open(mocked: aioresponses) -> None:
    mocked.get(f'{BASE}/api/health', payload={})
    async with aiohttp.ClientSession() as session:
        t = Transport(BASE, session=session)
        await t.open()
        await t.get_json('health')
        await t.close()
        assert not session.closed

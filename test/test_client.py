"""Tests of the client shell: its session lifecycle and the import of the package."""

import os
import subprocess
import sys
from pathlib import Path

import aiohttp

import gaggiuino_api
from conftest import FakeMachine
from gaggiuino_api import GaggiuinoClient


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

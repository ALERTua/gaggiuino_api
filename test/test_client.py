"""Tests of the client shell: its session lifecycle and the import of the package."""

import os
import subprocess
import sys
from pathlib import Path

import aiohttp

import gaggiuino_api
from gaggiuino_api import GaggiuinoClient


async def test_async_with_closes_own_session() -> None:
    async with GaggiuinoClient('http://gaggiuino.test/', timeout=1) as client:
        assert isinstance(client, GaggiuinoClient)
        session = client._transport._session
        assert session is not None
        assert not session.closed
    assert session.closed


async def test_caller_session_stays_open_after_close() -> None:
    async with aiohttp.ClientSession() as session:
        client = GaggiuinoClient(session=session)
        await client.connect()
        await client.close()
        assert not session.closed


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

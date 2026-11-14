"""Shared fixtures of the end-to-end tests against a real machine.

The machine answers at `GAGGIUINO_BASE_URL`, by default at `DEFAULT_BASE_URL`.
"""

import os
from collections.abc import AsyncIterator

import pytest_asyncio

from e2e.e2e_support import machine_state
from gaggiuino_api import GaggiuinoClient
from gaggiuino_api.const import DEFAULT_BASE_URL


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def machine() -> AsyncIterator[GaggiuinoClient]:
    """A client of the real machine, shared by the whole session."""
    base_url = os.getenv('GAGGIUINO_BASE_URL', DEFAULT_BASE_URL)
    async with GaggiuinoClient(base_url) as client:
        yield client


@pytest_asyncio.fixture(scope='session', loop_scope='session', autouse=True)
async def machine_unchanged(machine: GaggiuinoClient) -> AsyncIterator[None]:
    """Make sure that the session leaves the profiles and the written settings as it found them."""
    before = await machine_state(machine)
    yield
    assert await machine_state(machine) == before

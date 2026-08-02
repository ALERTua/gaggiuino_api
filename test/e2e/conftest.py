"""Shared fixtures for end-to-end tests against real hardware."""

import os

import pytest_asyncio

from gaggiuino_api import GaggiuinoAPI
from gaggiuino_api.const import DEFAULT_BASE_URL


@pytest_asyncio.fixture(loop_scope="session", name="real_api_client")
async def _real_api_client():
    """Real API client for end-to-end tests.

    Connects to the device at GAGGIUINO_BASE_URL (defaults to DEFAULT_BASE_URL).
    """
    base_url = os.getenv("GAGGIUINO_BASE_URL", DEFAULT_BASE_URL)
    async with GaggiuinoAPI(base_url=base_url) as client:
        yield client

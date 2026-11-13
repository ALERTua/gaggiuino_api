"""Tests of the firmware resource on the HTTP level."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from conftest import FakeMachine
from fixture_loader import load_fixture
from gaggiuino_api import GaggiuinoCommandError
from gaggiuino_api._transport import Transport
from gaggiuino_api.models.firmware import FirmwareProgress
from gaggiuino_api.resources import Firmware


@pytest_asyncio.fixture(loop_scope='function')
async def firmware(machine: FakeMachine) -> AsyncIterator[Firmware]:
    transport = Transport(machine.base_url, timeout=5)
    yield Firmware(transport)
    await transport.close()


async def test_update(machine: FakeMachine, firmware: Firmware) -> None:
    machine.answer(
        'POST', 'firmware/update-all', {'message': 'Update started', 'success': True}
    )
    assert await firmware.update() is None
    (request,) = machine.requests
    assert (request.method, request.path) == ('POST', '/api/firmware/update-all')
    assert request.raw == b''


async def test_update_refused(machine: FakeMachine, firmware: Firmware) -> None:
    machine.answer(
        'POST',
        'firmware/update-all',
        {'message': 'Failed to start update', 'success': False},
    )
    with pytest.raises(GaggiuinoCommandError) as exc_info:
        await firmware.update()
    assert str(exc_info.value) == 'Failed to start update'


async def test_progress(machine: FakeMachine, firmware: Firmware) -> None:
    fixture = load_fixture('firmware_progress')
    machine.answer('GET', 'firmware/progress', fixture)
    assert await firmware.progress() == FirmwareProgress.from_api(fixture)
    (request,) = machine.requests
    assert (request.method, request.path) == ('GET', '/api/firmware/progress')

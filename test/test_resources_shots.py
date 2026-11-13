"""Tests of the shots resource on the HTTP level."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from conftest import FakeMachine
from fixture_loader import load_fixture
from gaggiuino_api import GaggiuinoNotFoundError, GaggiuinoResponseFormatError
from gaggiuino_api._transport import Transport
from gaggiuino_api.models.shots import Shot
from gaggiuino_api.resources import Shots


@pytest_asyncio.fixture(loop_scope='function')
async def shots(machine: FakeMachine) -> AsyncIterator[Shots]:
    transport = Transport(machine.base_url, timeout=5)
    yield Shots(transport)
    await transport.close()


async def test_latest_id(machine: FakeMachine, shots: Shots) -> None:
    machine.answer('GET', 'shots/latest', load_fixture('shots_latest'))
    assert await shots.latest_id() == 580
    (request,) = machine.requests
    assert (request.method, request.path) == ('GET', '/api/shots/latest')


async def test_latest_id_of_empty_list(machine: FakeMachine, shots: Shots) -> None:
    machine.answer('GET', 'shots/latest', [])
    with pytest.raises(GaggiuinoResponseFormatError):
        await shots.latest_id()


async def test_get(machine: FakeMachine, shots: Shots) -> None:
    fixture = load_fixture('shot')
    machine.answer('GET', 'shots/580', fixture)
    assert await shots.get(580) == Shot.from_api(fixture)
    (request,) = machine.requests
    assert (request.method, request.path) == ('GET', '/api/shots/580')


async def test_get_missing(machine: FakeMachine, shots: Shots) -> None:
    machine.answer('GET', 'shots/999', text='Not Found', status=404)
    with pytest.raises(GaggiuinoNotFoundError):
        await shots.get(999)


@pytest.mark.parametrize('text', ['', 'OK'])
@pytest.mark.parametrize('as_model', [False, True], ids=['int', 'shot'])
async def test_delete(
    machine: FakeMachine, shots: Shots, text: str, as_model: bool
) -> None:
    machine.answer('DELETE', 'shots/580', text=text)
    shot = Shot.from_api(load_fixture('shot')) if as_model else 580
    assert await shots.delete(shot) is None
    (request,) = machine.requests
    assert (request.method, request.path) == ('DELETE', '/api/shots/580')

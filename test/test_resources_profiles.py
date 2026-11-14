"""Tests of the profiles resource on the HTTP level."""

import dataclasses
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from conftest import FakeMachine
from fixture_loader import load_fixture
from gaggiuino_api import (
    GaggiuinoNotFoundError,
    GaggiuinoResponseError,
    GaggiuinoResponseFormatError,
)
from gaggiuino_api._transport import Transport
from gaggiuino_api.models.profiles import (
    Phase,
    Profile,
    ProfileCreated,
    ProfileSummary,
)
from gaggiuino_api.resources import Profiles


@pytest_asyncio.fixture(loop_scope='function')
async def profiles(machine: FakeMachine) -> AsyncIterator[Profiles]:
    transport = Transport(machine.base_url, timeout=5)
    yield Profiles(transport)
    await transport.close()


async def test_list(machine: FakeMachine, profiles: Profiles) -> None:
    machine.answer('GET', 'profiles/all', load_fixture('profiles_all'))
    assert await profiles.list() == [
        ProfileSummary(id=7, name='_Long', selected=False),
        ProfileSummary(id=9, name='_OFF', selected=True),
    ]
    (request,) = machine.requests
    assert (request.method, request.path) == ('GET', '/api/profiles/all')


async def test_list_of_object_raises(machine: FakeMachine, profiles: Profiles) -> None:
    machine.answer('GET', 'profiles/all', {'id': 7})
    with pytest.raises(GaggiuinoResponseFormatError):
        await profiles.list()


async def test_get_sets_id(machine: FakeMachine, profiles: Profiles) -> None:
    fixture = load_fixture('profile')
    machine.answer(
        'GET',
        'profile/7',
        fixture,
        headers={'Content-Disposition': 'attachment; filename="profile.json"'},
    )
    profile = await profiles.get(7)
    assert profile.id == 7
    assert profile.name == fixture['name']
    assert profile.phases == [Phase.from_api(p) for p in fixture['phases']]
    (request,) = machine.requests
    assert (request.method, request.path) == ('GET', '/api/profile/7')


async def test_get_missing(machine: FakeMachine, profiles: Profiles) -> None:
    machine.answer('GET', 'profile/99', text='Not Found', status=404)
    with pytest.raises(GaggiuinoNotFoundError):
        await profiles.get(99)


def _profile(profile_id: int | None) -> Profile:
    return dataclasses.replace(Profile.from_api(load_fixture('profile')), id=profile_id)


@pytest.mark.parametrize(
    'profile',
    [7, ProfileSummary(id=7, name='_Long', selected=False), _profile(7)],
    ids=['int', 'summary', 'profile'],
)
async def test_select(
    machine: FakeMachine, profiles: Profiles, profile: int | ProfileSummary | Profile
) -> None:
    machine.answer('POST', 'profile-select/7', text='OK')
    assert await profiles.select(profile) is None
    (request,) = machine.requests
    assert (request.method, request.path) == ('POST', '/api/profile-select/7')
    assert request.raw == b''


async def test_select_missing(machine: FakeMachine, profiles: Profiles) -> None:
    machine.answer(
        'POST', 'profile-select/99', text='Failed to change profile', status=500
    )
    with pytest.raises(GaggiuinoResponseError) as exc_info:
        await profiles.select(99)
    assert exc_info.value.status == 500


@pytest.mark.parametrize('method', ['select', 'delete'])
async def test_profile_without_id_sends_nothing(
    machine: FakeMachine, profiles: Profiles, method: str
) -> None:
    with pytest.raises(ValueError, match='no id'):
        await getattr(profiles, method)(_profile(None))
    assert machine.requests == []


@pytest.mark.parametrize('method', ['get', 'select', 'delete'])
@pytest.mark.parametrize('value', [True, False])
async def test_bool_is_not_a_profile_id(
    machine: FakeMachine, profiles: Profiles, method: str, value: bool
) -> None:
    with pytest.raises(TypeError, match='bool'):
        await getattr(profiles, method)(value)
    assert machine.requests == []


@pytest.mark.parametrize('profile_id', [None, 7])
async def test_create_sends_no_id(
    machine: FakeMachine, profiles: Profiles, profile_id: int | None
) -> None:
    machine.answer('POST', 'profile', {'id': 4, 'name': '_Long'})
    created = await profiles.create(_profile(profile_id))
    assert created == ProfileCreated(id=4, name='_Long')
    (request,) = machine.requests
    assert (request.method, request.path) == ('POST', '/api/profile')
    assert request.json == load_fixture('profile')


async def test_create_422(machine: FakeMachine, profiles: Profiles) -> None:
    machine.answer('POST', 'profile', text='Unprocessable', status=422)
    with pytest.raises(GaggiuinoResponseError) as exc_info:
        await profiles.create(_profile(None))
    assert exc_info.value.status == 422


async def test_create_text_answer(machine: FakeMachine, profiles: Profiles) -> None:
    machine.answer('POST', 'profile', text='OK')
    with pytest.raises(GaggiuinoResponseFormatError):
        await profiles.create(_profile(None))


@pytest.mark.parametrize('text', ['', 'OK'])
async def test_delete(machine: FakeMachine, profiles: Profiles, text: str) -> None:
    machine.answer('GET', 'profiles/all', load_fixture('profiles_all'))
    machine.answer('DELETE', 'profile-select/7', text=text)
    assert await profiles.delete(7) is None
    listed, deleted = machine.requests
    assert (listed.method, listed.path) == ('GET', '/api/profiles/all')
    assert (deleted.method, deleted.path) == ('DELETE', '/api/profile-select/7')


async def test_delete_of_missing_id_sends_no_delete(
    machine: FakeMachine, profiles: Profiles
) -> None:
    machine.answer('GET', 'profiles/all', load_fixture('profiles_all'))
    # The real machine answers 200 to such a delete and can lose another profile.
    machine.answer('DELETE', 'profile-select/99', text='OK')
    with pytest.raises(GaggiuinoNotFoundError) as exc_info:
        await profiles.delete(99)
    assert exc_info.value.status == 404
    assert [request.method for request in machine.requests] == ['GET']

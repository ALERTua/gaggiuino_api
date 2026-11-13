"""Helpers of the end-to-end tests: waits and reads of the state that the tests change."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from gaggiuino_api import GaggiuinoClient

# The one time limit of each wait for the machine, in seconds.
WAIT_LIMIT = 10.0

# The settings groups that the tests write. The tests never write another group.
WRITTEN_GROUPS = ('led', 'display')


async def wait_until(check: Callable[[], Awaitable[bool]]) -> bool:
    """Ask `check` again until it is true or `WAIT_LIMIT` ends; return whether it became true."""
    try:
        async with asyncio.timeout(WAIT_LIMIT):
            while not await check():
                await asyncio.sleep(0.2)
    except TimeoutError:
        return False
    return True


async def profile_rows(machine: GaggiuinoClient) -> list[tuple[int, str, bool]]:
    """Return the id, the name and the selected flag of each saved profile, sorted by id."""
    return sorted((p.id, p.name, p.selected) for p in await machine.profiles.list())


async def is_selected(machine: GaggiuinoClient, profile_id: int) -> bool:
    """Return True when the list and the status both name `profile_id` as the active profile."""
    selected = [p.id for p in await machine.profiles.list() if p.selected]
    status_id = (await machine.status()).profile_id
    return selected == [profile_id] and status_id == profile_id


async def settings_equal(
    machine: GaggiuinoClient, group: str, expected: dict[str, Any]
) -> bool:
    """Return True when the raw settings group of the machine equals `expected`."""
    return await machine._transport.get_json(f'settings/{group}') == expected


async def machine_state(machine: GaggiuinoClient) -> dict[str, Any]:
    """Return the state that the tests change: the profiles and the written settings groups."""
    state: dict[str, Any] = {'profiles': await profile_rows(machine)}
    for group in WRITTEN_GROUPS:
        state[group] = await machine._transport.get_json(f'settings/{group}')
    return state

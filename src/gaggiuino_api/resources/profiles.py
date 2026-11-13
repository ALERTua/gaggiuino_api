"""The saved profiles of the machine: list, read, select, create and delete."""

import builtins
import dataclasses

from .._transport import Transport
from ..exceptions import GaggiuinoNotFoundError, GaggiuinoResponseFormatError
from ..models.profiles import Profile, ProfileCreated, ProfileSummary


def _profile_id(profile: int | ProfileSummary | Profile) -> int:
    """Return the id of a profile given as an id or as a model.

    Raise `ValueError` for a `Profile` without an id, and `TypeError` for a `bool`.
    """
    if isinstance(profile, bool):
        raise TypeError('A bool is not a profile id')
    if isinstance(profile, int):
        return profile
    if profile.id is None:
        raise ValueError(f'The profile {profile.name!r} has no id')
    return profile.id


class Profiles:
    """The saved profiles of the machine."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def list(self) -> builtins.list[ProfileSummary]:
        """Return the saved profiles: `GET /api/profiles/all`.

        Raise `GaggiuinoResponseFormatError` when the answer is not a JSON list
        of profiles.
        """
        data = await self._transport.get_json('profiles/all')
        if not isinstance(data, builtins.list):
            raise GaggiuinoResponseFormatError(
                f'Expected a JSON list of profiles, got {type(data).__name__}'
            )
        return [ProfileSummary.from_api(item) for item in data]

    async def get(self, profile_id: int) -> Profile:
        """Return the full profile with its phases: `GET /api/profile/<id>`.

        The machine leaves the id out of the answer, so the result gets
        `profile_id` as its id.
        Raise `GaggiuinoNotFoundError` when the profile does not exist.
        """
        data = await self._transport.get_json(f'profile/{profile_id}')
        return dataclasses.replace(Profile.from_api(data), id=profile_id)

    async def select(self, profile: int | ProfileSummary | Profile) -> None:
        """Make a saved profile the active one: `POST /api/profile-select/<id>`.

        `profile` is an id or a model with an id.
        Raise `ValueError` before any request for a `Profile` without an id, and
        `TypeError` for a `bool`.
        Raise `GaggiuinoResponseError` when the profile does not exist: the
        machine answers HTTP 500 for it, not 404.
        """
        profile_id = _profile_id(profile)
        await self._transport.command('POST', f'profile-select/{profile_id}')

    async def create(self, profile: Profile) -> ProfileCreated:
        """Save `profile` as a new profile: `POST /api/profile`.

        The machine always gives the new profile a new id, so the id of
        `profile` is not sent. Return the id and the name of the new profile.
        Raise `GaggiuinoResponseError` when the machine refuses the profile:
        HTTP 422 for bad data, HTTP 500 when it cannot save the profile.
        """
        body = profile.to_api()
        body.pop('id', None)
        data = await self._transport.command_json('POST', 'profile', body=body)
        return ProfileCreated.from_api(data)

    async def delete(self, profile: int | ProfileSummary | Profile) -> None:
        """Delete a saved profile: `DELETE /api/profile-select/<id>`.

        The firmware answers 200 for an id that it does not have and can remove another
        profile, so the id must be in `list()`. Otherwise raise `GaggiuinoNotFoundError`
        and send no delete. Raise `ValueError` for a `Profile` without an id, and
        `TypeError` for a `bool`.
        """
        profile_id = _profile_id(profile)
        if profile_id not in {saved.id for saved in await self.list()}:
            raise GaggiuinoNotFoundError(
                404, f'The machine has no profile with the id {profile_id}'
            )
        await self._transport.command('DELETE', f'profile-select/{profile_id}')

"""The shot history of the machine: the latest shot id, a shot and its deletion."""

from .._transport import Transport
from ..exceptions import GaggiuinoResponseFormatError
from ..models.shots import LatestShot, Shot


class Shots:
    """The saved shots of the machine."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def latest_id(self) -> int:
        """Return the id of the latest shot: `GET /api/shots/latest`.

        Raise `GaggiuinoResponseFormatError` when the answer is not a JSON list
        with at least one object that has the id.
        """
        data = await self._transport.get_json('shots/latest')
        if not isinstance(data, list) or not data:
            raise GaggiuinoResponseFormatError(
                'Expected a non-empty JSON list with the latest shot id'
            )
        return LatestShot.from_api(data[0]).last_shot_id

    async def get(self, shot_id: int) -> Shot:
        """Return a shot with its datapoints and its profile: `GET /api/shots/<id>`.

        Raise `GaggiuinoNotFoundError` when the shot does not exist.
        """
        data = await self._transport.get_json(f'shots/{shot_id}')
        return Shot.from_api(data)

    async def delete(self, shot: int | Shot) -> None:
        """Delete the data file of a shot: `DELETE /api/shots/<id>`.

        `shot` is an id or a `Shot`. The deletion cannot be undone. The machine
        needs an SD card for it.
        Raise `GaggiuinoResponseError` when the machine refuses the deletion.
        """
        shot_id = shot.id if isinstance(shot, Shot) else shot
        await self._transport.command('DELETE', f'shots/{shot_id}')

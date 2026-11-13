"""The service history of the machine: the answer of `GET /api/maintenance`."""

from dataclasses import dataclass

from .base import Model, api


@dataclass(frozen=True, kw_only=True)
class Maintenance(Model):
    """The service history that the machine tracks by itself.

    A `*_timestamp` field is in epoch seconds, and `0` means that the machine never recorded
    the event. The machine records a descale when the descale cycle reaches half of its
    progress. It records a backflush when the pressure is above 10 bar for more than 2 seconds
    in a flush mode. A `shots_since_*` counter counts only a shot of 5 seconds or longer.
    """

    last_descale_timestamp: int = api("lastDescaleTimestamp")
    shots_since_descale: int = api("shotsSinceDescale")
    last_backflush_timestamp: int = api("lastBackflushTimestamp")
    shots_since_backflush: int = api("shotsSinceBackflush")

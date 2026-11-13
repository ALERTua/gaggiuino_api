"""Models of the shot history: the id of the latest shot and a full shot with its datapoints."""

from dataclasses import dataclass

from .base import Model, api
from .profiles import Profile


@dataclass(frozen=True, kw_only=True)
class ShotDatapoints(Model):
    """The samples of a shot: one array for each measured value, one element for each sample.

    All arrays have the same length. Each value is an integer scaled by 10, so a
    `temperature` of 903 is 90.3. `time_in_shot` is in tenths of a second.
    `phase_index` is the index of the profile phase that was active at the sample.
    The firmware documentation does not describe it, so it is optional.
    """

    time_in_shot: list[int] = api("timeInShot")
    pressure: list[int] = api("pressure")
    pump_flow: list[int] = api("pumpFlow")
    weight_flow: list[int] = api("weightFlow")
    temperature: list[int] = api("temperature")
    shot_weight: list[int] = api("shotWeight")
    water_pumped: list[int] = api("waterPumped")
    target_temperature: list[int] = api("targetTemperature")
    target_pump_flow: list[int] = api("targetPumpFlow")
    target_pressure: list[int] = api("targetPressure")
    phase_index: list[int] | None = api("phaseIndex", default=None)


@dataclass(frozen=True, kw_only=True)
class Shot(Model):
    """A shot: the answer of `GET /api/shots/<id>`.

    `timestamp` is in epoch seconds. `duration` is in tenths of a second, the same scale as
    `ShotDatapoints.time_in_shot`. `profile` is the full profile of the shot, with its `id`.
    """

    id: int = api("id")
    timestamp: int = api("timestamp")
    duration: int = api("duration")
    datapoints: ShotDatapoints = api("datapoints")
    profile: Profile = api("profile")


@dataclass(frozen=True, kw_only=True)
class LatestShot(Model):
    """The one object in the list that `GET /api/shots/latest` returns."""

    last_shot_id: int = api("lastShotId")

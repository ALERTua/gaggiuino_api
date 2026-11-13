"""Models of the profiles: the list of the saved profiles and the full profile with its phases.

The firmware leaves out a key with a zero or empty value, so almost each key inside a
profile is optional. Each time is in milliseconds.
"""

from dataclasses import dataclass

from ..enums import CurveType, PhaseType
from .base import Model, api


@dataclass(frozen=True, kw_only=True)
class ProfileSummary(Model):
    """One saved profile in the answer of `GET /api/profiles/all`."""

    id: int = api("id")
    name: str = api("name")
    selected: bool = api("selected")


@dataclass(frozen=True, kw_only=True)
class PhaseTarget(Model):
    """The target of a phase: the transition from `start` to `end`.

    `time` is the duration of the transition in milliseconds.
    """

    start: float | None = api("start", default=None)
    end: float | None = api("end", default=None)
    curve: CurveType | str | None = api("curve", default=None)
    time: int | None = api("time", default=None)
    volume: float | None = api("volume", default=None)


@dataclass(frozen=True, kw_only=True)
class PhaseStopConditions(Model):
    """The conditions that end a phase. `time` is in milliseconds."""

    time: int | None = api("time", default=None)
    pressure_above: float | None = api("pressureAbove", default=None)
    pressure_below: float | None = api("pressureBelow", default=None)
    flow_above: float | None = api("flowAbove", default=None)
    flow_below: float | None = api("flowBelow", default=None)
    weight: float | None = api("weight", default=None)
    water_pumped_in_phase: float | None = api("waterPumpedInPhase", default=None)


@dataclass(frozen=True, kw_only=True)
class Phase(Model):
    """One phase of a profile of `GET /api/profile/<id>` and `POST /api/profile`."""

    type: PhaseType | str = api("type")
    target: PhaseTarget | None = api("target", default=None)
    restriction: float | None = api("restriction", default=None)
    stop_conditions: PhaseStopConditions | None = api("stopConditions", default=None)
    water_temperature: float | None = api("waterTemperature", default=None)
    name: str | None = api("name", default=None)
    skip: bool | None = api("skip", default=None)


@dataclass(frozen=True, kw_only=True)
class GlobalStopConditions(Model):
    """The conditions that end the whole shot. `time` is in milliseconds."""

    time: int | None = api("time", default=None)
    weight: float | None = api("weight", default=None)
    water_pumped: float | None = api("waterPumped", default=None)


@dataclass(frozen=True, kw_only=True)
class Recipe(Model):
    """The recipe of a profile: the dose in, the yield out and their ratio."""

    coffee_in: float | None = api("coffeeIn", default=None)
    coffee_out: float | None = api("coffeeOut", default=None)
    ratio: float | None = api("ratio", default=None)


@dataclass(frozen=True, kw_only=True)
class Profile(Model):
    """A full profile: the answer of `GET /api/profile/<id>` and the body of `POST /api/profile`.

    The answer of `GET /api/profile/<id>` has no `id`. The profile inside a shot has one.
    `POST /api/profile` always gives the new profile a new id.
    """

    id: int | None = api("id", default=None)
    name: str = api("name")
    phases: list[Phase] = api("phases")
    global_stop_conditions: GlobalStopConditions | None = api(
        "globalStopConditions", default=None
    )
    water_temperature: float | None = api("waterTemperature", default=None)
    recipe: Recipe | None = api("recipe", default=None)


@dataclass(frozen=True, kw_only=True)
class ProfileCreated(Model):
    """The answer of `POST /api/profile`: the id and the name of the new profile."""

    id: int = api("id")
    name: str = api("name")

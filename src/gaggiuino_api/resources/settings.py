"""The settings of the machine: read all of them, and read or update one group."""

import dataclasses
import typing
from enum import Enum
from typing import Any

from .._transport import Transport
from ..exceptions import GaggiuinoResponseFormatError
from ..models.base import Model
from ..models.settings import (
    BoilerSettings,
    DisplaySettings,
    LedSettings,
    ScalesSettings,
    Settings,
    SystemSettings,
    ThemeSettings,
    Versions,
)


class SettingsGroup[T: Model]:
    """One writable group of the settings, for example the boiler settings.

    The machine replaces the whole group on each write, so `update()` and `update_from()`
    read the group first and send it back whole with the changes laid over it. The update
    is a read followed by a write: a change that another client makes between the two is
    lost. Each key that the caller does not change goes back to the machine with the value
    that the machine sent, also each key that the library does not know.
    """

    def __init__(self, transport: Transport, group: str, model: type[T]) -> None:
        self._transport = transport
        self._group = group
        self._path = f'settings/{group}'
        self._model = model

    async def get(self) -> T:
        """Return the group: `GET /api/settings/<group>`."""
        data = await self._transport.get_json(self._path)
        return self._model.from_api(data)

    async def update(self, **changes: Any) -> None:
        """Change the named fields and keep the rest: `POST /api/settings/<group>`.

        Each name is a Python field name of the model, for example `steam_set_point=130`.
        A value is a plain value, an enum member, or a model for a nested field, for
        example `color=LedColor(r=255, g=0, b=0)`. A changed key goes to the machine in the
        form that the model writes, for example `"130"` as `130`.
        Raise `TypeError` before any request when no field is named, a name is not a
        field of the model, or a nested model is of another class than the field.
        Raise `ValueError` before any request for `None`, and before the write for a
        value that the model cannot read.
        Raise `GaggiuinoCommandError` when the machine refuses the write.
        """
        if not changes:
            raise TypeError(f'Name at least one field of the {self._group} settings')
        aliases = _aliases(self._model)
        hints = typing.get_type_hints(self._model)
        for name, value in changes.items():
            if name not in aliases:
                raise TypeError(f'The {self._group} settings have no field {name!r}')
            if value is None:
                raise ValueError(
                    f'The field {name!r} of the {self._group} settings cannot be None'
                )
            if isinstance(value, Model) and not isinstance(value, hints[name]):
                raise TypeError(
                    f'The field {name!r} of the {self._group} settings does not take '
                    f'a {type(value).__name__}'
                )
        await self._write(
            {aliases[name]: _to_json(value) for name, value in changes.items()}
        )

    async def update_from(self, settings: T) -> None:
        """Write each field of `settings` and keep the rest: `POST /api/settings/<group>`.

        A field that is `None` in `settings` changes nothing.
        Raise `TypeError` before any request when `settings` is not a model of this group.
        Raise `ValueError` before the write for a value that the model cannot read.
        Raise `GaggiuinoCommandError` when the machine refuses the write.
        """
        if not isinstance(settings, self._model):
            raise TypeError(
                f'The {self._group} settings take a {self._model.__name__}, '
                f'not a {type(settings).__name__}'
            )
        await self._write(settings.to_api())

    async def _write(self, changes: dict[str, Any]) -> None:
        """Lay `changes`, keyed by the firmware names, over the group and send the group.

        Raise `GaggiuinoResponseFormatError` when the group of the machine is not a JSON
        object that the model can read.
        """
        raw = await self._transport.get_json(self._path)
        if not isinstance(raw, dict):
            raise GaggiuinoResponseFormatError(
                f'Expected a JSON object of the {self._group} settings, '
                f'got {type(raw).__name__}'
            )
        # A bad answer of the machine is not a bad value of the caller.
        self._model.from_api(raw)
        try:
            parsed = self._model.from_api(_overlay(raw, changes))
        except GaggiuinoResponseFormatError as err:
            raise ValueError(
                f'A bad value for the {self._group} settings: {err}'
            ) from err
        normal = _pick(changes, parsed.to_api())
        await self._transport.command('POST', self._path, body=_overlay(raw, normal))


def _aliases(model: type[Model]) -> dict[str, str]:
    """Map each Python field name of `model` to the name that the firmware uses."""
    fields = dataclasses.fields(model)  # ty: ignore[invalid-argument-type]
    return {field.name: field.metadata['alias'] for field in fields}


def _to_json(value: object) -> object:
    """Return a value as JSON holds it: a model as its dict, an enum member as its value."""
    if isinstance(value, Model):
        return value.to_api()
    if isinstance(value, Enum):
        return value.value
    return value


def _overlay(base: dict[str, Any], changes: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of `base` with `changes` laid over it.

    A nested object of `changes` is laid over the nested object of `base`, so each key of
    `base` that `changes` does not name stays, at each depth.
    """
    result = dict(base)
    for key, value in changes.items():
        old = result.get(key)
        if isinstance(old, dict) and isinstance(value, dict):
            result[key] = _overlay(old, value)
        else:
            result[key] = value
    return result


def _pick(changes: dict[str, Any], written: dict[str, Any]) -> dict[str, Any]:
    """Return the value of `written` for each key of `changes`, at each depth.

    A key that `written` does not have keeps the value of `changes`.
    """
    picked: dict[str, Any] = {}
    for key, value in changes.items():
        if key not in written:
            picked[key] = value
        elif isinstance(value, dict) and isinstance(written[key], dict):
            picked[key] = _pick(value, written[key])
        else:
            picked[key] = written[key]
    return picked


class SettingsResource:
    """The settings of the machine: all groups at once, and each writable group."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport
        self.boiler = SettingsGroup(transport, 'boiler', BoilerSettings)
        self.system = SettingsGroup(transport, 'system', SystemSettings)
        self.led = SettingsGroup(transport, 'led', LedSettings)
        self.scales = SettingsGroup(transport, 'scales', ScalesSettings)
        self.display = SettingsGroup(transport, 'display', DisplaySettings)
        self.theme = SettingsGroup(transport, 'theme', ThemeSettings)

    async def get(self) -> Settings:
        """Return all settings in one answer: `GET /api/settings`."""
        data = await self._transport.get_json('settings')
        return Settings.from_api(data)

    async def versions(self) -> Versions:
        """Return the versions of the firmware parts: `GET /api/settings/versions`."""
        data = await self._transport.get_json('settings/versions')
        return Versions.from_api(data)

"""The base class of each model and the helper that declares a field with its firmware name."""

import annotationlib
import dataclasses
import types
import typing
from enum import Enum
from typing import Any, Self, overload

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.types import SerializationStrategy

from ..exceptions import GaggiuinoResponseFormatError


class _BoolStrategy(SerializationStrategy):
    """Read a JSON boolean, the string `true` or `false` in any case, or the integer 1 or 0.

    The firmware writes most booleans as JSON booleans and some as strings, for example
    `"selected": "false"`. Each other value is a parse failure. The model writes a JSON boolean.
    """

    def serialize(self, value: bool) -> bool:
        return value

    def deserialize(self, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, int) and value in (0, 1):
            return bool(value)
        if isinstance(value, str):
            text = value.lower()
            if text == "true":
                return True
            if text == "false":
                return False
        raise ValueError(f"not a boolean: {value!r}")


class _IntStrategy(SerializationStrategy):
    """Read a JSON integer or a string that holds an integer, for example `"150"`.

    A JSON boolean, a JSON float and a float string such as `"92.000000"` are parse failures,
    so a value never loses its fraction and `true` never turns into 1.
    """

    def serialize(self, value: int) -> int:
        return value

    def deserialize(self, value: object) -> int:
        if isinstance(value, bool):
            raise TypeError(f"not an integer: {value!r}")
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        raise ValueError(f"not an integer: {value!r}")


class _FloatStrategy(SerializationStrategy):
    """Read a JSON number or a string that holds a number, for example `"88.839622"`.

    The result is always a `float`, also for a JSON integer such as `"pumpFlow": 0`.
    A JSON boolean is a parse failure.
    """

    def serialize(self, value: float) -> float:
        return value

    def deserialize(self, value: object) -> float:
        if isinstance(value, bool):
            raise TypeError(f"not a number: {value!r}")
        if isinstance(value, int | float | str):
            return float(value)
        raise ValueError(f"not a number: {value!r}")


class _StrStrategy(SerializationStrategy):
    """Read a JSON string only.

    A number or `null` in a string field is a parse failure: it never turns into the text
    `"5"` or `"None"`. So an unknown value of a `TheEnum | str` field is always the raw string.
    """

    def serialize(self, value: str) -> str:
        return value

    def deserialize(self, value: object) -> str:
        if isinstance(value, str):
            return value
        raise ValueError(f"not a string: {value!r}")


_STRATEGIES: dict[Any, Any] = {
    bool: _BoolStrategy(),
    int: _IntStrategy(),
    float: _FloatStrategy(),
    str: _StrStrategy(),
}


@overload
def api[T](key: str, *, default: T) -> T: ...
@overload
def api(key: str) -> Any: ...
def api(key: str, *, default: object = dataclasses.MISSING) -> Any:
    """Declare a model field that the firmware calls `key`.

    The model reads the field from `key` and writes it back under `key`.
    Without `default` the field is required. Give `default=None` for an optional field.
    """
    return dataclasses.field(default=default, metadata={"alias": key})


def _check_enum_unions(cls: type, hint: object) -> None:
    """Refuse a union in which an enum comes after a raw type that the enum is based on.

    The parse tries the types of a union from left to right, so in `str | PhaseType` the
    known value `"FLOW"` would stay a plain `str` and never become `PhaseType.FLOW`.
    """
    args = typing.get_args(hint)
    if typing.get_origin(hint) in (typing.Union, types.UnionType):
        raw_types: list[type] = []
        for arg in args:
            if isinstance(arg, type) and issubclass(arg, Enum):
                if any(issubclass(arg, raw) for raw in raw_types):
                    raise TypeError(
                        f"{cls.__name__}: put the enum first in the union {hint}"
                    )
            elif isinstance(arg, type):
                raw_types.append(arg)
    for arg in args:
        _check_enum_unions(cls, arg)


class Model(DataClassDictMixin):
    """The base class of each model of the library.

    A model is a `@dataclass(frozen=True, kw_only=True)` subclass. Each field is declared
    with `api()`. The model ignores a key that it does not know, because a newer firmware
    adds keys. When the model is written back, a field with the value `None` is left out,
    because the firmware leaves out a key that has no value.

    In a union of an enum and its raw type, the enum comes first: `PhaseType | str`.
    A model class with the other order fails at its definition.
    """

    class Config(BaseConfig):
        serialization_strategy = _STRATEGIES
        serialize_by_alias = True
        omit_none = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        hints = annotationlib.get_annotations(
            cls, format=annotationlib.Format.FORWARDREF
        )
        for hint in hints.values():
            _check_enum_unions(cls, hint)

    @classmethod
    def from_api(cls, data: object) -> Self:
        """Parse a decoded JSON value from the machine into the model.

        Raise `GaggiuinoResponseFormatError` when the value is not a JSON object, a required
        key is missing, or a value has the wrong type.
        """
        try:
            if not isinstance(data, dict):
                raise TypeError(f"expected a JSON object, got {type(data).__name__}")
            return cls.from_dict(data)
        except (LookupError, ValueError, TypeError, AttributeError) as err:
            raise GaggiuinoResponseFormatError(f"{cls.__name__}: {err}") from err

    def to_api(self) -> dict[str, Any]:
        """Return the dict for the machine, with the firmware names of the fields."""
        return self.to_dict()

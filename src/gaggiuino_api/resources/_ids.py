"""The id of a saved item that a method takes as an id or as a model."""

from typing import Protocol


class _WithId(Protocol):
    @property
    def id(self) -> int | None: ...


def item_id(item: int | _WithId, noun: str) -> int:
    """Return the id of an item given as an id or as a model, `noun` names it in errors.

    Raise `TypeError` for a `bool`, and `ValueError` for a model without an id.
    """
    if isinstance(item, bool):
        raise TypeError(f'A bool is not a {noun} id')
    if isinstance(item, int):
        return item
    if item.id is None:
        name = getattr(item, 'name', None)
        label = noun if name is None else f'{noun} {name!r}'
        raise ValueError(f'The {label} has no id')
    return item.id

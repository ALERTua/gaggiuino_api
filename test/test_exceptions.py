"""Tests of the exceptions: they survive `pickle` and `copy`."""

import copy
import pickle
from collections.abc import Callable

import pytest

from gaggiuino_api import (
    GaggiuinoCommandError,
    GaggiuinoNotFoundError,
    GaggiuinoResponseError,
)

ERRORS: list[Exception] = [
    GaggiuinoResponseError(503, 'down'),
    GaggiuinoResponseError(500),
    GaggiuinoNotFoundError(404, 'Not found'),
    GaggiuinoCommandError('Refused', 422),
    GaggiuinoCommandError(),
]


def _pickled(error: Exception) -> Exception:
    return pickle.loads(pickle.dumps(error))


@pytest.mark.parametrize('clone', [_pickled, copy.copy, copy.deepcopy])
@pytest.mark.parametrize('error', ERRORS, ids=repr)
def test_error_survives_pickle_and_copy(
    error: Exception, clone: Callable[[Exception], Exception]
) -> None:
    other = clone(error)
    assert type(other) is type(error)
    assert str(other) == str(error)
    assert other.args == error.args
    assert vars(other) == vars(error)


def test_response_error_text_is_not_built_twice() -> None:
    assert str(_pickled(GaggiuinoResponseError(503, 'down'))) == 'HTTP 503: down'

"""Tests of the package itself: its exports and its constants."""

import importlib
import inspect
import pkgutil
from enum import Enum

import gaggiuino_api
import gaggiuino_api.enums
import gaggiuino_api.models
from gaggiuino_api.const import DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from gaggiuino_api.models import Model


def test_all_is_sorted_and_importable():
    for module in (gaggiuino_api, gaggiuino_api.models):
        assert module.__all__ == sorted(module.__all__)
        for name in module.__all__:
            assert hasattr(module, name)


def test_top_level_exports_each_model():
    missing = set(gaggiuino_api.models.__all__) - {'Model', 'api'}
    missing -= set(gaggiuino_api.__all__)
    assert not missing


def test_top_level_exports_each_enum():
    enums = {
        name
        for name, cls in inspect.getmembers(gaggiuino_api.enums, inspect.isclass)
        if issubclass(cls, Enum)
        and cls.__module__ == gaggiuino_api.enums.__name__
        and not name.startswith('_')
    }
    assert enums
    assert not enums - set(gaggiuino_api.__all__)


def test_models_export_each_model_class():
    defined = set()
    for info in pkgutil.iter_modules(gaggiuino_api.models.__path__):
        module = importlib.import_module(f'{gaggiuino_api.models.__name__}.{info.name}')
        defined |= {
            name
            for name, cls in inspect.getmembers(module, inspect.isclass)
            if issubclass(cls, Model)
            and cls is not Model
            and cls.__module__ == module.__name__
            and not name.startswith('_')
        }
    assert 'Status' in defined
    assert not defined - set(gaggiuino_api.models.__all__)


def test_transport_is_not_exported():
    assert 'Transport' not in gaggiuino_api.__all__


def test_default_base_url_has_no_trailing_slash():
    assert DEFAULT_BASE_URL == "http://gaggiuino.local"
    assert DEFAULT_TIMEOUT > 0

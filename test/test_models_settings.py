"""Tests of the settings models on real answers of the machine."""

import dataclasses
from typing import Any

import pytest

from fixture_loader import load_fixture
from gaggiuino_api.enums import ReleaseChannel
from gaggiuino_api.exceptions import GaggiuinoResponseFormatError
from gaggiuino_api.models.base import Model
from gaggiuino_api.models.settings import (
    BoilerSettings,
    DisplaySettings,
    LedColor,
    LedSettings,
    ScalesSettings,
    Settings,
    SystemSettings,
    ThemeSettings,
    TofSettings,
    Versions,
    WebUiSettings,
)

# The group of `GET /api/settings`, its fixture of its own endpoint and its model.
ENDPOINT_GROUPS: dict[str, tuple[str, type[Model]]] = {
    "boiler": ("settings_boiler", BoilerSettings),
    "system": ("settings_system", SystemSettings),
    "led": ("settings_led", LedSettings),
    "scales": ("settings_scales", ScalesSettings),
    "display": ("settings_display", DisplaySettings),
    "theme": ("settings_theme", ThemeSettings),
    "versions": ("settings_versions", Versions),
}

# The keys that the machine sends and that the models leave out.
LEFT_OUT: dict[str, set[str]] = {
    "boiler": {"dualBoilerStagger"},
    "system": {"pumpSpecValid", "pumpSpec"},
    "display": {
        "homeTileLeftTop",
        "homeTileLeftBottom",
        "homeTileRightTop",
        "homeTileLeftTopGroup",
        "homeTileLeftBottomGroup",
        "homeTileRightTopGroup",
        "homeLayout",
    },
    "webUi": {"configured", "themeId", "dashboardLayout", "dashboardFontSize"},
}

# The keys of a model that the firmware of the fixtures does not send.
NOT_SENT: dict[str, set[str]] = {"display": {"simpleUI"}}

OPTIONAL: dict[str, set[str]] = {
    "boiler": {"dualBoilerEnabled"},
    "system": {"machineName", "minShotDurationSeconds", "autoFlushDurationSeconds"},
    "display": {"simpleUI", "modernUI"},
    "webUi": {"brewHeaterWatts", "steamHeaterWatts", "pumpWatts", "idleWatts"},
    "settings": {"webUi"},
}


def _cases() -> dict[str, tuple[type[Model], dict[str, Any]]]:
    full = load_fixture("settings")
    led = load_fixture("settings_led")
    cases = {
        name: (model, load_fixture(fixture))
        for name, (fixture, model) in ENDPOINT_GROUPS.items()
    }
    cases["led.color"] = (LedColor, led["color"])
    cases["led.tof"] = (TofSettings, led["tof"])
    cases["webUi"] = (WebUiSettings, full["webUi"])
    cases["settings"] = (Settings, full)
    return cases


CASES = _cases()


def _fields(model: type[Model]) -> tuple[dataclasses.Field[Any], ...]:
    return dataclasses.fields(model)  # ty: ignore[invalid-argument-type]


def _name(model: type[Model], alias: str) -> str:
    return next(f.name for f in _fields(model) if f.metadata["alias"] == alias)


def _aliases(model: type[Model], *, optional: bool | None = None) -> set[str]:
    return {
        field.metadata["alias"]
        for field in _fields(model)
        if optional is None or (field.default is not dataclasses.MISSING) is optional
    }


def _field_params(optional: bool) -> list[Any]:
    return [
        pytest.param(name, alias, id=f"{name}.{alias}")
        for name, (model, _) in CASES.items()
        for alias in sorted(_aliases(model, optional=optional))
    ]


def _assert_written_back(written: dict[str, Any], raw: dict[str, Any]) -> None:
    for key, value in written.items():
        if isinstance(value, dict):
            _assert_written_back(value, raw[key])
        else:
            assert value == raw[key], key


def _without(raw: dict[str, Any], key: str) -> dict[str, Any]:
    return {k: v for k, v in raw.items() if k != key}


def test_group_fixtures_parse():
    boiler = BoilerSettings.from_api(load_fixture("settings_boiler"))
    assert boiler.brew_delta_state is True
    assert boiler.steam_set_point == 125
    system = SystemSettings.from_api(load_fixture("settings_system"))
    assert system.pump_flow_at_zero == 0.2401
    assert system.release_channel is ReleaseChannel.STABLE
    led = LedSettings.from_api(load_fixture("settings_led"))
    assert led.color == LedColor(r=9, g=0, b=9)
    assert led.tof == TofSettings(max=6, min=127)
    display = DisplaySettings.from_api(load_fixture("settings_display"))
    assert display.simple_ui is None
    assert display.modern_ui is True
    versions = Versions.from_api(load_fixture("settings_versions"))
    assert versions.core_version == "c929939"


def test_settings_parses():
    settings = Settings.from_api(load_fixture("settings"))
    assert settings.web_ui == WebUiSettings(
        brew_heater_watts=1300, steam_heater_watts=1000, pump_watts=45, idle_watts=4
    )
    assert settings.theme.colour_secondary == 17


@pytest.mark.parametrize("group", ENDPOINT_GROUPS)
def test_group_in_settings_equals_its_endpoint(group: str):
    fixture, model = ENDPOINT_GROUPS[group]
    settings = Settings.from_api(load_fixture("settings"))
    parsed = getattr(settings, _name(Settings, group))
    assert parsed == model.from_api(load_fixture(fixture))


@pytest.mark.parametrize("name", CASES)
def test_model_covers_each_key_of_the_fixture(name: str):
    model, raw = CASES[name]
    aliases = _aliases(model)
    assert set(raw) - aliases == LEFT_OUT.get(name, set())
    assert aliases - set(raw) == NOT_SENT.get(name, set())


@pytest.mark.parametrize("name", CASES)
def test_written_keys_equal_the_fixture(name: str):
    model, raw = CASES[name]
    _assert_written_back(model.from_api(raw).to_api(), raw)


@pytest.mark.parametrize("name", CASES)
def test_optional_aliases(name: str):
    assert _aliases(CASES[name][0], optional=True) == OPTIONAL.get(name, set())


@pytest.mark.parametrize(("name", "alias"), _field_params(optional=False))
def test_missing_required_key_is_a_format_error(name: str, alias: str):
    model, raw = CASES[name]
    with pytest.raises(GaggiuinoResponseFormatError):
        model.from_api(_without(raw, alias))


@pytest.mark.parametrize(("name", "alias"), _field_params(optional=True))
def test_missing_optional_key_gives_none(name: str, alias: str):
    model, raw = CASES[name]
    parsed = model.from_api(_without(raw, alias))
    assert getattr(parsed, _name(model, alias)) is None
    assert alias not in parsed.to_api()


def test_string_booleans_of_the_documentation():
    raw = load_fixture("settings_boiler") | {
        "brewDeltaState": "true",
        "dreamSteamState": "false",
    }
    boiler = BoilerSettings.from_api(raw)
    assert boiler.brew_delta_state is True
    assert boiler.dream_steam_state is False


def test_unknown_release_channel_stays_raw():
    raw = load_fixture("settings_system") | {"releaseChannel": 7}
    system = SystemSettings.from_api(raw)
    assert system.release_channel == 7
    assert type(system.release_channel) is int
    assert system.to_api()["releaseChannel"] == 7


def test_models_are_frozen():
    theme = ThemeSettings.from_api(load_fixture("settings_theme"))
    name = "colour_primary"
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(theme, name, 1)

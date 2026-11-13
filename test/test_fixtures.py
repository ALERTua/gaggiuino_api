from typing import Any

import pytest

from fixture_loader import FIXTURES_DIR, load_fixture

NEUTRAL_VALUES = {
    "machineName": "Gaggiuino",
    "sprofilerToken": "sprofiler-token",
    "visualizerToken": "visualizer-token",
    "mqttHost": "mqtt.example.com",
    "mqttUsername": "mqtt-user",
    "mqttPassword": "mqtt-password",
    "btScalesPinnedMac": "AA:BB:CC:DD:EE:FF",
}

FIXTURE_NAMES = sorted(p.stem for p in FIXTURES_DIR.glob("*.json"))


def _private_values(data: Any) -> list[tuple[str, Any]]:
    """Return each (key, value) pair of a private key at any depth."""
    found: list[tuple[str, Any]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key in NEUTRAL_VALUES:
                found.append((key, value))
            found.extend(_private_values(value))
    elif isinstance(data, list):
        for item in data:
            found.extend(_private_values(item))
    return found


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_fixture_has_only_neutral_private_values(name: str) -> None:
    data = load_fixture(name)
    for key, value in _private_values(data):
        assert value == NEUTRAL_VALUES[key], key


def test_shot_datapoints_have_equal_length() -> None:
    datapoints = load_fixture("shot")["datapoints"]
    assert len(datapoints) == 11
    assert len({len(series) for series in datapoints.values()}) == 1

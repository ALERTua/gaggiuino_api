"""Models for Gaggiuino"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class GaggiuinoShotDataPoints:
    pressure: list[int] | None = None
    pumpFlow: list[int] | None = None
    shotWeight: list[int] | None = None
    targetPressure: list[int] | None = None
    targetPumpFlow: list[int] | None = None
    targetTemperature: list[int] | None = None
    temperature: list[int] | None = None
    timeInShot: list[int] | None = None
    waterPumped: list[int] | None = None
    weightFlow: list[int] | None = None


@dataclass(frozen=True)
class GaggiuinoProfilePhaseStopCondition:
    """
    'stopConditions': {
        'pressureAbove': 2,
        'time': 15000,
        'weight': 0.1
    },
    """

    pressureAbove: int | None = None
    time: int | None = None
    weight: float | None = None


@dataclass(frozen=True)
class GaggiuinoProfilePhaseTarget:
    """
    'target': {
        'curve': 'INSTANT',
        'end': 2,
        'time': 10000
    },
    """

    curve: str
    end: int
    time: int


@dataclass(frozen=True)
class GaggiuinoProfileType:
    """
    'type': 'FLOW'
    """

    type: Literal['FLOW', 'PRESSURE']


@dataclass(frozen=True)
class GaggiuinoProfilePhase:
    """
    {
        'restriction': 2,
        'skip': False,
        'stopConditions': {
            'pressureAbove': 2,
            'time': 15000,
            'weight': 0.1
        },
        'target': {
            'curve': 'INSTANT',
            'end': 2,
            'time': 10000
        },
        'type': 'FLOW'
    },
    """

    restriction: int
    skip: bool
    stopConditions: GaggiuinoProfilePhaseStopCondition
    type: GaggiuinoProfileType


@dataclass(frozen=True)
class GaggiuinoProfile:
    """
    'profile': {
        'globalStopConditions': {
            'weight': 50
        },
        'id': 8,
        'name': '_Long',
        'phases': [
            {
                'restriction': 2,
                'skip': False,
                'stopConditions': {
                    'pressureAbove': 2,
                    'time': 15000,
                    'weight': 0.1
                },
                'target': {
                    'curve': 'INSTANT',
                    'end': 2,
                    'time': 10000
                },
                'type': 'FLOW'
            },
            {
                'restriction': 1,
                'skip': False,
                'stopConditions': {
                    'time': 15000
                },
                'target': {
                    'curve': 'INSTANT',
                    'end': 0
                },
                'type': 'FLOW'
            }, {
                'restriction': 9,
                'skip': False,
                'stopConditions': {},
                'target': {
                    'curve': 'EASE_IN_OUT',
                    'end': 1.5,
                    'start': 2,
                    'time': 15000
                },
                'type': 'FLOW'
            }
        ],
        'recipe': {},
        'waterTemperature': 90
    },
    """

    id: int
    name: str
    selected: bool | None = None
    globalStopConditions: dict[str, Any] | None = None
    phases: list[GaggiuinoProfilePhase] | None = None
    recipe: dict[str, Any] | None = None
    waterTemperature: int | None = None


@dataclass(frozen=True)
class GaggiuinoShot:
    """
    {
        'datapoints': {
            'pressure': [
                3, 3, 3, ...
            ],
            'pumpFlow': [
                0, 6, 12, 12, ...
            ],
            'shotWeight': [
                0, 0, 0, ...
            ],
            'targetPressure': [
                20, 20, 20, ...
            ],
            'targetPumpFlow': [
                20, 20, 20, ...
            ],
            'targetTemperature': [
                900, 900, 900, ...
            ],
            'temperature': [
                898, 898, 898, ...
            ],
            'timeInShot': [
                2, 3, 5, ...
            ],
            'waterPumped': [
                0, 2, 4, ...
            ],
            'weightFlow': [
                0, 0, 0, ...
            ]
        },
        'duration': 648,
        'id': 1,
        'profile': {
            'globalStopConditions': {
                'weight': 50
            },
            'id': 8,
            'name': '_Long',
            'phases': [
                {
                    'restriction': 2,
                    'skip': False,
                    'stopConditions': {
                        'pressureAbove': 2,
                        'time': 15000,
                        'weight': 0.1
                    },
                    'target': {
                        'curve': 'INSTANT',
                        'end': 2,
                        'time': 10000
                    },
                    'type': 'FLOW'
                },
                {
                    'restriction': 1,
                    'skip': False,
                    'stopConditions': {
                        'time': 15000
                    },
                    'target': {
                        'curve': 'INSTANT',
                        'end': 0
                    },
                    'type': 'FLOW'
                }, {
                    'restriction': 9,
                    'skip': False,
                    'stopConditions': {},
                    'target': {
                        'curve': 'EASE_IN_OUT',
                        'end': 1.5,
                        'start': 2,
                        'time': 15000
                    },
                    'type': 'FLOW'
                }
            ],
            'recipe': {},
            'waterTemperature': 90
        },
        'timestamp': 1731316192
    }
    """

    datapoints: GaggiuinoShotDataPoints
    duration: int
    id: int
    profile: GaggiuinoProfile
    timestamp: int


@dataclass
class GaggiuinoStatus:
    """
    {
      "upTime": "89107",
      "profileId": "7",
      "profileName": "OFF",
      "targetTemperature": "15.000000",
      "temperature": "22.500000",
      "pressure": "-0.028054",
      "waterLevel": "100",
      "weight": "0.000000",
      "brewSwitchState": "false",
      "steamSwitchState": "false"
    }

    """

    upTime: int
    profileId: int
    profileName: str
    targetTemperature: float
    temperature: float
    temperature: float
    pressure: float
    waterLevel: int
    weight: float
    brewSwitchState: bool
    steamSwitchState: bool


@dataclass(frozen=True)
class GaggiuinoLatestShotResult:
    """
    [
        {
            "lastShotId": "100"
        }
    ]
    """

    lastShotId: int

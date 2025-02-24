"""Models for Gaggiuino"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal


@dataclass
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


@dataclass
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


@dataclass
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


@dataclass
class GaggiuinoProfileType:
    """
    'type': 'FLOW'
    """

    type: Literal['FLOW', 'PRESSURE']


@dataclass
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


@dataclass
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
    globalStopConditions: dict[str, Any] | None = None
    phases: list[GaggiuinoProfilePhase] | None = None
    recipe: dict[str, Any] | None = None
    waterTemperature: int | None = None


@dataclass
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

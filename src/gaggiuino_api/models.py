"""Models for Gaggiuino"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal
from gaggiuino_api.tools import strtobool


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
    pressure: float
    waterLevel: int
    weight: float
    brewSwitchState: bool
    steamSwitchState: bool

    @staticmethod
    def from_dict(data: dict):
        return GaggiuinoStatus(
            upTime=int(data['upTime']),
            profileId=int(data['profileId']),
            profileName=data['profileName'],
            targetTemperature=float(data['targetTemperature']),
            temperature=float(data['temperature']),
            pressure=float(data['pressure']),
            waterLevel=int(data['waterLevel']),
            weight=float(data['weight']),
            brewSwitchState=strtobool(data['brewSwitchState']),
            steamSwitchState=strtobool(data['steamSwitchState']),
        )


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

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoLatestShotResult":
        """Create instance from API response dict.

        The API returns lastShotId as a string, so we convert it to int.
        """
        return GaggiuinoLatestShotResult(
            lastShotId=int(data["lastShotId"]),
        )

    def to_api_dict(self) -> dict:
        """Convert to API request format."""
        return {"lastShotId": str(self.lastShotId)}


# Settings Models


@dataclass
class GaggiuinoBoilerSettings:
    """Boiler settings model.

    Response Example:
    {
        "steamSetPoint": 145,
        "offsetTemp": 5,
        "hpwr": 1200,
        "mainDivider": 2,
        "brewDivider": 4,
        "brewDeltaState": "true",
        "dreamSteamState": "false",
        "startupHeatDelta": 10
    }
    """

    steamSetPoint: int
    offsetTemp: int
    hpwr: int
    mainDivider: int
    brewDivider: int
    brewDeltaState: str
    dreamSteamState: str
    startupHeatDelta: int

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoBoilerSettings":
        return GaggiuinoBoilerSettings(
            steamSetPoint=int(data["steamSetPoint"]),
            offsetTemp=int(data["offsetTemp"]),
            hpwr=int(data["hpwr"]),
            mainDivider=int(data["mainDivider"]),
            brewDivider=int(data["brewDivider"]),
            brewDeltaState=str(data["brewDeltaState"]),
            dreamSteamState=str(data["dreamSteamState"]),
            startupHeatDelta=int(data["startupHeatDelta"]),
        )

    def to_api_dict(self) -> dict:
        """Convert to API request format."""
        return {
            "steamSetPoint": self.steamSetPoint,
            "offsetTemp": self.offsetTemp,
            "hpwr": self.hpwr,
            "mainDivider": self.mainDivider,
            "brewDivider": self.brewDivider,
            "brewDeltaState": self.brewDeltaState,
            "dreamSteamState": self.dreamSteamState,
            "startupHeatDelta": self.startupHeatDelta,
        }


@dataclass
class GaggiuinoSystemSettings:
    """System settings model.

    Response Example:
    {
        "pumpFlowAtZero": 0.5,
        "timezoneOffsetMinutes": -300,
        "sprofilerToken": "abc123xyz",
        "visualizerToken": "def456uvw",
        "servicesState": true,
        "wifiEnabled": true,
        "releaseChannel": 0
    }

    Field Notes:
    - releaseChannel: 0 = stable, 1 = test, 2 = debug
    """

    pumpFlowAtZero: float
    timezoneOffsetMinutes: int
    sprofilerToken: str
    visualizerToken: str
    servicesState: bool
    wifiEnabled: bool
    releaseChannel: int

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoSystemSettings":
        return GaggiuinoSystemSettings(
            pumpFlowAtZero=float(data["pumpFlowAtZero"]),
            timezoneOffsetMinutes=int(data["timezoneOffsetMinutes"]),
            sprofilerToken=str(data.get("sprofilerToken", "")),
            visualizerToken=str(data.get("visualizerToken", "")),
            servicesState=bool(data["servicesState"]),
            wifiEnabled=bool(data["wifiEnabled"]),
            releaseChannel=int(data["releaseChannel"]),
        )

    def to_api_dict(self) -> dict:
        """Convert to API request format."""
        return {
            "pumpFlowAtZero": self.pumpFlowAtZero,
            "timezoneOffsetMinutes": self.timezoneOffsetMinutes,
            "sprofilerToken": self.sprofilerToken,
            "visualizerToken": self.visualizerToken,
            "servicesState": self.servicesState,
            "wifiEnabled": self.wifiEnabled,
            "releaseChannel": self.releaseChannel,
        }


@dataclass(frozen=True)
class GaggiuinoLedColor:
    """LED color RGB values.

    Response Example:
    {
        "R": 255,
        "G": 128,
        "B": 0
    }
    """

    R: int
    G: int
    B: int

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoLedColor":
        return GaggiuinoLedColor(
            R=int(data["R"]),
            G=int(data["G"]),
            B=int(data["B"]),
        )

    def to_api_dict(self) -> dict:
        return {"R": self.R, "G": self.G, "B": self.B}


@dataclass(frozen=True)
class GaggiuinoTofSettings:
    """Time-of-flight sensor settings.

    Response Example:
    {
        "max": 100,
        "min": 10
    }
    """

    max: int
    min: int

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoTofSettings":
        return GaggiuinoTofSettings(
            max=int(data["max"]),
            min=int(data["min"]),
        )

    def to_api_dict(self) -> dict:
        return {"max": self.max, "min": self.min}


@dataclass
class GaggiuinoLedSettings:
    """LED settings model.

    Response Example:
    {
        "color": {
            "R": 255,
            "G": 128,
            "B": 0
        },
        "state": "true",
        "disco": "false",
        "tof": {
            "max": 100,
            "min": 10
        }
    }
    """

    color: GaggiuinoLedColor
    state: bool
    disco: bool
    tof: GaggiuinoTofSettings

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoLedSettings":
        return GaggiuinoLedSettings(
            color=GaggiuinoLedColor.from_dict(data["color"]),
            state=strtobool(data["state"]),
            disco=strtobool(data["disco"]),
            tof=GaggiuinoTofSettings.from_dict(data["tof"]),
        )

    def to_api_dict(self) -> dict:
        return {
            "color": self.color.to_api_dict(),
            "state": bool(self.state),
            "disco": bool(self.disco),
            "tof": self.tof.to_api_dict(),
        }


@dataclass
class GaggiuinoScalesSettings:
    """Scales settings model.

    Response Example:
    {
        "forcePredictive": "false",
        "hwScalesEnabled": "true",
        "hwScalesF1": 1000,
        "hwScalesF2": 2000,
        "btScalesEnabled": "false",
        "btScalesAutoConnect": "false"
    }

    Field Notes:
    - hwScalesF1, hwScalesF2: Hardware scales calibration factors
    """

    forcePredictive: bool
    hwScalesEnabled: bool
    hwScalesF1: int
    hwScalesF2: int
    btScalesEnabled: bool
    btScalesAutoConnect: bool

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoScalesSettings":
        return GaggiuinoScalesSettings(
            forcePredictive=strtobool(data["forcePredictive"]),
            hwScalesEnabled=strtobool(data["hwScalesEnabled"]),
            hwScalesF1=int(data["hwScalesF1"]),
            hwScalesF2=int(data["hwScalesF2"]),
            btScalesEnabled=strtobool(data["btScalesEnabled"]),
            btScalesAutoConnect=strtobool(data["btScalesAutoConnect"]),
        )

    def to_api_dict(self) -> dict:
        return {
            "forcePredictive": bool(self.forcePredictive),
            "hwScalesEnabled": bool(self.hwScalesEnabled),
            "hwScalesF1": self.hwScalesF1,
            "hwScalesF2": self.hwScalesF2,
            "btScalesEnabled": bool(self.btScalesEnabled),
            "btScalesAutoConnect": bool(self.btScalesAutoConnect),
        }


@dataclass
class GaggiuinoDisplaySettings:
    """Display settings model.

    Response Example:
    {
        "lcdBrightness": 80,
        "lcdDarkMode": "false",
        "lcdSleep": 10,
        "lcdGoHome": 5
    }

    Field Notes:
    - lcdBrightness: Screen brightness (0-100)
    - lcdSleep: Time in minutes before screen sleeps
    - lcdGoHome: Time in seconds after shot finishes to close shot graph
    """

    lcdBrightness: int
    lcdDarkMode: str
    lcdSleep: int
    lcdGoHome: int

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoDisplaySettings":
        return GaggiuinoDisplaySettings(
            lcdBrightness=int(data["lcdBrightness"]),
            lcdDarkMode=str(data["lcdDarkMode"]),
            lcdSleep=int(data["lcdSleep"]),
            lcdGoHome=int(data["lcdGoHome"]),
        )

    def to_api_dict(self) -> dict:
        return {
            "lcdBrightness": self.lcdBrightness,
            "lcdDarkMode": self.lcdDarkMode,
            "lcdSleep": self.lcdSleep,
            "lcdGoHome": self.lcdGoHome,
        }


@dataclass(frozen=True)
class GaggiuinoThemeSettings:
    """Theme color settings model.

    Response Example:
    {
        "colourPrimary": 31,
        "colourSecondary": 63488
    }

    Field Notes:
    - Colors are in RGB565 format
    """

    colourPrimary: int
    colourSecondary: int

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoThemeSettings":
        return GaggiuinoThemeSettings(
            colourPrimary=int(data["colourPrimary"]),
            colourSecondary=int(data["colourSecondary"]),
        )

    def to_api_dict(self) -> dict:
        return {
            "colourPrimary": self.colourPrimary,
            "colourSecondary": self.colourSecondary,
        }


@dataclass(frozen=True)
class GaggiuinoVersions:
    """Version information for all system components.

    Response Example:
    {
        "coreVersion": "a06f97fd",
        "frontVersion": "a06f97fd",
        "staticVersion": "a06f97fd"
    }

    Field Notes:
    - coreVersion: Dynamically populated from system state
    - frontVersion: Frontend version
    - staticVersion: Static assets version
    - This endpoint is read-only (no POST method available)
    """

    coreVersion: str
    frontVersion: str
    staticVersion: str

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoVersions":
        return GaggiuinoVersions(
            coreVersion=str(data["coreVersion"]),
            frontVersion=str(data["frontVersion"]),
            staticVersion=str(data["staticVersion"]),
        )


@dataclass
class GaggiuinoSettings:
    """Aggregate settings model containing all settings categories.

    Response Example:
    {
        "boiler": { "steamSetPoint": 145, "offsetTemp": 5, ... },
        "system": { "pumpFlowAtZero": 0.5, "timezoneOffsetMinutes": -300, ... },
        "led": { "color": { "R": 255, "G": 128, "B": 0 }, ... },
        "scales": { "forcePredictive": false, "hwScalesEnabled": true, ... },
        "display": { "lcdBrightness": 80, "lcdDarkMode": false, ... },
        "theme": { "colourPrimary": 31, "colourSecondary": 63488 },
        "versions": { "coreVersion": "1.0.0", "frontVersion": "1.0.0", ... }
    }
    """

    boiler: GaggiuinoBoilerSettings
    system: GaggiuinoSystemSettings
    led: GaggiuinoLedSettings
    scales: GaggiuinoScalesSettings
    display: GaggiuinoDisplaySettings
    theme: GaggiuinoThemeSettings
    versions: GaggiuinoVersions

    @staticmethod
    def from_dict(data: dict) -> "GaggiuinoSettings":
        return GaggiuinoSettings(
            boiler=GaggiuinoBoilerSettings.from_dict(data["boiler"]),
            system=GaggiuinoSystemSettings.from_dict(data["system"]),
            led=GaggiuinoLedSettings.from_dict(data["led"]),
            scales=GaggiuinoScalesSettings.from_dict(data["scales"]),
            display=GaggiuinoDisplaySettings.from_dict(data["display"]),
            theme=GaggiuinoThemeSettings.from_dict(data["theme"]),
            versions=GaggiuinoVersions.from_dict(data["versions"]),
        )

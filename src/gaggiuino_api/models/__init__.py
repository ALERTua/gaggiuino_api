"""Models of the answers and the requests of the Gaggiuino REST API."""

from .base import Model, api
from .firmware import FirmwareProgress
from .health import Health
from .maintenance import Maintenance
from .profiles import (
    GlobalStopConditions,
    Phase,
    PhaseStopConditions,
    PhaseTarget,
    Profile,
    ProfileCreated,
    ProfileSummary,
    Recipe,
)
from .settings import (
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
from .shots import LatestShot, Shot, ShotDatapoints
from .status import Status

__all__ = [
    'BoilerSettings',
    'DisplaySettings',
    'FirmwareProgress',
    'GlobalStopConditions',
    'Health',
    'LatestShot',
    'LedColor',
    'LedSettings',
    'Maintenance',
    'Model',
    'Phase',
    'PhaseStopConditions',
    'PhaseTarget',
    'Profile',
    'ProfileCreated',
    'ProfileSummary',
    'Recipe',
    'ScalesSettings',
    'Settings',
    'Shot',
    'ShotDatapoints',
    'Status',
    'SystemSettings',
    'ThemeSettings',
    'TofSettings',
    'Versions',
    'WebUiSettings',
    'api',
]

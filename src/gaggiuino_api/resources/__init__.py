"""Resources of the client: each one groups the endpoints of one kind."""

from .firmware import Firmware
from .profiles import Profiles
from .settings import SettingsGroup, SettingsResource
from .shots import Shots

__all__ = [
    'Firmware',
    'Profiles',
    'SettingsGroup',
    'SettingsResource',
    'Shots',
]

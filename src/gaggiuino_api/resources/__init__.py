"""Resources of the client: each one groups the endpoints of one kind."""

from .firmware import Firmware
from .profiles import Profiles
from .shots import Shots

__all__ = [
    'Firmware',
    'Profiles',
    'Shots',
]

"""Exceptions for gaggiuino"""


class GaggiuinoError(Exception):
    """Generic Gaggiuino exception."""


class GaggiuinoConnectionError(GaggiuinoError):
    """Gaggiuino connection error exception."""


class GaggiuinoEndpointNotFoundError(GaggiuinoError):
    """Gaggiuino endpoint not found exception."""

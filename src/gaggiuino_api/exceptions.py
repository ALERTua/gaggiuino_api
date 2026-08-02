"""Exceptions for gaggiuino"""


class GaggiuinoError(Exception):
    """Generic Gaggiuino exception."""


class GaggiuinoConnectionError(GaggiuinoError):
    """Gaggiuino connection error exception."""


class GaggiuinoConnectionTimeoutError(GaggiuinoError):
    """Gaggiuino connection error exception."""


class GaggiuinoEndpointNotFoundError(GaggiuinoError):
    """Gaggiuino endpoint not found exception."""


class GaggiuinoResponseError(GaggiuinoError):
    """Gaggiuino HTTP error response exception (4xx/5xx)."""

    def __init__(self, status: int, body: str = ""):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}" if body else f"HTTP {status}")

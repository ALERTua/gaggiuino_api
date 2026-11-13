"""Exceptions of the Gaggiuino API client."""


class GaggiuinoError(Exception):
    """Base class of each error that the library raises."""


class GaggiuinoConnectionError(GaggiuinoError):
    """The connection to the machine failed."""


class GaggiuinoConnectionTimeoutError(GaggiuinoError):
    """The machine did not answer in time."""


class GaggiuinoResponseError(GaggiuinoError):
    """The machine answered with an HTTP error status (400 or higher)."""

    def __init__(self, status: int, body: str = "") -> None:
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}" if body else f"HTTP {status}")


class GaggiuinoNotFoundError(GaggiuinoResponseError):
    """The machine answered with HTTP 404, for example for a shot or a profile that does not exist.

    The delete of a profile also raises it, before the delete request, when
    the list of the machine does not have the profile.
    """


class GaggiuinoCommandError(GaggiuinoError):
    """The machine refused a command: its answer has `"success": false`."""

    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(message or "The machine refused the command")


class GaggiuinoResponseFormatError(GaggiuinoError):
    """The answer of the machine does not have the expected format."""

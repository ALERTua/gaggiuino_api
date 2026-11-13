"""Exceptions of the Gaggiuino API client."""


class GaggiuinoError(Exception):
    """Base class of each error that the library raises."""


class GaggiuinoConnectionError(GaggiuinoError):
    """The connection to the machine failed."""


class GaggiuinoConnectionTimeoutError(GaggiuinoError):
    """The machine did not answer in time."""


# The most characters of the answer body that the text of `GaggiuinoResponseError` holds.
_MESSAGE_BODY_LIMIT = 500


class GaggiuinoResponseError(GaggiuinoError):
    """The machine answered with an HTTP error status (400 or higher).

    The attribute `body` holds the whole body of the answer. The text of the exception
    holds at most 500 characters of it.
    """

    def __init__(self, status: int, body: str = "") -> None:
        self.status = status
        self.body = body
        if len(body) > _MESSAGE_BODY_LIMIT:
            shown = f"{body[:_MESSAGE_BODY_LIMIT]}..."
        else:
            shown = body
        super().__init__(f"HTTP {status}: {shown}" if shown else f"HTTP {status}")


class GaggiuinoNotFoundError(GaggiuinoResponseError):
    """The machine answered with HTTP 404, for example for a shot or a profile that does not exist.

    The delete of a profile also raises it, before the delete request, when
    the list of the machine does not have the profile.
    """


class GaggiuinoCommandError(GaggiuinoError):
    """The machine refused a command: its answer has `"success": false`.

    The attribute `status` is the HTTP status of the answer.
    """

    def __init__(self, message: str = "", status: int | None = None) -> None:
        self.message = message
        self.status = status
        super().__init__(message or "The machine refused the command")


class GaggiuinoResponseFormatError(GaggiuinoError):
    """The answer of the machine does not have the expected format."""

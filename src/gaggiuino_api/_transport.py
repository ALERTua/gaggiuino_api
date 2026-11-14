"""HTTP transport of the Gaggiuino API client: the session, the requests and the error mapping."""

import json
import logging
import math
from typing import Any, Literal, NoReturn

import aiohttp

from .const import DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from .exceptions import (
    GaggiuinoCommandError,
    GaggiuinoConnectionError,
    GaggiuinoConnectionTimeoutError,
    GaggiuinoNotFoundError,
    GaggiuinoResponseError,
    GaggiuinoResponseFormatError,
)

_LOGGER = logging.getLogger(__name__)

_GET_HEADERS = {'Accept': 'application/json'}
# A command declares a JSON body also when it sends none: aiohttp would declare an octet stream.
_COMMAND_HEADERS = {**_GET_HEADERS, 'Content-Type': 'application/json'}

type CommandMethod = Literal['POST', 'DELETE']


class Transport:
    """Send requests to the REST API of one machine and map each failure to a library error."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        session: aiohttp.ClientSession | None = None,
        timeout: float | aiohttp.ClientTimeout | None = None,
    ) -> None:
        self._base_url = base_url.rstrip('/')
        self._session = session
        self._owns_session = session is None
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        if not isinstance(timeout, aiohttp.ClientTimeout):
            # aiohttp treats a total <= 0 as no timeout.
            if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
                raise ValueError(
                    'The timeout must be a finite number above zero or a ClientTimeout, '
                    f'not {timeout!r}'
                )
            timeout = aiohttp.ClientTimeout(total=timeout)
        self._timeout = timeout

    @property
    def base_url(self) -> str:
        """The base URL of the machine, without a trailing slash."""
        return self._base_url

    async def open(self) -> None:
        """Create an own session. A session that the caller gave is used as it is."""
        self._ensure_session()

    async def close(self) -> None:
        """Close the own session. A session that the caller gave stays open."""
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    def _ensure_session(self) -> aiohttp.ClientSession:
        """Return the session, and create an own one when there is none."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_json(self, path: str) -> Any:
        """GET `/api/<path>` and return the parsed JSON, whatever its content type."""
        raw, _ = await self._request('GET', path)
        return _parse_json(raw)

    async def command_json(
        self, method: CommandMethod, path: str, *, body: Any = None
    ) -> Any:
        """Send a command that must answer with JSON, and return the parsed JSON.

        Raise `GaggiuinoResponseFormatError` when the answer is not valid JSON.
        """
        raw, status = await self._request(method, path, body)
        return _check_success(_parse_json(raw), status)

    async def command(
        self, method: CommandMethod, path: str, *, body: Any = None
    ) -> dict[str, Any] | None:
        """Send a command whose answer can be empty or not JSON.

        Return the answer when it is a JSON object, else None.
        """
        raw, status = await self._request(method, path, body)
        try:
            parsed = json.loads(raw)
        except ValueError:
            return None
        if not isinstance(parsed, dict):
            return None
        return _check_success(parsed, status)

    async def _request(
        self, method: str, path: str, body: Any = None
    ) -> tuple[bytes, int]:
        """Send one request and return the raw body and the status of a successful answer."""
        url = f'{self._base_url}/api/{path.lstrip("/")}'
        session = self._ensure_session()
        if session.closed:
            raise GaggiuinoConnectionError(
                f'{method} {path} failed: the session is closed'
            )
        try:
            # Map error statuses here, even for a caller session that raises on them.
            async with session.request(
                method,
                url,
                json=body,
                headers=_GET_HEADERS if method == 'GET' else _COMMAND_HEADERS,
                timeout=self._timeout,
                raise_for_status=False,
            ) as response:
                raw = await response.read()
                status = response.status
        except TimeoutError as err:
            _LOGGER.debug('%s %s timed out', method, path)
            raise GaggiuinoConnectionTimeoutError(f'{method} {path} timed out') from err
        except aiohttp.ClientError as err:
            _LOGGER.debug('%s %s failed: %s', method, path, type(err).__name__)
            raise GaggiuinoConnectionError(f'{method} {path} failed: {err}') from err
        _LOGGER.debug('%s %s -> %s', method, path, status)
        if status >= 400:
            _raise_for_status(status, raw)
        return raw, status


def _parse_json(raw: bytes) -> Any:
    """Parse a body that must be JSON."""
    try:
        return json.loads(raw)
    except ValueError as err:
        raise GaggiuinoResponseFormatError('The answer is not valid JSON') from err


def _check_success[T](parsed: T, status: int) -> T:
    """Raise `GaggiuinoCommandError` when `success` is false or the string "false" (any case)."""
    if isinstance(parsed, dict) and _is_refusal(parsed.get('success')):
        raise GaggiuinoCommandError(_refusal_message(parsed), status)
    return parsed


def _is_refusal(success: object) -> bool:
    if success is False:
        return True
    return isinstance(success, str) and success.lower() == 'false'


def _refusal_message(parsed: dict[str, Any]) -> str:
    """Return `error`, else `message`, else ''; null and '' count as missing."""
    for key in ('error', 'message'):
        value = parsed.get(key)
        if value is not None and value != '':
            return str(value)
    return ''


def _raise_for_status(status: int, raw: bytes) -> NoReturn:
    """Raise the library error for an HTTP error status."""
    text = raw.decode('utf-8', errors='replace')
    if status == 404:
        raise GaggiuinoNotFoundError(status, text)
    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = None
    _check_success(parsed, status)
    raise GaggiuinoResponseError(status, text)

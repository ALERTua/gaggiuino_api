"""Shared fixtures of the tests."""

import asyncio
import json
from collections import defaultdict, deque
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass, field
from typing import Any

import pytest_asyncio
from aiohttp import web
from aiohttp.test_utils import TestServer
from multidict import CIMultiDictProxy

_NO_JSON: Any = object()


@dataclass(frozen=True)
class Answer:
    """One answer of the fake machine."""

    body: bytes
    status: int
    headers: Mapping[str, str]
    delay: float


@dataclass(frozen=True)
class Request:
    """One request as the fake machine received it."""

    method: str
    path: str
    """The full path, for example `/api/health`."""
    headers: CIMultiDictProxy[str]
    raw: bytes
    json: Any
    """The decoded JSON body, or None when the body is empty or not JSON."""


@dataclass
class FakeMachine:
    """A local HTTP server that answers like the REST API of a machine."""

    base_url: str = ''
    requests: list[Request] = field(default_factory=list)
    _answers: defaultdict[tuple[str, str], deque[Answer]] = field(
        default_factory=lambda: defaultdict(deque)
    )
    _released: asyncio.Event = field(default_factory=asyncio.Event)

    def answer(
        self,
        method: str,
        path: str,
        json_value: Any = _NO_JSON,
        *,
        text: str | None = None,
        body: bytes | None = None,
        status: int = 200,
        headers: Mapping[str, str] | None = None,
        delay: float = 0.0,
    ) -> None:
        """Add an answer to `method /api/<path>`.

        Give one of a JSON value, `text` or `body`, or none for an empty body.
        Each call adds the next answer of the route; the last one repeats.
        `headers` override the default `Content-Type`.
        `delay` holds the answer for that many seconds, or until the server stops.
        """
        if json_value is not _NO_JSON:
            raw, content_type = json.dumps(json_value).encode(), 'application/json'
        elif text is not None:
            raw, content_type = text.encode(), 'text/plain'
        else:
            raw, content_type = body or b'', 'application/octet-stream'
        all_headers = {'Content-Type': content_type, **(headers or {})}
        key = (method.upper(), f'/api/{path.lstrip("/")}')
        self._answers[key].append(Answer(raw, status, all_headers, delay))

    async def _handle(self, request: web.Request) -> web.Response:
        """Record the request and send the next answer of its route."""
        raw = await request.read()
        try:
            parsed = json.loads(raw) if raw else None
        except ValueError:
            parsed = None
        self.requests.append(
            Request(request.method, request.path, request.headers, raw, parsed)
        )
        queue = self._answers.get((request.method, request.path))
        if not queue:
            return web.Response(status=404, text='Not found')
        answer = queue.popleft() if len(queue) > 1 else queue[0]
        if answer.delay:
            try:
                await asyncio.wait_for(self._released.wait(), answer.delay)
            except TimeoutError:
                pass
        return web.Response(
            body=answer.body, status=answer.status, headers=answer.headers
        )


@pytest_asyncio.fixture(loop_scope='function')
async def machine() -> AsyncIterator[FakeMachine]:
    """Run a fake machine on 127.0.0.1 and a free port for one test."""
    fake = FakeMachine()
    app = web.Application()
    app.router.add_route('*', '/{tail:.*}', fake._handle)
    server = TestServer(app, host='127.0.0.1')
    await server.start_server()
    fake.base_url = f'http://127.0.0.1:{server.port}'
    try:
        yield fake
    finally:
        fake._released.set()
        await server.close()

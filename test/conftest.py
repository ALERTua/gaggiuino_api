"""Shared fixtures of the tests."""

from collections.abc import Iterator
from typing import Any

import aiohttp
import aioresponses.core
import pytest
from aioresponses import aioresponses as AioResponses
from yarl import URL


class _SentRequestWriter:
    """Stand-in for the stream writer of a request that is already sent."""

    output_size = 0


class _MockResponse(aiohttp.ClientResponse):
    """A `ClientResponse` that aioresponses can build.

    aioresponses 0.7.9 builds a `ClientResponse` without the `stream_writer` argument
    that aiohttp 3.14 requires, so this class supplies one.
    """

    def __init__(self, method: str, url: URL, **kwargs: Any) -> None:
        kwargs.setdefault('stream_writer', _SentRequestWriter())
        super().__init__(method, url, **kwargs)


@pytest.fixture
def mocked(monkeypatch: pytest.MonkeyPatch) -> Iterator[AioResponses]:
    """Mock each request of each `aiohttp.ClientSession`; no request reaches the network."""
    monkeypatch.setattr(aioresponses.core, 'ClientResponse', _MockResponse)
    with AioResponses() as m:
        yield m

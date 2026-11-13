"""Tests of the package itself: its exports and its constants."""

import gaggiuino_api
from gaggiuino_api.const import DEFAULT_BASE_URL, DEFAULT_TIMEOUT


def test_all_is_sorted_and_importable():
    assert gaggiuino_api.__all__ == sorted(gaggiuino_api.__all__)
    for name in gaggiuino_api.__all__:
        assert hasattr(gaggiuino_api, name)


def test_default_base_url_has_no_trailing_slash():
    assert DEFAULT_BASE_URL == "http://gaggiuino.local"
    assert DEFAULT_TIMEOUT > 0

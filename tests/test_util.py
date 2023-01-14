from datetime import datetime

import pytest

from unifs.util import (
    dtfromisoformat,
    get_first_match,
    humanize_bytes,
    is_binary_string,
)


def test_humanize_bytes():
    assert humanize_bytes(1001) == "1001B"
    assert humanize_bytes(1024) == "1024B"
    assert humanize_bytes(1025) == "1.0KB"
    assert humanize_bytes(1024 * 1.23) == "1.23KB"
    assert humanize_bytes(1024 * 1.4211) == "1.42KB"
    assert humanize_bytes(1024**2 + 1) == "1.0MB"
    assert humanize_bytes(1024**3 + 1) == "1.0GB"
    assert humanize_bytes(1024**4 + 1) == "1.0TB"


def test_is_binary_string():
    assert not is_binary_string(b"to be")
    assert not is_binary_string("être".encode("utf-8"))
    assert not is_binary_string("要".encode("utf-8"))
    assert is_binary_string(b"\x03")


def test_get_first_match():
    assert get_first_match({}, "foo") is None
    assert get_first_match({"foo": "bar"}, "baz") is None
    assert get_first_match({"foo": "bar"}, "baz", "qux") is None
    assert get_first_match({"foo": "bar"}, "baz", "qux", "foo") == "bar"
    assert get_first_match({"foo": "bar"}, "baz", "foo", "qux") == "bar"
    assert get_first_match({"foo": "bar", "qux": "fred"}, "baz", "foo", "qux") == "bar"


def test_dtfromisoformat():
    # TODO: test with Tox
    # NOTE: this test currently runs on Python 3.7
    assert dtfromisoformat("2023-01-14 19:25:00") == datetime(2023, 1, 14, 19, 25, 0)
    assert dtfromisoformat("2023-01-14 19:25:00Z") == datetime(2023, 1, 14, 19, 25, 0)
    with pytest.raises(ValueError):
        assert dtfromisoformat("broken")

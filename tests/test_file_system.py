from datetime import datetime

import fsspec

from unifs.file_system import get_current, get_mtime


def test_get_current():
    fs = get_current()
    assert isinstance(fs, fsspec.AbstractFileSystem)

    fs_same = get_current()
    assert fs is fs_same


def test_get_mtime():
    now = datetime.now()
    assert get_mtime({}) is None
    assert get_mtime({"mtime": now}) == now
    assert get_mtime({"mtime": now.timestamp()}) == now
    assert get_mtime({"mtime": now.isoformat()}) == now
    assert get_mtime({"mtime": "broken"}) is None

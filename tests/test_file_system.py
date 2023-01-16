from datetime import datetime

import pytest

from unifs.exceptions import FatalError
from unifs.file_system import FileSystemProxy, get_current, get_mtime


def test_file_system_proxy(test_fs):
    proxy = FileSystemProxy(test_fs)

    assert proxy.protocol == "memory", "attributes should not be proxied"
    assert "/text.txt" in proxy.ls("/"), "methods should be proxied"

    test_fs.set_raise_next(NotImplementedError("any message"))
    with pytest.raises(FatalError) as err:
        proxy.ls("/")
    assert str(err.value) == "ls is not implemented in this file system"

    test_fs.set_raise_next(FileNotFoundError("file not found"))
    with pytest.raises(FatalError) as err:
        proxy.ls("/")
    assert str(err.value) == "file not found"

    proxied_exception = Exception("random exception")
    test_fs.set_raise_next(proxied_exception)
    with pytest.raises(Exception) as err:
        proxy.ls("/")
    assert err.value is proxied_exception


def test_get_current():
    fs = get_current()
    assert isinstance(fs, FileSystemProxy)

    fs_same = get_current()
    assert fs is fs_same


def test_get_mtime():
    now = datetime.now()
    assert get_mtime({}) is None
    assert get_mtime({"mtime": now}) == now
    assert get_mtime({"mtime": now.timestamp()}) == now
    assert get_mtime({"mtime": now.isoformat()}) == now
    assert get_mtime({"mtime": "broken"}) is None

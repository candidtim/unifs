import inspect
import os
from datetime import datetime
from functools import wraps

import fsspec
import pytest
from fsspec.implementations.memory import MemoryFileSystem

from unifs import config, file_system


class TestFileSystem(MemoryFileSystem):
    """Same as fsspec MemoryFileSystem, but adds features required for tests"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raise_next = None

    # Simulate exceptions from the FileSystem methods:

    def set_raise_next(self, err: Exception):
        """Configure this file system implementation to raise an error"""
        self.raise_next = err

    def _with_maybe_error(self, fn):
        """Wraps a function to maybe raise the 'raise_next', if it is set"""

        @wraps(fn)
        def wrapper(*args, **kwargs):
            if self.raise_next is None:
                return fn(*args, **kwargs)
            else:
                err = self.raise_next
                self.raise_next = None
                raise err

        return wrapper

    def __getattribute__(self, name: str):
        """Wrap all methods into _with_maybe_error wrapper"""
        attr = super().__getattribute__(name)
        if inspect.ismethod(attr):
            return TestFileSystem._with_maybe_error(self, attr)
        else:
            return attr

    # .. end of error simulation

    def touch(self, path, truncate, **kwargs):
        if not self.exists(path):
            self.pipe_file(path, b"")

        path = self._strip_protocol(path)
        self.store[path].modified = datetime.utcnow()

    def info(self, *args, **kwargs):
        """Overrides mtime to simplify tests"""
        res = super().info(*args, **kwargs)
        res["mtime"] = datetime(2023, 1, 14, 19, 25, 0)
        return res

    def ls(self, *args, detail: bool = False, **kwargs):
        """Overrides mtime to simplify tests"""
        res = super().ls(*args, detail=detail, **kwargs)
        if detail:
            for file_info in res:
                file_info["mtime"] = datetime(2023, 1, 14, 19, 25, 0)
        return res


@pytest.fixture(autouse=True, scope="session")
def register_test_file_system():
    """Registers the TestFileSystem as a replacement for MemoryFileSystem"""
    fsspec.register_implementation("memory", TestFileSystem, clobber=True)


@pytest.fixture(autouse=True)
def test_config_path(tmp_path):
    """Sets an env var to point a config path to a temporary file used for
    tests only. Returns the path itself."""
    path = str(tmp_path / "unifs-test-config.toml")
    os.environ["UNIFS_CONFIG_PATH"] = path
    return path


@pytest.fixture(autouse=True)
def test_config(test_config_path):
    """Creates (overwites if exists) a test config file at
    `test_config_path`."""
    conf = config.Config(
        current="memory",
        activated=True,
        fs={
            "memory": {"protocol": "memory"},
            "memalt": {"protocol": "memory"},
            "broken": {"protocol": "thisprotocoldoesnotexist"},
        },
    )
    config.save(conf, test_config_path)
    return conf


@pytest.fixture
def test_fs():
    fs = file_system.get_current()
    fs.pipe_file("/text.txt", b"text file")  # 9B
    fs.pipe_file("/table.csv", b"CSV,file")  # 8B
    fs.pipe_file("/dir/file-in-dir.txt", b"file in a directory")  # 19B
    fs.pipe_file("/special/text-in-dir.txt", b"another text file")  # 17B
    fs.pipe_file("/special/file.bin", b"\x03")
    fs.pipe_file("/special/bigfile.txt", b"foobarbazx" * 1024)  # 10KB
    return fs

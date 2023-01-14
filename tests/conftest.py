import os
from datetime import datetime

import fsspec
import pytest
from fsspec.implementations.memory import MemoryFileSystem

from unifs import config, file_system


class TestFileSystem(MemoryFileSystem):
    """Same as fsspec MemoryFileSystem, but adds features required for tests"""

    # TODO: contribute back to fsspec
    def touch(self, path, truncate, **kwargs):
        path = self._strip_protocol(path)
        self.store[path].modified = datetime.utcnow()


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
def test_fs_content():
    fs = file_system.get_current()
    fs.pipe_file("/file1.txt", b"file1")
    fs.pipe_file("/file2.csv", b"file2")
    fs.pipe_file("/dir1/file3.txt", b"file3")
    fs.pipe_file("/dir2/file4.txt", b"file4")
    fs.pipe_file("/dir2/file5.bin", b"\x03")
    fs.pipe_file("/dir2/file6.txt", b"foobarbazx" * 1024)  # 10KB
    return fs

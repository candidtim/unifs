import os

import pytest

from unifs import config, file_system


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

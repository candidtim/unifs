import os

import pytest

from unifs import config
from unifs.exceptions import RecoverableError


def test_config():
    conf = config.Config(
        current="test-fs-1",
        fs={
            "test-fs-1": {
                "protocol": "test-protocol-1",
                "test_param_1": "test-param-1-value",
            },
            "test-fs-2": {
                "protocol": "test-protocol-2",
                "test_param_2": "test-param-2-value",
            },
        },
    )

    assert conf.current_fs_name == "test-fs-1"
    assert conf.current_fs_conf == {
        "protocol": "test-protocol-1",
        "test_param_1": "test-param-1-value",
    }
    assert conf.file_systems == ["test-fs-1", "test-fs-2"]

    assert conf.set_current_fs("test-fs-1") == conf
    assert conf.set_current_fs("test-fs-2").current_fs_name == "test-fs-2"

    with pytest.raises(RecoverableError) as err:
        conf.set_current_fs("unknown-fs")
    assert "unknown-fs" in str(err)


def make_config_file(dir_path, content):
    path = dir_path / "config.toml"
    with open(path, "w") as f:
        f.write(content)
    return path


def lstriplines(text):
    lines = text.splitlines()
    head = lines[1]
    lstrip_length = len(head) - len(head.lstrip())
    return "\n".join([line[lstrip_length:] for line in lines[1:]])


def test_load_corrupted_toml_file(tmp_path):
    path = make_config_file(tmp_path, '{"this is": "not a toml file"}')
    with pytest.raises(RecoverableError) as err:
        config.load(path)
    assert "Invalid statement" in str(err)


def test_load_invalid_toml_file(tmp_path):
    path = make_config_file(tmp_path, "[notunifs]")
    with pytest.raises(RecoverableError) as err:
        config.load(path)
    assert "missing the [unifs] section" in str(err)


def test_load_invalid_config_file_missing_property(tmp_path):
    path = make_config_file(tmp_path, "[unifs]")
    with pytest.raises(RecoverableError) as err:
        config.load(path)
    assert 'missing value for field "current"' in str(err)


def test_load_invalid_config_file_inconsistent_setup(tmp_path):
    path = make_config_file(
        tmp_path,
        lstriplines(
            """
            [unifs]
            current = "unknown-fs"

            [unifs.fs.test-fs]
            protocol = "test-protocol"
            """
        ),
    )
    with pytest.raises(RecoverableError) as err:
        config.load(path)
    assert "unknown-fs is not a configured file system" in str(err)


def test_load_invalid_config_file_missing_fs_params(tmp_path):
    path = make_config_file(
        tmp_path,
        lstriplines(
            """
            [unifs]
            current = "test-fs"

            [unifs.fs.test-fs]
            param = "test-param"
            """
        ),
    )
    with pytest.raises(RecoverableError) as err:
        config.load(path)
    assert "file system test-fs: 'protocol' is missing" in str(err)


def test_load_config_file(tmp_path):
    path = make_config_file(
        tmp_path,
        lstriplines(
            """
            [unifs]
            current = "test-fs"

            [unifs.fs.test-fs]
            protocol = "test-protocol"
            """
        ),
    )
    conf = config.load(path)
    assert conf.current_fs_name == "test-fs"
    assert conf.current_fs_conf["protocol"] == "test-protocol"


def test_save(tmp_path):
    path = tmp_path / "config.toml"
    conf = config.Config(
        current="test-fs",
        fs={"test-fs": {"protocol": "test-protocol"}},
    )
    config.save(conf, path)
    assert config.load(path) == conf


def test_ensure_config(tmp_path):
    path = tmp_path / "config.toml"
    config.ensure_config(path)
    conf = config.load(path)
    assert conf.current_fs_name == "local"
    assert conf.current_fs_conf["protocol"] == "file"

    last_mtime = os.stat(path).st_mtime_ns
    config.ensure_config(path)
    new_mtime = os.stat(path).st_mtime_ns
    assert new_mtime == last_mtime


def test_get():
    config.ensure_config(config.site_config_file_path())
    assert isinstance(config.get(), config.Config)
    assert config.get() is config.get()


def test_save_site_config():
    path = config.site_config_file_path()
    last_mtime = os.stat(path).st_mtime_ns

    conf = config.get()
    config.save_site_config(conf)

    assert config.get() is not conf
    assert os.stat(path).st_mtime_ns > last_mtime

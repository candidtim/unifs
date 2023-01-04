import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List

import appdirs
import tomli_w

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

DEFAULT_CONFIG = {
    "current": "local",
    "fs": {
        "protocol": "file",
        "auto_mkdir": False,
    },
}


@dataclass
class FileSystemConf:
    name: str
    params: Dict[str, str]


def path() -> str:
    return os.path.join(appdirs.user_config_dir("unifs"), "config.toml")


@lru_cache(maxsize=1)
def get() -> Dict[str, Any]:
    return _load_from_file()["unifs"]


def list_fs() -> List[str]:
    """List of configured file systems"""
    return list(get()["fs"].keys())


def set(name: str):
    if name not in list_fs():
        raise ValueError(f"{name} is not a configured file system")

    conf = get()
    conf["current"] = name
    _write_config(conf)
    get.cache_clear()
    current_fs.cache_clear()


@lru_cache(maxsize=1)
def current_fs():
    """Get the currently-active file system configuration"""
    # TODO: manage "corrupted" configs (parsing error, logically incorrect setup)
    conf = get()
    current_name = conf["current"]
    current_conf = conf["fs"][current_name]
    return FileSystemConf(name=current_name, params=current_conf)


def _load_from_file() -> Dict[str, Any]:
    """Load config from the default configuration file location. Will create a
    default config file as a side-effect, if none exists yet."""
    _ensure_conf()
    with open(path(), "rb") as f:
        return tomllib.load(f)


def _ensure_conf():
    """Creates a default config if none exists, does nothing otherwise."""
    if not os.path.exists(path()):
        _write_config(DEFAULT_CONFIG)


def _write_config(conf: Dict[str, Any]):
    """Write config to the deafult configuration file location."""
    parent_dir = os.path.dirname(path())
    os.makedirs(parent_dir, exist_ok=True)
    with open(path(), "wb") as f:
        tomli_w.dump({"unifs": conf}, f)

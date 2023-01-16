import os
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from typing import Dict, List, Union

import appdirs
import dacite
import tomli_w

from .exceptions import FatalError

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


PrimitiveType = Union[str, int, float, bool]


@dataclass(frozen=True)
class Config:
    current: str
    activated: bool
    fs: Dict[str, Dict[str, PrimitiveType]]

    @property
    def current_fs_name(self) -> str:
        return self.current

    @property
    def current_fs_conf(self) -> Dict[str, PrimitiveType]:
        return self.fs[self.current]

    @property
    def file_systems(self) -> List[str]:
        return list(self.fs.keys())

    def set_current_fs(self, name: str) -> "Config":
        if name not in self.fs.keys():
            raise FatalError(f"'{name}' is not a configured file system")
        return replace(self, current=name)

    @property
    def accepted_usage_terms(self) -> bool:
        return self.activated

    def set_accepted_usage_terms(self) -> "Config":
        return replace(self, activated=True)


@lru_cache(maxsize=1)
def get() -> Config:
    """Get the configuration from the default config file location"""
    return load(site_config_file_path())


def save_site_config(config: Config):
    """Persist the configuration to the default config file location"""
    save(config, site_config_file_path())
    get.cache_clear()


def site_config_file_path() -> str:
    """Platform-specific config file path"""
    return os.environ.get(
        "UNIFS_CONFIG_PATH",
        os.path.join(appdirs.user_data_dir("unifs"), "config.toml"),
    )


def load(path: str) -> Config:
    """Load config from the default configuration file location. Will create a
    default config file as a side-effect, if none exists yet."""

    with open(path, "rb") as f:
        try:
            file_data = tomllib.load(f)
        except tomllib.TOMLDecodeError as err:
            raise FatalError(f"Invalid config file: {str(err)}")

    if "unifs" in file_data:
        conf_data = file_data["unifs"]
    else:
        raise FatalError("Invalid config file: missing the [unifs] section")

    try:
        config = dacite.from_dict(
            data_class=Config,
            data=conf_data,
            config=dacite.Config(strict=True),
        )
    except dacite.exceptions.DaciteError as err:
        raise FatalError(f"Invalid config file: {str(err)}")

    if config.current not in config.fs.keys():
        raise FatalError(
            f"Invalid config file: {config.current} is not a configured file system"
        )

    for fs_name, fs_conf in config.fs.items():
        if "protocol" not in fs_conf:
            raise FatalError(
                f"Invalid config file: file system {fs_name}: 'protocol' is missing"
            )

    return config


def save(conf: Config, path: str):
    """Write config to the file"""

    parent_dir = os.path.dirname(path)
    os.makedirs(parent_dir, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump({"unifs": asdict(conf)}, f)


def ensure_config(path: str):
    """Creates a default config file, if none exists"""
    if os.path.exists(path):
        return

    default_config = Config(
        current="local",
        activated=False,
        fs={
            "local": {
                "protocol": "file",
                "auto_mkdir": False,
            }
        },
    )
    save(default_config, path)

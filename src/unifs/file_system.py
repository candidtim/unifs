from typing import Dict

import fsspec

from . import config

_fs_cache: Dict[str, fsspec.AbstractFileSystem] = {}


def get_current():
    fs_name = config.get().current_fs_name
    if fs_name not in _fs_cache:
        _fs_cache[fs_name] = fsspec.filesystem(**config.get().current_fs_conf)
    return _fs_cache[fs_name]

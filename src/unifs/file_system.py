from typing import Dict

import fsspec

from . import config

_fs_cache: Dict[str, fsspec.AbstractFileSystem] = {}


def get_current():
    fs_conf = config.current_fs()
    if fs_conf.name not in _fs_cache:
        _fs_cache[fs_conf.name] = fsspec.filesystem(**fs_conf.params)
    return _fs_cache[fs_conf.name]

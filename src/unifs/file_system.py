from typing import Optional, Tuple

import fsspec

from . import config

_current: Optional[Tuple[str, fsspec.AbstractFileSystem]] = None


def get_current():
    global _current

    fs_conf = config.current_fs()
    if _current is None or _current[0] != fs_conf.name:
        _current = (fs_conf.name, fsspec.filesystem(**fs_conf.params))

    return _current[1]

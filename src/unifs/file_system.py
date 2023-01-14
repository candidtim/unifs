from datetime import datetime
from typing import Any, Dict, Optional

import fsspec

from . import config
from .util import dtfromisoformat, get_first_match

_fs_cache: Dict[str, fsspec.AbstractFileSystem] = {}


def get_current():
    fs_name = config.get().current_fs_name
    if fs_name not in _fs_cache:
        _fs_cache[fs_name] = fsspec.filesystem(**config.get().current_fs_conf)
    return _fs_cache[fs_name]


def get_mtime(file_info: Dict[str, Any]) -> Optional[datetime]:
    """Attempt to extract the mtime form the file_info, parse it and return a
    datetime.datetime instance. Attempts to handle differences of various file
    system implementations and returns None if the mtime cannot be reliably
    extracted."""
    mtime = get_first_match(
        file_info, "mtime", "LastModified", "last_modified", "updated"
    )
    if type(mtime) == datetime:
        result = mtime
    elif type(mtime) == float:
        result = datetime.fromtimestamp(mtime)  # type: ignore
    elif type(mtime) == str:
        try:
            result = dtfromisoformat(mtime)  # type: ignore
        except ValueError:
            result = None
    else:
        result = None
    return result

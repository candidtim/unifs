import inspect
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

import fsspec

from . import config
from .exceptions import FatalError
from .util import dtfromisoformat, get_first_match

_fs_cache: Dict[str, fsspec.AbstractFileSystem] = {}


class FileSystemProxy:
    """Wraps raw file system implementations to add generic features. In
    particular, adds error handling."""

    # FIXME: normalize file_info here? (in list, info, and even glob?)

    def __init__(self, fs: fsspec.AbstractFileSystem):
        self._fs = fs

    @classmethod
    def _with_error_handling(cls, fn):
        """Wraps a function to handle the commonly-seen excpetions that may be
        raised by fsspec implementation, in order to handle them consistently
        between the implementations."""

        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except NotImplementedError:
                raise FatalError(
                    f"{fn.__name__} is not implemented in this file system"
                )
            except FileNotFoundError as err:
                msg = cls._friendly_message(err, "found", "File not found")
                raise FatalError(msg)
            except FileExistsError as err:
                msg = cls._friendly_message(err, "exists", "File exists")
                raise FatalError(msg)
            except IsADirectoryError as err:
                msg = cls._friendly_message(err, "directory", "Is a directory")
                raise FatalError(msg)
            except NotADirectoryError as err:
                msg = cls._friendly_message(err, "directory", "Not a directory")
                raise FatalError(msg)
            except OSError as err:
                raise FatalError(str(err))

        return wrapper

    @classmethod
    def _friendly_message(cls, err: Exception, cue: str, prefix: str) -> str:
        """Some implementations raise "semantic errors" where an error class
        indicates an issue, and the message contains only the problematic file
        path. Attempting to make a message user-friendly by prefixing a text if
        the expected cue is not found in the message already."""
        # NOTE: incorrect cue detections are possible if the problematic file
        # path contains the cue, or if the error messages doesn't contain the
        # exact cue expected; users of this function should prefer latter (will
        # add a superfluous prefix).
        msg = str(err)
        return msg if cue in msg.lower() else f"{prefix}: {msg}"

    def __getattr__(self, name: str):
        """Applies the error handling wrapper to all methods. See
        _with_error_handling."""
        attr = getattr(self._fs, name)
        if inspect.ismethod(attr) or inspect.isfunction(attr):
            return FileSystemProxy._with_error_handling(attr)
        else:
            return attr


def get_current() -> FileSystemProxy:
    """Get the file system instance that corresponds to the currently active
    user configuration."""
    fs_name = config.get().current_fs_name
    if fs_name not in _fs_cache:
        fs_impl = fsspec.filesystem(**config.get().current_fs_conf)
        _fs_cache[fs_name] = FileSystemProxy(fs_impl)
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

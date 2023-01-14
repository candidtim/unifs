import sys
from datetime import datetime
from typing import Dict, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


def humanize_bytes(size):
    """Human-readable format for the file size."""
    power = 1024
    n = 0
    while size > power:
        size /= power
        n += 1
    size = round(size, 2)
    label = ["B", "KB", "MB", "GB", "TB"][n]
    return f"{size}{label}"


def is_binary_string(bb: bytes):
    """Guess if the given byte array is a binary string (as opposed to the
    text). Based on 'file' behavior (see file(1) man). Many thanks to this SO
    answer: https://stackoverflow.com/a/7392391/302343"""
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    return bool(bb.translate(None, textchars))


def get_first_match(d: Dict[K, V], *keys: K) -> Optional[V]:
    """Search for a first matching key in the dict and return the value of the
    matching item. Return None if none of the requested keys are found."""
    for k in keys:
        if k in d:
            return d[k]
    return None


def dtfromisoformat(s: str) -> datetime:
    """Same as datetime.datetime.fromisoformat, but backward-compatible with
    Python <3.11 to support formats ending with Z"""
    if sys.version_info.major == 3 and sys.version_info.minor < 11:
        if s[-1] == "Z" or s[-1] == "z":
            s = s[:-1]
    return datetime.fromisoformat(s)

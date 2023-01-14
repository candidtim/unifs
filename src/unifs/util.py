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

def humanize_bytes(size):
    """Human-readable format for the file size."""
    power = 2**10
    n = 0
    while size > power:
        size /= power
        n += 1
    size = round(size, 2)
    label = ["B", "KB", "MB", "GB", "TB"][n]
    return f"{size}{label}"

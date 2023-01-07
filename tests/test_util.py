from unifs.util import humanize_bytes


def test_humanize_bytes():
    assert humanize_bytes(1001) == "1001B"
    assert humanize_bytes(1024) == "1024B"
    assert humanize_bytes(1025) == "1.0KB"
    assert humanize_bytes(1024 * 1.23) == "1.23KB"
    assert humanize_bytes(1024 * 1.4211) == "1.42KB"
    assert humanize_bytes(1024**2 + 1) == "1.0MB"
    assert humanize_bytes(1024**3 + 1) == "1.0GB"
    assert humanize_bytes(1024**4 + 1) == "1.0TB"

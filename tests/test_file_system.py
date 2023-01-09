import fsspec

from unifs.file_system import get_current


def test_get_current():
    fs = get_current()
    assert isinstance(fs, fsspec.AbstractFileSystem)

    fs_same = get_current()
    assert fs is fs_same

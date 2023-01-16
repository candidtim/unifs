from unifs.logging import _log_exception


def test_log_exception(tmp_path):
    tmp_file_path = str(tmp_path / "error.log")

    try:
        raise Exception("test")
    except Exception:
        _log_exception("comment", tmp_file_path)

    with open(tmp_file_path, "r") as f:
        content = f.read()

    assert "comment" in content
    assert "Exception" in content
    assert "test" in content

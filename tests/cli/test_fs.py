import traceback

from click.testing import CliRunner

from unifs.cli import fs


def invoke(cmd, *args, **kwargs):
    runner = CliRunner()
    result = runner.invoke(cmd, args, **kwargs)
    if result.exception is not None:
        e = result.exception
        traceback.print_exception(type(e), e, e.__traceback__)
    assert result.exit_code == 0
    return result.output


def test_list_dir(test_fs):
    output = invoke(fs.ls, "/")
    assert "/text.txt" in output
    assert "/table.csv" in output
    assert "/dir/" in output
    assert "/special/" in output


def test_list_dir_long(test_fs):
    output = invoke(fs.ls, "-l", "/")
    assert "fil         9B 2023-01-14 19:25:00 /text.txt" in output
    assert "fil         8B 2023-01-14 19:25:00 /table.csv" in output
    assert "dir         0B 2023-01-14 19:25:00 /dir/" in output
    assert "dir         0B 2023-01-14 19:25:00 /special/" in output
    assert "file-in-dir.txt" not in output


def test_list_file_long(test_fs):
    output = invoke(fs.ls, "-l", "/text.txt")
    assert "fil         9B 2023-01-14 19:25:00 /text.txt" == output.strip()


def test_list_glob(test_fs):
    output = invoke(fs.ls, "*.txt")
    assert "text.txt" in output
    assert "table.csv" not in output

    output = invoke(fs.ls, "**/*.txt")
    assert "text.txt" not in output
    assert "table.csv" not in output
    assert "/dir/file-in-dir.txt" in output
    assert "/special/text-in-dir.txt" in output


def test_list_glob_long(test_fs):
    output = invoke(fs.ls, "-l", "/**/*.txt", input="y\n")
    assert "Continue?" in output
    assert "fil        19B 2023-01-14 19:25:00 /dir/file-in-dir.txt" in output
    assert "fil        17B 2023-01-14 19:25:00 /special/text-in-dir.txt" in output

    output = invoke(fs.ls, "-l", "/**/*.txt", input="n\n")
    assert "Continue?" in output
    assert "file-in-dir.txt" not in output


def test_ll(test_fs):
    output = invoke(fs.ll, "/text.txt")
    assert "fil         9B 2023-01-14 19:25:00 /text.txt" in output


def test_cat(test_fs):
    output = invoke(fs.cat, "/non-existing.txt")
    assert "No such file" == output.strip()

    output = invoke(fs.cat, "/dir")
    assert "No such file" == output.strip()

    output = invoke(fs.cat, "/special/bigfile.txt", input="y\n")
    assert "Are you sure?" in output
    assert "foobarbazx" in output

    output = invoke(fs.cat, "/special/bigfile.txt", input="n\n")
    assert "Are you sure?" in output
    assert "foobarbazx" not in output

    output = invoke(fs.cat, "/special/file.bin", input="y\n")
    assert "Continue?" in output
    assert b"\x03" in output.encode("ascii")

    output = invoke(fs.cat, "/special/file.bin", input="n\n")
    assert "Continue?" in output
    assert b"\x03" not in output.encode("ascii")


def test_head(test_fs):
    output = invoke(fs.head, "/non-existing.txt")
    assert "No such file" == output.strip()

    output = invoke(fs.head, "/special/bigfile.txt", "--bytes=3")
    assert "foo" == output.strip()


def test_tail(test_fs):
    output = invoke(fs.tail, "/non-existing.txt")
    assert "No such file" == output.strip()

    output = invoke(fs.tail, "/special/bigfile.txt", "--bytes=4")
    assert "bazx" == output.strip()


def test_touch(test_fs):
    prev_content = test_fs.cat("/text.txt")
    prev_mtime = test_fs.modified("/text.txt")
    invoke(fs.touch, "/text.txt")
    new_content = test_fs.cat("/text.txt")
    new_mtime = test_fs.modified("/text.txt")
    assert new_content == prev_content
    assert new_mtime > prev_mtime

    invoke(fs.touch, "/special/touch.txt")
    content = test_fs.cat("/special/touch.txt")
    assert len(content) == 0

    test_fs.set_raise_next(FileNotFoundError("not found"))
    output = invoke(fs.touch, "/newdir/touch.txt")
    assert "not found" == output.strip()

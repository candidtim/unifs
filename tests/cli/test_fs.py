from click.testing import CliRunner

from unifs.cli import fs


def invoke(cmd, *args, **kwargs):
    runner = CliRunner()
    result = runner.invoke(cmd, args, **kwargs)
    assert result.exit_code == 0
    return result.output


def test_list_dir(test_fs_content):
    output = invoke(fs.ls, "/")
    assert "/file1.txt" in output
    assert "/file2.csv" in output
    assert "/dir1/" in output
    assert "/dir2/" in output


def test_list_dir_long(test_fs_content):
    output = invoke(fs.ls, "-l", "/")
    assert "fil         5B /file1.txt" in output
    assert "fil         5B /file2.csv" in output
    assert "dir         0B /dir1/" in output
    assert "dir         0B /dir2/" in output
    assert "file3.txt" not in output


def test_list_dir_file_long(test_fs_content):
    output = invoke(fs.ls, "-l", "/file1.txt")
    assert "fil         5B /file1.txt" == output.strip()


def test_list_glob(test_fs_content):
    output = invoke(fs.ls, "*.txt")
    assert "file1.txt" in output
    assert "file2.csv" not in output

    output = invoke(fs.ls, "**/*.txt")
    assert "file1.txt" not in output
    assert "file2.csv" not in output
    assert "/dir1/file3.txt" in output
    assert "/dir2/file4.txt" in output


def test_list_glob_long(test_fs_content):
    output = invoke(fs.ls, "-l", "/**/*.txt", input="y\n")
    assert "Continue?" in output
    assert "fil         5B /dir1/file3.txt" in output
    assert "fil         5B /dir2/file4.txt" in output

    output = invoke(fs.ls, "-l", "/**/*.txt", input="n\n")
    assert "Continue?" in output
    assert "file3.txt" not in output


def test_cat(test_fs_content):
    output = invoke(fs.cat, "/non-existing.txt")
    assert "No such file" == output.strip()

    output = invoke(fs.cat, "/dir1")
    assert "No such file" == output.strip()

    output = invoke(fs.cat, "/dir2/file6.txt", input="y\n")
    assert "Are you sure?" in output
    assert "foobarbazx" in output

    output = invoke(fs.cat, "/dir2/file6.txt", input="n\n")
    assert "Are you sure?" in output
    assert "foobarbazx" not in output

    output = invoke(fs.cat, "/dir2/file5.bin", input="y\n")
    assert "Continue?" in output
    assert b"\x03" in output.encode("ascii")

    output = invoke(fs.cat, "/dir2/file5.bin", input="n\n")
    assert "Continue?" in output
    assert b"\x03" not in output.encode("ascii")


def test_head(test_fs_content):
    output = invoke(fs.head, "/non-existing.txt")
    assert "No such file" == output.strip()

    output = invoke(fs.head, "/dir2/file6.txt", "--bytes=3")
    assert "foo" == output.strip()


def test_tail(test_fs_content):
    output = invoke(fs.tail, "/non-existing.txt")
    assert "No such file" == output.strip()

    output = invoke(fs.tail, "/dir2/file6.txt", "--bytes=4")
    assert "bazx" == output.strip()

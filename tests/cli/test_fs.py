import traceback

from click.testing import CliRunner

from unifs.cli import fs


def invoke(cmd, *args, expected_exit_code: int = 0, **kwargs):
    runner = CliRunner()
    result = runner.invoke(cmd, args, **kwargs)
    if result.exception is not None:
        e = result.exception
        traceback.print_exception(type(e), e, e.__traceback__)
    assert result.exit_code == expected_exit_code
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
    output = invoke(fs.cat, "/text.txt")
    assert "text file" == output.strip()

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
    test_fs.rm("/special/touch.txt")


def test_rm_single_file(test_fs):
    test_fs.touch("/file.txt", truncate=False)
    invoke(fs.rm, "/file.txt", input="n\n")
    assert test_fs.isfile("/file.txt")

    test_fs.touch("/file.txt", truncate=False)
    invoke(fs.rm, "/file.txt", input="y\n")
    assert not test_fs.isfile("/file.txt")

    test_fs.touch("/file.txt", truncate=False)
    invoke(fs.rm, "-f", "/file.txt")
    assert not test_fs.isfile("/file.txt")


def test_rm_empty_dir(test_fs):
    test_fs.mkdir("/toremove")
    invoke(fs.rm, "/toremove", input="n\n")
    assert test_fs.isdir("/toremove")

    invoke(fs.rm, "/toremove", input="y\n")
    assert not test_fs.isdir("/toremove")

    test_fs.mkdir("/toremove")
    invoke(fs.rm, "-f", "/toremove")
    assert not test_fs.isdir("/toremove")


def test_rm_dir(test_fs):
    test_fs.mkdir("/toremove")
    test_fs.touch("/toremove/file.txt", truncate=False)
    output = invoke(fs.rm, "/toremove", input="y\n", expected_exit_code=1)
    assert "not empty" in output
    assert test_fs.isfile("/toremove/file.txt")

    output = invoke(fs.rm, "-f", "/toremove", expected_exit_code=1)
    assert "not empty" in output
    assert test_fs.isfile("/toremove/file.txt")

    output = invoke(fs.rm, "-r", "/toremove", input="y\ny\n")
    assert "Remove /toremove/file.txt?" in output
    assert "Remove /toremove?" in output
    assert not test_fs.isdir("/toremove")

    test_fs.mkdir("/toremove")
    test_fs.touch("/toremove/file.txt", truncate=False)
    output = invoke(fs.rm, "-rf", "/toremove")
    assert output == ""
    assert not test_fs.isdir("/toremove")


def test_rm_glob_files(test_fs):
    def given_some_files():
        test_fs.touch("/file1.txt", truncate=False)
        test_fs.touch("/file2.txt", truncate=False)
        test_fs.touch("/text.txt", truncate=False)

    def assert_matching_files_removed():
        assert not test_fs.isfile("/file1.txt")
        assert not test_fs.isfile("/file2.txt")
        assert test_fs.isfile("/text.txt")

    given_some_files()
    output = invoke(fs.rm, "/file?.txt", input="y\ny\n")
    assert "Remove /file1.txt?" in output
    assert "Remove /file2.txt?" in output
    assert_matching_files_removed()

    given_some_files()
    output = invoke(fs.rm, "-f", "/file?.txt")
    assert output.strip() == ""
    assert_matching_files_removed()


def test_rm_glob_dirs(test_fs):
    def given_some_files():
        test_fs.makedirs("/dir", exist_ok=True)
        test_fs.touch("/dir/file-in-dir.txt", truncate=False)
        test_fs.makedirs("/empty-dir", exist_ok=True)
        test_fs.touch("/file-in-root.txt", truncate=False)

    def assert_matching_files_removed():
        assert not test_fs.isdir("/dir")
        assert not test_fs.isdir("/empty-dir")
        assert test_fs.isfile("/file-in-root.txt")

    given_some_files()
    # missing -r option:
    output = invoke(fs.rm, "/*dir", input="y\ny\n", expected_exit_code=1)
    assert "Directory not empty" in output
    assert test_fs.isdir("/dir")
    assert test_fs.isfile("/dir/file-in-dir.txt")

    given_some_files()
    output = invoke(fs.rm, "-r", "/*dir", input="y\ny\ny\n")
    assert "Remove /dir/file-in-dir.txt?" in output
    assert "Remove /dir?" in output
    assert "Remove /empty-dir?" in output
    assert_matching_files_removed()

    given_some_files()
    output = invoke(fs.rm, "-rf", "/*dir")
    assert output.strip() == ""
    assert_matching_files_removed()


def test_mkdir(test_fs):
    invoke(fs.mkdir, "/newdir-1")
    assert test_fs.isdir("/newdir-1")

    invoke(fs.mkdir, "-p", "/newdir-2/subdir")
    assert test_fs.isdir("/newdir-2/subdir")

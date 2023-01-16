import click
from click.testing import CliRunner

from unifs.exceptions import FatalError, RecoverableError
from unifs.logging import _log_file_path
from unifs.tui import errorhandler, format_table


def test_format_table():
    output = format_table(
        header=["FOO", "BAR", "BAZZZ"],
        widths=[10, 5, 5],
        rows=[
            ("Hello", 42, None),
            ("What a wonderful world", 75014, False),
        ],
    )
    assert (
        output
        == """
FOO       BAR  B...
Hello     42
What a... 7... F...
""".strip()
    )


def test_errorhandler():
    @click.command()
    @errorhandler
    def raises_recoverabe_error():
        raise RecoverableError("be cool")

    runner = CliRunner()
    result = runner.invoke(raises_recoverabe_error)
    assert result.exit_code == 0
    assert result.output.strip() == "be cool"

    @click.command()
    @errorhandler
    def raises_fatal_error():
        raise FatalError("fail fast")

    runner = CliRunner()
    result = runner.invoke(raises_fatal_error)
    assert result.exit_code == 1
    assert result.output.strip() == "fail fast"

    @click.command()
    @errorhandler
    def raises_unexpected_exception():
        raise Exception("expect the unexpected")

    runner = CliRunner()
    result = runner.invoke(raises_unexpected_exception)
    assert result.exit_code == 2
    assert "expect the unexpected" in result.output
    with open(_log_file_path(), "r") as log_file:
        log_content = log_file.read()
        assert "expect the unexpected" in log_content

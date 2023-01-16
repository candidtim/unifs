import re

from click.testing import CliRunner

from unifs.cli.impl import impl


def test_list():
    runner = CliRunner()
    result = runner.invoke(impl, ["list"])
    assert result.exit_code == 0
    assert "file" in result.output
    assert "http" in result.output
    assert "git" in result.output
    assert "smb" in result.output


def test_info():
    runner = CliRunner()
    result = runner.invoke(impl, ["info", "ftp"])
    assert result.exit_code == 0
    assert 'protocol = "ftp"' in result.output


def test_info_missing_requirements():
    runner = CliRunner()
    result = runner.invoke(impl, ["info", "http"])
    assert result.exit_code == 0
    assert re.search("requires .* to be installed", result.output) is not None

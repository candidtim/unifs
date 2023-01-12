from click.testing import CliRunner

from unifs.cli import conf


def test_path():
    runner = CliRunner()
    result = runner.invoke(conf.path)
    assert result.exit_code == 0
    assert "config.toml" in result.output


def test_list():
    runner = CliRunner()
    result = runner.invoke(conf.list)
    assert result.exit_code == 0
    assert "local" in result.output

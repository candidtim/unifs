import re

from click.testing import CliRunner

from unifs.cli.conf import conf


def assert_output_contains(regexp: str, invoke_result):
    assert re.search(regexp, invoke_result.output) is not None


def test_path(test_config_path):
    runner = CliRunner()
    result = runner.invoke(conf, ["path"])
    assert result.exit_code == 0
    assert result.output.strip() == test_config_path


def test_list(test_config):
    runner = CliRunner()
    result = runner.invoke(conf, ["list"])
    assert result.exit_code == 0
    for name in test_config.file_systems:
        assert name in result.output


def test_use():
    runner = CliRunner()
    list_result = runner.invoke(conf, ["list"])
    assert_output_contains("\\*.*memory", list_result)

    use_result = runner.invoke(conf, ["use", "memalt"])
    assert "memalt" in use_result.output
    list_result = runner.invoke(conf, ["list"])
    assert_output_contains("\\*.*memalt", list_result)

    use_result = runner.invoke(conf, ["use", "nonexistingfs"])
    assert "'nonexistingfs' is not a configured file system" in use_result.output
    list_result = runner.invoke(conf, ["list"])
    assert_output_contains("\\*.*memalt", list_result)

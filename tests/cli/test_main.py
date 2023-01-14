import os

import pytest
from click.testing import CliRunner

from unifs import config
from unifs.cli import main


@pytest.fixture
def clear_config(test_config_path):
    os.remove(test_config_path)
    config.get.cache_clear()
    yield
    config.get.cache_clear()


def test_main_ensure_config(clear_config, test_config_path):
    runner = CliRunner()
    runner.invoke(main.cli, ["conf", "path"])
    assert os.path.exists(test_config_path)


def test_main_accept_terms(clear_config):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["conf", "path"], input="y\n")
    assert result.exit_code == 0
    assert "Do you agree?" in result.output


def test_main_do_not_accept_terms(clear_config):
    runner = CliRunner()
    result = runner.invoke(main.cli, ["conf", "path"], input="\n")
    assert result.exit_code == 81
    assert "Do you agree?" in result.output


def test_main_no_terms_prompt_second_time(clear_config):
    runner = CliRunner()

    result = runner.invoke(main.cli, ["conf", "path"], input="y\n")
    assert result.exit_code == 0
    assert "Do you agree?" in result.output

    result = runner.invoke(main.cli, ["conf", "path"])
    assert result.exit_code == 0
    assert "Do you agree?" not in result.output

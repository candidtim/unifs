import os

from click.testing import CliRunner

from unifs.cli import main


def test_main(test_config_path):
    os.remove(test_config_path)
    runner = CliRunner()
    result = runner.invoke(main.cli, ["conf", "list"])
    assert result.exit_code == 0
    assert os.path.exists(test_config_path)

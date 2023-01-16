import click

from .. import config
from ..tui import errorhandler, format_table
from .main import cli


@cli.group
def conf():
    """Change the application configuration settings"""
    pass


@conf.command(help="Show the configuration file location")
@errorhandler
def path():
    click.echo(config.site_config_file_path())


@conf.command(help="List configured file systems")
@errorhandler
def list():
    headers = ["CURRENT", "NAME"]
    widths = [8, 80]
    rows = []

    current_fs_name = config.get().current_fs_name
    for fs_name in config.get().file_systems:
        tag = "*" if fs_name == current_fs_name else ""
        rows.append([tag, fs_name])

    click.echo(format_table(headers, widths, rows))


@conf.command(help="Switch the active file system")
@click.argument("name")
@errorhandler
def use(name):
    new_conf = config.get().set_current_fs(name)
    config.save_site_config(new_conf)
    new_fs_name = config.get().current_fs_name
    click.echo(f"Current active file system: {new_fs_name}")

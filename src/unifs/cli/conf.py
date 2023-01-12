import click

from .. import config
from ..exceptions import RecoverableError
from .main import cli


@cli.group
def conf():
    """Change the application configuration settings"""
    pass


@conf.command(help="Show the configuration file location")
def path():
    click.echo(config.site_config_file_path())


@conf.command(help="List configured file systems")
def list():
    current_fs_name = config.get().current_fs_name
    click.echo("CURRENT\tNAME")
    for fs_name in config.get().file_systems:
        tag = "*" if fs_name == current_fs_name else ""
        click.echo(f"{tag}\t{fs_name}")


@conf.command(help="Switch the active file system")
@click.argument("name")
def use(name):
    try:
        new_conf = config.get().set_current_fs(name)
        config.save_site_config(new_conf)
    except RecoverableError as err:
        click.echo(str(err))
    else:
        new_fs_name = config.get().current_fs_name
        click.echo(f"Current active file system: {new_fs_name}")

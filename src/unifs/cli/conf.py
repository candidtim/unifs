import sys

import click

from .. import config
from .main import cli


@cli.group
def conf():
    """Change the application configuration settings"""
    pass


@conf.command(help="Show the configuration file location")
def path():
    click.echo(config.path())


@conf.command(help="List configured file systems")
def list():
    active = config.current_fs().name
    click.echo("CURRENT\tNAME")
    for name in config.list_fs():
        tag = "*" if name == active else ""
        click.echo(f"{tag}\t{name}")


@conf.command(help="Switch the active file system")
@click.argument("name")
def use(name):
    if name not in config.list_fs():
        click.echo(f"{name} is not a configured file system; use `conf list`")
        sys.exit(80)
    config.set(name)
    click.echo(f"Current active file system: {name}")

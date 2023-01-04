import inspect
import sys

import click
from fsspec.registry import get_filesystem_class, known_implementations

from .main import cli

IGNORED_IMPLEMENTATIONS = [
    "memory",
    "cached",
    "blockcache",
    "filecache",
    "simplecache",
    "reference",
    "generic",
]


@cli.group
def impl():
    """Get information about known file system implementations"""
    pass


@impl.command(help="List known file system implementations")
def list():
    click.echo(f"{'PROTOCOL':<15}REQUIREMENTS (if not available by default)")
    for key in known_implementations:
        if key in IGNORED_IMPLEMENTATIONS:
            continue
        note = known_implementations[key].get("err", "")
        click.echo(f"{key:<15}{note}")


@impl.command(help="Show details about a given file system implementation")
@click.argument("name")
def info(name):
    try:
        cls = get_filesystem_class(name)
    except (ImportError, ValueError) as err:
        click.echo(str(err))
        sys.exit(80)

    click.echo("Implementation notes")
    click.echo("=======================================")
    click.echo(cls.__doc__)

    click.echo("Parameters (and default values, if any)")
    click.echo("=======================================")
    click.echo(f"{'NAME':<30}DEFAULT")
    params = inspect.signature(cls.__init__).parameters.values()
    for param in params:
        if param.name not in ("self", "kwargs", "**kwargs"):
            default = "" if param.default == inspect.Parameter.empty else param.default
            click.echo(f"{param.name:<30}{default}")

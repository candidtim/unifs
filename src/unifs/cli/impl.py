import inspect
import sys

import click
import tomli_w
from fsspec.registry import get_filesystem_class, known_implementations

from ..tui import format_table
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
    headers = ["PROTOCOL", "REQUIREMENTS (if not available by default)"]
    widths = [15, 120]
    rows = []

    for key in known_implementations:
        if key in IGNORED_IMPLEMENTATIONS:
            continue
        note = known_implementations[key].get("err", "")
        rows.append([key, note])

    click.echo(format_table(headers, widths, rows))


@impl.command(help="Show details about a given file system implementation")
@click.argument("name")
def info(name):
    try:
        cls = get_filesystem_class(name)
    except (ImportError, ValueError) as err:
        click.echo(str(err))
        sys.exit(80)

    click.echo("Description")
    click.echo("===========")
    click.echo(cls.__doc__)
    click.echo("")

    click.echo("Sample configuration")
    click.echo("====================")
    params = inspect.signature(cls.__init__).parameters.values()
    sample_fs_config = {"unifs.fs.MYFSNAME": {"protocol": name}}
    for param in params:
        if param.name not in ("self", "kwargs", "**kwargs"):
            default = "" if param.default == inspect.Parameter.empty else param.default
            if default is None:
                default = ""
            sample_fs_config["unifs.fs.MYFSNAME"][param.name] = default
    click.echo(tomli_w.dumps(sample_fs_config))

import inspect

import click
import tomli_w
from fsspec.registry import get_filesystem_class, known_implementations

from ..exceptions import RecoverableError
from ..tui import errorhandler, format_table
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
@errorhandler
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
@errorhandler
def info(name):
    try:
        cls = get_filesystem_class(name)
    except (ImportError, ValueError) as err:
        raise RecoverableError(str(err))

    click.echo("Description")
    click.echo("===========")
    click.echo(cls.__doc__)
    click.echo("")

    def acceptable_param(param):
        is_param = param.name not in ("self", "kwargs", "**kwargs")
        toml_ok = type(param.default) in (type(None), str, int, float, bool, list, dict)
        return is_param and toml_ok

    click.echo("Sample configuration")
    click.echo("====================")
    params = inspect.signature(cls.__init__).parameters.values()
    sample_fs_config = {"unifs.fs.MYFSNAME": {"protocol": name}}
    for param in params:
        if acceptable_param(param):
            default = "" if param.default == inspect.Parameter.empty else param.default
            if default is None:
                default = ""
            sample_fs_config["unifs.fs.MYFSNAME"][param.name] = default
    click.echo(tomli_w.dumps(sample_fs_config))

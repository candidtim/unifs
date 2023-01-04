from typing import Any, Dict

import click

from .. import file_system
from .main import cli


def format_bytes(size):
    """Human-readable format for the file size."""
    power = 2**10
    n = 0
    while size > power:
        size /= power
        n += 1
    size = round(size, 2)
    label = ["B", "KB", "MB", "GB", "TB"][n]
    return f"{size}{label}"


def format_long(file_info: Dict[str, Any]) -> str:
    """Format fsspec file info dict to a string, in a safe manner (assumes that
    fsspec implementations may not respect the specification for the file info
    format)."""
    name = file_info.get("name", "???")
    size = file_info.get("size", 0)
    node_type = file_info.get("type", "???")
    size_str = format_bytes(size) if size is not None else "-"
    return f"{node_type[:3]:<5}{size_str:<10}{name}"


@cli.command
@click.option(
    "-l",
    "--long",
    is_flag=True,
    show_default=False,
    default=False,
    help="Use long output format (provides more details)",
)
@click.argument("path")
def ls(path, long):
    fs = file_system.get_current()
    fmt_fn = format_long if long else lambda x: x
    for item in fs.ls(path, detail=long):
        click.echo(fmt_fn(item))


@cli.command
def cat():
    click.echo("Not yet implemented")


@cli.command
def cp():
    click.echo("Not yet implemented")


@cli.command
def mv():
    click.echo("Not yet implemented")


@cli.command
def download():
    click.echo("Not yet implemented")


@cli.command
def upload():
    click.echo("Not yet implemented")

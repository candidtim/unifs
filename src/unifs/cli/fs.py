import glob
import os
from typing import Any, Dict

import click

from .. import file_system
from ..util import humanize_bytes, is_binary_string
from .main import cli


def format_long(file_info: Dict[str, Any]) -> str:
    """Format fsspec file info dict to a string, in a safe manner (assumes that
    some implementations may not respect the specification for the file info
    format)."""
    name = os.path.normpath(file_info.get("name", "???"))
    size = file_info.get("size", 0)
    node_type = file_info.get("type", "???")[:3]
    is_dir = node_type == "dir"
    if is_dir:
        name = name + "/"
    size_str = humanize_bytes(size) if size is not None else "-"
    return f"{node_type:<3} {size_str:>10} {name}"


def format_short(file_info: Dict[str, Any]) -> str:
    """Appends '/' to dir names, keeps file names as-is"""
    name = os.path.normpath(file_info.get("name", "???"))
    is_dir = file_info.get("type", "???")[:3] == "dir"
    if is_dir:
        name = name + "/"
    return name


@cli.command(help="List files in a directory, and optionally their details")
@click.option(
    "-l",
    "--long",
    is_flag=True,
    show_default=False,
    default=False,
    help="Use long output format (provides more details)",
)
@click.argument("path", default=".")
def ls(path, long):
    fs = file_system.get_current()
    is_glob = glob.escape(path) != path
    if is_glob:
        return _glob(fs, path, long)
    else:
        return _list(fs, path, long)


def _list(fs, path, long):
    """List a single path: a single directory content, or a single file"""
    fmt_fn = format_long if long else format_short
    # This implementation always issues two requests to list a directory or
    # file. An alternative would be to try to list a directory, and fallback to
    # listing a file in case of an exception. But which exception? Can we trust
    # implementations to always use the same base exception class?
    if fs.isdir(path):
        for item in fs.ls(path, detail=True):
            click.echo(fmt_fn(item))
    else:
        click.echo(fmt_fn(fs.info(path)))


def _glob(fs, globstr, long):
    """List paths matching a glob"""
    if long and not click.confirm(
        "Long output for a glob search may be slow and issue many requests. Continue?"
    ):
        return

    if long:
        for item in fs.glob(globstr):
            node_info = fs.info(item)
            click.echo(format_long(node_info))
    else:
        for item in fs.glob(globstr):
            click.echo(item)


# @cli.command
# def find():
#     click.echo("Not yet implemented")


def _cat_validate(fs, path):
    """Validate that the content of the given file can be printed out.
    Interactive. Returns True if the file can be printed, False otherwise."""

    if not fs.isfile(path):
        click.echo("No such file")
        return False

    head = fs.head(path)
    if is_binary_string(head) and not click.confirm(
        "The file appears to be binary. Continue?"
    ):
        return False

    return True


@cli.command(help="Print file content")
@click.argument("path")
def cat(path):
    fs = file_system.get_current()
    if not _cat_validate(fs, path):
        return

    size = fs.size(path)
    if size >= 10 * 1024 and not click.confirm(
        f"The file is {humanize_bytes(size)} long. Are you sure?"
    ):
        return

    click.echo(fs.cat(path))


@cli.command(help="Print first bytes of the file content")
@click.option(
    "-c",
    "--bytes",
    "bytes_count",
    type=int,
    default=512,
    show_default=True,
    help="Print at most this number of bytes",
)
@click.argument("path")
def head(path, bytes_count):
    fs = file_system.get_current()
    if _cat_validate(fs, path):
        click.echo(fs.head(path, bytes_count))


@cli.command(help="Print last bytes of the file content")
@click.option(
    "-c",
    "--bytes",
    "bytes_count",
    type=int,
    default=512,
    show_default=True,
    help="Print at most this number of bytes",
)
@click.argument("path")
def tail(path, bytes_count):
    fs = file_system.get_current()
    if _cat_validate(fs, path):
        click.echo(fs.tail(path, bytes_count))


# @cli.command
# def cp():
#     click.echo("Not yet implemented")


# @cli.command
# def mv():
#     click.echo("Not yet implemented")


# @cli.command
# def rm():
#     click.echo("Not yet implemented")


# @cli.command
# def touch():
#     click.echo("Not yet implemented")


# @cli.command
# def download():
#     click.echo("Not yet implemented")


# @cli.command
# def upload():
#     click.echo("Not yet implemented")


# @cli.command
# def mkdir():
#     click.echo("Not yet implemented")

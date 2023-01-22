import glob
import os
from typing import Any, Dict

import click

from .. import file_system
from ..exceptions import FatalError
from ..tui import errorhandler
from ..util import humanize_bytes, is_binary_string
from .main import cli


def format_long(file_info: Dict[str, Any]) -> str:
    """Format fsspec file info dict to a string, in a safe manner (assumes that
    some implementations may not respect the specification for the file info
    format)."""
    name = os.path.normpath(file_info.get("name", "???"))
    size = file_info.get("size", 0)
    mtime = file_system.get_mtime(file_info)
    mtime_str = (
        mtime.isoformat(sep=" ", timespec="seconds") if mtime is not None else ""
    )
    node_type = file_info.get("type", "???")[:3]
    is_dir = node_type == "dir"
    if is_dir:
        name = name + "/"

    size_str = humanize_bytes(size) if size is not None else "-"
    return f"{node_type:<3} {size_str:>10} {mtime_str} {name}"


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
@errorhandler
def ls(path, long):
    _ls(path, long)


@cli.command(help="List files in a directory in a long format (same as ls -l)")
@click.argument("path", default=".")
@errorhandler
def ll(path):
    _ls(path, long=True)


def _ls(path, long):
    """Undecorated version of the ls"""
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
# @errorhandler
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
@errorhandler
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
@errorhandler
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
@errorhandler
def tail(path, bytes_count):
    fs = file_system.get_current()
    if _cat_validate(fs, path):
        click.echo(fs.tail(path, bytes_count))


@cli.command(
    help="Copy files and directories within a file system. "
    "Overwrites target files, if they exist."
)
@click.option(
    "-r",
    "recursive",
    is_flag=True,
    show_default=False,
    default=False,
    help="Copy matching directories and their subtrees",
)
@click.argument("src")
@click.argument("dst")
@errorhandler
def cp(recursive, src, dst):
    fs = file_system.get_current()
    fs.cp(src, dst, recursive=recursive)


@cli.command(
    help="Move files and directories within a file system. "
    "Overwrites target files, if they exist."
)
@click.option(
    "-r",
    "recursive",
    is_flag=True,
    show_default=False,
    default=False,
    help="Move matching directories and their subtrees",
)
@click.argument("src")
@click.argument("dst")
@errorhandler
def mv(recursive, src, dst):
    fs = file_system.get_current()
    fs.mv(src, dst, recursive=recursive)


@cli.command(help="Remove files and directories")
@click.option(
    "-r",
    "recursive",
    is_flag=True,
    show_default=False,
    default=False,
    help="Remove matching directories and their subtrees",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    show_default=False,
    default=False,
    help="Remove all matching files and directories without prompting for confirmation",
)
@click.argument("path")
@errorhandler
def rm(recursive, force, path):
    fs = file_system.get_current()
    if not force:
        paths = reversed(fs.expand_path(path, recursive=recursive))
        for p in paths:
            if click.confirm(f"Remove {p}?"):
                if fs.isdir(p):
                    fs.rmdir(p)
                else:
                    fs.rm(p)
    else:
        fs.rm(path, recursive=recursive)


@cli.command(help="Create a file or update its modifiction time")
@click.argument("path")
@errorhandler
def touch(path):
    fs = file_system.get_current()

    # ! DANGER ZONE !
    # `truncate=False` part is important because otherwise `touch` truncates
    # the file content (clears the file content by opening it for write)
    fs.touch(path, truncate=False)


@cli.command(help="Get (download) a single file to a native local file system")
@click.argument("remote_file_path")
@click.argument("local_file_or_dir_path")
@errorhandler
def get(remote_file_path, local_file_or_dir_path):
    fs = file_system.get_current()

    if not fs.isfile(remote_file_path):
        raise FatalError(f"File not found: {remote_file_path}")

    fs.get(remote_file_path, local_file_or_dir_path)


@cli.command(help="Put (upload) a single file from a native local file system")
@click.argument("local_file_path")
@click.argument("remote_file_or_dir_path")
@errorhandler
def put(local_file_path, remote_file_or_dir_path):
    fs = file_system.get_current()

    if not os.path.isfile(local_file_path):
        raise FatalError(f"File not found: {remote_file_or_dir_path}")

    fs.put(local_file_path, remote_file_or_dir_path)


@cli.command(help="Creare directories")
@click.option(
    "-p",
    "mkdirs",
    is_flag=True,
    show_default=False,
    default=False,
    help="Create intermediate directories, if they don't exist",
)
@click.argument("path")
@errorhandler
def mkdir(mkdirs, path):
    fs = file_system.get_current()
    if mkdirs:
        fs.makedirs(path, exist_ok=True)
    else:
        fs.mkdir(path, create_parents=False)

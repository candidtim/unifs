import click

from ..config import ensure_config, site_config_file_path


@click.group
def cli():
    """This is the CLI entry point"""
    ensure_config(site_config_file_path())


from . import conf, fs, impl  # noqa: F401, E402

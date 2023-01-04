import click


@click.group
def cli():
    """This is the CLI entry point"""
    pass


from . import conf, fs, impl  # noqa: F401, E402

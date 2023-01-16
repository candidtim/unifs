import sys

import click

from .. import config
from ..config import ensure_config, site_config_file_path
from ..tui import errorhandler

TERMS_PROMPT = """
User is responsible for the operations performed by this program.
This program is designed to be used in an interactive mode.

All terms of the BSD 3-Clause License apply.
(Full licence text is distributed with the program source code.)

Do you agree?
""".strip()


@click.group
@errorhandler
def cli():
    """This is the CLI entry point"""
    ensure_config(site_config_file_path())
    prompt_accept_terms()


def prompt_accept_terms():
    # skip the rest if the user already accepter the terms:
    if config.get().accepted_usage_terms:
        return

    accepted = click.confirm(TERMS_PROMPT)

    # force exit if the user doesn't accept the terms
    if not accepted:
        sys.exit(81)

    new_conf = config.get().set_accepted_usage_terms()
    config.save_site_config(new_conf)


from . import conf, fs, impl  # noqa: F401, E402

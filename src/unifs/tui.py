import sys
from functools import wraps
from typing import Any, Iterable, Optional

import click

from .exceptions import FatalError, RecoverableError
from .logging import log_exception


def _format_row_value(val: Optional[Any], width: int) -> str:
    """Formats a value for the output as a "cell" in the table. See
    `format_table`."""
    if val is None:
        return ""
    elif len(str(val)) >= width:
        return str(val)[: width - 4] + "..."
    else:
        return str(val)


def format_table(
    header: Iterable[str], widths: Iterable[int], rows: Iterable[Iterable[Any]]
) -> str:
    """Format a table with a header and rows, columns left-adjusted with
    guaranteed widths."""

    line_fmt = "".join("{v%d:<%d}" % (i, w) for i, w in enumerate(widths))
    all_rows = [
        [_format_row_value(v, w) for v, w in zip(row, widths)]
        for row in [header] + list(rows)
    ]
    return "\n".join(
        line_fmt.format(**{f"v{i}": v for i, v in enumerate(row)}).rstrip()
        for row in all_rows
    )


def errorhandler(fn):
    """A decorator that enables generic error handling behavior on a click
    command function. Prints RecoverableErrors to the user, logs unexpected
    errors to a file, then prints a message to the user and exites with a
    non-zero exit code."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except RecoverableError as err:
            click.echo(str(err))
            sys.exit(0)
        except FatalError as err:
            click.echo(str(err))
            sys.exit(1)
        except Exception as ex:
            log_exception("Unhandled exception in a command")
            click.echo(f"An unexpected erorr ocurred: {str(ex)}")
            sys.exit(2)

    return wrapper

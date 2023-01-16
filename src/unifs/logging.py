"""
Although this is a command-line application, it may need to log to files in
some special cases (e.g., an unexpected exception), even if not in a
traditional sense of logging. This module provides means of logging for such
situations.
"""

import os
import traceback
from datetime import datetime

from appdirs import user_data_dir


def log_exception(comment: str):
    """Log the exception that is currently being handled to the "error.log"
    file in the user's data dir."""

    _log_exception(comment, _log_file_path())


def _log_file_path() -> str:
    # not using user_log_dir() because it raises an error in the current
    # version on MacOS (appdirs==1.4.4):
    return os.path.join(user_data_dir(), "error.log")


def _log_exception(comment: str, log_file_path: str):
    timestamp = datetime.now().isoformat()
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{timestamp} {comment}\n")
        # using 'traceback' because configuring 'logigng' seems to be an overkill
        traceback.print_exc(file=log_file)
        log_file.write("-- END OF THE ERROR MESSAGE --\n")

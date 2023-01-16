class RecoverableError(Exception):
    """Base class for exceptions that indicate an expected blocking condition.
    May be presented to the user. Depending on the context, user may be given a
    choice to fix the issue, or program may terminate.
    """

    pass


class FatalError(Exception):
    """Base class for exceptions that indicate that most the recent user
    operation was NOT performed. May be presented to the user. Indicates a
    definitve error which should lead to the program exit with a non-zero
    code."""

    pass

class RecoverableError(Exception):
    """Base class for exceptions that can be handled by the user and may be
    presented to them. Depending on the context, user may be given a choice to
    fix those, if possible, or program may terminate after showing the error to
    the user."""

    pass

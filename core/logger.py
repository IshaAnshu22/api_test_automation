import logging

LOGGER_NAME = None


def set_logger_name(name):
    """
    Ensures that only one logger is created during a session
    """
    global LOGGER_NAME

    if LOGGER_NAME is None:
        LOGGER_NAME = name
    elif LOGGER_NAME != name:
        raise RuntimeError(
            f"Logger already set to '{LOGGER_NAME}', cannot change to '{name}'"
        )


def get_logger():
    if not LOGGER_NAME:
        raise RuntimeError("Logger not initialized")

    return logging.getLogger(LOGGER_NAME)

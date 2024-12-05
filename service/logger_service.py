import logging

logger = None


def setup_logger() -> logging.Logger:
    global logger
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
    return logger

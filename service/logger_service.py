import logging

logger = None


def setup_logger() -> logging.Logger:
    global logger
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
    return logger

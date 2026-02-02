import logging
import sys


def setup_logger(verbose: bool) -> logging.Logger:
    logger = logging.getLogger("yt_media_kit")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.handlers = [handler]
    logger.propagate = False
    return logger
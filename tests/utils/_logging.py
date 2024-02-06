import logging
import sys


def enable_verbose_logging(logger=None):
    """Enables all messages to be shown to stdout"""
    if logger is None:
        logger =  logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    logger.addHandler(handler)

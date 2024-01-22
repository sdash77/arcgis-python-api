import logging
import sys


def enable_verbose_logging(logger=logging.getLogger()):
    """Enables all messages to be shown to stdout"""
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    logger.addHandler(handler)

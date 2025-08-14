import logging
import os
import pathlib
import sys
from ._common import environ_key_to_bool


def enable_verbose_logging(
    logger=None, log_level=None, log_name="integration_test.log"
):
    """Logs all messages to stdout, or to a integration_test.log if CI environment variable is set to true (i.e. Jenkins or GitHub Actions)."""
    if not log_level:
        log_level = logging.DEBUG
    logger = logger or logging.getLogger()
    logger.setLevel(log_level)
    # <<repository root directory>>/integration_test.log
    log_file = pathlib.Path(__file__).parent.parent.parent / log_name
    handler = (
        # If running in an automated environment, log to a file
        logging.FileHandler(str(log_file))
        if environ_key_to_bool("CI")
        else logging.StreamHandler(sys.stdout)
    )
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

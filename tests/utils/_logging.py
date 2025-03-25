import logging
import os
import pathlib
import sys
from ._common import environ_key_to_bool


def enable_verbose_logging(logger=None):
    """Logs all messages to stdout, or to a integration_test.log if CI environment variable is set to true (i.e. Jenkins or GitHub Actions)."""
    logger = logger or logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # <<repository root directory>>/integration_test.log
    log_file = pathlib.Path(__file__).parent.parent.parent / "integration_test.log"
    handler = (
        # If running in an automated environment, log to a file
        logging.FileHandler(str(log_file))
        if environ_key_to_bool("CI")
        else logging.StreamHandler(sys.stdout)
    )
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

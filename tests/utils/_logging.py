import logging
import os
import pathlib
import sys


def enable_verbose_logging(logger=None):
    """Logs all messages to stdout, or to a integration_test.log if CI environment variable is set to true (i.e. Jenkins or GitHub Actions)."""
    logger = logger or logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # If running in an automated environment, log to a file
    ci_environment = os.environ.get("CI", "").lower() in ["true", "1", "yes", "y"]
    # <<repository root directory>>/integration_test.log
    log_file = pathlib.Path(__file__).parent.parent.parent / "integration_test.log"
    handler = (
        logging.FileHandler(str(log_file))
        if ci_environment
        else logging.StreamHandler(sys.stdout)
    )
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

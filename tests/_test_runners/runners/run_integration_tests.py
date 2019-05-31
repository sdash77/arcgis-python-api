import pytest
import os
import logging
log = logging.getLogger("__main__")

from _test_runners._common import *

def run_integration_tests(config, paths, output_dir):
    if paths:
        log.info("Running integration tests...")
        output_xml_path = os.path.join(output_dir,
                                       "integration_tests_output.xml")
        run_pytest_on(paths, output_xml_path)

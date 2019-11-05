import pytest
import os
import logging
log = logging.getLogger("__main__")

from utils._common import *

def run_integration_tests(config, paths, output_dir):
    if not paths:
        raise Exception("Must specify some paths to run!")
    log.info("Running integration tests...")
    output_xml_path = os.path.join(output_dir,
                                   "integration_tests_output.xml")
    run_pytest_on(paths, output_xml_path)
    return output_xml_path

import pytest
import os
import logging
log = logging.getLogger("__main__")

from _test_runners._common import *

def run_integration_tests(config, paths, output_dir):
    log.info("Running integration tests...")
    out_xml = os.path.join(output_dir, "integration_tests_output.xml")
    pytest_args = ["-x",] + paths + [ 
        f"--junit-xml={out_xml}",
        ]
    log.debug(f"Running pytest.main({pytest_args})")
    os.chdir(INTEGRATION_TESTS_DIR)
    pytest.main(pytest_args)

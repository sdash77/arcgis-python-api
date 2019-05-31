import os
import logging
log = logging.getLogger("__main__")

from _test_runners._common import *

def run_unit_tests(config, paths, output_dir):
    if not paths:
        raise Exception("Must specify some paths!")
    log.info("Running unit tests...")
    output_xml_path = os.path.join(output_dir, "unit_tests_output.xml")
    run_pytest_on(paths, output_xml_path, block_network_access=True)
    return output_xml_path

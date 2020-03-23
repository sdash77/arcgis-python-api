import os
import shutil
import logging
log = logging.getLogger("__main__")

from utils._common import *

def run_unit_tests(config, paths, output_dir):
    if not paths:
        raise Exception("Must specify some paths!")
    log.info("Running unit tests...")
    output_xml_path = os.path.join(output_dir, "unit_tests_output.xml")
    output_coverage_dir = os.path.join(output_dir, "unit_tests_coverage")
    if os.path.exists(output_coverage_dir):
        shutil.rmtree(output_coverage_dir)
    run_pytest_on(paths, output_xml_path, 
                  output_coverage_dir, block_network_access=True)
    output_coverage_file = os.path.join(output_coverage_dir, "index.html")
    return output_xml_path, output_coverage_file

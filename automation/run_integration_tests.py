import sys
import os
from distutils.dir_util import copy_tree
import logging
log = logging.getLogger()

from automation._common import *

INTEGRATION_TESTS_DIR = os.path.join(GEOSAURUS_ROOT_DIR, "tests", "integration")
try:
    sys.path.append(os.path.join(INTEGRATION_TESTS_DIR))
    from run_test_cases import run_test_cases
except Exception as e:
    log.warn("Couldn't import run_test_cases from {}. failing."\
             "..".format(INTEGRATION_TESTS_DIR))
    raise e

def run_integration_tests(*args, **kwargs):
    log.info("Attempting to run all test cases...")
    args = [ # run_test_cases.py is called from cmd: this list mimics sys.argv
             'run_source_code_tests', # argv[0] is always the file name
             INTEGRATION_TESTS_DIR, # run all tests
             '--test_results_dir', STAGING_DIR # Send .xml files to staging
           ]
    run_test_cases(args)

if __name__ == '__main__':
    run_unit_tests()

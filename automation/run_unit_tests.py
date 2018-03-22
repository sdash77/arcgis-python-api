import sys
import os
from distutils.dir_util import copy_tree
import logging
log = logging.getLogger()

from __init__ import GEOSAURUS_ROOT_DIR, STAGING_DIR
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR, "unittests"))
from run_test_cases import run_test_cases

def run_unit_tests(*args, **kwargs):
    log.info("Attempting to run all test cases...")
    args = [ # run_test_cases.py is called from cmd: this list mimics sys.argv
             'run_unit_tests', # argv[0] is always the file name
             os.path.join(GEOSAURUS_ROOT_DIR, 'unittests'), # run all tests
             '--test_results_dir', STAGING_DIR # Send .xml files to staging
           ]
    run_test_cases(args)

if __name__ == '__main__':
    run_unit_tests()

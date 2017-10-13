import sys
import os
from distutils.dir_util import copy_tree

from __init__ import GEOSAURUS_ROOT_DIR, STAGING_DIR
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR, "unittests"))
from run_test_cases import run_test_cases

def run_unit_tests(*args, **kwargs):
#    subprocess.check_call(['python',os.path.join(GEOSAURUS_ROOT_DIR, 'unittests', 'run_test_cases.py'), os.path.join(GEOSAURUS_ROOT_DIR, 'unittests')],
#            timeout=600)
    args = ['run_unit_tests',
                #mimics sys.argv: argv[0] is always the file name
            os.path.join(GEOSAURUS_ROOT_DIR, 'unittests', 'geometry'),
                #Run the tests on geometry tests directory (for demo purposes)
            '--test_results_dir', STAGING_DIR
                #Send all test_results .xml files to the staging dir
            ]
    run_test_cases(args)
    print("run_test_cases has returned... Moving results to staging")

if __name__ == '__main__':
    run_unit_tests()

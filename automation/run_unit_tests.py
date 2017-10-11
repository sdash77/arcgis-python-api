import sys
import os
from distutils.dir_util import copy_tree

from __init__ import GEOSAURUS_ROOT_DIR, STAGING_DIR
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR, "unittests"))
from run_test_cases import run_test_cases

def run_unit_tests():
#    subprocess.check_call(['python',os.path.join(GEOSAURUS_ROOT_DIR, 'unittests', 'run_test_cases.py'), os.path.join(GEOSAURUS_ROOT_DIR, 'unittests')],
#            timeout=600)
    run_test_cases(['run_unit_tests', os.path.join(GEOSAURUS_ROOT_DIR, 'unittests', 'geometry')])
    print("run_test_cases has returned... Moving results to staging")
    copy_tree(os.path.join(GEOSAURUS_ROOT_DIR,"unittests","test-results"),
              os.path.join(STAGING_DIR,"test-results"))

if __name__ == '__main__':
    run_unit_tests()

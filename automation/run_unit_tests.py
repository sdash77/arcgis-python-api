import sys
import os
import subprocess

from __init__ import GEOSAURUS_ROOT_DIR, STAGING_DIR
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR, "unittests"))
from run_test_cases import run_test_cases

def run_unit_tests():
#    subprocess.check_call(['python',os.path.join(GEOSAURUS_ROOT_DIR, 'unittests', 'run_test_cases.py'), os.path.join(GEOSAURUS_ROOT_DIR, 'unittests')],
#            timeout=600)
    run_test_cases(['run_unit_tests', os.path.join(GEOSAURUS_ROOT_DIR, 'unittests')])

    print("run_test_cases has returned...")

if __name__ == '__main__':
    run_unit_tests()

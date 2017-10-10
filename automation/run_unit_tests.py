from __init__ import GEOSAURUS_ROOT_DIR, STAGING_DIR

import subprocess
import os

def run_unit_tests():
    subprocess.check_call(['python',os.path.join(GEOSAURUS_ROOT_DIR, 'unittests', 'run_test_cases.py'), os.path.join(GEOSAURUS_ROOT_DIR, 'unittests')],
            timeout=600)
    print("Running unit tests not supported through this interface yet")

if __name__ == '__main__':
    run_unit_tests()

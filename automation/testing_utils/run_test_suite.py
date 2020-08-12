import sys
import os
import logging
log = logging.getLogger(__name__)

from automation._common import *

# Import the test runner module at geosaurus/tests/_test_runner
sys.path.append(os.path.join(TESTS_DIR))
os.chdir(TESTS_DIR)
from _test_runners import read_suite, run_suite

def run_test_suite(suite_path, notebooks_root_dir, jenkins_job_url, **kwargs):
    log.info(f"Running test suite {suite_path}")
    suite = read_suite(suite_path, GEOSAURUS_ROOT_DIR, notebooks_root_dir)
    run_suite(suite = suite,
              output_dir = STAGING_DIR,
              jenkins_job_url = jenkins_job_url,
              run_setup_env = True,
              run_smoke_tests_before = True)

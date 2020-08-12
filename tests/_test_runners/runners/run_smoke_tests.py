import os
import glob
import logging
log = logging.getLogger("__main__")

from utils._common import *

def run_smoke_tests(output_dir):
    try:
        log.info("running smoke tests..")
        smoke_test_paths = glob.glob(
            os.path.join(SMOKE_TESTS_DIR, "**", "*.py"),
            recursive=True)
        smoke_test_xml_output = os.path.join(output_dir, "smoke_test.xml")
        run_pytest_on(smoke_test_paths, smoke_test_xml_output,
                      max_fail=0,
                      throw_exc_on_fail = True)
        log.info("Smoke tests appear to have passed, continuing...")
        return smoke_test_xml_output
    except Exception as e:
        log.exception(e)
        msg = f'Smoke tests failed! Rest of suite not running since it '\
              f'would give errenous, potentially false-positive output. '
        raise Exception(msg)

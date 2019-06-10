import os
import glob
import logging
log = logging.getLogger("__main__")

from utils._common import *

def run_sanity_tests(output_dir):
    try:
        log.info("running sanity tests..")
        sanity_test_paths = glob.glob(
            os.path.join(SANITY_TESTS_DIR, "**", "*.py"),
            recursive=True)
        sanity_test_xml_output = os.path.join(output_dir, "sanity_test.xml")
        run_pytest_on(sanity_test_paths, sanity_test_xml_output,
                      max_fail=0,
                      run_geosaurus_exec_throw_exc_on_fail = True)
        return sanity_test_xml_output
    except Exception as e:
        log.exception(e)
        msg = f'Sanity tests failed! Rest of suite not running since it '\
              f'would give errenous, potentially false-positive output. '
        raise Exception(msg)

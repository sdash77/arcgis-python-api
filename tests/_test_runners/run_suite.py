import os
import json
import logging
log = logging.getLogger("__main__")

from _test_runners.runners import *

def run_suite(suite, output_dir, jenkins_root="http://zion/jenkins"):
    log.debug(f"running suite {json.dumps(suite)}")

    if "sanity_tests_to_run" in suite:
        run_sanity_tests(suite["sanity_tests_to_run"]["config"],
                          suite["sanity_tests_to_run"]["paths"],
                          output_dir)
    if "unit_tests_to_run" in suite:
        run_unit_tests(suite["unit_tests_to_run"]["config"],
                        suite["unit_tests_to_run"]["paths"],
                        output_dir)
    if "integration_tests_to_run" in suite:
        run_integration_tests(suite["integration_tests_to_run"]["config"],
                               suite["integration_tests_to_run"]["paths"],
                               output_dir)
    if "nbconvert_notebook_tests_to_run" in suite:
        run_notebook_tests(suite["nbconvert_notebook_tests_to_run"]["config"],
                            suite["nbconvert_notebook_tests_to_run"]["paths"],
                            output_dir,
                            jenkins_root = jenkins_root,
                            runner = "nbconvert")
    if "selenium_notebook_tests_to_run" in suite:
        run_notebook_tests(suite["selenium_notebook_tests_to_run"]["config"],
                            suite["selenium_notebook_tests_to_run"]["paths"],
                            output_dir,
                            jenkins_root = jenkins_root,
                            runner = "selenium")
    if "widget_unit_tests_to_run" in suite:
        run_widget_unit_tests(suite["widget_unit_tests_to_run"]["config"],
                               suite["widget_unit_tests_to_run"]["paths"],
                               output_dir)

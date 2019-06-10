import os
import json
import pathlib
import logging
log = logging.getLogger("__main__")

from _test_runners.runners import *
from utils._common import *

file_uri_output_dir = pathlib.Path(TESTS_DIR).as_uri()

def run_suite(suite, output_dir, 
              jenkins_job_url=file_uri_output_dir,
              run_setup_env = False):
    log.debug(f"running suite {json.dumps(suite)}")
    output_xml_results = []

    if run_setup_env:
        _setup_env()

    xml_output = run_sanity_tests(output_dir)
    output_xml_results.append(xml_output)

    if "unit_tests_to_run" in suite and \
       suite["unit_tests_to_run"]["paths"]:
        xml_output = \
            run_unit_tests(suite["unit_tests_to_run"]["config"],
                           suite["unit_tests_to_run"]["paths"],
                           output_dir)
        output_xml_results.append(xml_output)

    if "integration_tests_to_run" in suite and \
       suite["integration_tests_to_run"]["paths"]:
        xml_output = \
            run_integration_tests(suite["integration_tests_to_run"]["config"],
                                  suite["integration_tests_to_run"]["paths"],
                                  output_dir)
        output_xml_results.append(xml_output)

    if "nbconvert_notebook_tests_to_run" in suite and \
       suite["nbconvert_notebook_tests_to_run"]["paths"]:
        xml_output = \
            run_notebook_tests(suite["nbconvert_notebook_tests_to_run"]["config"],
                               suite["nbconvert_notebook_tests_to_run"]["paths"],
                               output_dir,
                               jenkins_job_url = jenkins_job_url,
                               notebook_runner = "nbconvert")
        output_xml_results.append(xml_output)

    if "selenium_notebook_tests_to_run" in suite and \
       suite["selenium_notebook_tests_to_run"]["paths"]:
        xml_output = \
            run_notebook_tests(suite["selenium_notebook_tests_to_run"]["config"],
                               suite["selenium_notebook_tests_to_run"]["paths"],
                               output_dir,
                               jenkins_job_url = jenkins_job_url,
                               notebook_runner = "selenium")
        output_xml_results.append(xml_output)

    if "widget_unit_tests_to_run" in suite and \
       suite["widget_unit_tests_to_run"]["paths"]:
        xml_output = \
            run_widget_unit_tests(suite["widget_unit_tests_to_run"]["config"],
                                  suite["widget_unit_tests_to_run"]["paths"],
                                  output_dir)
        output_xml_results.append(xml_output)

    return output_xml_results

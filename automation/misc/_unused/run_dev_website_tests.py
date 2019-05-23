import os
import logging
log = logging.getLogger()

from automation._common import *
from automation.misc._unused._classes import *

def run_dev_website_tests(dev_website_server, **kwargs):
    """Runs tests on every html file in STAGING/arcgis-for-developers,
    outputs .xml files to staging/dev_website_test_results.

    At the moment, Goes through every image and url and checks the validity
    """
    log.info(f"Running tests against {dev_website_server}, this may take a "\
              "while... All test results will be available to view at on "\
              "http://zion in a nice viewable format. All test output is "\
              "written to log.debug(). The rest of this console log will be "\
              "success messages for each test ran, please ignore.")

    # Make the output dir for the test xml results to be placed in
    html_files_dir = os.path.join(STAGING_DIR, "arcgis-for-developers")
    tests_output_dir = os.path.join(STAGING_DIR, "dev_website_test_results")
    if not os.path.exists(tests_output_dir):
        os.makedirs(tests_output_dir)

    # Run a test suite for each html file in html_files_dir
    for root, dirs, files in os.walk(html_files_dir):
        for name in [x for x in files if ".html" in x]:
            html_file_path = os.path.join(root, name)
            html_suite = HtmlFileTestSuite(html_file_path,
                                           tests_output_dir,
                                           dev_website_server)
            html_suite.run_tests()


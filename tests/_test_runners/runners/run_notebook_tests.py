import sys
import os
import unittest
import shutil
from glob import glob
import tempfile
from uuid import uuid4
import logging
log = logging.getLogger("__main__")

from xmlrunner import XMLTestRunner

from _test_runners.TestNotebook import TestNotebook
from _test_runners._common import *

def run_notebook_tests(config, paths, output_dir,
                       jenkins_job_url, notebook_runner = "nbconvert"):
    log.info("Running notebook tests...")

    # Make a folder to put all output executed notebooks
    output_executed_notebooks_dir = os.path.join(output_dir,
        "executed_notebooks")
    output_xml_path = os.path.join(output_dir, 
        f"{notebook_runner}_notebook_tests_output.xml")

    # Add all tests from `paths` to a unittest.TestSuite() instance
    utest_test_suite = unittest.TestSuite()
    for notebook_path in paths:
        test = TestNotebook(notebook_file_path = notebook_path,
                            output_dir = output_executed_notebooks_dir,
                            cell_timeout_sec = config['cell_timeout_sec'],
                            jenkins_job_url = jenkins_job_url,
                            notebook_runner = notebook_runner,
                            browser = config.get("browser", None))
        utest_test_suite.addTest(test)

    # Run the actual tests, run setup/teardown if applicable
    if 'setup_script' in config:
        run_shell_command(f"python {config['setup_script']}")

    with _empty_temp_folder() as empty_temp_dir:
        runner = XMLTestRunner(empty_temp_dir)
        runner.run(utest_test_suite)
        for temp_xml_path in glob(os.path.join(empty_temp_dir, "*.xml")):
            os.rename(temp_xml_path, output_xml_path)

    if 'teardown_script' in config:
        run_shell_command(f"python {config['teardown_script']}")

    # Write an index file for easier viewing, return outputted xml file
    _write_index_html_file_for_outputted_notebooks(
        output_executed_notebooks_dir)
    return output_xml_path

def _write_index_html_file_for_outputted_notebooks(output_dir):
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write("<h1>Press a link below to see an outputted notebook</h1>\n")
        for notebook_html_file in glob(os.path.join(output_dir, "*.html")):
            notebook_html_file_name_no_ext = os.path.splitext(
                os.path.basename(notebook_html_file))[0]
            f.write('<p><a href="./{0}.html">{0}</a></p>\n'.format(
                notebook_html_file_name_no_ext))

class _empty_temp_folder:
    """Use with "with" syntax like "with empty_temp_folder() as tmp:"
    Creates a temporary folder and deletes it after finished being used
    """
    def __enter__(self):
        self.temp_folder = os.path.join(tempfile.gettempdir(),
                                        ".{}".format(uuid4()))
        os.makedirs(self.temp_folder)
        return self.temp_folder

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.temp_folder)


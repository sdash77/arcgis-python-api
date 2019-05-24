import sys
import os
import unittest
from glob import glob
import logging
log = logging.getLogger()

from xmlrunner import XMLTestRunner

from _test_runners.TestNotebook import TestNotebook

def run_notebook_tests(config, paths, output_dir,
                       jenkins_root, runner = "nbconvert"):
    log.info("Running notebook tests...")
    """
    suite = _discover_tests_get_suite(notebooks_root_dir = notebooks_root_dir,
                                      output_dir = STAGING_DIR,
                                      automation_type = automation_type,
                                      build_number = build_number,
                                      jenkins_root = jenkins_root,
                                      cell_timeout_sec = cell_timeout_sec)
    runner = XMLTestRunner(output=STAGING_DIR)

    setup_py_file = os.path.join(notebooks_root_dir, "misc", "setup.py")
    run_shell_command(f"python {setup_py_file}", throw_exc_on_fail=False)

    runner.run(suite)

    teardown_py_file = os.path.join(notebooks_root_dir, "misc", "teardown.py")
    run_shell_command(f"python {teardown_py_file}", throw_exc_on_fail=False)

    _write_index_html_file_for_outputted_notebooks()
    """

def _discover_tests_get_suite(notebooks_root_dir, output_dir,
                              automation_type, build_number,
                              jenkins_root, cell_timeout_sec):
    output_suite = unittest.TestSuite()
    log.info("Discovering notebooks to test in {}".format(notebooks_root_dir))

    for root, dirs, files in os.walk(notebooks_root_dir):
        for name in [file_ for file_ in files if ".ipynb" in file_]:
            notebook_path = os.path.join(root, name)
            if (".ipynb_checkpoints" not in notebook_path) and \
               ("talks" not in notebook_path):
                log.debug("Adding to suite notebook {}".format(notebook_path))
                test = TestNotebook(notebook_file_path = notebook_path,
                                    output_dir = output_dir,
                                    cell_timeout_sec = cell_timeout_sec,
                                    jenkins_job_url = "/".join([jenkins_root,
                                                        "job",
                                                        automation_type,
                                                        str(build_number),
                                                        ""]),
                                    notebook_runner="selenium")
                output_suite.addTest(test)

    if output_suite.countTestCases() == 0:
        raise RuntimeError("0 Notebooks found to run: Make sure '{}' "\
            "contains runnable notebooks.".format(notebooks_root_dir))
    else:
        log.info("Found {} notebooks to run".format(
                 output_suite.countTestCases()))
    
    return output_suite

def _write_index_html_file_for_outputted_notebooks():
    with open(os.path.join(STAGING_DIR, "index.html"), "w") as f:
        f.write("<h1>Press a link below to see an outputted notebook</h1>\n")
        for notebook_html_file in glob(os.path.join(STAGING_DIR, "*.html")):
            notebook_html_file_name_no_ext = os.path.splitext(
                os.path.basename(notebook_html_file))[0]
            f.write('<p><a href="./{0}.html">{0}</a></p>\n'.format(
                notebook_html_file_name_no_ext))

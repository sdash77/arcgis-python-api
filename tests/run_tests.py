#!/usr/bin/env python
"""
Developer script to run the correct test suite. 
`python run_tests.py --help` for more info
"""

import os
import sys
import re
import argparse
import shutil
import platform
import subprocess
import tempfile
import glob
import logging
log = logging.getLogger(__name__)

from _test_runners._common import *
from _test_runners import *

def _main():
    args = _parse_cmd_line_args()
    _setup_logging(args)
    _run_tests(args)

# Running from cmd line setup funcs
def _parse_cmd_line_args():
    parser = argparse.ArgumentParser(description = "User cmd line tool "\
        "to run specified tests. Results are stored in ./_output/. "\
        "See README.md for more information.\n\n"\
        "To run specific tests: \n"\
        "    `python run_tests.py ./unit/foo.py ./integration/bar.py`\n"\
        "To run all unit tests and all tests in ./integration/foobar/ dir:\n"\
        "   `python run_tests.py ./unit/ ./integration/foobar/`\n",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("tests", type=str, nargs='*',
        help="A list of test paths to run: either paths to files directly, "
             "or paths to directories") 
    parser.add_argument("--suite", "-s", type=str,
        help="Run the tests in the specified /path/to/suite.yaml")
    parser.add_argument("--output-dir", "-o", type=str, 
        default=os.path.join(TESTS_DIR, "_output"),
        help="Output directory to write junit xml etc. files to. "\
             "DEFAULT: .\_output")
    parser.add_argument("--verbose", "-v", action="store_true",
        help="Verbose logging output")
    args = parser.parse_args(sys.argv[1:]) #don't use filename as 1st arg
    if not any([args.suite, args.tests]):
        raise Exception("You must specify either positional argument `tests`,"\
                        " or --suite /path/to/suite.yml")
    return args

def _setup_logging(args):
    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
         log.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(logging.Formatter(
        '-----    %(levelname)s    |    '\
        '%(asctime)s    |    '\
        '%(filename)s line %(lineno)d'\
        '     -----\n'\
        '"%(message)s"'))
    log.addHandler(stdout_handler)
    log.info("Logging at level {}.".format(logging.getLevelName(log.level)))
    log.debug("args passed in => {}".format(args))

def _run_tests(args):
    if args.suite:
        suite = read_suite(args.suite)
    else:
        suite = read_suite(DEFAULT_EMPTY_SUITE_FILE_PATH)
    _add_to_suite_cmd_arg_tests(suite, args.tests)
    _parse_suite(suite)
    run_suite(suite, args.output_dir)

def _add_to_suite_cmd_arg_tests(suite, tests):
    for test in tests:
        test = os.path.abspath(test)
        _add_to_suite_if_unit_test(suite, test)
        _add_to_suite_if_integration_test(suite, test)
        _add_to_suite_if_notebook_test(suite, test)
        _add_to_suite_if_widget_test(suite, test)

def _parse_suite(suite):
    """Unblogs any paths and removes blacklist items when added in from
    cmd arguments
    """
    unglob_paths(suite)
    remove_blacklist_paths(suite)

def _add_to_suite_if_unit_test(suite, test):
    if UNIT_TESTS_DIR in test:
        if os.path.isdir(test):
            test = os.path.join(test, "**", "*.py")
        suite['unit_tests_to_run']['paths'].append(test)

def _add_to_suite_if_integration_test(suite, test):
    if INTEGRATION_TESTS_DIR in test:
        if os.path.isdir(test):
            test = os.path.join(test, "**", "*.py")
        suite['integration_tests_to_run']['paths'].append(test)

def _add_to_suite_if_notebook_test(suite, test):
    if NOTEBOOK_TESTS_DIR in test:
        if os.path.isdir(test):
            test = os.path.join(test, "**", "*.ipynb")
        suite['nbconvert_notebook_tests_to_run']['paths'].append(test)

def _add_to_suite_if_widget_test(suite, test):
    if WIDGET_INTEGRATION_TESTS_DIR in test:
        if os.path.isdir(test):
            test = os.path.join(test, "**", "*.ipynb")
        suite['selenium_notebook_tests_to_run']['paths'].append(test)
    if WIDGET_UNIT_TESTS_DIR in test:
        if os.path.isdir(test):
            test = os.path.join(test, "**", "*.js")
        suite['widget_unit_tests_to_run']['paths'].append(test)

if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        log.exception(e)
        log.info("Program did not succesfully complete (unhandled exception)")
        sys.exit(1)

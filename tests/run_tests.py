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

import logging
log = logging.getLogger(__name__)

from _test_runners._common import *
from _test_runners import read_suite_file, run_suite

def _main():
    args = _parse_cmd_line_args()
    _setup_logging(args)
    _run_tests(args)

# Running from cmd line setup funcs
def _parse_cmd_line_args():
    parser = argparse.ArgumentParser(description = "User cmd line tool "\
        "to run specific test suites. Results are stored in ./output/.\n\n"\
        "Most common use case for short dev runs: "\
        "`python run_tests.py --unit --sanity`",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--unit", "-u", action="store_true",
        help="Run all unit tests")
    parser.add_argument("--sanity", "-s", action="store_true",
        help="Run all sanity tests")
    parser.add_argument("--suite", "-y", type=str,
        help="Run the tests in the specified /path/to/suite.yaml")
    parser.add_argument("--output-dir", "-o", type=str, default=".",
        help="(Optional) Output directory to write junit xml etc. files to. "\
             "DEFAULT: this directory")
    parser.add_argument("--verbose", "-v", action="store_true",
        help="Verbose logging output")
    args = parser.parse_args(sys.argv[1:]) #don't use filename as 1st arg
    if any([args.unit, args.sanity, args.suite]):
        return args
    else:
        raise Exception("You must specify at least one of --unit, --sanity, "\
                        "or --suite. Run with --help for more info.")

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
        suite = read_suite_file(args.suite)
    else:
        suite = {}

    if args.unit:
        suite = _add_to_suite_all_unit_tests(suite)
    if args.sanity:
        suite = _add_to_suite_all_sanity_tests(suite)

    run_suite(suite, args.output_dir)

def _add_to_suite_all_unit_tests(suite):
    suite['unit_tests_to_run'] = {}
    suite['unit_tests_to_run']['config'] = {}
    suite['unit_tests_to_run']['paths'] = \
        [os.path.join(GEOSAURUS_ROOT_DIR, "tests", "unit", "**", "*.py"),]
    return suite

def _add_to_suite_all_sanity_tests(suite):
    suite['sanity_tests_to_run'] = {}
    suite['sanity_tests_to_run']['config'] = {}
    suite['sanity_tests_to_run']['paths'] = \
        [os.path.join(GEOSAURUS_ROOT_DIR, "tests", "sanity", "**", "*.py"),]
    return suite

if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        log.exception(e)
        log.info("Program did not succesfully complete (unhandled exception)")
        sys.exit(1)

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

import yaml

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..'))
AUTOMATION_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "automation"))
TESTS_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "tests"))
TESTS_OUTPUT = os.path.abspath(os.path.join(
    TESTS_DIR,
    "_tests_output"))

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
    parse.add_argument("--output", "-o", type=str, default=".",
        help="Output directory to write junit xml etc. files to")
    parser.add_argument("--verbose", "-v", action="store_true",
        help="Verbose logging output")
    parser.add_argument("--dry-run", "-d", action="store_true",
        help="Stage each test for run, then skip each test, outputting the "\
             "same .xml file as specified")
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
    if args.unit:
        _run_unit_tests()
    if args.sanity:
        _run_sanity_tests()
    if args.suite:
        _run_suite_tests(args.suite)

def _run_unit_tests():
    log.info("Running all unit tests...")

def _run_sanity_tests():
    log.info("Running all sanity tests...")

def _run_suite_tests(suite):
    log.info(f"Running all tests in this suite: {suite}")

if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        log.exception(e)
        log.info("Program did not succesfully complete (unhandled exception)")
        sys.exit(1)

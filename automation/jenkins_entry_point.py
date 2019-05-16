#!/usr/bin/env python3

import sys
import re
import os
import argparse
import logging
log = logging.getLogger()

#Import everything in this module
from _common import *
sys.path.insert(0, os.path.join(GEOSAURUS_ROOT_DIR))
from automation import *

#The core logic of what functions are run in what order for each job
_regex_and_funcs = [(MASTER_REGEX, [build_conda_package,
                                    build_pip_package,
                                    publish_to_ftp_site,
                                    build_documentation]),

              (LINUX_SLAVE_REGEX,  [build_conda_package,
                                    publish_to_ftp_site]),
              
              (GEOS_PULL_REQUEST_REGEX, [build_documentation]),

              (PUB_REPO_PULL_REQUEST_REGEX, [build_dummy_dev_site]),

                   (PUBLISH_REGEX, [build_conda_package,
                                    publish_to_ftp_site]),

          (SOURCE_CODE_TEST_REGEX, [run_integration_tests]),

                 (NOTEBOOK_TEST_REGEX, [run_notebook_tests]),

                 (ALL_TEST_REGEX, [run_integration_tests,
                                   run_notebook_tests]),

                 (DEV_SITE_REGEX, [stage_notebooks_for_dev_web_repo,
                                   build_dev_website_and_publish,
                                   run_dev_website_tests])]

def _main():
    args = _parse_args()
    kwargs = vars(args) #Converts to dict of keyword arguments
    funcs = _get_funcs_for_auto_type(args.automation_type)
    
    automation_setup(**kwargs)
    for func in funcs:
        func(**kwargs)
    automation_cleanup(**kwargs)

def _parse_args():
    parser = argparse.ArgumentParser(description = "Call the correct funcs "\
        "for the type of jenkins job calling this.")
    parser.add_argument("--automation-type", "-a", type=str, required=True,
        help="The name of the job (geosaurus_master, pull_request, etc.)")
    parser.add_argument("--build-number", "-b", type=int, required=False,
        help="The build number currently running")
    parser.add_argument("--username", "-u", type=str, required=False,
        help="The username for any authentication (i.e. ftp uploading)")
    parser.add_argument("--password", "-p", type=str, required=False,
        help="The password for the previously entered username")
    parser.add_argument("--ftp-folder-name", "-f", type=str, required=False,
        help="For -a publish, the name of the folder to write "\
             "conda packages to on the FTP server.")
    parser.add_argument("--notebooks-root-dir", "-n", type=str, required=False,
        help="For -a dev_site, the root dir of arcgis-python-api repo. "\
             "For -a public_repo_pull_request, the same thing. "\
             "For -a notebooks_test, the root dir of notebooks to test")
    parser.add_argument("--dev-website-repo", "-d", type=str, required=False,
        help="for -a dev_site, the root dir of arcgis-for-developers repo")
    parser.add_argument("--html-output-dir", "-o", type=str, required=False,
        help="For -a dev_site, the dir where outputted html files get put") 
    parser.add_argument("--dev-website-server", "-s", type=str, required=False,
        help="For -a dev_site, the dev site server to run tests against")
    parser.add_argument("--jenkins-root", "-j", type=str, required=False,
        help="For -a notebook_test, the root of the jenkins website. DEFAULT:"\
             " {}".format(JENKINS_ROOT), default=JENKINS_ROOT)
    parser.add_argument("--notebook-timeout", "-t", type=int, required=False,
        help="For -a notebook_test, the max # of secs a CELL in a notebook "\
             "can run. DEFAULT: {}".format(NB_TIMEOUT), default=NB_TIMEOUT)
    return parser.parse_args(sys.argv[1:]) #don't use filename as 1st arg

def _get_funcs_for_auto_type(automation_type):
    for regex_, funcs in _regex_and_funcs:
        if re.match(regex_, automation_type):
            return funcs
    msg = "'{}' auto type matches no regex on file: ".format(automation_type)
    msg += "Check the geosaurus/automation/__init__.py for the regexes"
    raise RuntimeError(msg)

if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        log.info("Unhandled exception caught: Adding to log...")
        log.exception(e)
        log.info("Succesfully logged exception: Raising it again...") 
        raise e

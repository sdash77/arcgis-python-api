#!/usr/bin/env python
import sys
import re
import os
import argparse
import logging
log = logging.getLogger()

from __init__ import *
#import geosaurus_root/src seperate module
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR, "src"))
from arcgis import __version__ as _geosaurus_version

from automation_setup import automation_setup
from build_conda_package import build_conda_package
from build_documentation import build_documentation
from run_unit_tests import run_unit_tests
from publish_results import publish_results
from automation_cleanup import automation_cleanup

_regex_and_funcs = [(MASTER_REGEX, [automation_setup,
                                    run_unit_tests, 
                                    build_documentation,
                                    build_conda_package,
                                    publish_results,
                                    automation_cleanup]),

              (LINUX_SLAVE_REGEX,  [automation_setup,
                                    build_conda_package,
                                    publish_results,
                                    automation_cleanup]),
              
              (PULL_REQUEST_REGEX, [automation_setup,
                                    run_unit_tests,
                                    build_documentation,
                                    automation_cleanup]),
              
                   (PUBLISH_REGEX, [automation_setup,
                                    build_conda_package,
                                    publish_results,
                                    automation_cleanup])]

def _main():
    args = _parse_args()
    args = _append_build_tag_to_args(args)
    kwargs = vars(args) #Converts to dict of keyword arguments
    funcs = _get_funcs_for_auto_type(args.automation_type)
    for func in funcs:
        func(**kwargs)

def _parse_args():
    parser = argparse.ArgumentParser(description = "Call the correct funcs "\
        "for the type of jenkins job calling this.")
    parser.add_argument("--automation-type", "-a", type=str, required=True,
        help="The name of the job (geosaurus_master, pull_request, etc.)")
    parser.add_argument("--build-number", "-b", type=int, required=False,
        help="The build number currently running")
    parser.add_argument("--username", "-u", type=str, required=False,
        help="The username for any ftp uploading")
    parser.add_argument("--password", "-p", type=str, required=False,
        help="The password for the previously entered username")
    parser.add_argument("--ftp-folder-name", "-f", type=str, required=False,
        help="If 'publish' auto-type,the name of the folder to write "\
             "conda packages to on the FTP server.")
    return parser.parse_args(sys.argv[1:]) #don't use filename as 1st arg

def _append_build_tag_to_args(args):
    """Assembles build tag, adds to it args, returns args"""
    if re.match(MASTER_REGEX, args.automation_type):
        args.build_tag = "geosaurus_{}_master_j{}".format(_geosaurus_version,
                                                          args.build_number)
    elif re.match(PULL_REQUEST_REGEX, args.automation_type):
        args.build_tag = "geosaurus_{}_dev_j{}".format(_geosaurus_version,
                                                       args.build_number)
    else:
        args.build_tag = "unspecified_{}_j{}".format(args.automation_type, 
                                                     args.build_number)
    return args

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

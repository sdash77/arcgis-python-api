import sys
import re
import os
import logging
log = logging.getLogger()

#import geosaurus_root/src seperate module
from __init__ import *
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR, "src"))
from arcgis import __version__ as _geosaurus_version

from automation_setup import automation_setup
from build_conda_package import build_conda_package
from build_docker_image import build_docker_image
from build_documentation import build_documentation
from run_unit_tests import run_unit_tests
from publish_results import publish_results

_master_regex = ".*master.*"
_pull_request_regex = ".*pull.*request.*"

# Build tag args determined at run time: this is updated in
# check_parse_args_get_automation_type()
_build_tag_args = []
_no_args = []
_funcs_for_auto = [(_master_regex, [(automation_setup, _no_args),
                                    (run_unit_tests, _no_args),
                                    (build_documentation, _no_args),
                                    (build_conda_package, _build_tag_args),
                                    (build_docker_image, _no_args),
                                    (publish_results, _build_tag_args)]),

             (_pull_request_regex, [(automation_setup, _no_args),
                                    (run_unit_tests, _no_args),
                                    (build_documentation, _no_args)])]
def main():
    automation_type = _check_parse_args_get_automation_type()
    funcs_and_args = _get_functions_to_call_for_auto_type(automation_type)
    for func, args in funcs_and_args:
        func(*args)

def _check_parse_args_get_automation_type():
    _check_args()
    automation_type = sys.argv[1]
    build_num = sys.argv[2]
    assemble_build_tag_add_to_args_global_var(build_num, automation_type)
    return automation_type

def _check_args():
   """Exactly 2 command line argument should be passed to this function"""
   if len(sys.argv) != 3:
        msg = "{} should be called with exactly 2 arg. ".format(sys.argv[0])
        msg += "You called it with args '{}'\n".format(sys.argv[1:])
        msg += "Please provide both args to specify automation to run.\n"
        msg += "(Ex. python jenkins_entry_point {AUTOTYPE} {BUILDNUM})"
        raise RuntimeError(msg)
   else:
       log.info("Arguments passed in: {}".format(sys.argv[1:]))
 
def assemble_build_tag_add_to_args_global_var(build_num, automation_type):
    if re.match(_master_regex, automation_type):
        build_tag = "geosaurus_{}_master_j{}".format(_geosaurus_version,
                                                     build_num)
    elif re.match(_pull_request_regex, automation_type):
        build_tag = "geosaurus_{}_dev_j{}".format(_geosaurus_version,
                                                  build_num)
    else:
        build_tag = "unspecified_{}_j{}".format(_automation_type, _build_num)

    _build_tag_args.append(build_tag)

def _get_functions_to_call_for_auto_type(automation_type):
    """Depending on what command line argument is passed in, there will be
    different actions that need to be done (master merge requests require
    a docker image being built, whereas pull requests don't. Both require
    a documentation build, etc.). Return what functions need to be called
    depending on what command line argument is passed in"""
    for regex_, funcs_and_args in _funcs_for_auto:
        if re.match(regex_, automation_type):
            return funcs_and_args
    msg = "'{}' input argument matches no regex on file: ".format(sys.argv[1])
    msg += "Check the {} file in geosaurus for the regexes".format(sys.argv[0])
    raise RuntimeError(msg)

def _get_build_tag():
    if _build_tag:
        return _build_tag
    else:
        return "geosaurus{}_{}_UNSPECIFIED_j{}".format(_py_api_version,
                                                       automation_type,
                                                       _build_num)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.info("Unhandled exception caught: Adding to log...")
        log.exception(e)
        log.info("Succesfully logged exception: Raising it again...") 
        raise e

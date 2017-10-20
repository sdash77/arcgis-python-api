import sys
import re
import os
import logging
log = logging.getLogger()

#import geosaurus_root/src seperate module
from __init__ import *
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR, "src"))
from arcgis import __version__ as _py_api_version

from automation_setup import automation_setup
from build_conda_package import build_conda_package
from build_docker_image import build_docker_image
from build_documentation import build_documentation
from run_unit_tests import run_unit_tests
from publish_results import publish_results

_master_regex = ".*master.*"
_pull_request_regex = ".*pull.*request.*"
_funcs_to_run_for_arg = [(_master_regex, [automation_setup,
                                          run_unit_tests,
                                          build_documentation,
                                          build_conda_package,
                                          build_docker_image,
                                          publish_results]),
                         (_pull_request_regex, [automation_setup,
                                                run_unit_tests,
                                                build_documentation])]
_automation_type = ""
_build_num = ""
_build_tag = ""

def main():
    _check_and_parse_arguments()
    funcs = _get_functions_to_call_for_cmd_arg()
    for func in funcs:
        func(_get_build_tag())

def _check_and_parse_arguments():
    """Exactly 2 command line argument should be passed to this function"""
    if len(sys.argv) != 3:
        msg = "{} should be called with exactly 2 arg. ".format(sys.argv[0])
        msg += "You called it with args '{}'\n".format(sys.argv[1:])
        msg += "Please provide both args to specify automation to run.\n"
        msg += "(Ex. python jenkins_entry_point {AUTOTYPE} {BUILDNUM})"
        raise RuntimeError(msg)
    else:
        log.info("Arguments passed in: {}".format(sys.argv[1:]))
        global _automation_type, _build_num, _build_tag
        _automation_type = sys.argv[1]
        _build_num = sys.argv[2]
        if _automation_type_matches_regex(_master_regex):
            _build_tag = "geosaurus{}_master_j{}".format(_py_api_version,
                                                         _build_num)
        elif _automation_type_matches_regex(_pull_request_regex):
            _build_tag = "geosaurus{}_dev_j{}".format(_py_api_version,
                                                      _build_num)

def _get_functions_to_call_for_cmd_arg():
    """Depending on what command line argument is passed in, there will be
    different actions that need to be done (master merge requests require
    a docker image being built, whereas pull requests don't. Both require
    a documentation build, etc.). Return what functions need to be called
    depending on what command line argument is passed in"""
    for regex_, funcs in _funcs_to_run_for_arg:
        if _automation_type_matches_regex(regex_):
            return funcs
    msg = "'{}' input argument matches no regex on file: ".format(sys.argv[1])
    msg += "Check the {} file in geosaurus for the regexes".format(sys.argv[0])
    raise RuntimeError(msg)

def _automation_type_matches_regex(regex_):
    return re.match(regex_, _automation_type)

def _get_build_tag():
    if _build_tag:
        return _build_tag
    else:
        return "geosaurus{}_{}_UNSPECIFIED_j{}".format(_py_api_version,
                                                       automation_type,
                                                       _build_num)

if __name__ == "__main__":
    try:
        raise RuntimeError("unhandled")
        main()
    except Exception as e:
        log.exception(e)
        raise e

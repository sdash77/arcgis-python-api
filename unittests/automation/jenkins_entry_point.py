import sys
import re

from build_conda_package import build_conda_package
from build_docker_image import build_docker_image
from build_documentation import build_documentation
from run_unit_tests import run_unit_tests
from publish_results import publish_results

def main():
    _check_arguments()
    funcs = _get_functions_to_call_for_cmd_arg()
    for func in funcs:
        func()

def _check_arguments():
    """Exactly 1 command line argument should be passed to this function"""
    if len(sys.argv) != 2:
        msg = "{} should be called with exactly 1 arg. ".format(sys.argv[0])
        msg += "You called it with args '{}'\n".format(sys.argv[1:])
        raise RuntimeError(msg)
    else:
        print("Argument passed in: {}".format(sys.argv[1]))

def _get_functions_to_call_for_cmd_arg():
    """Depending on what command line argument is passed in, there will be
    different actions that need to be done (master merge requests require
    a docker image being built, whereas pull requests don't. Both require
    a documentation build, etc.). Return what functions need to be called
    depending on what command line argument is passed in"""
    for regex_, funcs in _funcs_to_run_for_arg:
        if _argument_matches_regex(regex_):
            return funcs
    msg = "'{}' input argument matches no regex on file: ".format(sys.argv[1])
    msg += "Check the {} file in geosaurus for the regexes".format(sys.argv[0])
    raise RuntimeError(msg)

def _argument_matches_regex(regex_):
    return re.match(regex_, sys.argv[1])

_funcs_to_run_for_arg = [(".*master.*", [run_unit_tests,
                                         build_documentation,
                                         build_conda_package,
                                         build_docker_image,
                                         publish_results]),
                         (".*pull.*request.*", [run_unit_tests,
                                                build_documentation,
                                                publish_results])]

if __name__ == "__main__":
    main()

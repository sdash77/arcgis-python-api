import os
import sys
import re
import argparse
import shutil
import subprocess
import logging
log = logging.getLogger(__name__)

from __init__ import *

def _main():
    args = _parse_cmd_line_args()
    _setup_logging(args)

    if _no_target_specified(args):
        build_conda_pkg_with_default_meta_yaml()
    elif _all_is_specified_anywhere(args):
        build_conda_pkg_for_all_supported_os_and_py_versions()
    elif _only_python_is_specified(args):
        build_conda_pkg(python_version = args.python)
    elif _only_os_is_specified(args):
        build_conda_pkg(os_build_target = args.os)
    elif _both_os_and_python_are_specified(args):
        build_conda_pkg(os_build_target = args.os,
                        python_version = args.python)
    else:
        args.print_help()
        raise Exception("Incorrect usage: See the --help text and try again")

def _parse_cmd_line_args():
    parser = argparse.ArgumentParser(description = "Builds arcgis conda "\
        "packages for specific O.S. and python versions. Will default to "\
        "using ./meta/default_meta.yaml if you don't specify -o, -p, or --all")
    parser.add_argument("--python", "-p", type=str,
        help="What python version to target for the build (3.5, 3.6, etc.)")
    parser.add_argument("--os", "-o", type=str,
        help="What O.S. to target for the build (linux, windows, etc.)")
    parser.add_argument("--all", action="store_true",
        help="builds for all supported O.S. and python versions")
    parser.add_argument("--verbose", "-v", action="store_true",
        help="Print all DEBUG log msgs (i.e. print 'conda build' cmd output)")
    return parser.parse_args(sys.argv[1:]) #don't use filename as 1st arg

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

def _no_target_specified(args):
    """returns False if at least one of --all, --python, or --os passed in"""
    return (not args.all) and (not args.os) and (not args.python)

def build_conda_pkg_with_default_meta_yaml():
    """Use build/arcgis/default_meta.yaml file as the meta.yaml file that
    the "conda build" process will use"""
    _clear_output_folder()
    _restore_default_meta_yml()
    log.info("Using {} as meta.yaml file...".format(DEFAULT_META_YML_FILE))
    _run_conda_build_command(python_version = DEFAULT_PY)

def _all_is_specified_anywhere(args):
    return args.all

def build_conda_pkg_for_all_supported_os_and_py_versions():
    _clear_output_folder()
    for os in SUPPORTED_OSES:
        for py in SUPPORTED_PYS:
            build_conda_pkg(os_build_target = os,
                            python_version = py,
                            clear_output_folder = False)

def _only_python_is_specified(args):
    return args.python and not args.os

def _only_os_is_specified(args):
    return args.os and not args.python

def _both_os_and_python_are_specified(args):
    return args.os and args.python

def build_conda_pkg(os_build_target = DEFAULT_OS,
                    python_version = DEFAULT_PY,
                    clear_output_folder = True):
    if clear_output_folder:
        _clear_output_folder()
    _check_edge_cases(os_build_target)
    _setup_meta_yaml_file_for(os_build_target)
    _run_conda_build_command(python_version)
    _restore_default_meta_yml()

def _clear_output_folder():
    for full_path in _items_in_dir_to_delete(OUTPUT_DIR,
                                             items_to_ignore = [".gitignore"]):
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)

def _items_in_dir_to_delete(dir_, items_to_ignore=[]):
    return [
        os.path.join(dir_, item)
        for item in os.listdir(dir_)
        if item not in items_to_ignore]

def _check_edge_cases(os_build_target):
    """At the moment, you can only build for windows on a win machine"""
    if (re.match(WINDOWS_REGEX, os_build_target) and 
        re.match(UNIX_REGEX, os.name)):
        #if you are building for windows but your current os is unix
        raise RuntimeError("Building for win on a unix system not supported")

def _setup_meta_yaml_file_for(os_build_target):
    """Copies a meta.yaml file to build/arcgis/ that is needed for the 
    conda-build process. The meta.yaml file is assembled for the target OS
    based off the base_meta.yaml files located in build/env"""
    os_specific_meta_file = os.path.join(
                                 BUILD_DIR,
                                 "meta",
                                 _assemble_folder_name_for_os(os_build_target),
                                 "meta.yaml")
    shutil.copyfile(os_specific_meta_file, ACTIVE_META_YML_FILE)
    log.info("using {} for build process.".format(os_specific_meta_file))

def _assemble_folder_name_for_os(os_build_target):
    if re.match(UNIX_REGEX, os_build_target):
        return "unix"
    if re.match(WINDOWS_REGEX, os_build_target):
        return "windows"
    else:
        raise RuntimeError("{} is not a valid os".format(os_build_target))

def _run_conda_build_command(python_version):
    build_cmd = "cd {build_dir} && "\
                "conda build --py {py_ver} arcgis "\
                "--output-folder {output_dir}"
    if re.match(PY36_REGEX, python_version):
        build_cmd = build_cmd.format(build_dir=BUILD_DIR,
                                     py_ver="3.6",
                                     output_dir=OUTPUT_DIR)
    elif re.match(PY35_REGEX, python_version):
        build_cmd = build_cmd.format(build_dir=BUILD_DIR,
                                     py_ver="3.5",
                                     output_dir=OUTPUT_DIR)
    else:
        raise RuntimeError("{} is not a valid python version for 'conda "\
                           "build' commands".format(python_version))
    _run_shell_cmd(build_cmd)

def _run_shell_cmd(cmd):
    log.info("Currently running cmd '{}'. Output of cmd will be logged after "\
             "it completes. (DEBUG if success, WARN if failure)".format(cmd))
    try:
        byte_output = subprocess.check_output(cmd,
                                              stderr=subprocess.STDOUT,
                                              shell=True)
        log.debug("cmd output => {}".format(byte_output.decode("utf-8")))
    except subprocess.CalledProcessError as e:
        log.warn("cmd failed, returned non-zero code. Output:\n"\
                 "{}".format(e.output.decode("utf-8")))
        raise e

def _restore_default_meta_yml():
    shutil.copyfile(DEFAULT_META_YML_FILE,
                    ACTIVE_META_YML_FILE)

if __name__ == "__main__":
    try:
        _main()
        log.info("Program successfully completed! Exiting....")
    except Exception as e:
        log.exception(e)
        _restore_default_meta_yml()
        log.info("Program did not succesfully complete (unhandled exception)")
        sys.exit(1)

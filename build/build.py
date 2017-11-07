import os
import sys
import re
import argparse
import logging
log = logging.getLogger(__name__)

from __init__ import *

supported_oses = ['win', 'unix']
supported_py = ['3.5', '3.6']
default_py = '3.6'
default_os = os.name

def build_conda_package(cmd_line_args):
    args = _parse_cmd_line_args(cmd_line_args)
    if args.quiet:
        log.setLevel(logging.INFO)
    if args.all:
        _build_conda_package_for_all_supported_platforms()
    elif args.os and args.python:
        build_conda_package_for(os_build_target = args.os,
                                python_version = args.python)
    else:
        log.info("Either no args passed in, or incomplete args passed in. "\
            "Using default args of {} and {}".format(default_os, default_py))
        build_conda_package_for(os_build_target = default_os,
                                python_version = default_py)

def _parse_cmd_line_args(cmd_line_args):
    parser = argparse.ArgumentParser(description = "Builds arcgis conda "\
        "packages for specific O.S. and python versions. Will default to "\
        "your current OS/python 3.6 if you don't specify or call with --all")
    parser.add_argument("--python", "-p", type=str,
        help="What version of python to target for the build (3.6, etc.)")
    parser.add_argument("--os", "-o", type=str,
        help="What O.S. to target for the build (linux, windows, etc.)")
    parser.add_argument("--all", action="store_true",
        help="builds for all supported O.S. and python versions")
    parser.add_argument("-q", "--quiet", action="store_true",
        help="Supress DEBUG log messages from the console")
    args = parser.parse_args(cmd_line_args)
    log.info("args passed in: {}".format(args))
    return args

def _build_conda_package_for_all_supported_platforms():
    for os in supported_os:
        for py in supported_py:
            build_conda_package_for(os_build_target = os,
                                    python_version = py)

py36_regex = ".*3\.?6.*" #will match if '36' or '3.6' is anywhere in string
py35_regex = ".*3\.?5.*" #will match if '35' or '3.5' is anywhere in string
unix_regex = "".join([
             "(?i).*unix.*",#if 'unix' (case insensitive) in string
             "|.*linux.*",  #OR if 'linux' (case insensitive) in string
             "|.*osx.*",    #OR if 'osx' (case insensitive) in string
             "|.*macos.*",  #OR if 'macos' (case insensitive) in string
             "|.*posix.*"]) #OR if 'posix' (case insensitive) in string
windows_regex = "".join([
                "(?i).*win.*", #if 'win' (case insensitive) in string
                ".*nt.*"])     #OR if 'nt' (case insensitive) in string

def build_conda_package_for(os_build_target, python_version):
    _check_edge_cases(os_build_target)
    create_meta_yml_for(os_build_target, python_version)
    run_shell_command(_assemble_conda_build_command_for(python_version))

def _check_edge_cases(os_build_target):
    """At the moment, you can only build for windows on a win machine"""
    if (re.match(windows_regex, os_build_target) and 
        re.match(unix_regex, os.name)):
        #if you are building for windows but your current os is unix
        raise RuntimeError("Building for win on a unix system not supported")

def _assemble_conda_build_command_for(python_version):
    base_conda_build_cmd = "conda build --py {} arcgis --output-folder output"
    if re.match(py36_regex, python_version):
        return base_conda_build_cmd.format("3.6")
    if re.match(py35_regex, python_version):
        return base_conda_build_cmd.format("3.5")
    else:
        raise RuntimeError("{} is not a valid python version for 'conda "\
                           "build' commands".format(python_version))

def create_meta_yml_for(os_build_target, python_version):
    """Creates a meta.yaml file in build/arcgis/ that is needed for the 
    conda-build process. This meta.yaml file is assembled for the target OS
    based off the base_meta.yaml files located in build/env, as well
    as the os-specific enviroment.yml files in build/env"""
    env_file_path = os.path.join(BUILD_DIR,
                                 "env",
                                 _assemble_folder_name_for_os(os_build_target),
                                 _assemble_folder_name_for_py(python_version),
                                 "environment.yml")
    env_file = open(env_file_path, "r")
    base_meta_yaml_file_path = os.path.join(BUILD_DIR,
                                            "env",
                                            "base_meta.yaml")
    base_meta_file = open(base_meta_yaml_file_path, "r")
    output_meta_yaml_file_path = os.path.join(BUILD_DIR,
                                              "arcgis",
                                              "meta.yaml")
    output_metal_file = open(output_meta_yaml_file_path, "w")

def _assemble_folder_name_for_os(os_build_target):
    if re.match(unix_regex, os_build_target):
        return "unix"
    if re.match(windows_regex, os_build_target):
        return "windows"
    else:
        raise RuntimeError("{} is not a valid os".format(os_build_target))

def _assemble_folder_name_for_py(python_version):
    if re.match(py36_regex, python_version):
        return "py36"
    if re.match(py35_regex, python_version):
        return "py35"
    else:
        raise RuntimeError("{} not a valid py version".format(python_version))

if __name__ == "__main__":
    try:
        build_conda_package(sys.argv[1:])
    except Exception as e:
        log.info("Unhandled exception caught: Adding to log...")
        log.exception(e)
        log.info("Succesfully logged exception: Raising it again...") 
        raise e

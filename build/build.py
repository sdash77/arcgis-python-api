#!/usr/bin/env python
"""Build the arcgis python api for any specified os/py, placing the generated
conda packages and pip packages in ./output/. 
Can be run as a standalone script ('python build.py --all') 
or imported as a library ('from build import build_conda_packages')
Run with --help or see README.md for more info."""

import os
import sys
import re
import argparse
import shutil
import platform
import subprocess
import tempfile
from uuid import uuid4
import logging
log = logging.getLogger(__name__)

import yaml

BASE_BUILD_CMD = "cd {build_dir} && conda build arcgis --py {python_version} "\
                 "--output-folder {output_dir}"
BASE_CONVERT_CMD = "conda convert -f -p {os_build_target} {conda_package} "\
                   "-o {output_dir}" 
BASE_INDEX_CMD = "cd {output_dir} && conda index {os_build_target}"
BASE_UPLOAD_CMD = "anaconda upload -f {conda_package}"

#Note that this command alone will place pkgs in src/dist, not build/output
BASE_PIP_BUILD_CMD = "cd {src_dir} && python setup.py sdist"

SUPPORTED_WIN = ['win-32', 'win-64']
SUPPORTED_LINUX = ['linux-32', 'linux-64']
SUPPORTED_OSX = ['osx-64']
SUPPORTED_UNIX = SUPPORTED_LINUX + SUPPORTED_OSX
SUPPORTED_OSES = SUPPORTED_WIN +\
                 SUPPORTED_LINUX +\
                 SUPPORTED_OSX
SUPPORTED_PYS = ['3.5', '3.6', '3.7']
DEFAULT_PYS = SUPPORTED_PYS

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..'))
BUILD_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "build"))
BUILD_OUTPUT_DIR = os.path.abspath(os.path.join(
    BUILD_DIR,
    "output"))
BUILD_OUTPUT_PIP_DIR = os.path.abspath(os.path.join(
    BUILD_OUTPUT_DIR,
    "pip"))
SRC_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "src"))
SRC_DIST_DIR = os.path.abspath(os.path.join(
    SRC_DIR,
    "dist"))
META_YAML_FILE_PATH = os.path.abspath(os.path.join(
    BUILD_DIR,
    "arcgis",
    "meta.yaml"))

def _main():
    args = _parse_cmd_line_args()
    _setup_logging(args)

    if _no_target_specified(args):
        build_conda_packages_default()
    elif _all_is_specified_anywhere(args):
        build_conda_packages_for_all_os_and_py()
        build_pip_package(clear_output_folder = False)
    elif _only_pip_is_specified(args):
        build_pip_package()
        return
    elif _only_python_is_specified(args):
        build_conda_packages(python_versions = args.python,
                             os_build_targets = [ _determine_current_os() ],
                             build_number = args.build_number)
    elif _only_os_is_specified(args):
        build_conda_packages(python_versions = DEFAULT_PYS,
                             os_build_targets = args.os,
                             build_number = args.build_number)
    elif _both_os_and_python_are_specified(args):
        build_conda_packages(os_build_targets = args.os,
                             python_versions = args.python,
                             build_number = args.build_number)
    else:
        args.print_help()
        raise Exception("Incorrect usage: See the --help text and try again")

    if _upload_is_specified_anywhere(args):
        upload_any_conda_packages_in_output_folder()

    if _pip_is_specified_anywhere(args):
        build_pip_package(clear_output_folder = False)

# Running from cmd line setup funcs
def _parse_cmd_line_args():
    parser = argparse.ArgumentParser(description = "Builds arcgis conda "\
        "packages for specified O.S. and python versions. Must have "\
        "conda-build and anaconda-client installed on root conda enviroment. "\
        "Can only build windows conda packages from a windows machine, and "\
        "can only build osx/linux conda packages from a unix machine. "\
        "Generated conda pkgs in ./output/. See ./README.md for more info."\
        "\n - 'python build_conda_package.py' for default build behavior"\
        "\n - 'python build_conda_package.py -p 3.5 3.6 -o osx-64 linux-32' "\
        "for building both py3.5 and py3.6 for both osx-64 and linux-32"\
        "\n - 'python build_conda_package.py --all' for building for all "\
        "platforms and all python versions supported by this system"\
        "\n - 'python build_conda_package.py --upload' for default build "\
        "behavior, plus upload any results to the anaconda cloud",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--python", "-p", type=str, nargs="*",
        help="What python versions to target for conda (3.5, 3.6, etc.)")
    parser.add_argument("--os", "-o", type=str, nargs="*",
        help="What OSes/archs. to target for conda (linux-64, win-32, etc.)")
    parser.add_argument("--all", "-a", action="store_true",
        help="Builds for pip AND all supported conda pkgs for O.S. and py")
    parser.add_argument("--upload", "-u", action="store_true",
        help="Upload conda results to anaconda cloud (Note: anaconda-client "\
             "must be configured on root conda enviroment and 'anaconda "\
             "login' must have been run)")
    parser.add_argument("--pip", "-i", action="store_true",
        help="Build the pip .tar.gz package and place it in ./output/pip")
    parser.add_argument("--verbose", "-v", action="store_true",
        help="Print all DEBUG log msgs (i.e. print 'conda build' cmd output)")
    parser.add_argument("--build-number", "-b", default=0,
        help="What build number int to apply to meta.yaml/output conda pkg.")
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
    log.info("Logging at level {}.".format(logging.getLevelName(log.level)))
    log.debug("args passed in => {}".format(args))

# Human readable cmd arg parsing funcs
def _no_target_specified(args):
    """returns False if >= 1 of --all, --python, --os, --pip passed in"""
    return ((not args.all) and (not args.os) and
            (not args.python) and (not args.pip))

def _all_is_specified_anywhere(args):
    return args.all

def _upload_is_specified_anywhere(args):
    return args.upload

def _only_python_is_specified(args):
    return args.python and not args.os

def _only_os_is_specified(args):
    return args.os and not args.python

def _both_os_and_python_are_specified(args):
    return args.python and args.os

def _pip_is_specified_anywhere(args):
    return args.pip

def _only_pip_is_specified(args):
    return args.pip and not (args.python or args.os or args.upload)

# build conda package funcs (Public facing)
def build_conda_packages_default(clear_output_folder = True):
    """Build for all supported python, don't conda convert"""
    if clear_output_folder:
        _clear_output_folder()
    for python_version in DEFAULT_PYS:
        _run_conda_build_command(python_version = python_version,
                                 output_dir = BUILD_OUTPUT_DIR)

def build_conda_packages_for_all_os_and_py():
    """Will generate conda packages for all supported os and pys"""
    if _is_current_os_windows():
        os_build_targets = SUPPORTED_WIN
    elif _is_current_os_unix():
        os_build_targets = SUPPORTED_UNIX
    else:
        raise RuntimeError("{} is not a supported OS".format(os.name))

    build_conda_packages(os_build_targets = os_build_targets,
                         python_versions = SUPPORTED_PYS)

def build_conda_packages(os_build_targets,
                         python_versions,
                         build_number=0,
                         clear_output_folder = True):
    """Will build conda packages for specified oses, and pys. Places pkgs
    in output folder, will clear output folder if specified. Can only build
    windows conda packages on windows machine, unix packages on unix machines

    os_build_targets: a list of strings of target oses to build for. See
        SUPPORTED_OSES for all supported. Ex: ['win-64', 'linux-32']
    python_versions: a list of strings of python versions to build for. See
        SUPPORTED_PYS for all supported. Ex: ['3.6', '3.5']
    clear_output_folder: bool to toggle if BUILD_OUTPUT_DIR is cleared
    """
    _apply_build_number_to_meta_yaml(build_number)

    if clear_output_folder:
        _clear_output_folder()
    _check_edge_cases(os_build_targets,
                      python_versions)

    for python_version in python_versions:
        with _empty_temp_folder() as tmp_dir:
            _run_conda_build_command(python_version = python_version,
                                     output_dir = tmp_dir)
            _convert_conda_package(conda_package = _find_conda_package(tmp_dir),
                                   os_build_targets = os_build_targets,
                                   output_dir = BUILD_OUTPUT_DIR)
            _copy_noarch_dir(src = tmp_dir, dst = BUILD_OUTPUT_DIR)

    _restore_default_build_number_to_meta_yaml()

# Public facing conda uploading func
def upload_any_conda_packages_in_output_folder():
    """runs the anaconda upload command on any generated .tar.bz2 files
    in the BUILD_OUTPUT_DIR folder.
    """
    log.info("Uploading any conda packages in {}. Make sure anaconda login "\
             "has been run to authenticate your anaconda cloud credentials "\
             "(cryptic errors are thrown otherwise)".format(BUILD_OUTPUT_DIR))
    for root, dirs, files in os.walk(BUILD_OUTPUT_DIR):
        for name in files:
            if ".tar.bz2" in name:
                conda_package_path = os.path.join(root, name)
                _run_conda_upload_command(conda_package = conda_package_path)

# Helper funcs
def _is_windows(os_build_target):
    return os_build_target in SUPPORTED_WIN

def _is_unix(os_build_target):
    return (os_build_target in SUPPORTED_LINUX) or\
           (os_build_target in SUPPORTED_OSX)

def _is_current_os_windows():
    return os.name == "nt"

def _is_current_os_unix():
    return os.name == "posix"

def _clear_output_folder():
    items_to_ignore = [ ".gitignore" ]
    for filtered_item in [ os.path.join(BUILD_OUTPUT_DIR, dir_item)
                           for dir_item in os.listdir(BUILD_OUTPUT_DIR)
                           if dir_item not in items_to_ignore ]:
        if os.path.isdir(filtered_item):
            shutil.rmtree(filtered_item)
        else:
            os.remove(filtered_item)

def _check_edge_cases(os_build_targets,
                      python_versions):
    """check is os_build_targets and python_version are sane, assert building 
    for windows on windows and unix on unix
    """
    for os_build_target in os_build_targets:
        if _is_windows(os_build_target) and _is_current_os_unix():
            #if you are building for windows but your current os is unix
            raise RuntimeError("You're building for {}: Windows pkgs cannot "\
                               "be built on unix sys".format(os_build_targets))
        if _is_unix(os_build_target) and _is_current_os_windows():
            #if you are building for unix but your current os is windows
            raise RuntimeError("You're building for {}: Unix pkgs cannot "\
                               "be built on win sys".format(os_build_targets)) 
        if os_build_target not in SUPPORTED_OSES: 
            raise RuntimeError("{} not supported OS. Supported OSes = "\
                               "{}".format(os_build_target, SUPPORTED_OSES))
    for python_version in python_versions:
        if python_version not in SUPPORTED_PYS:
            raise RuntimeError("{} not supported py. Supported pys = "\
                               "{}".format(python_version, SUPPORTED_PYS))

def _run_conda_build_command(python_version, output_dir):
    _run_shell_cmd(BASE_BUILD_CMD.format(build_dir = BUILD_DIR,
                                         python_version = python_version,
                                         output_dir = output_dir))

def _find_conda_package(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if ".tar.bz2" in name:
                return os.path.join(root, name)

def _convert_conda_package(conda_package, os_build_targets, output_dir):
    for os_build_target in os_build_targets:
        _run_conda_convert_command(conda_package = conda_package,
                                   os_build_target = os_build_target,
                                   output_dir = output_dir)
        _run_conda_index_command(output_dir = output_dir,
                                 os_build_target = os_build_target)

def _run_conda_convert_command(conda_package, os_build_target, output_dir):
    output = _run_shell_cmd(BASE_CONVERT_CMD.format(
                                conda_package = conda_package,
                                os_build_target = os_build_target,
                                output_dir = output_dir))
    if "Skipping conversion" in output:
        #If converting to current platform, the command silent failed and
        #we need to manually copy over the results
        target_folder = os.path.join(output_dir, os_build_target)
        os.makedirs(target_folder, exist_ok=True)
        shutil.copy(conda_package, target_folder)
        log.debug("conda convert didn't complete: manually copied {} to "
                  "{}".format(conda_package, target_folder))

def _run_conda_index_command(output_dir, os_build_target):
    """Generates repodata.json and other metadata files needed for local
    file deployment installation (See 
    https://conda.io/docs/user-guide/tasks/create-custom-channels.html)
    """
    _run_shell_cmd(BASE_INDEX_CMD.format(output_dir = output_dir,
                                         os_build_target = os_build_target))

def build_pip_package(clear_output_folder = True):
    """Build the pip .tar.gz for hosting on pypi servers"""
    if clear_output_folder:
       _clear_output_folder() 
    _run_shell_cmd(BASE_PIP_BUILD_CMD.format(src_dir = SRC_DIR))
    if os.path.exists(BUILD_OUTPUT_PIP_DIR):
        shutil.rmtree(BUILD_OUTPUT_PIP_DIR)
    shutil.copytree(SRC_DIST_DIR, BUILD_OUTPUT_PIP_DIR)

def _copy_noarch_dir(src, dst):
    noarch_dir_src = os.path.join(src, "noarch")
    noarch_dir_dst = os.path.join(dst, "noarch")
    if not os.path.isdir(noarch_dir_dst):
        shutil.copytree(noarch_dir_src, noarch_dir_dst)

def _run_conda_upload_command(conda_package):
    _run_shell_cmd(BASE_UPLOAD_CMD.format(conda_package = conda_package))

def _run_shell_cmd(cmd):
    """Runs a shell cmd on linux, osx, or windows. Outputs results to log"""
    log.info("Currently running cmd '{}'. After it completes, output will "\
             "be logged to DEBUG if success, WARN if failure".format(cmd))
    try:
        byte_output = subprocess.check_output(cmd,
                                              stderr=subprocess.STDOUT,
                                              shell=True)
        str_output = byte_output.decode("utf-8")
        log.debug("cmd output => {}".format(str_output))
        return str_output
    except subprocess.CalledProcessError as e:
        log.warn("cmd failed, returned non-zero code. Output:\n"\
                 "{}".format(e.output.decode("utf-8")))
        raise e

class _empty_temp_folder:
    """Use with "with" syntax like "with empty_temp_folder() as tmp:"
    Creates a temporary folder and deletes it after finished being used
    """
    def __enter__(self):
        self.temp_folder = os.path.join(tempfile.gettempdir(),
                                        ".{}".format(uuid4()))
        os.makedirs(self.temp_folder)
        return self.temp_folder

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.temp_folder)

def _determine_current_os():
    """Returns string representing current os in conda format (ex. 'win-64')"""
    target_os = ""
    system = platform.system().lower()
    if "darwin" in system:
        target_os = "osx"
    elif "window" in system:
        target_os = "win"
    elif "linux" in system:
        target_os = "linux"
    is_64_bit = platform.machine().endswith('64')
    architecture = "64" if is_64_bit else "32"
    return "{target_os}-{architecture}".format(target_os = target_os,
                                               architecture = architecture)

def _apply_build_number_to_meta_yaml(build_number: int):
    meta_yaml = {}
    with open(META_YAML_FILE_PATH, "r") as f:
        meta_yaml = yaml.load(f)
        meta_yaml["build"]["number"] = str(build_number)
    with open(META_YAML_FILE_PATH, "w") as f:
        yaml.dump(meta_yaml, f, default_flow_style=False)

def _restore_default_build_number_to_meta_yaml():
    _apply_build_number_to_meta_yaml(0)

if __name__ == "__main__":
    try:
        _main()
        log.info("Program successfully completed! Any generated packages in "\
                 "{}. Exiting....".format(BUILD_OUTPUT_DIR))
    except Exception as e:
        log.exception(e)
        log.info("Program did not succesfully complete (unhandled exception)")
        sys.exit(1)

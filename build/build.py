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

BASE_BUILD_CMD = "cd {build_dir} && conda build arcgis --py {python_version} "\
                 "--output-folder {output_dir}"

BASE_CONVERT_CMD = "conda convert -f -p {os_build_target} {conda_package} "\
                   "-o {output_dir}" 

SUPPORTED_WIN = ['win-32', 'win-64']
SUPPORTED_LINUX = ['linux-32', 'linux-64']
SUPPORTED_OSX = ['osx-64']

SUPPORTED_OSES = SUPPORTED_WIN +\
                 SUPPORTED_LINUX +\
                 SUPPORTED_OSX

SUPPORTED_PYS = ['3.5', '3.6']
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

DEFAULT_META_YML_FILE = os.path.abspath(os.path.join(
    BUILD_DIR,
    "meta",
    "default_meta.yaml"))

ACTIVE_META_YML_FILE = os.path.abspath(os.path.join(
    BUILD_DIR,
    "arcgis",
    "meta.yaml"))

def _main():
    args = _parse_cmd_line_args()
    _setup_logging(args)

    if _no_target_specified(args):
        build_conda_pkg_with_default_meta_yaml()
    elif _all_is_specified_anywhere(args):
        build_conda_packages_for_all_os_and_py()
    elif _only_python_is_specified(args):
        build_conda_packages(python_versions = args.python,
                             os_build_targets = [ _determine_current_os() ])
    elif _only_os_is_specified(args):
        build_conda_packages(python_versions = DEFAULT_PYS,
                             os_build_targets = args.os)
    elif _both_os_and_python_are_specified(args):
        build_conda_packages(os_build_targets = args.os,
                             python_versions = args.python)
    else:
        args.print_help()
        raise Exception("Incorrect usage: See the --help text and try again")

def _parse_cmd_line_args():
    parser = argparse.ArgumentParser(description = "Builds arcgis conda "\
        "packages for specified O.S. and python versions. Will use ./meta/"\
        "default_meta.yaml if -o, -p, or -a aren't specified. Must have "\
        "conda-build and anaconda-client installed on root conda enviroment. "\
        "See ./README.md in this directory for more information. \n "\
        "\n - 'python build_conda_package.py' for default build behavior"\
        "\n - 'python build_conda_package.py -p 3.5 3.6 -o win-32 linux-64' "\
        "for building both py3.5 and py3.6 for both win-32 and linux-64"\
        "\n - 'python build_conda_package.py --all' for building for all "\
        "platforms and all python versions"\
        "\n - 'python build_conda_package.py --upload' for default build "\
        "behavior, plus upload any results to the anaconda cloud",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--python", "-p", type=str, nargs="*",
        help="What python versions to target (3.5, 3.6, etc.)")
    parser.add_argument("--os", "-o", type=str, nargs="*",
        help="What OSes and architectures to target (linux-64, win-32, etc.)")
    parser.add_argument("--all", "-a", action="store_true",
        help="Builds for all supported O.S. and python versions")
    parser.add_argument("--upload", "-u", action="store_true",
        help="Upload results to anaconda cloud (Note: anaconda-client must "\
             "be configured on root conda enviroment)")
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
    log.debug("Logging set up: args passed in => {}".format(args))

def _no_target_specified(args):
    """returns False if at least one of --all, --python, or --os passed in"""
    return (not args.all) and (not args.os) and (not args.python)

def build_conda_pkg_with_default_meta_yaml():
    """Use build/arcgis/default_meta.yaml file as the meta.yaml file that
    the "conda build" process will use. Build for all supported python"""
    _clear_output_folder()
    _restore_default_meta_yml()
    log.info("Using {} as meta.yaml file...".format(DEFAULT_META_YML_FILE))
    for python_version in DEFAULT_PYS:
        _run_conda_build_command(python_version = python_version,
                                 output_dir = BUILD_OUTPUT_DIR)

def _all_is_specified_anywhere(args):
    return args.all

def _only_python_is_specified(args):
    return args.python and not args.os

def _only_os_is_specified(args):
    return args.os and not args.python

def _both_os_and_python_are_specified(args):
    return args.python and args.os

def build_conda_packages_for_all_os_and_py():
    build_conda_packages(os_build_targets = SUPPORTED_OSES,
                         python_versions = SUPPORTED_PYS)

def build_conda_packages(os_build_targets,
                         python_versions,
                         clear_output_folder = True):
    if clear_output_folder:
        _clear_output_folder()
    _check_edge_cases(os_build_targets,
                      python_versions)
    unix_oses, win_oses = _split_oses_to_unix_and_win(os_build_targets)

    if unix_oses:
        _setup_meta_yaml_file_for("unix")
        _run_and_convert(os_build_targets = unix_oses,
                         python_versions = python_versions)
    if win_oses:
        _setup_meta_yaml_file_for("windows")
        _run_and_convert(os_build_targets = win_oses,
                         python_versions = python_versions)
    
    _restore_default_meta_yml()

def _run_and_convert(os_build_targets, python_versions):
    for python_version in python_versions:
        with empty_temp_folder() as tmp_dir:
            _run_conda_build_command(python_version = python_version,
                                     output_dir = tmp_dir)
            _convert_conda_package(conda_package = _find_conda_package(tmp_dir),
                                   os_build_targets = os_build_targets,
                                   output_dir = BUILD_OUTPUT_DIR)

def _split_oses_to_unix_and_win(os_build_targets):
    unix = []
    win = []
    for os in os_build_targets:
        if _is_unix(os):
            unix.append(os)
        elif _is_windows(os):
            win.append(os)
    return unix, win

def _is_windows(os_build_target):
    return os_build_target in SUPPORTED_WIN

def _is_unix(os_build_target):
    return (os_build_target in SUPPORTED_LINUX) or\
           (os_build_target in SUPPORTED_OSX)

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
    """At the moment, you can only build for windows on a win machine"""
    for os_build_target in os_build_targets:
        if _is_windows(os_build_target) and os.name == "posix":
            #if you are building for windows but your current os is unix
            raise RuntimeError("You're building for {}: Windows pkgs cannot "\
                               "be built on unix sys".format(os_build_targets))
        if os_build_target not in SUPPORTED_OSES: 
            raise RuntimeError("{} not supported OS. Supported OSes = "\
                               "{}".format(os_build_target, SUPPORTED_OSES))
    for python_version in python_versions:
        if python_version not in SUPPORTED_PYS:
            raise RuntimeError("{} not supported py. Supported pys = "\
                               "{}".format(python_version, SUPPORTED_PYS))


def _setup_meta_yaml_file_for(os_folder_name):
    os_specific_meta_file = os.path.join(
                                 BUILD_DIR,
                                 "meta",
                                 os_folder_name,
                                 "meta.yaml")
    shutil.copyfile(os_specific_meta_file, ACTIVE_META_YML_FILE)
    log.info("using {} file for build.".format(os_specific_meta_file))

def _run_conda_build_command(python_version,
                             output_dir):
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
        dir_containing_conda_package = os.path.dirname(conda_package)
        _copy_repodata_files(src = dir_containing_conda_package,
                             dst = os.path.join(output_dir, os_build_target))

def _run_conda_convert_command(conda_package, os_build_target, output_dir):
    output = _run_shell_cmd(BASE_CONVERT_CMD.format(
                                conda_package = conda_package,
                                os_build_target = os_build_target,
                                output_dir = output_dir))
    if "Skipping conversion" in output:
        #If converting to current platform, cmd will silent fail and skip
        target_folder = os.path.join(output_dir, os_build_target)
        os.makedirs(target_folder)
        shutil.copy(conda_package, target_folder)
        log.debug("conda convert didn't complete: manually copied {} to "
                  "{}".format(conda_package, target_folder))
        
def _copy_repodata_files(src, dst):
    for root, dirs, files in os.walk(src):
        for name in files:
            if "repodata" in name:
                found_repodata_file = os.path.join(root, name)
                log.debug("moving repodata {}".format(found_repodata_file))
                shutil.copy(found_repodata_file, dst)

def _run_shell_cmd(cmd):
    log.info("Currently running cmd '{}'. Output of cmd will be logged after "\
             "it completes. (DEBUG if success, WARN if failure)".format(cmd))
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

def _restore_default_meta_yml():
    shutil.copyfile(DEFAULT_META_YML_FILE,
                    ACTIVE_META_YML_FILE)

class empty_temp_folder:
    """Use with "with" syntax like "with empty_temp_folder() as tmp:"
    Creates a temporary folder and deletes it after finished being used"""
    def __enter__(self):
        self.temp_folder = os.path.join(tempfile.gettempdir(),
                                   ".{}".format(hash(os.times())))
        os.makedirs(self.temp_folder)
        return self.temp_folder

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.temp_folder)

def _determine_current_os():
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
if __name__ == "__main__":
    try:
        _main()
        log.info("Program successfully completed! Exiting....")
    except Exception as e:
        log.exception(e)
        _restore_default_meta_yml()
        log.info("Program did not succesfully complete (unhandled exception)")
        sys.exit(1)

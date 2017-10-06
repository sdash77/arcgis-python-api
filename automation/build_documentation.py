import os 
import subprocess

from __init__ import GEOSAURUS_ROOT_DIR, STAGING_DIR

DOCS_DIR = os.path.abspath(os.path.join(GEOSAURUS_ROOT_DIR, "docs"))

def build_documentation():
    """Detects what OS is being used, runs the appropriate 'make' mechanism
    in the ../docs/ folder. The resulting compiled html is then located in
    ./staging folder. (NOTE: Running this script multiple times will
    overwrite the previous generated documentation. Please move all files
    out of the ./staging folder (see the publish functions in this dir)"""
    
    print("Starting to build the documentation...")

    if os.name == 'posix':
        _build_doc_for_unix()
    elif os.name == 'nt':
        _build_doc_for_windows()
    else:
        raise RuntimeError("Doc building not supported on this platform")

    print("Documentation building finished! Any results in {}".format(
        os.path.join(GEOSAURUS_ROOT_DIR, 'automation', 'staging')))

def _build_doc_for_unix():
    print("Building for *nix system...")
    make_command = "make singlehtml"
    flag_to_force_output_to_staging_dir = "BUILDDIR={}".format(STAGING_DIR)
    final_bash_command = "cd {} && {} {}".format(
            DOCS_DIR,
            make_command,
            flag_to_force_output_to_staging_dir)

    _run_sys_command(final_bash_command)

def _build_doc_for_windows():
    print("Building for Windows system...")
    bat_make_command = ".\make.bat singlehtml"
    flag_to_force_output_to_staging_dir = STAGING_DIR
    final_make_command = 'cd "{}" && {} {}'.format(
            DOCS_DIR,
            bat_make_command,
            flag_to_force_output_to_staging_dir)

    _run_sys_command(final_make_command)

def _run_sys_command(cmd):
    print("About to run the following command: '{}'".format(cmd))
    subprocess.check_call(cmd, shell=True)

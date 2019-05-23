import os 
import subprocess
import logging
log = logging.getLogger()

from automation._common import *
from automation.documentation.undocumentation_stats import get_undoc_stats
DOCS_DIR = os.path.abspath(os.path.join(GEOSAURUS_ROOT_DIR, 
                                        "docs", "api_ref"))
infile = os.path.abspath(os.path.join(STAGING_DIR,
                                        "coverage", "undoc.pickle"))
outfile = os.path.abspath(os.path.join(STAGING_DIR, 
                                        "undocumented.txt"))

def build_documentation(*args, **kwargs):
    """Detects what OS is being used, runs the appropriate 'make' mechanism
    in the ../docs/ folder. The resulting compiled html is then located in
    ./staging folder. (NOTE: Running this script multiple times will
    overwrite the previous generated documentation. Please move all files
    out of the ./staging folder (see the publish functions in this dir)"""
    
    log.info("Starting to build the documentation...")

    if os.name == 'posix':
        _build_doc_coverage_for_unix()
        _build_doc_for_unix()
    elif os.name == 'nt':
        _build_doc_coverage_for_windows()
        _build_doc_for_windows()
    else:
        raise RuntimeError("Doc building not supported on this platform")

    log.info("Documentation building finished! Any results in {}".format(
        STAGING_DIR))

def _build_doc_for_unix():
    log.info("Building for *nix system...")
    make_command = "make html"
    flag_to_force_output_to_staging_dir = "BUILDDIR={}".format(STAGING_DIR)
    final_bash_command = "cd {} && {} {}".format(
            DOCS_DIR,
            make_command,
            flag_to_force_output_to_staging_dir)

    run_shell_command(final_bash_command)

def _build_doc_coverage_for_unix():
    log.info("Building for *nix system...")
    make_command = "make coverage"
    flag_to_force_output_to_staging_dir = "BUILDDIR={}".format(STAGING_DIR)
    final_bash_command = "cd {} && {} {}".format(
            DOCS_DIR,
            make_command,
            flag_to_force_output_to_staging_dir)

    run_shell_command(final_bash_command)
    get_undoc_stats(infile, outfile)

def _build_doc_for_windows():
    log.info("Building for Windows system...")
    bat_make_command = ".\make.bat html"
    flag_to_force_output_to_staging_dir = STAGING_DIR
    final_make_command = 'cd "{}" && {} {}'.format(
            DOCS_DIR,
            bat_make_command,
            flag_to_force_output_to_staging_dir)

    run_shell_command(final_make_command)

def _build_doc_coverage_for_windows():
    log.info("Building for Windows system...")
    bat_make_command = ".\make.bat coverage"
    flag_to_force_output_to_staging_dir = STAGING_DIR
    final_make_command = 'cd "{}" && {} {}'.format(
            DOCS_DIR,
            bat_make_command,
            flag_to_force_output_to_staging_dir)

    run_shell_command(final_make_command)
    get_undoc_stats(infile, outfile)

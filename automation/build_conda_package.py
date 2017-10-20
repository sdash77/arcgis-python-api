import os
import subprocess
from glob import glob
import shutil
import logging
log = logging.getLogger()

from __init__ import *

def build_conda_package(*args, **kwargs):
    build_tag = args[0]
    if os.name == 'posix':
        raise RuntimeError("Conda building not supported on *nix systems")
    elif os.name == 'nt':
        _build_conda_for_windows(build_tag)
    else:
        raise RuntimeError("Conda building not supported on this platform")

    log.info("Conda building finished! Any results in {}".format(
        os.path.join(GEOSAURUS_ROOT_DIR, 'automation', 'staging')))

def _build_conda_for_windows(build_tag):
    log.info("Building for Windows system...")
    bat_build_command = "buildanduploadarcgis"
    flag_to_change_build_tag = build_tag
    final_make_command = 'cd "{}" && {} {}'.format(
            BUILD_DIR,
            bat_build_command,
            flag_to_change_build_tag)

    run_shell_command(final_make_command)
    _move_output_to_staging(build_tag)
    _add_to_linux_build_name(build_tag)

def _move_output_to_staging(build_tag):
    output_dir_of_conda_packages = os.path.join(BUILD_DIR, "___output")
    shutil.copytree(output_dir_of_conda_packages,
                    os.path.join(STAGING_DIR, "conda_builds"))
    log.info("moved {} contents to {}...".format(output_dir_of_conda_packages,
                                                 STAGING_DIR))

def _add_to_linux_build_name(str_):
    """Supports adding an arbitrary string to the conda package name
    so as to differentiate between packages hosted on server"""
    linux_conda_dir = os.path.join(STAGING_DIR,"conda_builds","linux-64")
    for original_filename in os.listdir(linux_conda_dir):
        name, ext = os.path.splitext(original_filename)
        renamed_filename = "{}{}{}".format(name, str_, ext)
        os.rename(os.path.join(linux_conda_dir, original_filename),
                  os.path.join(linux_conda_dir, renamed_filename))

if __name__ == "__main__":
    build_conda_package("UNSPECIFIED_VERSION")

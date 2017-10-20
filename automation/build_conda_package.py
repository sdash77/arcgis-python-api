import os
import subprocess
from glob import glob
import shutil
import re
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
    _rename_linux_build_using(build_tag)

def _move_output_to_staging(build_tag):
    output_dir_of_conda_packages = os.path.join(BUILD_DIR, "___output")
    shutil.copytree(output_dir_of_conda_packages,
                    os.path.join(STAGING_DIR, "conda_builds"))
    log.info("moved {} contents to {}...".format(output_dir_of_conda_packages,
                                                 STAGING_DIR))

def _rename_linux_build_using(build_tag):
    """Supports adding the build tag to the conda package name
    so as to differentiate between packages hosted on server"""
    linux_conda_dir = os.path.join(STAGING_DIR,"conda_builds","linux-64")

    for original_filename in os.listdir(linux_conda_dir):
        root, ext = _split_extension(original_filename)
        py_version = _get_py_version_section_of_filename(root)
        renamed_filename = "{}_{}{}".format(build_tag, py_version, ext)
        
        os.rename(os.path.join(linux_conda_dir, original_filename),
                  os.path.join(linux_conda_dir, renamed_filename))

def _split_extension(filename):
    """os.path.splitext doesn't support .tar.bz2, other double extensions"""
    DOUBLE_EXTENSIONS = ['tar.gz','tar.bz2']
    root, ext = os.path.splitext(filename)
    if any([filename.endswith(x) for x in DOUBLE_EXTENSIONS]):
        root, first_ext = os.path.splitext(root)
        ext = first_ext + ext
    return root, ext

def _get_py_version_section_of_filename(filename):
    output = ""
    for filename_section in re.split("-|_", filename):
        output += filename_section if "py" in filename_section else ""
    return output

if __name__ == "__main__":
    build_conda_package("UNSPECIFIED_VERSION")

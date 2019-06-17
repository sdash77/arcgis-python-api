import os
import subprocess
from glob import glob
import shutil
import re
import logging
log = logging.getLogger()

from automation._common import *

#import python package from the BUILD_DIR dir
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR))
from build import build

def build_conda_package(build_number, *args, **kwargs):
    build.build_conda_packages_for_all_os_and_py(build_number = build_number)
    _move_output_to_staging()   

def _move_output_to_staging():
    output_dir_of_conda_packages = os.path.join(BUILD_DIR, "output")
    shutil.copytree(output_dir_of_conda_packages,
                    os.path.join(STAGING_DIR, 'conda_builds'))
    log.info("moved {} contents to {}...".format(output_dir_of_conda_packages,
                                                 STAGING_DIR))

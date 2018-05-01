import os
import subprocess
from glob import glob
import shutil
import re
import logging
log = logging.getLogger()

from automation._common import *
try:
    #import python package from the BUILD_DIR dir
    sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR))
    from build import build
except Exception:
    log.warn("Couldn't import 'build' from {}. Attempting to continue..."\
             "".format(GEOSAURUS_ROOT_DIR))

def build_pip_package(*args, **kwargs):
    build.build_pip_package()
    _move_output_to_staging()   

def _move_output_to_staging():
    output_dir_of_pip_package = os.path.join(BUILD_DIR, "output", "pip")
    shutil.copytree(output_dir_of_pip_package,
                    os.path.join(STAGING_DIR, 'pip_builds'))
    log.info("moved {} contents to {}...".format(output_dir_of_pip_package,
                                                 STAGING_DIR))

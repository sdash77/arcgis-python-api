import os
import sys
import shutil
import logging
log = logging.getLogger()

from __init__ import STAGING_DIR
#import python package from the BUILD_DIR dir
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR))
from build import build

def publish_results(*args, **kwargs):    
    log.info("About to publish results to local fileshare...")
    build_tag = args[0]
    if os.name == 'posix':
        raise RuntimeError("Conda building not supported on unix systems")
    elif os.name == 'nt':
        publish_dir_win = r"C:\Users\Public\conda_packages\{}".format(build_tag)
        shutil.copytree(os.path.join(STAGING_DIR, "conda_builds"),
                                     publish_dir_win)
    log.info("About to publish results to anaconda cloud...")
    build.upload_any_conda_packages_in_output_folder()

import os
import shutil
import logging
log = logging.getLogger()

from __init__ import STAGING_DIR

def publish_results(*args, **kwargs):    
    log.info("About to publish results...")
    build_tag = args[0]
    if os.name == 'posix':
        raise RuntimeError("Conda building not supported on *nix systems")
    elif os.name == 'nt':
        publish_dir_win = r"C:\Users\Public\conda_packages\{}".format(build_tag)
        shutil.copytree(os.path.join(STAGING_DIR, "conda_builds"), publish_dir_win)      

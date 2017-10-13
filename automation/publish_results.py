import os
import shutil

from __init__ import STAGING_DIR

def publish_results(*args, **kwargs):    
    build_tag = args[0]
    if os.name == 'posix':
        raise RuntimeError("Conda building not supported on *nix systems")
    elif os.name == 'nt':
        publish_dir_win = r"C:\Users\Public\conda_packages\{}".format(build_tag)
        shutil.copy_tree(os.path.join(STAGING_DIR, build_tag), publish_dir_win)      

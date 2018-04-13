import os 
import subprocess
import shutil
import logging
log = logging.getLogger()

from automation._common import *
def automation_setup(*args, **kwargs):
    """Clears results Installs correct packages, builds geosaurus source"""
    log.info("Starting setup...")
    _clear_staging_folder([".gitignore", "log.log"])
    log.info("Setup complete!")

def _clear_staging_folder(files_to_ignore):
    for full_path in _paths_in_dir_to_delete(STAGING_DIR, files_to_ignore):
        if os.path.isdir(full_path):
            shutil.rmtree(full_path, ignore_errors=True)
        else:
            os.remove(full_path)

def _paths_in_dir_to_delete(dir_, files_to_ignore):
    return [
        os.path.join(dir_, item)
        for item in os.listdir(dir_)
        if item not in files_to_ignore]

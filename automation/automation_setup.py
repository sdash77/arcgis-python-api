import os 
import subprocess
import shutil
import logging
log = logging.getLogger()

from __init__ import * 

def automation_setup(*args, **kwargs):
    """Clears results Installs correct packages, builds geosaurus source"""
    log.info("Starting setup...")
    _clear_staging_folder([".gitignore", "log.log"])
    _install_correct_packages()
    _install_geosaurus_src()
    log.info("Setup complete!")

def _clear_staging_folder(files_to_ignore):
    for full_path in _paths_in_dir_to_delete(STAGING_DIR, files_to_ignore):
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)

def _paths_in_dir_to_delete(dir_, files_to_ignore):
    return [
        os.path.join(dir_, item)
        for item in os.listdir(dir_)
        if item not in files_to_ignore]

def _install_correct_packages():
    run_shell_command("pip install xmlrunner")
    run_shell_command("conda install -c conda-forge ipywidgets")

def _install_geosaurus_src():
   run_shell_command("pip install -e {}".format(
        os.path.join(GEOSAURUS_ROOT_DIR,"src")))
 
if __name__ == "__main__":
    try:
        automation_setup()
    except Exception as e:
        log.exception(e)

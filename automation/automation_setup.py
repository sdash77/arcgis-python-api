import os 
import shutil
import subprocess
import glob
import logging
log = logging.getLogger()

from __init__ import * 

def automation_setup(*args, **kwargs):
    """Clears results Installs correct packages, builds geosaurus source"""
    log.info("Starting setup...")
    _clear_staging_folder()
    _install_correct_packages()
    _install_geosaurus_src()
    log.info("Setup complete!")

def _clear_staging_folder():
    shutil.move(os.path.join(STAGING_DIR, ".gitignore"),
                os.path.join(STAGING_DIR, "..", ".gitignore"))
    shutil.rmtree(STAGING_DIR)
    os.makedirs(STAGING_DIR)
    shutil.move(os.path.join(STAGING_DIR, "..", ".gitignore"),
                os.path.join(STAGING_DIR, ".gitignore"))

def _install_correct_packages():
    run_shell_command("pip install xmlrunner")

def _install_geosaurus_src():
   run_shell_command("pip install -e {}".format(
        os.path.join(GEOSAURUS_ROOT_DIR,"src")))
 
if __name__ == "__main__":
    try:
        automation_setup()
    except Exception as e:
        log.exception(e)

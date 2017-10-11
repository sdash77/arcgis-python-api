import os 
import shutil
import subprocess

from __init__ import GEOSAURUS_ROOT_DIR, STAGING_DIR

def automation_setup():
    """Clears results Installs correct packages, builds geosaurus source"""
    print("Starting setup...")
    _clear_staging_folder()
    _install_correct_packages()
    _install_geosaurus_src()
    print("Setup complete!")

def _clear_staging_folder():
    folders_to_delete = ["singlehtml", "doctrees", "test-results"]
    for folder_name in folders_to_delete:
        shutil.rmtree(os.path.join(STAGING_DIR, folder_name),
                      ignore_errors=True)

def _install_correct_packages():
    _run_sys_command("pip install xmlrunner")
    _run_sys_command("conda install -c conda-forge ipywidgets -y")
    _run_sys_command("conda install pandas -y")
 
def _install_geosaurus_src():
   _run_sys_command("pip install -e {}".format(
        os.path.join(GEOSAURUS_ROOT_DIR,"src")))
 
def _run_sys_command(cmd):
    print("About to run the following command: '{}'".format(cmd))
    subprocess.check_call(cmd, shell=True)

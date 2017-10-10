import os 
import subprocess

from __init__ import GEOSAURUS_ROOT_DIR

def geosaurus_setup():
    """Installs correct packages, builds geosaurus source"""
    
    print("Setting up the geosaurus repository...")
    _run_sys_command("pip install xmlrunner")
    _run_sys_command("conda install -c conda-forge ipywidgets -y")
    _run_sys_command("conda install pandas -y")
    _run_sys_command("pip install -e {}".format(
        os.path.join(GEOSAURUS_ROOT_DIR,"src")))
    print("Success! Dependencies installed and source built")

def _run_sys_command(cmd):
    print("About to run the following command: '{}'".format(cmd))
    subprocess.check_call(cmd, shell=True)

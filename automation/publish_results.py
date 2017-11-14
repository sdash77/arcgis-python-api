import os
import sys
import shutil
import logging
log = logging.getLogger()

from __init__ import *
#import python package from the BUILD_DIR dir
sys.path.append(os.path.join(GEOSAURUS_ROOT_DIR))
from build import build

def publish_results(*args, **kwargs):
    build_tag = args[0]
    _publish_to_fileshare(build_tag)
    _publish_to_conda_cloud()

def _publish_to_fileshare(build_tag):
    log.info("About to publish results to local fileshare...")
    if os.name == 'posix':
        raise RuntimeError("Conda building not supported on unix systems")
    elif os.name == 'nt':
        publish_dir_win = r"C:\Users\Public\conda_packages\{}".format(build_tag)
        shutil.copytree(os.path.join(STAGING_DIR, "conda_builds"),
                                     publish_dir_win)
def _publish_to_conda_cloud():
    log.info("About to publish results to anaconda cloud...")
    _clear_arcgispyapibot_conda_packages()
    build.upload_any_conda_packages_in_output_folder()

def _clear_arcgispyapibot_conda_packages():
    """https://anaconda.org/ArcGISPyAPIBot/arcgis contains http://zion/'s
    outputted conda packages. We should be clearing them before uploading
    any new ones.
    This command will silently fail if 1) ArcGISPyAPIBot/arcgis  doesn't exit 
    or 2) if the anaconda login username isn't ArcGISPyAPIBot"""
    run_shell_command("anaconda remove ArcGISPyAPIBot/arcgis --force") 

if __name__ == "__main__":
    publish_results("NOT_SPECIFIED")

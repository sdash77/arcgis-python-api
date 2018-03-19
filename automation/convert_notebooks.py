import os
import shutil
import logging
log = logging.getLogger()

from __init__ import *

#import bld_sdk seperate module for notebook conversion
sys.path.insert(0, os.path.join(BUILD_DIR, "bld_sdk"))
from export_guide_samples_nb import export_notebooks

def convert_notebooks(notebooks_root_dir, *args, **kwargs):
    """Converts notebooks, outputs them to the staging folder.
    Takes all images and outputs them to staging folder.
    Staging folder should mimic structure of the arcgis-for-developers repo
    """
    _convert_notebooks_to_html(notebooks_root_dir)
    _copy_imgs_to_staging(notebooks_root_dir)
    _copy_remaining_files(notebooks_root_dir)

def _convert_notebooks_to_html(notebooks_root_dir):
    """Converts all .ipynb files to html, outputs to STAGING"""
    log.info("Converting notebooks to HTML, putting in STAGING...")
    guide_notebook_dir = os.path.join(notebooks_root_dir, "guide")
    samples_notebook_dir = os.path.join(notebooks_root_dir, "samples")

    guide_html_dir = os.path.join(STAGING_DIR,
                                  "src", "python", "guide")
    samples_html_dir = os.path.join(STAGING_DIR,
                                  "src", "python", "sample-notebooks")
    _make_dirs([guide_html_dir, samples_html_dir])

    with set_stdout_log_to(logging.WARNING):
        export_notebooks(guide_notebook_dir, guide_html_dir,
                         replace_img_path = True)
        export_notebooks(samples_notebook_dir, samples_html_dir,
                         replace_img_path = True)

def _make_dirs(list_of_dirs):
    for dir_ in list_of_dirs:
        if not os.path.isdir(dir_):
            os.makedirs(dir_)

def _copy_imgs_to_staging(notebooks_root_dir):
    """Moves all images from notebooks folder to correct folder in STAGING"""
    log.info("Copying image files from notebooks dir to STAGING...")
    img_src_dir = os.path.join(notebooks_root_dir, "static", "img")
    img_html_dir = os.path.join(STAGING_DIR,
                                "src", "assets", "img", "python-graphics")
    shutil.copytree(img_src_dir, img_html_dir)

def _copy_remaining_files(notebooks_root_dir):
    """Copy any remaining files needed that aren't notebooks/img (index.md, 
    etc.) as well as html files you want to override converted notebooks with.
    """
    dev_site_subdir = os.path.join(notebooks_root_dir, "static", "dev_site")
    log.info("recursive copy of {} to STAGING...".format(dev_site_subdir))
    recursive_file_copy(src_dir_root = dev_site_subdir,
                        dst_dir_root = STAGING_DIR,
                        files_to_ignore=["log.log", ".gitignore"])

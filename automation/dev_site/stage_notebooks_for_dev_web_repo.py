import sys
import os
import shutil
import logging
log = logging.getLogger()

from automation._common import *
from automation.dev_site._export_guide_samples_nb import export_notebooks

def stage_notebooks_for_dev_web_repo(notebooks_root_dir,
                 output_dir=os.path.join(STAGING_DIR, "arcgis-for-developers"),
                 log_func = log.debug, #what export_notebooks uses to log
                 *args, **kwargs):
    """Converts notebooks, outputs them to the staging folder.
    Takes all images and outputs them to staging folder.
    Takes the dev-site-overrides folder and outputs to staging.
    At the end, ./staging/arcgis-for-developers should mimic structure of the
    arcgis-for-developers repo with all new changes from notebooks
    """
    _make_dirs([output_dir])
    _convert_notebooks_to_html(notebooks_root_dir, output_dir, log_func)
    _copy_imgs(notebooks_root_dir, output_dir)
    _copy_videos(notebooks_root_dir, output_dir)

def _convert_notebooks_to_html(notebooks_root_dir, output_dir, log_func):
    """Converts all .ipynb files to html, outputs to STAGING"""
    log.info(f"Converting notebooks to HTML, putting in {output_dir}")
    guide_notebook_dir = os.path.join(notebooks_root_dir, "guide")
    samples_notebook_dir = os.path.join(notebooks_root_dir, "samples")
    items_metadata_yaml_path = os.path.join(notebooks_root_dir, "items_metadata.yaml")

    guide_html_dir = os.path.join(output_dir,
                                  "src", "python", "guide")
    samples_html_dir = os.path.join(output_dir,
                                  "src", "python", "sample-notebooks")
    _make_dirs([guide_html_dir, samples_html_dir])

    export_notebooks(guide_notebook_dir, guide_html_dir,
                     embed_try_it_live = False,
                     replace_img_path = True,
                     replace_video_path = True,
                     log_func = log_func)
    export_notebooks(samples_notebook_dir, samples_html_dir,
                     embed_try_it_live = True,
                     replace_img_path = True,
                     replace_video_path = True,
                     log_func = log_func,
                     items_metadata_yaml_path = items_metadata_yaml_path)

def _make_dirs(list_of_dirs):
    for dir_ in list_of_dirs:
        if not os.path.isdir(dir_):
            log.debug(f"Making dir {dir_}")
            os.makedirs(dir_, exist_ok = True)

def _copy_imgs(notebooks_root_dir, output_dir):
    """Moves all images from notebooks folder to correct folder in STAGING"""
    log.info(f"Copying image files from notebooks dir to {output_dir}")
    img_src_dir = os.path.join(notebooks_root_dir, "static", "img")
    img_html_dir = os.path.join(output_dir,
                                "src", "assets", "img", "python-graphics")
    if os.path.isdir(img_html_dir):
        recursive_file_copy(src_dir_root = img_src_dir,
                            dst_dir_root = img_html_dir)
    else:
        shutil.copytree(img_src_dir, img_html_dir)

def _copy_videos(notebooks_root_dir, output_dir):
    """Moves all video from notebooks folder to correct folder in STAGING"""
    log.info(f"Copying video files from notebooks dir to {output_dir}")
    video_src_dir = os.path.join(notebooks_root_dir, "static", "video")
    video_html_dir = os.path.join(output_dir,
                                  "static", "python", "assets", "video")
    if os.path.isdir(video_html_dir):
        recursive_file_copy(src_dir_root = video_src_dir,
                            dst_dir_root = video_html_dir)
    else:
        shutil.copytree(video_src_dir, video_html_dir)

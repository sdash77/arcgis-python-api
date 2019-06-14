import os
import glob
from shutil import copyfile
import logging
log = logging.getLogger()

from automation._common import *
from automation.dev_site._export_guide_samples_nb import export_notebooks  
from automation.dev_site.stage_notebooks_for_dev_web_repo \
    import recursive_file_copy

def build_dummy_dev_site(notebooks_root_dir, **kwargs):
    log.info("Building a dummy developer's website...")
    output_dir = os.path.join(STAGING_DIR, "dummy_dev_site")
    guide_notebook_dir = os.path.join(notebooks_root_dir, "guide")
    samples_notebook_dir = os.path.join(notebooks_root_dir, "samples")
    os.mkdir(output_dir)

    export_notebooks(guide_notebook_dir, output_dir,
                     embed_try_it_live = False,
                     replace_img_path = True, img_prefix="./",
                     log_func = log.debug,
                     dummy_mode_css_add_head=True)

    export_notebooks(samples_notebook_dir, output_dir,
                     embed_try_it_live = False,
                     replace_img_path = True, img_prefix="./",
                     log_func = log.debug,
                     dummy_mode_css_add_head=True)

    img_dir = os.path.join(notebooks_root_dir, "static", "img")

    # Copy all images
    recursive_file_copy(src_dir_root = img_dir,
                        dst_dir_root = output_dir)

    # Copy all CSS
    css_dir = os.path.join(AUTOMATION_DIR, "misc", "_assets", "css")
    for g in glob.glob(os.path.join(css_dir, "*.css")):
        copyfile(g, os.path.join(output_dir, os.path.basename(g)))

    # Write index file to navigate through all outputted files
    _write_index_html_file_for_outputted_html(output_dir)

def _write_index_html_file_for_outputted_html(output_dir):
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write("<h1>Dummy developers.arcgis.com/python/</h1>\n")
        f.write("<p>Press any of the below links to view a dummy "\
                "representation of what the notebook would look like "\
                "on the developers.arcgis.com site when it gets deployed. "\
                "It won't be a perfect representation, but the general "\
                "idea will be the same.<p><br>-----<br>")
        for html_file in glob.glob(os.path.join(output_dir, "*.html")):
            html_file_name_no_ext = os.path.splitext(
                os.path.basename(html_file))[0]
            f.write('<p><a href="./{0}.html">{0}</a></p>\n'.format(
                html_file_name_no_ext))

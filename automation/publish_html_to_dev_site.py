import logging
log = logging.getLogger()

from __init__ import *

def publish_html_to_dev_site(html_output_dir, *args, **kwargs):
    log.info("Moving everything in STAGING to {}".format(html_output_dir))
    recursive_file_copy(src_dir_root = STAGING_DIR,
                        dst_dir_root = html_output_dir,
                        files_to_ignore=["log.log", ".gitignore"])

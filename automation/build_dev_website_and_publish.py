import os
import shutil
import uuid
import tempfile
import logging
log = logging.getLogger()

from automation._common import *

def build_dev_website_and_publish(dev_website_repo, html_output_dir,
                                  *args, **kwargs):
    """Take whatever dev site artifacts are in staging, move them to the
    dev_website_repo path, attempt to build the dev website, and attempt to 
    publish the result to the specified html_output_dir that zion serves up
    """
    log.info(f"Attempting to publish site to {html_output_dir}")
    dev_repo_build_dir = os.path.join(dev_website_repo, "build")
    staging_dev_site_dir = os.path.join(STAGING_DIR, "arcgis-for-developers")
    # Clear all changes to the arcgis-dev repo, copy all from STAGING -> repo
    run_shell_command(f"cd {dev_website_repo} && "\
                       "git reset --hard && "\
                       "git clean -fd")
    recursive_file_copy(src_dir_root = staging_dev_site_dir,
                        dst_dir_root = dev_website_repo,
                        files_to_ignore=["log.log", ".gitignore"]) 
    # Do a full build in that repository
    _apply_redirect_workaround(dev_website_repo)
    run_shell_command(f"cd {dev_website_repo} && "
                       "npm install && "
                       "npm run-script build")
    # Replace everything in html_output_dir with the newly built site
    _delete_contents_of_dir(html_output_dir)
    _copy_contents(src_dir=dev_repo_build_dir,
                   dst_dir=html_output_dir)

def _apply_redirect_workaround(dev_website_repo):
    """Deletes content of 'src/data/redirects.yml' for redirect bug fix"""
    redirect_file_path = os.path.join(dev_website_repo,
                                      'src', 'data', 'redirects.yml')
    redirect_file = open(redirect_file_path, "w")
    redirect_file.write("")
    redirect_file.close()

def _delete_contents_of_dir(dir_):
    """Deletes all content from dir without deleting the dir"""
    log.debug(f"Deleting all content from {dir_}")
    for file_ in os.listdir(dir_):
        file_path = os.path.join(dir_, file_)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path, ignore_errors=True)
    assert not os.listdir(dir_)

def _copy_contents(src_dir, dst_dir):
    """Recursive copy of src_dir to an empty dst_dir. Doesn't need to
    follow the same dir format like recursive_file_copy"""
    for file_ in os.listdir(src_dir):
        src_file_path = os.path.join(src_dir, file_)
        dst_file_path = os.path.join(dst_dir, file_)
        log.debug(f"copying {src_file_path} to {dst_file_path}")
        if os.path.isfile(src_file_path):
            shutil.copyfile(src_file_path, dst_file_path)
        elif os.path.isdir(src_file_path):
            shutil.copytree(src_file_path, dst_file_path)

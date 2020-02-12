from ftplib import FTP, error_perm
import re
import os
import urllib.request
import logging
log = logging.getLogger()

from bs4 import BeautifulSoup
import requests

from automation._common import *

FTP_SITE = "zion"
ESRI_CHANNEL_DEV = "http://zion/conda/esri_channel_dev_2/"
NUM_BUILDS_TO_KEEP = 100

def publish_to_ftp_site(username, password, automation_type, build_number,
                        ftp_folder_name, *args, **kwargs):
    ftp = FTP(host = FTP_SITE,
              user = username,
              passwd = password)

    if re.match(MASTER_REGEX, automation_type):
        _publish_conda_to_ftp_master(ftp = ftp,
                                     build_number = build_number)
        _publish_pip_to_ftp_packages(ftp = ftp,
                                     build_number = build_number)
        _remove_old_builds_from_ftp_server(ftp = ftp,
                                     build_number = build_number)

    if re.match(LINUX_SLAVE_REGEX, automation_type):
        _publish_conda_to_ftp_master(ftp = ftp,
                                     build_number = build_number)
    if re.match(PUBLISH_REGEX, automation_type):
        _publish_conda_to_ftp_branch(ftp = ftp,
                                     ftp_folder_name = ftp_folder_name)

def _publish_conda_to_ftp_master(ftp, build_number):
    """Pushes any files in staging/conda_builds to ftp://zion/master"""
    src_dir_path = os.path.join(STAGING_DIR, "conda_builds")
    # conda packages for the specific build number, installable via:
    # conda install -c ftp://zion/master/{build_num}
    buildnum_dst_dir_path = "master/{}".format(build_number)
    # conda packages for the most recent master, overwritten. installable via:
    # conda install -c ftp://zion/master
    rootmaster_dst_dir_path = "master"  

    _make_dir_ignore_if_exists(ftp, buildnum_dst_dir_path)
    _merge_w_esri_channel_dev_and_upload(ftp = ftp,
                                         src_dir_path = src_dir_path,
                                         dst_dir_path = buildnum_dst_dir_path)
    _merge_w_esri_channel_dev_and_upload(ftp = ftp,
                                         src_dir_path = src_dir_path,
                                         dst_dir_path = rootmaster_dst_dir_path)

def _publish_conda_to_ftp_branch(ftp, ftp_folder_name):
    """Pushes any files in staging/conda_builds to ftp://zion/ftp_fold_name"""
    src_dir_path = os.path.join(STAGING_DIR, "conda_builds")
    _make_dir_ignore_if_exists(ftp, ftp_folder_name) 
    _merge_w_esri_channel_dev_and_upload(ftp = ftp,
                                         src_dir_path = src_dir_path,
                                         dst_dir_path = ftp_folder_name)

def _merge_w_esri_channel_dev_and_upload(ftp, src_dir_path, dst_dir_path):
    ext = '.tar.bz2'
    def download_files_recurs(url, ext=''):
        output = []
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        for url2 in [url + '/' + node.get('href') for node in soup.find_all('a')]:
            if url2.endswith(ext):
                output.append(url2)
            output += download_files_recurs(url2, ext)
        return output

    for file_url in download_files_recurs(ESRI_CHANNEL_DEV, ext):
        filename = os.path.basename(file_url)
        arch_dir = os.path.join(src_dir_path, 
                                os.path.dirname(file_url).split("/")[-1])
        download_file_dst = os.path.join(arch_dir, filename)
        if not os.path.exists(arch_dir):
            os.mkdir(arch_dir)
        urllib.request.urlretrieve(file_url, download_file_dst)

    run_shell_command(f"conda index {src_dir_path}")
    _upload_directory_recursive(ftp = ftp,
                                src_dir_path = src_dir_path,
                                dst_dir_path = dst_dir_path,
                                overwrite_dir = True)

def _publish_pip_to_ftp_packages(ftp, build_number):
    """Pushes any files in staging/pip_builds to ftp://zion/packages"""
    src_dir_path = os.path.join(STAGING_DIR, "pip_builds")
    for root, _, files in os.walk(src_dir_path):
        for file_name in files:
            src_file_path = os.path.join(root, file_name)
            #The 'master' tarball is the most recently uploaded one (overwrite)
            master_dst = "packages/{}".format(file_name)
            _storbinary_overwrite_if_exists(ftp, master_dst, src_file_path)
            log.info("Uploading {} -> ftp://{}/{}".format(src_file_path,
                                                          FTP_SITE,
                                                          master_dst))
            #The 'buildnumber' tarball is specific to this build
            bldnum_dst = "packages/build-number-{}.tar.gz".format(build_number)
            _storbinary_overwrite_if_exists(ftp, bldnum_dst, src_file_path)
            log.info("Uploading {} -> ftp://{}/{}".format(src_file_path,
                                                          FTP_SITE,
                                                          bldnum_dst))

def _upload_directory_recursive(ftp, src_dir_path, dst_dir_path,
                                overwrite_dir = True):
    """Upload the contents of a directory, overwriting folders and files"""
    for name in os.listdir(src_dir_path):
        curr_src_path = os.path.join(src_dir_path, name)
        curr_dst_path = "{}/{}".format(dst_dir_path, name) #ftp servers use '/'
        if os.path.isfile(curr_src_path):
            log.debug("Uploading {} -> ftp://{}/{}".format(curr_src_path,
                                                           FTP_SITE,
                                                           curr_dst_path))
            _storbinary_overwrite_if_exists(ftp, curr_dst_path, curr_src_path)
        elif os.path.isdir(curr_src_path):
            log.info("Uploading {} -> ftp://{}/{}".format(curr_src_path,
                                                          FTP_SITE,
                                                          curr_dst_path))
            if overwrite_dir:
                _make_dir_overwrite_if_exists(ftp, curr_dst_path)
            else:
                _make_dir_ignore_if_exists(ftp, curr_dst_path)
            _upload_directory_recursive(ftp, curr_src_path,
                                        curr_dst_path, overwrite_dir)

def _delete_directory_recursive(ftp, dst_dir_path):
    """Delete everything in a directory"""
    _del_dir_recurs_helper(ftp, dst_dir_path)
    ftp.rmd(dst_dir_path)
    log.info("ftp://{}/{}/ deleted recursively".format(FTP_SITE, dst_dir_path))

def _del_dir_recurs_helper(ftp, dst_dir_path):
    for curr_path in ftp.nlst(dst_dir_path):
        try: # will not throw exception if durr_path is a file
            ftp.delete(curr_path)
        except error_perm as e: # will throw exception if curr_path is a dir
            if e.args[0].startswith('550'):
                _del_dir_recurs_helper(ftp, curr_path)
                ftp.rmd(curr_path)

def _remove_old_builds_from_ftp_server(ftp, build_number):
    """Only keep NUM_BUILDS on build server, delete old files/folders"""
    log.debug("Attempting to delete old builds...")
    upper_range_builds = int(build_number) - NUM_BUILDS_TO_KEEP
    for build_num_to_delete in range(1, upper_range_builds):
        conda_fld = "master/{}".format(build_num_to_delete)
        pip_pkg = "packages/build-number-{}.tar.gz".format(build_num_to_delete)
        try:
            _delete_directory_recursive(ftp, conda_fld)
            log.debug("Deleted ftp://{}/{}".format(FTP_SITE, conda_fld))

            _delete_file_ignore_if_doesnt_exist(ftp, pip_pkg)
            log.debug("Deleted ftp://{}/{}".format(FTP_SITE, pip_pkg))
        except error_perm as e:
            log.debug("Skipping deleting build {}".format(build_num_to_delete))

def _storbinary_overwrite_if_exists(ftp, curr_dst_path, curr_src_path):
    try:
        _storbinary(ftp, curr_dst_path, curr_src_path)
    except error_perm as e:
        if e.args[0].startswith('550'):
            ftp.delete(curr_dst_path)
            _storbinary(ftp, curr_dst_path, curr_src_path)
        else:
            raise e

def _storbinary(ftp, curr_dst_path, curr_src_path):
    ftp.storbinary("STOR {}".format(curr_dst_path),
                   open(curr_src_path, 'rb'))

def _delete_file_ignore_if_doesnt_exist(ftp, file_path_on_ftp_server):
    try:
        ftp.delete(file_path_on_ftp_server)
    except error_perm as e:
        if e.args[0].startswith('550'):
            return
        else:
            raise e

def _make_dir_ignore_if_exists(ftp, dir_):
    try:
        ftp.mkd(dir_)
    except error_perm as e:
        if not e.args[0].startswith('550'):
            raise e

def _make_dir_overwrite_if_exists(ftp, dir_):
    try:
        ftp.mkd(dir_)
    except error_perm as e:
        if e.args[0].startswith('550'):
            _delete_directory_recursive(ftp, dir_)
            ftp.mkd(dir_)
        else:
            raise e

def _remove_dir_ignore_if_doesnt_exist(ftp, dir_):
    try:
        ftp.rmd(dir_)
    except error_perm as e:
        if not e.args[0].startswith('550'):
            raise e

from ftplib import FTP
import re
import logging
log = logging.getLogger()

from __init__ import *

FTP_SITE = "zion"
NUM_BUILDS_TO_KEEP = 100

def publish_results(*args, **kwargs):
    try:
        ftp = FTP(host = FTP_SITE,
                  user = kwargs["username"],
                  passwd = kwargs["password"])
    except KeyError as e:
        log.exception("FTP username/password not specified. Skipping "\
                      "publishing (Exception thrown => {}".format(e))
        return

    if re.match(MASTER_REGEX, kwargs["automation_type"]):
        _publish_to_ftp_site_master(ftp = ftp,
                                    build_number = kwargs["build_number"])

def _publish_to_ftp_site_master(ftp,
                                build_number):
    src_dir_path = os.path.join(STAGING_DIR, "conda_builds")
    dst_dir_path = 'master/{}'.format(build_number)
    ftp.mkd(dst_dir_path)
    _upload_directory_recursive(ftp = ftp,
                                src_dir_path = src_dir_path,
                                dst_dir_path = dst_dir_path)

def _upload_directory_recursive(ftp, src_dir_path, dst_dir_path):
    for name in os.listdir(src_dir_path):
        curr_src_path = os.path.join(src_dir_path, name)
        curr_dst_path = "{}/{}".format(dst_dir_path, name) #ftp servers use '/'
        if os.path.isfile(curr_src_path):
            log.info("Uploading {} -> ftp://{}/{}".format(curr_src_path,
                                                           FTP_SITE,
                                                           curr_dst_path))
            ftp.storbinary('STOR ' + curr_dst_path, open(curr_src_path, 'rb'))
        elif os.path.isdir(curr_src_path):
            ftp.mkd(curr_dst_path)
            _upload_directory_recursive(ftp, curr_src_path, curr_dst_path)

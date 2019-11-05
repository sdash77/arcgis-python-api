import sys
import codecs
import os
import shutil
import subprocess
import logging
log = logging.getLogger()

JENKINS_ROOT = "http://zion/jenkins"
NB_TIMEOUT = 120

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..'))

AUTOMATION_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "automation"))

STAGING_DIR = os.path.abspath(os.path.join(
    AUTOMATION_DIR,
    "staging"))

BUILD_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "build"))

TESTS_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "tests"))

MASTER_REGEX = ".*master.*"
GEOS_PULL_REQUEST_REGEX = ".*geo.*pull.*request.*"
PUB_REPO_PULL_REQUEST_REGEX = ".*pub.*repo.*pull.*request"
PUBLISH_REGEX = ".*publish.*"
LINUX_SLAVE_REGEX = ".*linux.*slave.*"
RUN_TEST_SUITE_REGEX = ".*test.*suite.*"

def run_shell_command(cmd, throw_exc_on_fail=True):
    try:
        log.info("Currently running command '{}'".format(cmd))
        byte_output = subprocess.check_output(cmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        str_output = _bytes_to_str_cp850_workaround(byte_output)
        log.debug(str_output)
        return str_output
    except subprocess.CalledProcessError as e:
        log.warn("cmd failed, returned non-zero code. Output:\n"\
                 "{}".format(e.output.decode("utf-8")))
        if throw_exc_on_fail:
            raise e

def _bytes_to_str_cp850_workaround(bytes_):
    """Although python encodes everything in utf-8, The Windows CMD prompt 
    has issues printing out some characters (A error was seen printing out 
    the \u03BC Greek 'u'). These stack overflows: http://bit.ly/2HW4fXP and
    http://bit.ly/2DLdbfX provide some insight. The workaround is to
    decode to unicode, encode to cp850, decode from cp850, replacing 
    unprinteable characters every step along the way with '?'
    """
    return bytes_.decode('utf-8',
        'replace').encode('cp850',
        'replace').decode('cp850',
        'replace')

def recursive_file_copy(src_dir_root, dst_dir_root, files_to_ignore=[]):
    """Given two dirs with the same folder structure, copy all files from
    src to dst, overwriting existing files, ignoring specified files
    """
    for root, dirs, files in os.walk(src_dir_root):
        for name in [x for x in files if x not in files_to_ignore]:
            rel_path = os.path.join(root, name).split(src_dir_root)[-1]
            abs_path = src_dir_root + rel_path
            _overwrite_copy(src = abs_path,
                            dst = dst_dir_root + rel_path)

def _overwrite_copy(src, dst):
    log.debug("Copying {} to {}...".format(src, dst))
    shutil.copyfile(src, dst)


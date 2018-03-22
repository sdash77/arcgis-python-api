import sys
import codecs
import os
import shutil
import subprocess
import logging
log = logging.getLogger()

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..'))

STAGING_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "automation",
    "staging"))

BUILD_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "build"))

MASTER_REGEX = ".*master.*"
PULL_REQUEST_REGEX = ".*pull.*request.*"
PUBLISH_REGEX = ".*publish.*"
LINUX_SLAVE_REGEX = ".*linux.*slave.*"
UNIT_TEST_REGEX = ".*unit.*test.*"
DEV_SITE_REGEX = ".*dev.*site.*"

log.setLevel(logging.DEBUG)
log_file_path = os.path.join(STAGING_DIR, "log.log")
formatter = logging.Formatter(
    u'-----    %(levelname)s    |    '\
     '%(asctime)s    |    '\
     '%(filename)s line %(lineno)d'\
     '     -----\n'\
     '"%(message)s"')

file_handler = logging.FileHandler(log_file_path, "w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
log.addHandler(stdout_handler)

def run_shell_command(cmd):
    try:
        log.info("About to run command '{}'".format(cmd))
        byte_output = subprocess.check_output(cmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
        str_output = _bytes_to_str_cp850_workaround(byte_output)
        log.debug(str_output)
        return str_output
    except subprocess.CalledProcessError as e:
        log.warn("cmd failed, returned non-zero code. Output:\n"\
                 "{}".format(e.output.decode("utf-8")))
        raise e

def _bytes_to_str_cp850_workaround(bytes_):
    """Although python encodes everything in utf-8, The Windows CMD prompt 
    has issues printing out some characters (A error was seen printing out 
    the \u03BC Greek 'u'). These stack overflows: http://bit.ly/2HW4fXP and
    http://bit.ly/2DLdbfX provide some insight. The workaround is to
    decode to cp850, replace all unprinteable characters, encode
    """
    return bytes_.decode('utf-8').encode('cp850','replace').decode('cp850')

class set_stdout_log_to:
    """temporarely change the level of stdout logging.
    Use with "with" syntax like 'with _raise_log_to_warn(foo)'
    """
    def __init__(self, level):
        self.target_level = level

    def __enter__(self):
        self.prev_level = stdout_handler.level
        stdout_handler.setLevel(self.target_level)

    def __exit__(self, type, value, traceback):
        stdout_handler.setLevel(self.prev_level)

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


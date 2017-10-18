import os
import sys
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

log.setLevel(logging.DEBUG)
log_file_path = os.path.join(STAGING_DIR, "log.log")
formatter = logging.Formatter(
    '-----    %(levelname)s    |    '\
    '%(asctime)s    |    '\
    '%(filename)s line %(lineno)d'\
    '     -----\n'\
    '"%(message)s"')

file_handler = logging.FileHandler(log_file_path, "w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
log.addHandler(stdout_handler)

def run_shell_command(cmd):
    log.info("About to run command '{}'".format(cmd))
    byte_output = subprocess.check_output(cmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
    log.debug(byte_output.decode("utf-8"))

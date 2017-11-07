import os
import sys
import subprocess
import logging
log = logging.getLogger(__name__)

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..'))

BUILD_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "build"))

OUTPUT_DIR = os.path.abspath(os.path.join(
    BUILD_DIR,
    "output"))

log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '-----    %(levelname)s    |    '\
    '%(asctime)s    |    '\
    '%(filename)s line %(lineno)d'\
    '     -----\n'\
    '"%(message)s"')

stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)
log.addHandler(stdout_handler)

def run_shell_command(cmd):
    log.info("About to run command '{}'".format(cmd))
    byte_output = subprocess.check_output(cmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
    log.debug(byte_output.decode("utf-8"))

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging
log = logging.getLogger("__main__")

import pytest

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..',
    '..'))
AUTOMATION_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "automation"))
TESTS_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "tests"))
UNIT_TESTS_DIR = os.path.abspath(os.path.join(
    TESTS_DIR,
    "unit"))
INTEGRATION_TESTS_DIR = os.path.abspath(os.path.join(
    TESTS_DIR,
    "integration"))
NOTEBOOK_TESTS_DIR = os.path.abspath(os.path.join(
    TESTS_DIR,
    "notebook"))
WIDGET_INTEGRATION_TESTS_DIR = os.path.abspath(os.path.join(
    TESTS_DIR,
    "widget",
    "integration",
    "automated"))
WIDGET_UNIT_TESTS_DIR = os.path.abspath(os.path.join(
    TESTS_DIR,
    "widget",
    "unit"))
SUITES_DIR = os.path.abspath(os.path.join(
    TESTS_DIR,
    "_suites"))
DEFAULT_EMPTY_SUITE_FILE_PATH = os.path.abspath(os.path.join(
    SUITES_DIR,
    "default_empty_suite.yml"))

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
    decode to cp850, replace all unprinteable characters, encode
    """
    return bytes_.decode('utf-8').encode('cp850','replace').decode('cp850')

def run_pytest_on(paths, output_xml_path, block_network_access=False):
    pytest_args = ["-x",] + paths + [ 
        f"--junit-xml={output_xml_path}",
        "--maxfail=99999999999999999",
        ]
    if block_network_access:
        pytest_args.append("--blockage")
    log.debug(f"Running pytest.main({pytest_args})")
    _run_pytest_subprocess(pytest_args)

def _run_pytest_subprocess(pytest_args):
    print("Running subprocess")
    args = ['python', '-m', 'pytest'] + pytest_args
    with Popen(args, cwd=TESTS_DIR, stderr=PIPE) as p:
        for line in p.stderr:
            print(str(line.decode('utf-8')), end='')

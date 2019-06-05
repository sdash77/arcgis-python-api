import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging
log = logging.getLogger("__main__")

import pytest
from utils._common import *

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

def run_pytest_on(paths, output_xml_path, 
                  block_network_access=False,
                  max_fail = 9999999999999999,
                  throw_exc_on_fail = False):
    pytest_args = ["-x",] + paths + [ 
        f"--junit-xml={output_xml_path}",
        f"--maxfail={max_fail}",
        ]
    if block_network_access:
        pytest_args.append("--blockage")
    log.debug(f"Running pytest.main({pytest_args})")
    if not throw_exc_on_fail:
        _run_pytest_subprocess(pytest_args)
    else:
        cmd = " ".join(["python", "-m", "pytest"] + pytest_args)
        run_shell_command(cmd, throw_exc_on_fail = throw_exc_on_fail)

def _run_pytest_subprocess(pytest_args):
    args = ['python', '-m', 'pytest'] + pytest_args
    log.debug(f"Running Popen({args},...")
    with Popen(args, cwd=TESTS_DIR, stderr=PIPE) as p:
        for line in p.stderr:
            print(str(line.decode('utf-8')), end='')
        print(f"REturn code = {p.returncode}")

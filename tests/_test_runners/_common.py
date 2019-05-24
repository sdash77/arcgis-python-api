import os
import subprocess

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
TESTS_OUTPUT = os.path.abspath(os.path.join(
    TESTS_DIR,
    "_tests_output"))

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



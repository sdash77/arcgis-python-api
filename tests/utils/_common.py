import os
import sys
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging

log = logging.getLogger("__main__")

GEOSAURUS_ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
GEOSAURUS_SRC_DIR = os.path.abspath(os.path.join(GEOSAURUS_ROOT_DIR, "src"))
GEOSAURUS_SRC_ARCGIS_DIR = os.path.abspath(os.path.join(GEOSAURUS_SRC_DIR, "arcgis"))
AUTOMATION_DIR = os.path.abspath(os.path.join(GEOSAURUS_ROOT_DIR, "automation"))
TESTS_DIR = os.path.abspath(os.path.join(GEOSAURUS_ROOT_DIR, "tests"))
TESTS_UTILS_DIR = os.path.abspath(os.path.join(TESTS_DIR, "utils"))
UNIT_TESTS_DIR = os.path.abspath(os.path.join(TESTS_DIR, "unit"))
SMOKE_TESTS_DIR = os.path.abspath(os.path.join(TESTS_DIR, "smoke"))
INTEGRATION_TESTS_DIR = os.path.abspath(os.path.join(TESTS_DIR, "integration"))
NOTEBOOK_TESTS_DIR = os.path.abspath(os.path.join(TESTS_DIR, "notebooks"))
SUITES_DIR = os.path.abspath(os.path.join(TESTS_DIR, "_suites"))
DEFAULT_EMPTY_SUITE_FILE_PATH = os.path.abspath(
    os.path.join(SUITES_DIR, "default_empty_suite.yml")
)

# The python executable cmd that guarantees that `import arcgis` will pull
# The `arcgis` from this repository's `geosaurus/src/arcgis`
GEOSAURUS_PYTHON_EXEC = [
    '"' + sys.executable + '"',
    "-m",
    "pip",
    "install",
    "-e",
    '"' + GEOSAURUS_SRC_DIR + '"',
    "--no-deps",
    "&&",
    '"' + sys.executable + '"',
]
GEOSAURUS_PYTHON_EXEC_STR = " ".join(GEOSAURUS_PYTHON_EXEC)


def run_shell_command(cmd, throw_exc_on_fail=True):
    try:
        log.info("Currently running command '{}'".format(cmd))
        byte_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        str_output = _bytes_to_str_cp850_workaround(byte_output)
        log.debug(str_output)
        return str_output
    except subprocess.CalledProcessError as e:
        log.warning(
            "cmd failed, returned non-zero code. Output:\n"
            "{}".format(e.output.decode("utf-8"))
        )
        if throw_exc_on_fail:
            raise e


def _bytes_to_str_cp850_workaround(bytes_):
    """Although python encodes everything in utf-8, The Windows CMD prompt
    has issues printing out some characters (A error was seen printing out
    the \u03BC Greek 'u'). These stack overflows: http://bit.ly/2HW4fXP and
    http://bit.ly/2DLdbfX provide some insight. The workaround is to
    decode to cp850, replace all unprinteable characters, encode
    """
    return bytes_.decode("utf-8").encode("cp850", "replace").decode("cp850")


def setup_env():
    """Installs the Python API located at ../../src. Called before
    test runs when run on Jenkins, not when run from run_tests.py
    """
    log.info(f"Setting up env to use `arcgis` from {GEOSAURUS_ROOT_DIR}...")
    python_cmd = [
        f'"{sys.executable}"',
    ]
    pip_install_cmd = python_cmd + [
        "-m",
        "pip",
        "install",
        "-e",
        '"' + GEOSAURUS_SRC_DIR + '"',
        "--no-deps",
    ]
    run_shell_command(" ".join(pip_install_cmd))

def should_smoketest_arcgis_learn():
    test_arcgis_learn = os.environ.get("TEST_ARCGIS_LEARN", "true")
    return test_arcgis_learn.lower() in ["true", "yes", "1"]

def run_unittest_on(
    paths,
    output_xml_path,
    output_coverage_dir=False,
    block_network_access=False,
    max_fail=9999999999999999,
    throw_exc_on_fail=False,
):
    def _assemble_unittest_args(
        paths,
        output_xml_path,
        output_coverage_dir,
        block_network_access,
        surround_paths_with_quotes=False,
    ):
        unittest_args = []
        if surround_paths_with_quotes:
            unittest_args += [f'"{sys.executable}"', "-m", "nose", "-v", "-x"] + list(
                f'"{x}"' for x in paths
            )
        else:
            unittest_args += [sys.executable, "-m", "nose", "-v", "-x"] + paths
        unittest_args += ["--with-xunit", f"--xunit-file={output_xml_path}"]
        """
        if block_network_access:
            unittest_args += [
                "--blockage",
            ]
        """
        if output_coverage_dir:
            unittest_args += [
                "--with-coverage", "--cover-html",
                f"--cover-html-dir={output_coverage_dir}"
            ]
        return unittest_args

    # ------------------------------------------------------------------------
    if not throw_exc_on_fail:
        unittest_args = _assemble_unittest_args(
            paths,
            output_xml_path,
            output_coverage_dir,
            block_network_access,
            surround_paths_with_quotes=False,
        )
        with Popen(unittest_args, cwd=TESTS_DIR, stderr=PIPE) as p:
            for line in p.stderr:
                print(str(line.decode("utf-8")), end="")
    else:
        unittest_args = _assemble_unittest_args(
            paths,
            output_xml_path,
            output_coverage_dir,
            block_network_access,
            surround_paths_with_quotes=True,
        )
        run_shell_command(" ".join(unittest_args))


def _run_test_subprocess(unittest_args):
    args = [sys.executable, "-m", "unittest"] + unittest_args
    log.debug(f"Running Popen({args},...")
    with Popen(args, cwd=TESTS_DIR, stderr=PIPE) as p:
        for line in p.stderr:
            print(str(line.decode("utf-8")), end="")

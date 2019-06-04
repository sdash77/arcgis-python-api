import os

GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..',
    '..'))
GEOSAURUS_SRC_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_ROOT_DIR,
    "src"))
GEOSAURUS_SRC_ARCGIS_DIR = os.path.abspath(os.path.join(
    GEOSAURUS_SRC_DIR,
    "arcgis"))
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

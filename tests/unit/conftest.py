import os
import sys


THIS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
TESTS_DIR = os.path.join(THIS_DIR, "..")


def pytest_configure():
    sys.path.append(TESTS_DIR)

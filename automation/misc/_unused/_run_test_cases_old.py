"""
Run unit test cases.

This command parses the command line for names of 1) directories, 2) files,
and/or 3) individual test cases.

1. Directories are recursively traversed to look for Python modules
   containing test cases.
2. Files are directly opened to look for test cases.
3. Valid test case names are those that are accepted by
   unittest.TestLoader.loadTestsFromName().

Names of directories, files and test cases can be mixed.
Python modules that don't contain test cases are skipped.

Warning: All Python modules found are imported, in effect executing the module.
         Make sure that free functions in stand-alone modules are guarded by:
         if __name__ == "__main__":

Examples:

# Show usage.
run_test_cases.py --help

# Run all test cases found in the current directory and below.
run_test_cases.py .

# Run all test cases found in MyTests.py.
run_test_cases.py MyTests.py

# Run a specific test case.
run_test_cases.py MyTests.MyTests.testCR1234
"""
import argparse
import fnmatch
import imp
import os
import unittest
import sys
import xmlrunner
import atexit
import traceback
import time

#Make sure we're importing the arcgis package at ../../src
GEOSAURUS_ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname( __file__ ),
    '..',
    '..'))
sys.path.insert(0, os.path.join(GEOSAURUS_ROOT_DIR, "src"))
import arcgis
expected_file_path = os.path.join(GEOSAURUS_ROOT_DIR, "src", "arcgis", "__init__.py")
try:
    assert arcgis.__file__ == expected_file_path
except AssertionError as e:
    print("ERROR: the arcgis package being tested should be {}".format(expected_file_path))
    print("Instead, it is {}. Not running tests...".format(arcgis.__file__))

def module(pathName):
    """
    Return the module pointed to by *pathName*.
    """
    moduleName = os.path.splitext(os.path.basename(pathName))[0]
    return imp.load_source(moduleName, pathName)


def load_test_suite_from_file(pathName):
    """
    Return a test suite containing the test cases in *pathName*, if any.
    """
    return unittest.defaultTestLoader.loadTestsFromModule(module(pathName))


def load_test_suite_from_directory(pathName):
    """
    Return list with test suites of all Python modules in the directory tree
    rooted at *pathName*.
    """
    modulePathNames = []
    for rootDirectoryName, subDirectoryNames, fileNames in os.walk(pathName):
        for filename in fnmatch.filter(fileNames, "*.py"):
            modulePathNames.append(os.path.join(rootDirectoryName, filename))
    return [load_test_suite_from_file(pathName) for pathName in modulePathNames]


def remove_tests_to_skip(tests, test_suite_names_to_skip):
    """
    Remove tests given the names passed in.
    """
    assert isinstance(tests, list), type(tests)
    assert isinstance(test_suite_names_to_skip, list), \
           type(test_suite_names_to_skip)

    tests_to_skip = []
    for test in tests:
        if isinstance(test, unittest.TestSuite):
            remove_tests_to_skip(test._tests, test_suite_names_to_skip)
        else:
            for test_suite_name_to_skip in test_suite_names_to_skip:
                tokens = test_suite_name_to_skip.split(".")
                if len(tokens) == 2:
                    # User passed the name of a test suite (<module>.<class>).
                    # Skip all tests that are part of this suite.
                    if test_suite_name_to_skip == "{}.{}".format(
                        test.__class__.__module__, test.__class__.__name__):
                        tests_to_skip.append(test)
                elif len(tokens) == 3:
                    # User passed the name of a test case
                    # (<module>.<class>.<function>).
                    # Skip that specific test case.
                    assert False, \
                           "Skipping test cases is not implemented yet: " \
                           "update script or skip entire test suite"

    tests[:] = [test for test in tests if test not in tests_to_skip]

suites = []
test_results_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                    'test-results')
def _trigger_xml_runner():
    xmlrunner.XMLTestRunner(output=test_results_dir).run(unittest.TestSuite(suites))
    print("XML files successfully written.")
    print("{} is now exiting...".format(sys.argv[0]))

def run_test_cases(args):
    print("Running tests against this arcgis src at {}".format(arcgis.__file__))
    try:
        _setup_testing(args)
    except Exception as e:
        print("Unhandled exception on setting up unit testing. Still attemping to run..")
        print(traceback.format_exc())
    _trigger_xml_runner()

def _setup_testing(args):
    global suites, test_results_dir
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbosity", dest="verbosity", default="1", type=int,
                        help= "Verbosity level for the test runner")
    parser.add_argument("--skip", dest="skip", help=
                        "Name of tests to skip")
    parser.add_argument("names", metavar="N", nargs="+", help=
                        "Name of file containing test cases, or name of directory containing "
                        "files that contain test cases, or name of test case, using the "
                        "folowing syntax: <module name>[.<class name>[.<test case name>]].")
    parser.add_argument("--coverage", dest="coverage", required=False,
                        help="Output a coverage report to the specified path.")
    parser.add_argument("--run_on_src", dest="run_on_src", default=True, type=bool, required=False,
                        help="Run tests on source code found in src instead of on conda pkg")
    parser.add_argument("--test_results_dir", dest="test_results_dir",
                        default=os.path.join(os.path.dirname(os.path.realpath(__file__)),'test-results'),
                        type=str, required=False,
                        help="What directory you want the test-results xml files to get written to")
    arguments = parser.parse_args(args)
    test_names_to_skip = arguments.skip
    names = arguments.names
    coverage_path = arguments.coverage
    test_results_dir = arguments.test_results_dir
    from pathlib import Path
    current_file_path = Path(os.path.realpath(__file__))
    unittest_path = current_file_path.parent

    for name in names:
        if os.path.isdir(name):
            suites = suites + load_test_suite_from_directory(name)
        elif os.path.isfile(name):
            suites = suites + [load_test_suite_from_file(name)]
        else:
            suites = suites + \
                [unittest.defaultTestLoader.loadTestsFromName(name)]

    if not test_names_to_skip is None:
        remove_tests_to_skip(suites, [test_names_to_skip])

    if coverage_path:
        import coverage
        cov = coverage.coverage()
        cov.start()

    # unittest.TextTestRunner(verbosity=arguments.verbosity).run(
    #     unittest.TestSuite(suites))

    if coverage_path:
        cov.stop()
        cov.html_report(directory=coverage_path)

if __name__ == "__main__":
    print("You should not be running tests by calling this file. Use the "\
          "logic in geosaurus/tests instead that utilizes pytest. To "\
          "continue running tests using this file anyway, press Ctrl + C "\
          "in the next 10 seconds, or else this program will quit")
    try:
        i = 0;
        while i<10:
            time.sleep(1)
            i += 1
    except KeyboardInterrupt:
        run_test_cases(sys.argv)

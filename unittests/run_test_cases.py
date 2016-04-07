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


def module(
    pathName):
    """
    Return the module pointed to by *pathName*.
    """
    moduleName = os.path.splitext(os.path.basename(pathName))[0]
    return imp.load_source(moduleName, pathName)


def load_test_suite_from_file(
    pathName):
    """
    Return a test suite containing the test cases in *pathName*, if any.
    """
    return unittest.defaultTestLoader.loadTestsFromModule(module(pathName))


def load_test_suite_from_directory(
    pathName):
    """
    Return list with test suites of all Python modules in the directory tree
    rooted at *pathName*.
    """
    modulePathNames = []
    for rootDirectoryName, subDirectoryNames, fileNames in os.walk(pathName):
        for filename in fnmatch.filter(fileNames, "*.py"):
            modulePathNames.append(os.path.join(rootDirectoryName, filename))
    return [load_test_suite_from_file(pathName) for pathName in modulePathNames]


def remove_tests_to_skip(
    tests,
    test_suite_names_to_skip):
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

if __name__ == "__main__":
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
    arguments = parser.parse_args()
    test_names_to_skip = arguments.skip
    names = arguments.names
    coverage_path = arguments.coverage

    # Update module path, because otherwise loadTestsFromame cannot find the
    # modules to import.
    sys.path = [os.getcwd()] + sys.path

    suites = []
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

    unittest.TextTestRunner(verbosity=arguments.verbosity).run(
        unittest.TestSuite(suites))

    if coverage_path:
        cov.stop()
        cov.html_report(directory=coverage_path)


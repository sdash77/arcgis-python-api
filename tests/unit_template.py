import unittest

# import mock utils if needed from tests/utils, or MagicMock from unittest
# from utils.mocks import *  
from unittest.mock import MagicMock


# These are test classes for class and functions below
# Tests can be varied for different modules, all based on the classes and methods in arcgis src
# Please include as much as possible test cases to improve unit test coverage :)
# Test class should be named as Test<ClassName> and should inherit from unittest.TestCase
class TestFoo(unittest.TestCase):
    """
    Unittest class for unit testing ArcGIS Python API classes
    Run tests that do not need gis connection, as well as static methods in classes
    """

    def setUp(self):
        """optional method to set up test data, run before each test"""
        # can set up test input, test object, and mock object here
        gis = MagicMock()
        self.obj = Foo(gis)
        pass

    def tearDown(self):
        """optional method to tear down test fixture, run after each test"""
        # can set up test output deletion here
        pass

    # all tests should be named as test_<method_name> or test_<method_name>_<case>
    # tests should accept self (representing the test case harness) as only parameter
    def test_foo_returns_valid_payload(self):
        """method to test method of a class"""
        data = "test_data"
        # use unittest assertions here
        result = self.obj.foo(data)
        # use built-in assert statements on the unittest class
        self.assertIsInstance(result, dict)
        # use assert keyword
        assert result
        # optionally include error message
        assert "data" in result, "data key not found in result"

    def test_convert_foo_raises_error(self):
        """method to test private method of a class, demonstrating a raised exception"""
        with self.assertRaises(NotImplementedError):
            self.obj._convert_foo()

    # test utils / static methods
    def test_util_validate_succeeds_even_number_true(self):
        result = Foo.util_is_valid(10)
        assert result
    
    def test_util_validate_succeeds_odd_number_false(self):
        result = Foo.util_is_valid(11)
        assert not result
    
    def test_util_validate_fails_string_false(self):
        result = Foo.util_is_valid("test")
        assert not result

    def test_util_double(self):
        result = Foo.util_double(10)
        self.assertEqual(result, 20)


#########################################################
# sample class stub for demonstrating unit test template
# for sample purposes only, not part of the test harness
#########################################################
class Foo:
    """
    Sample Class for Unit Test Template
    This is a sample class that requires gis connection
    """

    def __init__(self, gis):
        self.gis = gis

    def foo(self, data):
        # a sample method in Foo class
        # just return a valid dict payload
        return {"data": data}

    def _convert_foo(self):
        # a sample private method in Foo class
        # raise an exception to demonstrate a test that verifies exception
        raise NotImplementedError("_convert_foo not yet implemented")


    # sample util functions
    # static methods should manipulate inputs and return pure outputs
    # they should not depend on class instance or class variables
    # testing these should be the most straight forward and lowest hanging fruit for unit testing
    # but this will require a TDD approach and a change in the way the code is written
    @staticmethod
    def util_double(number: int) -> int:
        return number * 2
    
    @staticmethod
    def util_is_valid(data) -> bool:
        """returns True if data is a number and is even, else False"""
        return isinstance(data, int) and data % 2 == 0
#########################################################
# end of sample class stub
#########################################################

# if running this file directly, run the tests
# please include this stub with your test
if __name__ == "__main__":
    unittest.main()
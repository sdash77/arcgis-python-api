import unittest
from unittest.mock import MagicMock
from utils.mocks import *  # import mock utils if needed from tests/utils, or MagicMock from unittest
from sample_class import Foo
from sample_class import util_function_a, util_function_b


# These are test classes for class and functions from tests/sample_class.py
# Tests can be varied for different modules, all based on the classes and methods in arcgis src
# Please include as much as possible test cases to improve unit test coverage :)
class TestFoo(unittest.TestCase):
    """
    Unittest class for unit testing ArcGIS Python API classes
    Run tests that do not need gis connection, as well as static methods in classes
    """

    def setUp(self):
        """optional method to set up test data, run before each test"""
        # can set up test input, test object, and mock object here
        self.gis = MagicMock()
        self.obj = Foo(self.gis)
        pass

    def tearDown(self):
        """optional method to tear down test fixture, run after each test"""
        # can set up test output deletion here
        pass

    def test_foo_method(self, data):
        """method to test method of a class"""
        # use unittest assertions here
        result = self.obj.foo_method(data)
        assert result

    def test_foo_private_method(self, data):
        """method to test private method of a class"""
        result = self.obj._private_method()
        assert result

    def test_foo_method_raise_exception(self, error_raising_data):
        """method to test exception raising cases"""
        with self.assertRaises(Exception) as e:
            result = self.obj.foo_method(error_raising_data)
            assert result
            assert "<error_message>" in e


class TestUtil(unittest.TestCase):
    """
    Unittest class for unit testing ArcGIS Python API utils
    Run tests that do not need gis connection, as well as static methods in classes
    """
    def setUp(self):
        """optional method to set up test data, run before each test"""
        # can set up test input, test object, and mock object here
        self.obj = Foo()

    def tearDown(self):
        """optional method to tear down test fixture, run after each test"""
        # can set up test output deletion here
        pass

    def test_util_function_a(self, data):
        result = self.obj.util_function_a(data)
        assert result

    def test_util_function_b(self, data):
        result = self.obj.util_function_b(data)
        assert result


if __name__ == "__main__":
    unittest.main()

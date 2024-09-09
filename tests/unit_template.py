import unittest
from unittest.mock import MagicMock
from utils.mocks import *  # import mock utils if needed from tests/utils, or MagicMock from unittest
# import Python API class to test


class TestFoo(unittest.TestCase):
    """
    Unittest class for unit testing ArcGIS Python API classes
    Run tests that do not need gis connection, as well as static methods in classes
    """

    def setUp(self):
        """optional method to set up test data, run before each test"""
        pass

    def tearDown(self):
        """optional method to tear down test fixture, run after each test"""
        pass

    def test_foo(self):
        """method to test functionality of a class"""
        # use unittest assertions here
        pass

    def test_foo_raise_exception(self):
        """method to test exception raising cases"""
        # with self.assertRaises(SomeException):
        #    test_that_raises_exception()
        pass


if __name__ == "__main__":
    unittest.main()

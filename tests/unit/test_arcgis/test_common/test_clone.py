import unittest
from arcgis._impl.common._clone import _deep_get

class TestClone(unittest.TestCase):
    def test_deep_get_happy_path(self):
        self.assertEqual(_deep_get({'a': {'b': {'c': 42}}}, 'a', 'b', 'c'), 42)
    
    def test_deep_get_missing_key(self):
        self.assertIsNone(_deep_get({'a': {'b': {'c': 42}}}, 'a', 'x', 'c'))
    
    def test_deep_get_non_dict(self):
        self.assertIsNone(_deep_get({'a': {'b': 'b'}}, 'a', 'b', 'c'))

if __name__ == '__main__':
    unittest.main()

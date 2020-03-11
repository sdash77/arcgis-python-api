import pytest
import unittest
from arcgis._impl.common._isd import InsensitiveDict
import json
class TestInsensitiveDict(unittest.TestCase):
    """Test Suite for the InsensitiveDict Class"""
    #----------------------------------------------------------------------
    def test_creation(self):
        """tests the object creation options"""
        i = InsensitiveDict()
        assert len(i) == 0
        assert isinstance(i, InsensitiveDict)
        i1 = InsensitiveDict({'a' : 1, 'q' : {'2' : 'bee'}})
        assert len(i1) > 0
        assert i1.q['2'] == 'bee'
        assert isinstance(i1, InsensitiveDict)        
        case_3 = InsensitiveDict({'a' : 1, 'b' : {'c': {'d' : [{'fish' : 'duck'}]}}})
        assert case_3.b.c.d[0].fish
        assert dict(case_3.items()) == {'a' : 1, 'b' : {'c': {'d' : [{'fish' : 'duck'}]}}}
    #----------------------------------------------------------------------
    def test_json(self):
        """tests the object json property"""
        i = InsensitiveDict()
        i1 = InsensitiveDict({'a' : 1})
        assert i.json == '{}'
        assert i1.json == '{"a": 1}'
        i1 = InsensitiveDict({'a' : 1, 'b' : {'c': 'd'}})
        assert i1.json
        i1 = InsensitiveDict({'a' : 1, 'b' : {'c': {'d' : [{'fish' : 'duck'}]}}})
        assert i1.json == json.dumps({'a' : 1, 'b' : {'c': {'d' : [{'fish' : 'duck'}]}}})
        i1 = InsensitiveDict({'a' : 1, 'b' : {'c': {'d' : [{'fish' : 'duck'}]}}})
        i1.b.c.d.append([1,2,3])
        i1.b.c.d.append({'dog':'cat'})
        assert i1.json == '{"a": 1, "b": {"c": {"d": [{"fish": "duck"}, [1, 2, 3], {"dog": "cat"}]}}}'
    #----------------------------------------------------------------------
    def test_dot_notation_settting(self):
        """tests the object ability to add new data using dot notation"""
        i = InsensitiveDict()
        i.a = 1
        assert i.a == 1
        i.b = {'fish' : 'pond'}
        assert "b" in i
        assert ("c" in i)  == False
        assert isinstance(i.b, InsensitiveDict)
        assert i.b
    #----------------------------------------------------------------------
    def test_bracket_notation_settting(self):
        """tests the object ability to add new data using bracket notation"""
        i = InsensitiveDict()
        i["a"] = 1
        assert i["a"] == 1
        i["b"] = {'fish' : 'pond'}
        assert "b" in i
        assert ("c" in i)  == False
        assert isinstance(i["b"], InsensitiveDict)
        assert i["b"]
    #----------------------------------------------------------------------
    def test_bracket_notation_get(self):
        """tests the object ability to get the data"""    
        i1 = InsensitiveDict({'a' : 1, 'q' : {'2' : 'bee'}})
        assert i1['q']['2'] == 'bee'
    #----------------------------------------------------------------------
    def test_dot_notation_get(self):
        """tests the object ability to get the data"""    
        i1 = InsensitiveDict({'a' : 1, 'q' : {'two' : 'bee'}})
        assert i1.q.two == 'bee'    
    #----------------------------------------------------------------------
    def test_from_json(self):
        """tests the from_json to InsensitiveDict staticmethod"""    
        i1 = InsensitiveDict.from_json('{"a" : "b"}')
        assert i1
        assert "a" in i1
        assert i1.a == 'b'        
        assert isinstance(i1, InsensitiveDict)
    #----------------------------------------------------------------------
    def test_from_dict(self):
        """tests the from_dict to InsensitiveDict staticmethod"""    
        i1 = InsensitiveDict.from_dict({"a" : "b"})
        assert i1
        assert "a" in i1
        assert i1.a == 'b'
        assert isinstance(i1, InsensitiveDict)
    #----------------------------------------------------------------------
    def test_is_equal_copy(self):
        """tests the equal and copy method"""
        i1 = InsensitiveDict({'a' : 1, 'q' : {'2' : 'bee'}})
        copy_i1 = i1.copy()
        assert i1 == copy_i1
    #----------------------------------------------------------------------
    def test__dir__(self):
        """tests the equal and copy method"""
        i1 = InsensitiveDict({'a' : 1, 'q' : {'2' : 'bee'}})
        assert list(i1.__dir__()) == ['a', 'q']
    #----------------------------------------------------------------------
    def test_del(self):
        """tests the delete operation method"""
        i1 = InsensitiveDict({'a' : 1, 'q' : {'2' : 'bee'}})
        del i1['q']
        assert ('q' in i1) == False


if __name__ == "__main__":
    unittest.main()

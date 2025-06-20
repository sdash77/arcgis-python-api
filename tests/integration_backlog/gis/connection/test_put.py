import unittest
import json
from arcgis.gis._impl._con import Connection
from utils.decorators import integration_test


@integration_test
class TestPutVerb(unittest.TestCase):
    # ----------------------------------------------------------------------
    def test_simple_put(self):
        """tests a simple default PUT"""
        url = "https://reqbin.com/sample/put/json"
        params = {"f": "json"}
        con = Connection()
        assert isinstance(con, Connection)
        res = con.put(url=url, params=params)
        assert res["success"]

    # ----------------------------------------------------------------------
    def test_json_post_json_put(self):
        """tests a simple default PUT"""
        url = "https://reqbin.com/sample/put/json"
        params = {"f": "json"}
        con = Connection()
        assert isinstance(con, Connection)
        res = con.put(url=url, params=params, post_json=True)
        assert res["success"]
        res = con.put(url=url, params=params, post_json=False)
        assert res["success"]

    # ----------------------------------------------------------------------
    def test_json_post_json_encode_put(self):
        """tests a simple default PUT"""
        url = "https://reqbin.com/sample/put/json"
        params = {"f": "json"}
        con = Connection()
        assert isinstance(con, Connection)
        res = con.put(url=url, params=params, json_encode=True, post_json=True)
        assert res["success"]
        res = con.put(url=url, params=params, json_encode=True, post_json=False)
        assert res["success"]
        res = con.put(url=url, params=params, json_encode=False, post_json=False)
        assert res["success"]
        res = con.put(url=url, params=params, json_encode=False, post_json=True)
        assert res["success"]


if __name__ == "__main__":
    unittest.main()

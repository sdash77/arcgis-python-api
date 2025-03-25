import unittest
import pandas as pd
from arcgis.geometry import Geometry


g1 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 4326}})
g2 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 4326, "latestWKID": 4326}})
g3 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 3857}})
data1 = {"OID": [1], "global_var": "y", "test": "new_column", "SHAPE": [g1]}
data2 = {"OID": [1], "global_var": "x",  "SHAPE": [g2]}


class TestSRCompareOnSeDF(unittest.TestCase):
    """tests the join test"""
    def test_compare_sedf_sr(self):
        """
        compares SeDF sr properties
        """
        sdf1 = pd.DataFrame(data1)
        assert sdf1.spatial.name
        sdf2 = pd.DataFrame(data2)
        assert sdf2.spatial.name
        assert sdf1.spatial.sr == sdf2.spatial.sr

    def test_join_columns(self):
        sdf1 = pd.DataFrame(data1)
        sdf2 = pd.DataFrame(data2)
        sdf3 = sdf1.spatial.join(sdf2)
        assert sdf3.columns.tolist() == [
            "OID_left",
            "global_var_left",
            "test",
            "SHAPE",
            "index_right",
            "OID_right",
            "global_var_right",
        ]

    def test_sr_equals(self):
        """
        compares SeDF sr properties
        """
        assert g1.spatial_reference == g2.spatial_reference
        assert g1.spatial_reference != g3.spatial_reference
        assert (g1.spatial_reference == g3.spatial_reference) == False
        assert (g1.spatial_reference != g2.spatial_reference) == False

    def test_sedf_equals(self):
        """
        Test the equal method on GeoAccessor
        """
        sdf1 = pd.DataFrame(data1)
        sdf2 = pd.DataFrame(data2)

        assert sdf1.spatial.eq(sdf2.spatial) is False
        assert sdf1.spatial.eq(sdf1.spatial)
        assert (sdf1.spatial == sdf2.spatial) is False

    def test_sedf_compare(self):
        """
        Test the compare method on GeoAccessor
        """
        sdf1 = pd.DataFrame(data1)
        sdf2 = pd.DataFrame(data2)

        res = sdf1.spatial.compare(sdf2.spatial, match_field="global_var") #dict
        assert isinstance(res, dict)
        assert len(res["added_rows"]["global_var"]) == 1

if __name__ == "__main__":
    unittest.main()

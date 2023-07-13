import sys
sys.path.insert(0, r"C:\ipython_workfolder\geosaurus\src")

import unittest

import pandas as pd
from arcgis.gis import GIS
from arcgis.geometry import Geometry, Point
from arcgis.features import GeoAccessor, GeoSeriesAccessor


g1 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 4326}})
g2 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 4326, "latestWKID": 4326}})
g3 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 3857}})
data1 = {"OID": [1], "SHAPE": [g1]}
data2 = {"OID": [1], "SHAPE": [g2]}


class TestSRCompareOnSeDF(unittest.TestCase):
    """tests the join test"""

    # ----------------------------------------------------------------------
    def test_SR_SeDF_Compare(self):
        """
        compares SeDF sr properties
        """
        sdf1 = pd.DataFrame(data1)
        sdf1.spatial.name
        sdf2 = pd.DataFrame(data2)
        sdf2.spatial.name
        assert sdf1.spatial.sr == sdf2.spatial.sr
        sdf3 = sdf1.spatial.join(sdf2)
        assert sdf3.columns.tolist() == [
            "OID_left",
            "SHAPE",
            "index_right",
            "OID_right",
        ]

    # ----------------------------------------------------------------------
    def test_SR_equals(self):
        """
        compares SeDF sr properties
        """
        assert g1.spatial_reference == g2.spatial_reference
        assert g1.spatial_reference != g3.spatial_reference
        assert (g1.spatial_reference == g3.spatial_reference) == False
        assert (g1.spatial_reference != g2.spatial_reference) == False

    # ----------------------------------------------------------------------
    def test_sedf_eq(self):
        """
        Test the equal method on GeoAccessor
        """
        sdf1 = pd.DataFrame(data1)
        sdf2 = pd.DataFrame(data2)

        assert sdf1.spatial.eq(sdf2.spatial) is False
        assert sdf1.spatial.eq(sdf1.spatial)
        assert (sdf1.spatial == sdf2.spatial) is False

    # ----------------------------------------------------------------------
    def test_sedf_compare(self):
        """
        Test the compare method on GeoAccessor
        """
        sdf1 = pd.DataFrame(data1)
        sdf2 = pd.DataFrame(data2)

        assert sdf1.spatial.compare(sdf2.spatial) #dict

    # ----------------------------------------------------------------------
    def test_sedf_series_equal(self):
        """
        Test the equal method on GeoSeriesAccessor
        """
        # establish active gis
        gis = GIS(profile="your_online_profile")

        # Create first GeoSeriesAccessor
        addresses = ['123 Main St, New York, NY', '456 Elm St, Los Angeles, CA', '789 Oak St, Chicago, IL']
        data = {'address': addresses}
        df = pd.DataFrame(data)
        sdf = GeoAccessor.from_df(df)
        geo_series_accessor = sdf["SHAPE"].geom

        # Create second GeoSeriesAccessor
        addresses = ['456 Main St, New York, NY', '789 Elm St, Los Angeles, CA', '100 Oak St, Chicago, IL']
        data = {'address': addresses}
        df = pd.DataFrame(data)
        sdf2 = GeoAccessor.from_df(df)
        geo_series_accessor2 = sdf2["SHAPE"].geom
        # Test if equal
        assert geo_series_accessor.equals(geo_series_accessor2) is False
        assert geo_series_accessor2.equals(geo_series_accessor2)

if __name__ == "__main__":
    unittest.main()

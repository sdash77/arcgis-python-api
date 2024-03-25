import unittest

import pandas as pd
from arcgis.gis import GIS
from arcgis.geometry import Geometry
from arcgis.features import GeoAccessor
from utils.decorators import integration_test


g1 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 4326}})
g2 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 4326, "latestWKID": 4326}})
g3 = Geometry({"x": 1, "y": 2, "spatialReference": {"wkid": 3857}})
data1 = {"OID": [1], "SHAPE": [g1]}
data2 = {"OID": [1], "SHAPE": [g2]}


@integration_test
class TestSRCompareOnSeDF(unittest.TestCase):
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

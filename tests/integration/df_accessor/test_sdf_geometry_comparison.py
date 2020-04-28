
import unittest

import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.geometry import Geometry
from arcgis.features import GeoAccessor, GeoSeriesAccessor


g1 = Geometry({'x' : 1, 'y' : 2, 'spatialReference' : {'wkid' : 4326}})
g2 = Geometry({'x' : 1, 'y' : 2, 'spatialReference' :  {'wkid': 4326, 'latestWKID': 4326}})
g3 = Geometry({'x' : 1, 'y' : 2, 'spatialReference' :  {'wkid': 3857}})
data1 = {"OID" :[1], "SHAPE" : [g1]}
data2 = {"OID" :[1], "SHAPE" : [g2]}

class TestSRCompareOnSeDF(unittest.TestCase):
    """tests the join test"""
    #----------------------------------------------------------------------
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
        assert sdf3.columns.tolist() == ['OID_left', 'SHAPE', 'index_right', 'OID_right']
    #----------------------------------------------------------------------
    def test_SR_equals(self):
        """
        compares SeDF sr properties
        """
        assert g1.spatial_reference == g2.spatial_reference
        assert g1.spatial_reference != g3.spatial_reference
        assert (g1.spatial_reference == g3.spatial_reference) == False
        assert (g1.spatial_reference != g2.spatial_reference) == False
        

if __name__ == "__main__":
    unittest.main()

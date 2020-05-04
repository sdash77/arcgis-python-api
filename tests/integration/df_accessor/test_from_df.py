import sys
sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork\src")
import unittest
import pytest
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

polygon_data = [
    """MULTIPOLYGON (((30 20, 45 40, 10 40, 30 20)), ((15 5, 40 10, 10 20, 5 10, 15 5)))""", # WKT
    { # GeoJSON
                   "type": "Polygon",
                   "coordinates": [
                     [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                       [100.0, 1.0], [100.0, 0.0] ]
                     ]
    },
    {
        "rings" : [ 
            [ [-97.06138,32.837], [-97.06133,32.836], [-97.06124,32.834], [-97.06127,32.832], [-97.06138,32.837] ], 
            [ [-97.06326,32.759], [-97.06298,32.755], [-97.06153,32.749], [-97.06326,32.759] ]
            ],
        "spatialReference" : {"wkid" : 4326}
    }
    
]

class TestFromDF(unittest.TestCase):
    """Tests the `from_df` functionality"""
    
    def test_from_df(self):
        """tests the geometry_column set to value"""
        from arcgis.features import GeoAccessor, GeoSeriesAccessor
        df = pd.DataFrame(data={"geom" : polygon_data, "oid" : [1,2,3]})
        sdf = pd.DataFrame.spatial.from_df(df, geometry_column='geom')
        assert sdf.spatial.name
        assert sdf.spatial.sr['wkid'] == 4326
    def test_from_df_sr(self):
        """tests the geometry_column set to value"""
        from arcgis.features import GeoAccessor, GeoSeriesAccessor
        df = pd.DataFrame(data={"geom" : polygon_data, "oid" : [1,2,3]})
        sdf = pd.DataFrame.spatial.from_df(df, geometry_column='geom', sr=4326)
        assert sdf.spatial.name
        assert sdf.spatial.sr['wkid'] == 4326
    

if __name__ == "__main__":
    unittest.main()
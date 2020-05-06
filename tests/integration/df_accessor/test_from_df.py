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

dataset2 = [{"Unnamed: 0": 0, "Unnamed: 0.1": 0, "OBJECTID": 1, "iOEEncounteredID": 1, "ftNorthing": 1501166.5480627269, "ftEasting": 566546.4904219806}, {"Unnamed: 0": 1, "Unnamed: 0.1": 1, "OBJECTID": 2, "iOEEncounteredID": 2, "ftNorthing": 1501210.1001409742, "ftEasting": 567718.5333534777}, {"Unnamed: 0": 2, "Unnamed: 0.1": 2, "OBJECTID": 3, "iOEEncounteredID": 3, "ftNorthing": 1501548.460028559, "ftEasting": 568784.0131779015}, {"Unnamed: 0": 3, "Unnamed: 0.1": 3, "OBJECTID": 4, "iOEEncounteredID": 4, "ftNorthing": 1502049.1299589726, "ftEasting": 568425.8432905674}, {"Unnamed: 0": 4, "Unnamed: 0.1": 4, "OBJECTID": 5, "iOEEncounteredID": 5, "ftNorthing": 1501499.460126549, "ftEasting": 568779.0131879002}, {"Unnamed: 0": 5, "Unnamed: 0.1": 5, "OBJECTID": 6, "iOEEncounteredID": 6, "ftNorthing": 1499585.798927635, "ftEasting": 570088.1404908895}, {"Unnamed: 0": 6, "Unnamed: 0.1": 6, "OBJECTID": 7, "iOEEncounteredID": 7, "ftNorthing": 1500230.9800519643, "ftEasting": 577231.3834222257}, {"Unnamed: 0": 7, "Unnamed: 0.1": 7, "OBJECTID": 8, "iOEEncounteredID": 8, "ftNorthing": 1480716.5801044703, "ftEasting": 586698.8034637272}, {"Unnamed: 0": 8, "Unnamed: 0.1": 8, "OBJECTID": 9, "iOEEncounteredID": 9, "ftNorthing": 1496939.527973473, "ftEasting": 580633.4002402276}, {"Unnamed: 0": 9, "Unnamed: 0.1": 9, "OBJECTID": 10, "iOEEncounteredID": 10, "ftNorthing": 1496976.7939750552, "ftEasting": 580634.1702518165}, {"Unnamed: 0": 10, "Unnamed: 0.1": 10, "OBJECTID": 11, "iOEEncounteredID": 11, "ftNorthing": 1496969.403897971, "ftEasting": 580634.3992539793}, {"Unnamed: 0": 11, "Unnamed: 0.1": 11, "OBJECTID": 12, "iOEEncounteredID": 12, "ftNorthing": 1496949.6460634768, "ftEasting": 580633.6722213179}, {"Unnamed: 0": 12, "Unnamed: 0.1": 12, "OBJECTID": 13, "iOEEncounteredID": 13, "ftNorthing": 1496947.230057806, "ftEasting": 580633.5603448898}, {"Unnamed: 0": 13, "Unnamed: 0.1": 13, "OBJECTID": 14, "iOEEncounteredID": 14, "ftNorthing": 1496945.0781592282, "ftEasting": 580634.2102779746}, {"Unnamed: 0": 14, "Unnamed: 0.1": 14, "OBJECTID": 15, "iOEEncounteredID": 15, "ftNorthing": 1496954.600121811, "ftEasting": 580633.748336643}]

class TestFromDF(unittest.TestCase):
    """Tests the `from_df` functionality"""
    
    def test_from_df(self):
        """tests the geometry_column set to value"""
        from arcgis.features import GeoAccessor, GeoSeriesAccessor
        df = pd.DataFrame(data={"geom" : polygon_data, "oid" : [1,2,3]})
        sdf = pd.DataFrame.spatial.from_df(df, geometry_column='geom')
        assert sdf.spatial.name
        assert sdf.spatial.sr['wkid'] == 4326
    def test_from_df_no_sr(self):
        """tests converting data from a dataframe to a SeDF without an SR value"""
        from arcgis.features import GeoAccessor, GeoSeriesAccessor
        import arcgis
        df = pd.DataFrame(data=dataset2)
        df['geom'] = df.apply(lambda row : arcgis.geometry.Geometry({'x': row['ftNorthing'], 'y': row['ftEasting']}), axis=1 )
        sdf = df.spatial.from_df(df, geometry_column='geom')
        assert sdf.spatial.name
        assert sdf.spatial.sr['wkid'] == 4326        
        df = pd.DataFrame(data=dataset2)
        df['geom'] = df.apply(lambda row : arcgis.geometry.Geometry({'x': row['ftNorthing'], 'y': row['ftEasting']}), axis=1 )
        sdf = df.spatial.from_df(df, geometry_column='geom', sr=3857)        
        assert sdf.spatial.name
        assert sdf.spatial.sr['wkid'] in [3857, 102100]
        
    def test_from_df_sr(self):
        """tests the geometry_column set to value"""
        from arcgis.features import GeoAccessor, GeoSeriesAccessor
        df = pd.DataFrame(data={"geom" : polygon_data, "oid" : [1,2,3]})
        sdf = pd.DataFrame.spatial.from_df(df, geometry_column='geom', sr=4326)
        assert sdf.spatial.name
        assert sdf.spatial.sr['wkid'] == 4326
    

if __name__ == "__main__":
    unittest.main()
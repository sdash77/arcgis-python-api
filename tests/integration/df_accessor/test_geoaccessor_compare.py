import unittest
import pandas as pd
from arcgis.features.geo._accessor import GeoAccessor
from arcgis.geometry import Geometry



class TestGeoAccessorCompare(unittest.TestCase):
    def test_compare(self):
        # Create two DataFrames with a spatial column 'id' and some other columns
        df1 = pd.DataFrame({
            'id': [1, 2, 3],
            'value': ['a', 'b', 'c'],
            'SHAPE': [
                Geometry({'x': 1, 'y': 2, 'spatialReference': {'wkid': 4326}}),
                Geometry({'x': 2, 'y': 3, 'spatialReference': {'wkid': 4326}}),
                Geometry({'x': 3, 'y': 4, 'spatialReference': {'wkid': 4326}}),
            ],
        })
        df2 = pd.DataFrame({
            'id': [2, 3, 4],
            'value': ['b', 'x', 'd'],
            'SHAPE': [
                Geometry({'x': 2, 'y': 3, 'spatialReference': {'wkid': 4326}}),
                Geometry({'x': 3, 'y': 5, 'spatialReference': {'wkid': 4326}}),  # changed geometry for id=3
                Geometry({'x': 4, 'y': 6, 'spatialReference': {'wkid': 4326}}),
            ],
        })
        # Use actual GeoAccessor
        if df1.spatial.name != 'SHAPE': 
            df1.spatial.set_geometry('SHAPE')
        if df2.spatial.name != 'SHAPE':            
            df2.spatial.set_geometry('SHAPE')        
        geo1 = df1.spatial
        result = geo1.compare(df2, match_field='id')

        # Added rows: id=4
        self.assertFalse(result['added_rows'].empty)
        self.assertEqual(set(result['added_rows']['id']), {4})
        # Deleted rows: id=1
        self.assertFalse(result['deleted_rows'].empty)
        self.assertEqual(set(result['deleted_rows']['id']), {1})
        # Modified rows: id=3 (value changed from 'c' to 'x')
        self.assertFalse(result['modified_rows'].empty)
        self.assertEqual(set(result['modified_rows']['id']), {3})
        self.assertEqual(set(result['modified_rows']['value']), {'x'})

if __name__ == '__main__':
    unittest.main()
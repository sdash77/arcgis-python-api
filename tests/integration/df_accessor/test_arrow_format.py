import os
import sys
import uuid
import tempfile
import unittest
from arcgis.gis import GIS
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcgis.geometry import Geometry

###########################################################################
feather_data = [{'ADMIN_NAME': 'Mato Grosso',
  'CITY_NAME': 'Cuiaba',
  'CNTRY_NAME': 'Brazil',
  'FID': 1,
  'FIPS_CNTRY': 'BR',
  'GMI_ADMIN': 'BRA-MGR',
  'LABEL_FLAG': 0,
  'ObjectID': 0,
  'POP': 521934,
  'POP_CLASS': '500,000 to 999,999',
  'POP_RANK': 3,
  'PORT_ID': 0,
  'SHAPE': {'spatialReference': {'latestWkid': 3857, 'wkid': 102100},
            'x': -6244244.606196579,
            'y': -1760180.1804674473},
  'STATUS': 'Provincial capital'},
 {'ADMIN_NAME': 'Kentucky',
  'CITY_NAME': 'Frankfort',
  'CNTRY_NAME': 'United States',
  'FID': 2,
  'FIPS_CNTRY': 'US',
  'GMI_ADMIN': 'USA-KEN',
  'LABEL_FLAG': 0,
  'ObjectID': 500,
  'POP': 16315,
  'POP_CLASS': 'Less than 50,000',
  'POP_RANK': 7,
  'PORT_ID': 0,
  'SHAPE': {'spatialReference': {'latestWkid': 3857, 'wkid': 102100},
            'x': -9444234.68158556,
            'y': 4607859.987737344},
  'STATUS': 'Provincial capital'},
 {'ADMIN_NAME': 'Tennessee',
  'CITY_NAME': 'Nashville',
  'CNTRY_NAME': 'United States',
  'FID': 3,
  'FIPS_CNTRY': 'US',
  'GMI_ADMIN': 'USA-TNN',
  'LABEL_FLAG': 0,
  'ObjectID': 501,
  'POP': 530852,
  'POP_CLASS': '500,000 to 999,999',
  'POP_RANK': 3,
  'PORT_ID': 0,
  'SHAPE': {'spatialReference': {'latestWkid': 3857, 'wkid': 102100},
            'x': -9664535.074973334,
            'y': 4320178.250506939},
  'STATUS': 'Provincial capital'}]
###########################################################################
class TestEWKTFunctions(unittest.TestCase):
    def test_to_ewkt(self):
        """Tests the to Extended WKT format"""
        g = Geometry({'x': -6244244.606196579, 'y': -1760180.1804674473, 'spatialReference': {'wkid': 102100}})
        self.assertTrue( g.EWKT == "SRID=102100;POINT (-6244244.6061965786 -1760180.1804674473)")
        
    def test_from_ewkt(self):
        """Tests the From Extended WKT format"""
        g = Geometry("SRID=102100;POINT (-6244244.6061965786 -1760180.1804674473)")
        self.assertTrue(dict(g) == {'spatialReference': {'wkid': 102100},'x': -6244244.606196579,'y': -1760180.1804674473})
###########################################################################
class TestToFromArrow(unittest.TestCase):
    def test_to_feather(self):
        """tests the to_feather option `__arrow_array__` gets called"""
        sdf = pd.DataFrame(data=feather_data)
        sdf.spatial.set_geometry('SHAPE')
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, str(uuid.uuid4()) + ".feather")   
            sdf.to_feather(path=fp)
            assert os.path.isfile(fp)
    def test_to_feather_spatial_column(self):
        """tests the to_feather option `__arrow_array__` gets called and honors reading `GEOM` as geometry column"""
        sdf = pd.DataFrame(data=feather_data)
        sdf = sdf.rename(columns={"SHAPE" :"GEOM"})
        sdf.spatial.set_geometry('GEOM')
        
        with tempfile.TemporaryDirectory() as d:
            
            fp = os.path.join(d, str(uuid.uuid4()) + ".feather")            
            sdf.to_feather(path=fp)
            assert os.path.isfile(fp)
            sdf2 = pd.DataFrame.spatial.from_feather(fp, spatial_column='GEOM')
            assert sdf2.spatial.name == 'GEOM'
    def test_from_feather(self):
        """tests the GeoArray auto converting the EWKT to `Geometry`"""
        sdf = pd.DataFrame(data=feather_data)
        sdf.spatial.set_geometry('SHAPE')
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            fp = os.path.join(d, str(uuid.uuid4()) + ".feather")   
            sdf.to_feather(path=fp)
            sdf = pd.DataFrame.spatial.from_feather(fp)
            assert sdf.spatial.bbox
###########################################################################
if __name__ == "__main__":
    unittest.main()
    
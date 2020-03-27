import os
import sys
try:
    import arcpy
    _HASARCPY = True
except ImportError:
    _HASARCPY = False
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor
from arcgis.geometry import Geometry

import unittest
import pytest

SAMPLE_GEOMETRY_HASZ_HASM = {'hasZ': True, 'hasM' : True, 
                        'paths': [[[11559865.5434, 147204.92960000038, 0, 4], [11559866.5434, 147205.92960000038, 0, 4.1]]], 
                        'spatialReference': {'wkid': 102100, 'latestWkid': 3857}}
SAMPLE_GEOMETRY_HASZ_ONLY = {'hasZ': True, 'hasM' : False, 
                             'paths': [[[11559865.5434, 147204.92960000038, 0], [11559866.5434, 147205.92960000038, 10]]], 
                             'spatialReference': {'wkid': 102100, 'latestWkid': 3857}}
SAMPLE_GEOMETRY_MISSING = {'paths': [[[11559865.5434, 147204.92960000038], [11559866.5434, 147205.92960000038]]], 
                           'spatialReference': {'wkid': 102100, 'latestWkid': 3857}}
SAMPLE_GEOMETRY_HASM_ONLY = {'hasZ': False, 'hasM' : True, 
                             'paths': [[[11559865.5434, 147204.92960000038, 1], [11559866.5434, 147205.92960000038, 1.1]]], 
                             'spatialReference': {'wkid': 102100, 'latestWkid': 3857}}

GEOMS = [
    Geometry(g) for g in [SAMPLE_GEOMETRY_HASM_ONLY, 
                          SAMPLE_GEOMETRY_HASZ_HASM, 
                          SAMPLE_GEOMETRY_HASZ_ONLY, 
                          SAMPLE_GEOMETRY_MISSING]
         ]
###########################################################################
class TestHasZHasMGeometry(unittest.TestCase):
    """Tests the HasZ and HasM Geometries"""
    #----------------------------------------------------------------------
    def test_has_z(self):
        """tests the has z property on a Geometry object"""
        g1, g2, g3, g4 = GEOMS
        assert g1.has_z == False
        assert g2.has_z == True
        assert g3.has_z == True
        assert g4.has_z == False
    #----------------------------------------------------------------------
    def test_has_m(self):
        """tests the has z property on a Geometry object"""
        g1, g2, g3, g4 = GEOMS
        assert g1.has_m == True
        assert g2.has_m == True
        assert g3.has_m == False
        assert g4.has_m == False
###########################################################################
class TestGeoAccessorSpatialHasMHasZ(unittest.TestCase):
    """Tests the `spatial` has_z and has_m properties"""
    #----------------------------------------------------------------------
    def test_has_z_m(self):
        data = {
            "SHAPE" : [GEOMS[1]] * 4,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        assert sdf.spatial.has_z == True
        assert sdf.spatial.has_m == True
    #----------------------------------------------------------------------
    def test_does_not_have_z_m(self):
        data = {
            "SHAPE" : [GEOMS[3]] * 4,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        assert sdf.spatial.has_z == False
        assert sdf.spatial.has_m == False
    #----------------------------------------------------------------------
    def test_mixed_z_m(self):
        """tests the z/m mixture.  This should return False unless overwritten"""
        data = {
            "SHAPE" : GEOMS,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        assert sdf.spatial.has_z == False
        assert sdf.spatial.has_m == False
###########################################################################
class TestGeoSeriesAccessorSpatialHasMHasZ(unittest.TestCase):
    #----------------------------------------------------------------------
    def test_has_z_m(self):
        data = {
            "SHAPE" : [GEOMS[1]] * 4,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        sdf.spatial.name
        s1 = sdf.SHAPE.geom.has_z
        s2 = sdf.SHAPE.geom.has_m
        assert isinstance(s1, pd.Series)
        assert isinstance(s2, pd.Series)
        assert s1.all()
        assert s2.all()        
    #----------------------------------------------------------------------
    def test_does_not_have_z_m(self):
        data = {
            "SHAPE" : [GEOMS[3]] * 4,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        sdf.spatial.name
        assert sdf.SHAPE.geom.has_z.any() == False
        assert sdf.SHAPE.geom.has_m.any() == False  
    #----------------------------------------------------------------------
    def test_mixed_z_m(self):
        data = {
            "SHAPE" : GEOMS,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        sdf.spatial.name
        assert sdf.SHAPE.geom.has_z.any()
        assert sdf.SHAPE.geom.has_m.any()
        
@unittest.skipIf(_HASARCPY == False, "Missing ArcPy, skipping")
class TestSeDFIOCheckZCheckM(unittest.TestCase):
    """tests the IO operations"""
    #----------------------------------------------------------------------
    def test_io_featureclass_zm_2(self):
        """tests that the `to_featureclass` where has_z=True and has_m=False"""
        data = {
            "SHAPE" : [GEOMS[2]] * 4,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        sdf.spatial.name        
        fc = sdf.spatial.to_featureclass(
            os.path.join("in_memory", "hasmztest"), 
            has_z=True, 
            has_m=False)
        desc = arcpy.da.Describe(fc)
        assert desc['hasM'] == False
        assert desc['hasZ'] == True
        arcpy.management.Delete(fc)
    #----------------------------------------------------------------------
    def test_io_featureclass_zm_1(self):
        """tests that the `to_featureclass` where has_z=False and has_m=False"""
        data = {
            "SHAPE" : GEOMS,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        sdf.spatial.name        
        fc = sdf.spatial.to_featureclass(
            os.path.join("in_memory", "hasmztest"), 
            has_z=False, 
            has_m=False)
        desc = arcpy.da.Describe(fc)
        assert desc['hasM'] == False
        assert desc['hasZ'] == False
        arcpy.management.Delete(fc)
    #----------------------------------------------------------------------
    def test_io_featureclass_zm_3(self):
        """tests that the `to_featureclass` where has_z=False and has_m=True"""
        g = Geometry({'hasM': True, 'paths': [[[11559865.5434, 147204.92960000038, 1], [11559866.5434, 147205.92960000038, 1.1]]], 'spatialReference': {'wkid': 102100, 'latestWkid': 3857}})
        data = {
            "SHAPE" : [g] * 4,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        sdf.spatial.name        
        fc = sdf.spatial.to_featureclass(
            os.path.join("in_memory", "hasmztest"), 
            has_z=False, 
            has_m=True)
        desc = arcpy.da.Describe(fc)
        assert desc['hasM'] == True
        assert desc['hasZ'] == False
        arcpy.management.Delete(fc)    
    #----------------------------------------------------------------------
    def test_io_featureclass_zm_4(self):
        """tests that the `to_featureclass` where has_z=True and has_m=False"""
        data = {
            "SHAPE" : [GEOMS[0]] * 4,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        sdf.spatial.name        
        fc = sdf.spatial.to_featureclass(
            os.path.join("in_memory", "hasmztest"), 
            has_z=False, 
            has_m=True)
        desc = arcpy.da.Describe(fc)
        assert desc['hasM'] == True
        assert desc['hasZ'] == False
        arcpy.management.Delete(fc)     
    #----------------------------------------------------------------------
    def test_io_featureclass_no_z_m_5(self):
        """tests that the feature class will have M/Z in the feature class"""
        data = {
            "SHAPE" : [GEOMS[-1]] * 4,
            "OID" : [1,2,3,4]
        }
        sdf = pd.DataFrame(data)
        sdf.spatial.name        
        fc = sdf.spatial.to_featureclass(os.path.join("in_memory", "hasnomztest"))
        desc = arcpy.da.Describe(fc)
        assert desc['hasM'] == False
        assert desc['hasZ'] == False   
        arcpy.management.Delete(fc)
if __name__ == "__main__":
    unittest.main()
import os
import sys
#sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_issue_viz_take_3\src")
import json
import pytest
import unittest
import tempfile
from arcgis.features.geo._tools._metadata import _Metadata
from arcgis._impl.common._mixins import PropertyMap
from arcgis._impl.common._isd import InsensitiveDict
import pandas as pd
import arcgis

class TestSeDFRenderer(unittest.TestCase):
    """tests the visualizer on the SeDF"""
    
    def test_from_feature_layer(self):
        """tests pulling in the renderer from the FeatureLayer"""
        from arcgis.features import FeatureLayer
        fl = FeatureLayer("https://sampleserver1.arcgisonline.com/ArcGIS/rest/services/Demographics/ESRI_Census_USA/MapServer/5")        
        sdf = fl.query(as_df=True)        
        assert sdf.spatial.renderer == InsensitiveDict(fl.properties.drawingInfo.renderer)
    
    def test_self_created(self):
        """tests the case when a SeDF is created manually"""
        from arcgis.geometry import Geometry
        geoms = [Geometry({"x" : -118.15, "y" : 33.80, "spatialReference" : {"wkid" : 4326}})] * 5        
        data = {'SHAPE' : geoms,
                'L1' : [1,2,3,4,5]}
        df = pd.DataFrame(data=data)
        df.spatial.sr
        assert df.spatial._meta
        assert df.spatial.renderer
        assert df.spatial._meta
        assert df.spatial._meta.source_type is None
        assert df.spatial._meta.source is None
    
    def test_from_feature_class(self):
        """tests shows that feature classes get assigned a default symbology and it should not equal the feature layer"""
        from arcgis.features import FeatureLayer
        fl = FeatureLayer("https://sampleserver1.arcgisonline.com/ArcGIS/rest/services/Demographics/ESRI_Census_USA/MapServer/5")        
        sdf = fl.query(as_df=True) 
        with tempfile.TemporaryDirectory() as tmpdirectory:
            fp = os.path.join(tmpdirectory, "states.shp")
            data = sdf.spatial.to_featureclass(fp)
            sdf2 = pd.DataFrame.spatial.from_featureclass(fp)
            assert sdf2.spatial.renderer != InsensitiveDict(fl.properties.drawingInfo.renderer)
            assert sdf2.spatial._meta
            assert sdf2.spatial._meta.renderer
            assert sdf2.spatial._meta.source
            assert sdf2.spatial._meta.source_type
    
if __name__ == "__main__":
    unittest.main()
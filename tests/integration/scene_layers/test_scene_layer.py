import sys, os
from uuid import uuid4
import unittest
from arcgis.gis import GIS
from arcgis.mapping import (SceneLayer, #
                            Object3DLayer, #
                            Point3DLayer, 
                            PointCloudLayer, # 
                            IntegratedMeshLayer, #
                            BuildingLayer) #

packages = [
    "6bab267f92234ffd8b76d8436d6c3b15", # Building
    "3a1f02f2c5e942b78864f62ba3928dd5", # 3DObject
    "273aa54c3ec640cd99c88460e8a7c1d7", # Integrated Mask Layer
    "dcf46a9224f846f49e6e28fc316d5251", # Point Cloud Layer
    "fea8ebd688124281afd8f526de77bfc9",
]
###########################################################################
class TestSceneLayer(unittest.TestCase):
    """Tests the Scene Layer Operations"""
    def test_scene_layer(self):
        """tests the factory code"""
        sl = SceneLayer(url="https://tiles.arcgis.com/tiles/P3ePLMYs2RVChkJx/arcgis/rest/services/Buildings_Hamburg/SceneServer")
        assert isinstance(sl, Object3DLayer)

###########################################################################        
class TestOtherSceneLayer(unittest.TestCase):
    """tests the other scene layer types"""    
    def test_scene_layer_from_item(self):        
        gis = GIS(profile='your_online_profile', verify_cert=False)
        for itemid in packages:
            i = gis.content.get(itemid)
            layers = i.layers
            l = layers[0]
            assert isinstance(l._lyr_json, (dict, str))
            assert isinstance(l._lyr_dict, (dict, str))
            assert isinstance(layers, list)
            _ = [l._lyr_json for l in layers]
            _ = [l._lyr_dict for l in layers]
            _ = [l.properties for l in layers]
            assert all([isinstance(l, (BuildingLayer, Object3DLayer, 
                                       IntegratedMeshLayer, PointCloudLayer, 
                                       Point3DLayer)) \
                        for l in layers])

if __name__ == "__main__":
    unittest.main()
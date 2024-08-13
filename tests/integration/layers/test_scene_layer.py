from uuid import uuid4
import unittest
from arcgis.gis import GIS
from arcgis.layers import (
    SceneLayer,  #
    Object3DLayer,  #
    Point3DLayer,
    PointCloudLayer,  #
    IntegratedMeshLayer,  #
    BuildingLayer,
    Tiles3DLayer,
)  #
from utils.decorators import integration_test

packages = [
    "6bab267f92234ffd8b76d8436d6c3b15",  # Building
    "c09bdd6a31264991ab20a46509b2f324",  # 3DObject
    "273aa54c3ec640cd99c88460e8a7c1d7",  # Integrated Mask Layer
    "dcf46a9224f846f49e6e28fc316d5251",  # Point Cloud Layer
    "fea8ebd688124281afd8f526de77bfc9",
    "0c9a62b019aa4c5297f7ff1ff46bfd14",  # 3D Tiles
]


###########################################################################
@integration_test
class TestSceneLayer(unittest.TestCase):
    """Tests the Scene Layer Operations"""

    def test_scene_layer(self):
        """tests the factory code"""
        sl = SceneLayer(
            url="https://tiles.arcgis.com/tiles/P3ePLMYs2RVChkJx/arcgis/rest/services/Buildings_Hamburg/SceneServer"
        )
        assert isinstance(sl, Object3DLayer)


###########################################################################
@integration_test
class TestOtherSceneLayer(unittest.TestCase):
    """tests the other scene layer types"""

    def test_scene_layer_from_item(self):
        gis = GIS(profile="your_online_profile", verify_cert=False)
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
            assert all(
                [
                    isinstance(
                        l,
                        (
                            BuildingLayer,
                            Object3DLayer,
                            IntegratedMeshLayer,
                            PointCloudLayer,
                            Point3DLayer,
                            Tiles3DLayer,
                        ),
                    )
                    for l in layers
                ]
            )


if __name__ == "__main__":
    unittest.main()

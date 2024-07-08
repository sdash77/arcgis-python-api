import unittest
from arcgis.map import Scene
from arcgis.layers import (
    IntegratedMeshLayer,
    PointCloudLayer,
    SceneLayer,
    VoxelLayer,
    BuildingLayer,
    Object3DLayer,
)
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestAddLayersToMap(unittest.TestCase):

    def setUp(self):
        # create webmap
        self.wm = Scene()
        assert self.wm

    def test_integrated_mesh_layer(self):
        """Test adding an integrated mesh layer"""
        # add layer
        layer = IntegratedMeshLayer(
            "https://tiles.arcgis.com/tiles/cFEFS0EWrhfDeVw9/arcgis/rest/services/Buildings_Frankfurt_2021/SceneServer",
            self.gis,
        )

        assert layer
        self.wm.content.add(layer)
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], IntegratedMeshLayer)

    def test_building_layer(self):
        """Test adding a building layer"""
        # add layer
        layer = BuildingLayer(
            "https://tiles.arcgis.com/tiles/V6ZHFr6zdgNZuVG0/arcgis/rest/services/Esri_Admin_Building/SceneServer",
            self.gis,
        )

        assert layer
        self.wm.content.add(layer)
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], BuildingLayer)

    def test_point_cloud_layer(self):
        """Test adding a point cloud layer"""
        # add layer
        layer = PointCloudLayer(
            "https://tiles.arcgis.com/tiles/V6ZHFr6zdgNZuVG0/arcgis/rest/services/BARNEGAT_BAY_LiDAR_UTM/SceneServer",
            self.gis,
        )

        assert layer
        self.wm.content.add(layer)
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], PointCloudLayer)

    def test_scene_layer(self):
        """Test adding a scene layer"""
        # add layer (object 3D layer in the Python API)
        layer = SceneLayer(
            "https://services.arcgis.com/V6ZHFr6zdgNZuVG0/arcgis/rest/services/Paris_3D_Local_WSL2/SceneServer/layers/0",
            self.gis,
        )

        assert layer
        self.wm.content.add(layer)
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], Object3DLayer)

    def test_voxel_layer(self):
        """Test adding a voxel layer"""
        # add layer
        layer = VoxelLayer(
            "https://tiles.arcgis.com/tiles/z2tnIkrLQ2BRzr6P/arcgis/rest/services/EMU_Caribbean_Voxel/SceneServer",
            self.gis,
        )

        assert layer
        self.wm.content.add(layer)
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], VoxelLayer)


if __name__ == "__main__":
    unittest.main()

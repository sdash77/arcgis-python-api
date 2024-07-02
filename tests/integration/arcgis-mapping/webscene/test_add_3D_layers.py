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

PROFILES = ["your_online_profile"]


class TestAddLayersToMap(unittest.TestCase):
    def test_integrated_mesh_layer(self):
        """Test adding an integrated mesh layer"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Scene()
            assert wm

            # add layer
            layer = IntegratedMeshLayer(
                "https://tiles.arcgis.com/tiles/cFEFS0EWrhfDeVw9/arcgis/rest/services/Buildings_Frankfurt_2021/SceneServer",
                gis,
            )

            assert layer
            wm.content.add(layer)
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], IntegratedMeshLayer)

    def test_building_layer(self):
        """Test adding a building layer"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Scene()
            assert wm

            # add layer
            layer = BuildingLayer(
                "https://tiles.arcgis.com/tiles/V6ZHFr6zdgNZuVG0/arcgis/rest/services/Esri_Admin_Building/SceneServer",
                gis,
            )

            assert layer
            wm.content.add(layer)
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], BuildingLayer)

    def test_point_cloud_layer(self):
        """Test adding a point cloud layer"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Scene()
            assert wm

            # add layer
            layer = PointCloudLayer(
                "https://tiles.arcgis.com/tiles/V6ZHFr6zdgNZuVG0/arcgis/rest/services/BARNEGAT_BAY_LiDAR_UTM/SceneServer",
                gis,
            )

            assert layer
            wm.content.add(layer)
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], PointCloudLayer)

    def test_scene_layer(self):
        """Test adding a scene layer"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Scene()
            assert wm

            # add layer (object 3D layer in the Python API)
            layer = SceneLayer(
                "https://services.arcgis.com/V6ZHFr6zdgNZuVG0/arcgis/rest/services/Paris_3D_Local_WSL2/SceneServer/layers/0",
                gis,
            )

            assert layer
            wm.content.add(layer)
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], Object3DLayer)

    def test_voxel_layer(self):
        """Test adding a voxel layer"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            # create webmap
            wm = Scene()
            assert wm

            # add layer
            layer = VoxelLayer(
                "https://tiles.arcgis.com/tiles/z2tnIkrLQ2BRzr6P/arcgis/rest/services/EMU_Caribbean_Voxel/SceneServer",
                gis,
            )

            assert layer
            wm.content.add(layer)
            assert wm.content.layers
            assert len(wm.content.layers) == 1
            assert isinstance(wm.content.layers[0], VoxelLayer)


if __name__ == "__main__":
    unittest.main()

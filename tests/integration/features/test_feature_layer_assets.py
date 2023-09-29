import sys

# sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus\\src")
import unittest
from arcgis.features import FeatureLayer
from arcgis.gis import GIS

# Devext profile for now and enterprise
profiles = ["your_dev_profile"]
# 3D Object Feature Layer
fl_3d_online = FeatureLayer(
    "https://servicesdev.arcgis.com/5xC5Wrapp1gUAl2r/ArcGIS/rest/services/CUBE_WGS84_APIforPython/FeatureServer/0"
)
fl_3d_enterprise = FeatureLayer("https://zhsvteb03.esri.com/server/rest/services/Hosted/CUBE_APIforPython/FeatureServer/0")


class TestQueryFeatureLayer(unittest.TestCase):
    def test_assets(self):
        """
        Test the assets method for 3D object feature layers.
        """
        for profile in profiles:
            gis = GIS(profile=profile)

            if gis._is_agol:
                fl_3d = fl_3d_online
            else:
                fl_3d = fl_3d_enterprise

            resp = fl_3d.assets(
                "d7facaf8526acb749214d05d0ee5fc28145b013d2906edf1fc3baef81f0ae509"
            )
            assert resp

    def test_cleanup_assets(self):
        """
        Test the cleanup assets method for 3D object feature layers.
        """
        for profile in profiles:
            gis = GIS(profile=profile)

            if gis._is_agol:
                fl_3d = fl_3d_online
            else:
                fl_3d = fl_3d_enterprise
            resp = fl_3d.cleanup_assets(1000, "days")
            assert resp

    def test_has_assets(self):
        """
        Test the has assets method for 3D object feature layers.
        """
        for profile in profiles:
            gis = GIS(profile=profile)

            if gis._is_agol:
                fl_3d = fl_3d_online
            else:
                fl_3d = fl_3d_enterprise
            resp = fl_3d.has_assets(
                ["d7facaf8526acb749214d05d0ee5fc28145b013d2906edf1fc3baef81f0ae509"]
            )
            assert resp

    def test_query_assets(self):
        for profile in profiles:
            gis = GIS(profile=profile)

            if gis._is_agol:
                fl_3d = fl_3d_online
            else:
                fl_3d = fl_3d_enterprise
            resp = fl_3d.query_assets(
                ["d7facaf8526acb749214d05d0ee5fc28145b013d2906edf1fc3baef81f0ae509"]
            )
            assert resp

    def test_upload_assets(self):
        for profile in profiles:
            gis = GIS(profile=profile)

            if gis._is_agol:
                fl_3d = fl_3d_online
            else:
                fl_3d = fl_3d_enterprise
            assets = [
                {
                    "assetType": "3D_gltf",
                    "assetData": "Z2xURgIAAACoiRAAsFcAAEpTT057ImFjY2Vzc29ycyI6W3siYnVmZmVyVmlldyI6MSwiY29tcG9uZ",
                },
                {
                    "assetType": "IM_png",
                    "assetUploadId": "i0bcaf83a-85e2-40a3-b1e7-f80c7b63b832",
                },
            ]

            resp = fl_3d.upload_assets(assets)
            assert resp

if __name__ == "__main__":
    unittest.main()
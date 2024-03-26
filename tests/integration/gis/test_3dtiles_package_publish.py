import json
import time
import datetime
import unittest

from arcgis.gis import GIS, Item

PROFILES = [
    "your_online_profile",  
    #"your_enterprise_profile" #enterprise 11.3
    ]

class TestPublish3DFile(unittest.TestCase):
    def test_publish_3dtile_3dobject(self):
        for profile in PROFILES:
            gis = GIS(profile=profile)

            new_package = gis.content.add({"title": "NewTilePackage3D"}, data=r"\\qalab_server\checklist_data\SceneLayers\3DTiles\ESRICreated\with_compression\PhillyTextured.3tz")
            new_item = new_package.publish()
            self.assertIsNotNone(new_item)
            self.assertEqual(new_item.type, "3DTiles Service")
            self.assertTrue(new_item.delete())

    def test_publish_3dtile_integrated_mesh(self):
        for profile in PROFILES:
            gis = GIS(profile=profile)

            new_package = gis.content.add({"title": "NewTilePackage3D"}, data=r"\\qalab_server\checklist_data\SceneLayers\3DTiles\ESRICreated\with_compression\Boston.3tz")
            new_item = new_package.publish()
            self.assertIsNotNone(new_item)
            self.assertEqual(new_item.type, "3DTiles Service")
            self.assertTrue(new_item.delete())

if __name__ == "__main__":
    unittest.main()
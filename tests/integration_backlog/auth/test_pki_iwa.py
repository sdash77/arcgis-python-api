import os
import unittest
import uuid
from arcgis.gis import GIS, ItemTypeEnum
from utils import INTEGRATION_TESTS_DIR
from pathlib import Path
from utils.decorators import credentials, integration_test
from utils.data_utils import cleanup_published_items, publish_test_item
from integration.config import get_resource_path
import requests


@integration_test
@credentials.enterprise_all_iwa
class TestIWAConnections(unittest.TestCase):
    """Tests IWA access to portal/server"""

    @classmethod
    def setUpClass(cls):
        cls.published_items = []
        cls.fp = get_resource_path(
            "staging_data/auth/dataset_test_123a.zip", unique_copy=True
        )

    def setUp(self):
        try:
            self.gis = GIS(
                url=self.portal_url,
                verify_cert=False,
                proxy={
                    "http": "http://127.0.0.1:8999",
                    "https": "http://127.0.0.1:8999",
                },
            )
            print("ddd")
        except requests.exceptions.RequestException:
            # TODO: failure is not very descriptive
            # requests.exceptions.RequestException: A general exception was raised: Expecting value: line 1 column 1 (char 0)
            # consider raising an invalid credentials exception with a more descriptive message
            print(
                "Failed to connect to IWA GIS using integration method, attempting to pass credentials"
            )
            self.gis = GIS(
                url=self.portal_url,
                verify_cert=False,
                username=self.username,
                password=self.password,
            )

    def test_login(self):
        assert self.gis
        assert self.gis.users.me

    def test_geocoding(self):
        """tests geocoding with IWA"""
        from arcgis.geocoding import get_geocoders

        assert self.gis
        geocoders = get_geocoders(self.gis)
        if len(geocoders) == 0:
            self.skipTest("No geocoders available")
        assert geocoders[0]._geocode(address="12 york street, camden, NJ")

    def test_publish_fgdb(self):
        """tests publishing an item via IWA"""
        assert self.gis
        assert self.gis.users.me

        uid = uuid.uuid4().hex[:5]
        published_item = publish_test_item(
            gis=self.gis,
            layer_name=f"miwa_layer_{uid}",
            source_data_path=self.fp,
            item_type=ItemTypeEnum.FILE_GEODATABASE,
            prep_for_editing=False,
        )
        self.assertTrue(published_item, "Item not published correctly")
        self.published_items.append(published_item)
        assert published_item
        assert published_item.layers
        assert published_item.layers[0].properties

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(cls.published_items)


# @integration_test
# @credentials.enterprise_all_pki
# class TestPKIConnections(unittest.TestCase):
#     """Tests PKI access to portal/server"""
#
#     @classmethod
#     def setUpClass(cls):
#         cls.published_items = []
#         cls.fp = get_resource_path("staging_data/auth/dataset_test_123a.zip")
#
#     def setUp(self):
#         self.gis = GIS(
#             url=self.portal_url,
#             cert_file=self.cert,
#             password=self.password,
#             verify_cert=False,
#         )
#
#     def test_login(self):
#         assert self.gis
#         assert self.gis.users.me
#
#     def test_publish_fgdb(self):
#         """tests publishing an item via PKI"""
#         assert self.gis
#         assert self.gis.users.me
#
#         uid = uuid.uuid4().hex[:5]
#         published_item = publish_test_item(
#             gis=self.gis,
#             layer_name=f"miwa_layer_{uid}",
#             source_data_path=self.fp,
#             item_type=ItemTypeEnum.FILE_GEODATABASE,
#             prep_for_editing=False,
#         )
#         self.assertTrue(published_item, "Item not published correctly")
#         self.published_items.append(published_item)
#         assert published_item
#         assert published_item.layers
#         assert published_item.layers[0].properties
#
#     def test_geocoding(self):
#         """tests using geocoding with PKI"""
#         assert self.gis
#         from arcgis.geocoding import get_geocoders
#
#         geocoders = get_geocoders(self.gis)
#         if len(geocoders) == 0:
#             self.skipTest("No geocoders available")
#
#         assert geocoders[0]._geocode(address="12 york street, camden, NJ")
#
#     @classmethod
#     def tearDownClass(cls):
#         cleanup_published_items(cls.published_items)


if __name__ == "__main__":
    unittest.main()

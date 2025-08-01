# --------------------------------------------------------------------------------------
# Name:        Test for the registration of applications with the Item class. 
#              Mutiple app types are registered and unregistred with property
#              values confirmed.
# Purpose:     Integration tests for registering app items using the  ArcGIS Python API.
# --------------------------------------------------------------------------------------

import unittest
import time

from integration.config import (
    INTEGRATION_TEST_ITEM_TAG
)
from utils.decorators import integration_test, profiles
from utils.data_utils import (
    cleanup_published_items,
    cleanup_folders
)

from arcgis.gis import GIS, ItemProperties, ItemTypeEnum

@profiles.admin_all
@integration_test
class Test_Item_app_registration(unittest.TestCase):  
    @classmethod
    def setUpClass(cls):
        
        # Enteprise 11.5
        cls.gis = GIS(
            url="https://rextapilnx02eb.esri.com/portal",
            username="PAPIadmin",
            password="PAPIletmein01"
        )
        # Enterprise 12.0 - bld 58615
        #cls.gis = GIS(
            #url="https://rqawinbi01pt.ags.esri.com/gis",
            #username="PAPIadmin",
            #password="PAPIletmein01"
        #)        
        
        # Kubernetes 11.5
        #cls.gis = GIS(
            #url="https://1150pubbi-1150pubbi.apps.openshift416release.esri.com/web",
            #username="PAPIadmin",
            #password="PAPIletmein01"            
        #)
        # Kubernetes 12.0
        #cls.gis = GIS(
            #url="https://devet00110.esri.com/arcgis",
            #username="administrator",
            #password="esri.agp1"
        #)
        
        cls.item_test_app_register_folder = cls.gis.content.folders._get_or_create(
           "item_app_register_ntgrtn_tests"
        )
        
        cls.app_reg = cls.item_test_app_register_folder.add(
            item_properties=ItemProperties(
                title=f"multiple_app_register_api_unreg_test",
                item_type=ItemTypeEnum.APPLICATION,
                snippet="Test application for register method in api.",
                tags=INTEGRATION_TEST_ITEM_TAG,
            )
        ).result()
        
    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")
        test_items = list(cls.item_test_app_register_folder.list())
        if test_items:
            cleanup_published_items(test_items)
        else:
            print(f"Test items already cleared from test folder.")
        cleanup_folders(
            gis=cls.gis,
            folder_names=[cls.item_test_app_register_folder.name]
        )
        
    def setUp(self):
        print(f"\n{'-' * 40}\nTest: starting {self._testMethodName}...")
        self._start_time = time.time()
        
    def tearDown(self):
        elapsed_time = time.time() - self._start_time
        print(f"{' ' * 4}...test took {elapsed_time / 60:.2f} minutes.\n")    

    def test_register_application(self):
        """tests the registering of an Application item"""
        
        for at in ["browser", "native", "server", "multiple"]:
            with self.subTest(f"Test for registering {at} app with api.", i=at):
                ip = ItemProperties(
                    title=f"{at}_app_register_api_test",
                    item_type=ItemTypeEnum.APPLICATION,
                    snippet="Test application for register method in api.",
                    tags=INTEGRATION_TEST_ITEM_TAG,
                )
                item = self.item_test_app_register_folder.add(
                    item_properties=ip
                ).result()
                
                reg = item.register(app_type=at)
                self.assertIsInstance(
                    item.app_info,
                    dict,
                    "The app_info property failed to return a dict."
                )
                self.assertGreater(
                    len(item.app_info),
                    0,
                    "the app_info property for registered app returns empty dict."
                )
                self.assertTrue(
                    reg.get("client_id", False),
                    f"Registering application {item.title} failed to generate client_id."
                )
                self.assertTrue(
                    reg.get("client_secret", False),
                    f"Registering application {item.title} failed to generate client_secret."
                )

    def test_unregister_application(self):
        """tests the unregistering of an Application item"""
        
        item = self.app_reg
        
        registered_app = item.register(app_type="multiple")

        unreg = item.unregister()

        self.assertTrue(
            unreg,
            "Unregistering an app field to return True."
        )
        self.assertEqual(
            len(item.app_info),
            0,
            "After unregistering an app the app_info property still returns dict with content."
        )
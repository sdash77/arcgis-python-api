# -------------------------------------------------------------------------------
# Name:        Item class tests for various aspects of the ResourceManager class
#              using items known to have reource output.
# Purpose:     Integration tests for resources property of the Item class using
#              the ArcGIS Python API.
# -------------------------------------------------------------------------------

import unittest

from utils.decorators import integration_test, profiles

from arcgis.gis import ResourceManager

#@profiles.admin_enterprise_and_agol
@integration_test
class Test_Item_resources_methods(unittest.TestCase):  
    """Testing the resources property and methods on the Resource Manager."""
    
    @classmethod
    def setUpClass(cls):
        """
        Test for resource manager on StoryMap items, which always have resources.
        """
        cls.smap_items = cls.gis.content.search(
            query="Giraffes *",
            item_type="StoryMap"
        )
        if not cls.smap_items:
            cls.smap_items = cls.gis.content.search(
                query=f"owner:{cls.gis.users.me.username}",
                item_type="StoryMap"
            )
        cls.smap_item = cls.smap_items[0]      
        
    def test_resources_property(self):
        res_mgr = self.smap_item.resources
        
        self.assertIsInstance(
            res_mgr,
            ResourceManager,
            "The resources property did not return ResourceManager object."
        )        
        self.assertEqual(
            self.smap_item.type,
            "StoryMap",
            "Item for test is not a Story Map item as expected."
        )
        self.assertGreater(
            len(res_mgr.list()),
            0,
            "StoryMap item has no resources as expected."
        )
        self.assertIsInstance(
            res_mgr.list()[0],
            dict,
            "Resource Manager list method does not return list of dictionaries as expected."
        )
        self.assertIn(
            res_mgr.list()[0]["resource"][-4:],
            ["json", "jpeg", "png"],
            "Story Map resource not in list of expected extensions."
        )

if __name__ == "__main__":
    unittest.main()
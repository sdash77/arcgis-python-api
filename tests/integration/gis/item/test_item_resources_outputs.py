# -------------------------------------------------------------------------------
# Name:        Item class tests for various aspects of the ResourceManager class
#              using items known to have reource output.
# Purpose:     Integration tests for resources property of the Item class using
#              the ArcGIS Python API.
# -------------------------------------------------------------------------------

import unittest

from utils.decorators import integration_test, profiles
from utils.data_utils import cleanup_published_items, INTEGRATION_TEST_ITEM_TAG
from integration.config import get_resource_path

from arcgis.gis import ResourceManager

@profiles.admin_all
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
            try:
                cls.smap_item = cls.gis.content.search(
                    query=f"owner:{cls.gis.users.me.username}",
                    item_type="StoryMap"
                    )[0]
            except IndexError as ie:
                from arcgis.apps.storymap import StoryMap, Image, Themes
                
                cls.story = StoryMap(gis=cls.gis)
            
                # image for story cover
                resource_path = get_resource_path("storymap")
                cls.river = Image(f'{resource_path}/storymap_image_river.jpg')
                # Edit story cover
                cover = cls.story.content_list[0]
                cover.title = "River Story Map for Kubernetes"
                cover.summary = "StoryMap to test Python API ResourceManager in Kubernetes."
                cover.by_line = "Python API Test-Runner"
                cover.media = cls.river
        
                # Change the story theme
                cls.story.theme(Themes.SLATE)
        
                # Save the storymap changes
                cls.smap_item = cls.story.save(
                    title="River Storymap for Python API Testing",
                    tags=INTEGRATION_TEST_ITEM_TAG
                )
        else:
            cls.smap_item = cls.smap_items[0]
    
    @classmethod
    def tearDownClass(cls):
        if cls.gis._is_kubernetes:
            cleanup_published_items(items=[cls.smap_item])
        
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
import unittest
from arcgis.gis import GIS, Item
from arcgis.apps.storymap import StoryMap
from arcgis.apps.storymap.story_content import Map, Scales
from utils.decorators import integration_test, profiles


@integration_test
@profiles.enterprise_and_agol
class TestMapContent(unittest.TestCase):
    """Test adding an map and seeing properties"""

    def test_add_map(self):
        """
        Test adding a Map and seeing the properties
        Map id can be changed if not found.
        """
        for profile in profiles:
            with self.subTest(msg=profile):
                # establish gis connection
                gis = GIS(profile=profile, verify_cert=False)
                story = StoryMap()
                import arcgis.map as arcgismapping

                wm_test = arcgismapping.Map()
                wm_item = wm_test.save(
                    item_properties={
                        "title": "Test WebMap for ArcGIS StoryMap Test",
                        "tags": ["python", "storymaps"],
                        "snippet": "Creating a map for the purpose of the ArcGIS StoryMap in Python API Test.",
                    }
                )
                map_content = Map(wm_item.id)
                map = story.add(
                    map_content, caption="This is a map that has nothing special on it."
                )
                map = story.get(map)
                assert map
                assert map_content.properties
                assert isinstance(map_content.map, Item)
                assert map_content.caption
                assert isinstance(map.set_viewpoint(scale=Scales.CONTINENT), dict)

        item = gis.content.get(story._itemid)
        assert item.delete()


if __name__ == "__main__":
    unittest.main()

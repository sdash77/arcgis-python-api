import unittest
from arcgis.gis import GIS, Item
from arcgis.layers import Service
from arcgis.apps import storymap
from utils.decorators import integration_test, profiles
from arcgis.auth.tools import LazyLoader
arcgismapping = LazyLoader("arcgis.map")


@integration_test
@profiles.agol
class TestMapContent(unittest.TestCase):
    """Test adding an map and seeing properties"""

    def test_add_map(self):
        """
        Test adding a Map and seeing the properties
        Map id can be changed if not found.
        """
        # establish gis connection
        story = storymap.StoryMap(gis=gis)

        wm_test = arcgismapping.Map()
        wm_item = wm_test.save(
            item_properties={
                "title": "Test WebMap for ArcGIS StoryMap Test",
                "tags": ["python", "storymaps"],
                "snippet": "Creating a map for the purpose of the ArcGIS StoryMap in Python API Test.",
            }
        )
        smap = storymap.Map(wm_item)
        story.add(
            smap, caption="This is a map that has nothing special on it."
        )
        assert smap
        assert smap.properties
        assert isinstance(smap.map, Item)
        assert smap.caption
        assert isinstance(smap.set_viewpoint(scale=storymap.Scales.CONTINENT), dict)
        assert story._item.delete(permanent=True)
        
    def test_map_properties(self):
        """
        Test the properties found on the Map in the StoryMap
        """
        # establish gis connection
        story = storymap.StoryMap(gis=gis)

        wm_test = arcgismapping.Map()
        wm_test.content.add(Service("https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/2"))
        wm_item = wm_test.save(
            item_properties={
                "title": "Test WebMap for ArcGIS StoryMap Test",
                "tags": ["python", "storymaps"],
                "snippet": "Creating a map for the purpose of the ArcGIS StoryMap in Python API Test.",
            }
        )
        smap = storymap.Map(wm_item)
        story.add(
            smap, caption="This is a map that has nothing special on it."
        )
        assert isinstance(smap, storymap.Map)
        assert smap.caption == "This is a map that has nothing special on it."
        assert isinstance(smap.map_layers, list)
        
        assert smap.pinned_popup_info is None
        smap.pinned_popup_info = {
            "layerId": smap.map_layers[0]["id"],
            "idFieldName": "OBJECTID",
            "idFieldValue": 1,
            "location": {}
        }
        assert smap.pinned_popup_info
        
        assert smap.show_legend is False
        smap.show_legend = True
        assert smap.show_legend is True
        
        assert smap.legend_pinned is False
        smap.legend_pinned = True
        assert smap.legend_pinned is True
        
        assert smap.show_search is False
        smap.show_search = True
        assert smap.show_search is True
        
        assert smap.time_slider is False
        smap.time_slider = True
        assert smap.time_slider is True
        
        assert smap.popup_docked is False
        smap.popup_docked = True
        assert smap.popup_docked is True
        
        assert story._item.delete(permanent=True)
        
        


if __name__ == "__main__":
    unittest.main()

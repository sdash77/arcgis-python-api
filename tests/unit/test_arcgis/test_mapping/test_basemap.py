import unittest

gen_input_item_prop = {"title": "title", "snippet": "snippet", "tags": ["tags"]}
class TestBasemap(unittest.TestCase):

    def test_set_basemap_to_invalid_string(self):
        """Tests that WebMap.save throws an exception if a user doesn't pass in
        a dict with the 'title', 'snippet', 'tags' keys
        """
        from arcgis.mapping import WebMap

        wm = WebMap()
        try:
            wm.basemap = "hello"
        except RuntimeError as e:
            assert "Basemap 'hello' isn't valid" in str(e)

    def test_set_basemap_to_valid_string(self):
        """Tests that WebMap.save throws an exception if a user doesn't pass in
        a dict with the 'title', 'snippet', 'tags' keys
        """
        from arcgis.mapping import WebMap

        wm = WebMap()
        wm.basemap = "oceans"
        assert "oceans" in str(wm.basemap["baseMapLayers"]) and "oceans" in str(
            wm._webmapdict
        )

    def test_set_basemap_using_webmap_basemap(self):
        from arcgis.mapping import WebMap

        wm = WebMap()
        wm.basemap = "osm"
        wm2 = WebMap()
        wm2.basemap = wm.basemap
        assert "osm" in str(wm.basemap["baseMapLayers"]) and "osm" in str(wm._webmapdict)

    def test_set_basemap_using_webmap_object(self):
        from arcgis.mapping import WebMap

        wm = WebMap()
        wm.basemap = "dark-gray-vector"
        wm2 = WebMap()
        wm2.basemap = wm
        assert "dark-gray-base-layer" in str(wm.basemap["baseMapLayers"]) and "Dark Gray Vector" in str(
            wm._webmapdict
        )

    def test_default_basemap_no_gis(self):
        from arcgis.mapping import WebMap

        wm = WebMap()
        assert wm.basemap



if __name__ == "__main__":

    unittest.main()

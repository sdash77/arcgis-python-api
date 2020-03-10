import pytest
from arcgis.mapping import WebMap
gen_input_item_prop = {'title':'title', 'snippet':'snippet', 'tags':['tags']}


def test_set_basemap_to_invalid_string():
    """Tests that WebMap.save throws an exception if a user doesn't pass in
    a dict with the 'title', 'snippet', 'tags' keys
    """
    wm = WebMap()
    with pytest.raises(RuntimeError) as e:
        wm.basemap = 'hello'
    assert "Basemap 'hello' isn't valid" in str(e.value)


def test_set_basemap_to_valid_string():
    """Tests that WebMap.save throws an exception if a user doesn't pass in
    a dict with the 'title', 'snippet', 'tags' keys
    """
    wm = WebMap()
    wm.basemap = 'oceans'
    assert "oceans" in str(wm.basemap["baseMapLayers"]) and "oceans" in str(wm._webmapdict)


def test_set_basemap_using_webmap_basemap():
    wm = WebMap()
    wm.basemap = 'osm'
    wm2 = WebMap()
    wm2.basemap = wm.basemap
    assert "osm" in str(wm.basemap["baseMapLayers"]) and "osm" in str(wm._webmapdict)


def test_set_basemap_using_webmap_object():
    wm = WebMap()
    wm.basemap = 'dark-gray'
    wm2 = WebMap()
    wm2.basemap = wm
    assert "dark-gray" in str(wm.basemap["baseMapLayers"]) and "dark-gray" in str(wm._webmapdict)


def test_default_basemap_no_gis():
    wm = WebMap()
    assert "World Topographic Map" in str(wm.basemap)


def test_gallery_basemap_no_gis():
    wm = WebMap()
    assert len(wm.gallery_basemaps) == 0
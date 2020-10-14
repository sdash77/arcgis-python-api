import pytest
from unittest.mock import patch

from utils.mocks import MockMapView

gen_input_item_prop = {'title':'title', 'snippet':'snippet', 'tags':['tags']}

@patch("arcgis.widgets.MapView", MockMapView)
def test_set_basemap_to_invalid_string():
    """Tests that WebMap.save throws an exception if a user doesn't pass in
    a dict with the 'title', 'snippet', 'tags' keys
    """
    from arcgis.mapping import WebMap
    wm = WebMap()
    with pytest.raises(RuntimeError) as e:
        wm.basemap = 'hello'
    assert "Basemap 'hello' isn't valid" in str(e.value)

@patch("arcgis.widgets.MapView", MockMapView)
def test_set_basemap_to_valid_string():
    """Tests that WebMap.save throws an exception if a user doesn't pass in
    a dict with the 'title', 'snippet', 'tags' keys
    """
    from arcgis.mapping import WebMap
    wm = WebMap()
    wm.basemap = 'oceans'
    assert "oceans" in str(wm.basemap["baseMapLayers"]) and "oceans" in str(wm._webmapdict)

@patch("arcgis.widgets.MapView", MockMapView)
def test_set_basemap_using_webmap_basemap():
    from arcgis.mapping import WebMap
    wm = WebMap()
    wm.basemap = 'osm'
    wm2 = WebMap()
    wm2.basemap = wm.basemap
    assert "osm" in str(wm.basemap["baseMapLayers"]) and "osm" in str(wm._webmapdict)

@patch("arcgis.widgets.MapView", MockMapView)
def test_set_basemap_using_webmap_object():
    from arcgis.mapping import WebMap
    wm = WebMap()
    wm.basemap = 'dark-gray'
    wm2 = WebMap()
    wm2.basemap = wm
    assert "dark-gray" in str(wm.basemap["baseMapLayers"]) and "dark-gray" in str(wm._webmapdict)

@patch("arcgis.widgets.MapView", MockMapView)
def test_default_basemap_no_gis():
    from arcgis.mapping import WebMap
    wm = WebMap()
    assert "World Topographic Map" in str(wm.basemap)

@patch("arcgis.widgets.MapView", MockMapView)
def test_gallery_basemap_no_gis():
    from arcgis.mapping import WebMap
    wm = WebMap()
    assert len(wm.gallery_basemaps) == 0
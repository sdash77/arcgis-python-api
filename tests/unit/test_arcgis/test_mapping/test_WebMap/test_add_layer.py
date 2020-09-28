import pytest
from unittest.mock import patch

from utils.mocks import MockMapView, MockWebMap, MockGIS, PlaceholderItem

@patch("arcgis.widgets.MapView", MockMapView)
def test_add_item_map_service():
    """
    Tests that adding an `Item` Map Service won't add sub layers like
    other item types, but instead adds as a Map Image Layer
    """
    from arcgis.mapping import WebMap

    mock_webmap = MockWebMap()
    placeholder_item = PlaceholderItem()
    placeholder_item.type = "Map Service"
    placeholder_item.id = "7de187039a6e430f855f34bded8b6ee4"
    placeholder_item.url = "https://arbitrary.url"

    WebMap.add_layer(mock_webmap, placeholder_item)

    assert len(mock_webmap._webmapdict['operationalLayers']) == 1
    wm_out_oplayer = mock_webmap._webmapdict['operationalLayers'][0]
    assert wm_out_oplayer["itemId"] == "7de187039a6e430f855f34bded8b6ee4"
    assert wm_out_oplayer["url"] == "https://arbitrary.url"
    assert wm_out_oplayer["layerType"] == "ArcGISMapServiceLayer"
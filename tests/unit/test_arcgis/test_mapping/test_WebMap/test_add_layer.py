import pytest
from unittest.mock import patch

from utils.mocks import MockMapView, MockWebMap, MockGIS, MockFeatureLayer, PlaceholderItem
from utils.mocks.placeholders.placeholder_featurecollection import PlaceholderFeatureLayerCollection
from utils.mocks.placeholders.placeholder_featurelayer import PlaceholderFeatureLayer

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

@patch("arcgis.widgets.MapView", MockMapView)
def test_add_featurecollection_different_renderers():
    """FeatureCollections can have multiple layers with different renderers.
    Check that each sublayer has the correct renderer attached to it when
    added to a WebMap
    """
    from arcgis.mapping import WebMap
    from arcgis.gis import Layer

    mock_webmap = MockWebMap()
    # make sure recursive function gets called correctly
    mock_webmap.add_layer = lambda layer, options: WebMap.add_layer(mock_webmap, layer, options) 
    renderer_1 = { "type": "simple",
                   "symbol": {
                       "type": "esriPMS" }}
    renderer_2 = { "type": "simple",
                   "symbol" : {
                       "type": "esriSFS" }}
    mock_fl_1 = PlaceholderFeatureLayer("https://example.com")
    mock_fl_2 = PlaceholderFeatureLayer("https://example.com")
    mock_fl_1.renderer = renderer_1
    mock_fl_2.renderer = renderer_2
    assert isinstance(mock_fl_1, Layer)

    placeholder_flc = PlaceholderFeatureLayerCollection("https://example.com")
    placeholder_flc.layers = [
        mock_fl_1,
        mock_fl_2
    ]

    WebMap.add_layer(mock_webmap, placeholder_flc)
    assert len(mock_webmap._webmapdict['operationalLayers']) == 2
    assert mock_webmap._webmapdict['operationalLayers'][0].get('layerDefinition')\
        .get('drawingInfo').get('renderer') == renderer_1
    assert mock_webmap._webmapdict['operationalLayers'][1].get('layerDefinition')\
        .get('drawingInfo').get('renderer') == renderer_2

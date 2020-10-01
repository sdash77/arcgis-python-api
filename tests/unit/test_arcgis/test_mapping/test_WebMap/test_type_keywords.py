import pytest
from unittest.mock import patch

from utils.mocks import MockMapView, MockWebMap

@patch("arcgis.widgets.MapView", MockMapView)
def test_type_keyword_no_item():
    """Tests that WebMap._eval_map_viewer_keywords does not
    throw an exception when there is no internal `item` property
    (this is the case on creation of a new blank WebMap() inst)
    """
    from arcgis.mapping import WebMap

    mwm = MockWebMap()
    mwm.item = None

    actual = WebMap._eval_map_viewer_keywords(mwm)
    
@patch("arcgis.widgets.MapView", MockMapView)
def test_type_keyword_discard_offline():
    """Tests that WebMap._eval_map_viewer_keywords discards the
    offline keyword when no layers are present
    """
    from arcgis.mapping import WebMap

    mwm = MockWebMap()
    mwm.item.typeKeywords = ['Offline']
    mwm.layers = None

    assert 'Offline' not in WebMap._eval_map_viewer_keywords(mwm)
    
@patch("arcgis.widgets.MapView", MockMapView)
def test_type_keyword_discard_collector():
    """Tests that WebMap._eval_map_viewer_keywords discards the
    Collector keyword when no layers are present
    """
    from arcgis.mapping import WebMap

    mwm = MockWebMap()
    mwm.item.typeKeywords = ['Collector']
    mwm.layers = None

    assert 'Collector' not in WebMap._eval_map_viewer_keywords(mwm)
    

@patch("arcgis.widgets.MapView", MockMapView)
def test_type_keyword_offline_disabled():
    """Tests that WebMap._eval_map_viewer_keywords discards the
    offline keyword when OfflineDisabled is present
    """
    from arcgis.mapping import WebMap

    mwm = MockWebMap()
    mwm.item.typeKeywords = ['OfflineDisabled']

    assert 'Offline' not in WebMap._eval_map_viewer_keywords(mwm)
    
    
@patch("arcgis.widgets.MapView", MockMapView)
def test_type_keyword_collector_disabled():
    """Tests that WebMap._eval_map_viewer_keywords discards the
    Collector keyword when CollectorDisabled is present
    """
    from arcgis.mapping import WebMap

    mwm = MockWebMap()
    mwm.item.typeKeywords = ['CollectorDisabled']

    assert 'Collector' not in WebMap._eval_map_viewer_keywords(mwm)
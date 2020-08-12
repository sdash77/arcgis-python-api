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

    actual = WebMap._eval_map_viewer_keywords(mwm, {})
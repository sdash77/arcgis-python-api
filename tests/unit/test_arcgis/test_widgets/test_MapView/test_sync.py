from unittest.mock import patch, MagicMock

import pytest

from utils.mocks import MockMapView
from arcgis.widgets import MapView

@patch("ipywidgets.dlink")
def test_two_sync(mock_dlink):
    mock_mapview1 = MockMapView()
    mock_mapview2 = MockMapView()
    MapView._sync_navigation(mock_mapview1, mock_mapview2)

    # Assert that each mapview has the correct reference to each other
    assert mock_mapview1 in mock_mapview2._synced_mapviews
    assert mock_mapview1._uuid in mock_mapview2._mapview_uuid_to_dlinks

    assert mock_mapview2 in mock_mapview1._synced_mapviews
    assert mock_mapview2._uuid in mock_mapview1._mapview_uuid_to_dlinks

    # Assert that the correct dlinks are setup

    dlinks1 = mock_mapview1._mapview_uuid_to_dlinks[mock_mapview2._uuid]
    dlinks2 = mock_mapview2._mapview_uuid_to_dlinks[mock_mapview1._uuid]

    assert len(dlinks1) != 0 and len(dlinks1) == len(dlinks2)
    assert mock_dlink.call_count == 8

@patch("ipywidgets.dlink")
def test_two_unsync(mock_dlink):
    mock_mapview1 = MockMapView()
    mock_mapview2 = MockMapView()

    mock_mapview1._synced_mapviews.append(mock_mapview2)
    mock_mapview2._synced_mapviews.append(mock_mapview1)

    dl1 = MagicMock()
    dl2 = MagicMock()
    dl3 = MagicMock()
    dl4 = MagicMock()
    dl5 = MagicMock()
    dl6 = MagicMock()
    dl7 = MagicMock()
    dl8 = MagicMock()

    m1_dlinks = [dl1, dl2, dl3, dl4]
    m2_dlinks = [dl5, dl6, dl7, dl8]

    mock_mapview1._mapview_uuid_to_dlinks[mock_mapview2._uuid] = m1_dlinks
    mock_mapview2._mapview_uuid_to_dlinks[mock_mapview1._uuid] = m2_dlinks

    MapView._unsync_navigation(mock_mapview1, mock_mapview2)

    # Assert correct references are cleared
    assert {} == mock_mapview1._mapview_uuid_to_dlinks
    assert [] == mock_mapview1._synced_mapviews
    assert {} == mock_mapview2._mapview_uuid_to_dlinks
    assert [] == mock_mapview2._synced_mapviews

    for dlink in [dl1, dl2, dl3, dl4, dl5, dl6, dl7, dl8]:
        dlink.unlink.assert_called()

@patch("ipywidgets.dlink")
def test_three_sync_unsync(mock_dlink):
    mock_mapview1 = MockMapView()
    mock_mapview2 = MockMapView()
    mock_mapview3 = MockMapView()
    # Note: in the real `MapView.sync_navigation()` call, you only need to call
    # It twice, and it'll call the respective third link. For this test,
    # Do that manually and call it 3 times
    MapView._sync_navigation(mock_mapview1, mock_mapview2)
    MapView._sync_navigation(mock_mapview1, mock_mapview3)
    MapView._sync_navigation(mock_mapview2, mock_mapview3)

    # Assert that each mapview has the correct reference to each other
    assert mock_mapview2 in mock_mapview1._synced_mapviews
    assert mock_mapview3 in mock_mapview1._synced_mapviews
    assert mock_mapview2._uuid in mock_mapview1._mapview_uuid_to_dlinks
    assert mock_mapview3._uuid in mock_mapview1._mapview_uuid_to_dlinks

    assert mock_mapview1 in mock_mapview2._synced_mapviews
    assert mock_mapview3 in mock_mapview2._synced_mapviews
    assert mock_mapview1._uuid in mock_mapview2._mapview_uuid_to_dlinks
    assert mock_mapview3._uuid in mock_mapview2._mapview_uuid_to_dlinks

    assert mock_mapview2 in mock_mapview3._synced_mapviews
    assert mock_mapview1 in mock_mapview3._synced_mapviews
    assert mock_mapview2._uuid in mock_mapview3._mapview_uuid_to_dlinks
    assert mock_mapview1._uuid in mock_mapview3._mapview_uuid_to_dlinks

    assert mock_dlink.call_count == 24

    preunsync_dlink_len_mapview1 = len(mock_mapview1._mapview_uuid_to_dlinks)
    preunsync_dlink_len_mapview2 = len(mock_mapview2._mapview_uuid_to_dlinks)
    preunsync_dlink_len_mapview3 = len(mock_mapview3._mapview_uuid_to_dlinks)

    MapView._unsync_navigation(mock_mapview2, mock_mapview3)

    # Assert that only the correct dlinks were removed
    assert preunsync_dlink_len_mapview1 == len(mock_mapview1._mapview_uuid_to_dlinks) 
    assert preunsync_dlink_len_mapview2 > len(mock_mapview2._mapview_uuid_to_dlinks) 
    assert preunsync_dlink_len_mapview3 > len(mock_mapview3._mapview_uuid_to_dlinks) 

    assert mock_mapview2 not in mock_mapview3._synced_mapviews
    assert mock_mapview2._uuid not in mock_mapview3._mapview_uuid_to_dlinks

    assert mock_mapview3 not in mock_mapview2._synced_mapviews
    assert mock_mapview3._uuid not in mock_mapview2._mapview_uuid_to_dlinks

@patch("arcgis.widgets._mapview._mapview._is_iterable", lambda x: False)
def test_assert_correct_internal_methods_are_called():
    mock_mapview1 = MockMapView()
    mock_mapview1._isinstance.return_value = True
    mock_mapview2 = MockMapView()
    mock_mapview2._isinstance.return_value = True

    MapView.sync_navigation(mock_mapview1, mock_mapview2)
    mock_mapview1._sync_navigation.assert_called_with(mock_mapview2,
                                                      ignore_errors = False)

    MapView.unsync_navigation(mock_mapview1, mapview=mock_mapview2)
    mock_mapview1._unsync_navigation.assert_called_with(mock_mapview2,
                                                        ignore_errors = False)


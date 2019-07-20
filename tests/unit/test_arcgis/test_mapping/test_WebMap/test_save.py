from unittest.mock import patch

import pytest

from utils.mocks import MockWebMap
from arcgis.mapping import WebMap

gen_input_item_prop = {'title':'title', 'snippet':'snippet', 'tags':['tags']}
gen_full_item_prop = {**gen_input_item_prop,
                      **{'type': 'Web Map', 'extent': '', 'text': '{}'}}

def test_noarg_save():
    """Tests that WebMap.save throws an exception if a user doesn't pass in
    a dict with the 'title', 'snippet', 'tags' keys
    """
    mock_webmap = MockWebMap()
    with pytest.raises(RuntimeError) as e:
        WebMap.save(mock_webmap, {})
    assert "title" in str(e.value) and "required" in str(e.value)

def test_process_extent_called_correctly():
    """Tests that a WebMap.save() calls self._process_extent() and sets
    the result of that func in the `extent` field of the item_properties arg
    """
    mock_webmap = MockWebMap()
    validation_extent = {'arbitrary':'values'}
    mock_webmap._process_extent.return_value = validation_extent
    expected_item_prop = {**gen_full_item_prop,
                          **{'extent': validation_extent}}

    WebMap.save(mock_webmap, gen_input_item_prop)
    mock_webmap._gis.content.add.assert_called_with(expected_item_prop,
        folder=None, metadata=None, owner=None, thumbnail=None)

_mock_project_resp_1 = [
        {"x": "NaN",
         "y": "NaN" },
        {"x": 116.4447558099451,
         "y": 87.78601210184834}]

import arcgis.geometry
@patch("arcgis.geometry.project", return_value=_mock_project_resp_1)
def test_process_extent_non_4326_wkid_project_1(mock_project):
    _test_process_extent_non_4326_wkid_project("")

_mock_project_resp_2 = [
        {"x": "NaN",
         "y": "NaN" },
        {"x": "NaN",
         "y": "NaN"}]

@patch("arcgis.geometry.project", return_value=_mock_project_resp_2)
def test_process_extent_non_4326_wkid_project_2(mock_project):
    _test_process_extent_non_4326_wkid_project("")

_mock_project_resp_3 = [
        {"x": 116.4447558099451,
         "y": 87.78601210184834},
        {"x": 124.123,
         "y": 81.34}]

@patch("arcgis.geometry.project", return_value=_mock_project_resp_3)
def test_process_extent_non_4326_wkid_project_3(mock_project):
    _test_process_extent_non_4326_wkid_project(
        "116.4447558099451,87.78601210184834,124.123,81.34")

def _test_process_extent_non_4326_wkid_project(expected_value):
    """Tests a bug where an extent with a  non 4326 spatial reference will get
    converted to 4326 reference, but will display `NaN` in some fields. This 
    causes a failure in WebMap.save since WebMaps cannot have `NaN` field. 
    The Geometry Service of AGOL returns these NaNs, so mock out that response
    """
    mock_webmap = MockWebMap()
    mock_webmap._extent = {'xmin': 'notused', 'ymin': 'notused',
                           'xmax': 'notused', 'ymax': 'notused',
                           'spatialReference': {'latestWkid' : -9999 } }
    mock_webmap._contains_nans = \
        lambda result: WebMap._contains_nans(mock_webmap, result)
    resp = WebMap._process_extent(mock_webmap)
    assert resp == expected_value


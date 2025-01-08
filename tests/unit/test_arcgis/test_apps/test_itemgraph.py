import unittest
from unittest.mock import MagicMock, patch
import uuid
from arcgis.apps.itemgraph._get_dependencies import _parse_webmap, _parse_dashboard, _parse_exb, _parse_wma, _parse_storymap

class TestItemGraph(unittest.TestCase):
    def test_parse_webmap_item_ids(self):
        item_ids = ["abc", "def"]
        mock_item = get_mock_item({"operationalLayers": [{"itemId": item_id} for item_id in item_ids]})
        parsed_items = _parse_webmap(mock_item)
        assert all(item in item_ids for item in parsed_items)
        assert all(item in parsed_items for item in item_ids)
        mock_item.get_data.assert_called()
    
    @patch('arcgis.apps.itemgraph._get_dependencies.FeatureLayer')
    def test_parse_webmap_url(self, mock_feature_layer):
        feature_layer_url = "https://gis.enterprise.local/arcgis/rest/services/abc123/FeatureServer"
        feature_layer_item_id = "abc123"
        mock_feature_layer().properties = {"serviceItemId": feature_layer_item_id}
        mock_item = get_mock_item({"operationalLayers": [{"url": feature_layer_url}]})
        parsed_items = _parse_webmap(mock_item)
        mock_feature_layer.assert_called_with(feature_layer_url)
        assert feature_layer_item_id in parsed_items
        mock_item.get_data.assert_called()
    
    def test_parse_webmap_group_layer_item_ids(self):
        item_ids = ["abc", "def"]
        mock_item = get_mock_item({"operationalLayers": [{"layerType": "GroupLayer", "layers": [{"itemId": item_id} for item_id in item_ids]}]})
        parsed_items = _parse_webmap(mock_item)
        assert all(item in item_ids for item in parsed_items)
        assert all(item in parsed_items for item in item_ids)
        mock_item.get_data.assert_called()
    
    def test_parse_dashboard_extracts_map_widget_item_ids(self):
        item_ids = ["ghi", "jkl"]
        mock_item = get_mock_item({"widgets": [{"type": "mapWidget", "itemId": item_id} for item_id in item_ids]})
        parsed_items = _parse_dashboard(mock_item)
        assert all(item in item_ids for item in parsed_items)
        assert all(item in parsed_items for item in item_ids)
        mock_item.get_data.assert_called()
    
    def test_parse_dashboard_extracts_dataset_item_ids(self):
        item_ids = ["mno", "pqr"]
        mock_item = get_mock_item({
            "widgets": [
                {"datasets": [{"type": "serviceDataset", "dataSource": {"type": "itemDataSource", "itemId": item_id}} for item_id in item_ids]}
            ]
        })
        parsed_items = _parse_dashboard(mock_item)
        assert all(item in item_ids for item in parsed_items)
        assert all(item in parsed_items for item in item_ids)
        mock_item.get_data.assert_called()
    
    def test_parse_dashboard_extracts_arcade_item_ids(self):
        item_ids = ["c09a2b15cc914ddf8ca3584f93119230", "ef57c78326494a48ac6ded09601151fe"]
        mock_item = get_mock_item({
            "widgets": [
                {"datasets": [{"type": "serviceDataset", "dataSource": {"type": "arcadeDataSource", "script": {"i": [item_ids] + ["not_a_uuid"]}}}]}
            ]
        })
        parsed_items = _parse_dashboard(mock_item)
        assert all(item in item_ids for item in parsed_items)
        assert all(item in parsed_items for item in item_ids)
        mock_item.get_data.assert_called()
    
    def test_parse_exb_extracts_item_ids(self):
        pub_item_ids = ["abc", "def"]
        draft_item_ids = ["ghi", "jkl"]
        expected_item_ids = pub_item_ids + draft_item_ids
        item_data = {"dataSources": {item_id: {"itemId": item_id} for item_id in pub_item_ids}}
        item_draft_data = {"dataSources": {item_id: {"itemId": item_id} for item_id in draft_item_ids}}
        mock_item = get_mock_item(item_data,
                                  {'config/config.json': item_draft_data})
        parsed_items = _parse_exb(mock_item)
        assert all(item in expected_item_ids for item in parsed_items)
        assert all(item in parsed_items for item in expected_item_ids)
        mock_item.get_data.assert_called()

    def test_parse_wma_extracts_map_item_ids(self):
        item_id = "mno"
        item_data = {"map": {"itemId": item_id}}
        mock_item = get_mock_item(item_data)
        parsed_items = _parse_wma(mock_item)
        assert all(item in [item_id] for item in parsed_items)
        assert all(item in parsed_items for item in [item_id])
        mock_item.get_data.assert_called()
    
    def test_parse_wma_extracts_data_source_item_ids(self):
        item_ids = ["stu", "vwx", "eee"]
        item_data = {"dataSource": {"dataSources": {item_id: {"itemId": item_id} for item_id in item_ids}}}
        mock_item = get_mock_item(item_data)
        parsed_items = _parse_wma(mock_item)
        assert all(item in item_ids for item in parsed_items)
        assert all(item in parsed_items for item in item_ids)
        mock_item.get_data.assert_called()
    
    def test_parse_storymap_extracts_item_ids(self):
        item_ids = ["yza", "bcd"]
        theme_item_ids = ["efg", "hij"]
        draft_item_ids = ["nop"]
        draft_theme_item_ids = ["qrs"]
        expected_item_ids = item_ids + theme_item_ids + draft_item_ids + draft_theme_item_ids

        item_data = {"resources": {uuid.uuid4().hex: res for res in [{"type": "webmap", "data": {"itemId": item_id}} for item_id in item_ids] + [{"type": "story-theme", "data": {"themeItemId": item_id}} for item_id in theme_item_ids]}}
        draft_item_data = {"resources": {uuid.uuid4().hex: res for res in [{"type": "webmap", "data": {"itemId": item_id}} for item_id in draft_item_ids] + [{"type": "story-theme", "data": {"themeItemId": item_id}} for item_id in draft_theme_item_ids]}}
        
        mock_resources = MagicMock()
        mock_resources.list.return_value = [{"resource": "draft123"}]
        mock_resources.get.return_value = draft_item_data
        mock_item = get_mock_item(item_data, mock_resources)
        parsed_items = _parse_storymap(mock_item)
        # assert collections are equal
        assert all(item in expected_item_ids for item in parsed_items)
        assert all(item in parsed_items for item in expected_item_ids)
        mock_item.get_data.assert_called()

def get_mock_item(data, resources=None):
    item = MagicMock()
    item.get_data.return_value = data
    if resources:
        item.resources = resources
    return item

if __name__ == "__main__":
    unittest.main()
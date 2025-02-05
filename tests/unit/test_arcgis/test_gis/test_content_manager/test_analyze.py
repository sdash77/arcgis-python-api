import unittest
import uuid
from arcgis.gis import ContentManager

class TestAnalyze(unittest.TestCase):
    def test_analyze_params_agol_item(self):
        item_id = uuid.uuid4().hex
        analyze_params = ContentManager._get_analyze_params(is_arcgis_online=True, item=item_id)
        assert analyze_params['itemid'] == item_id
    
    def test_analyze_params_raises_value_error_geojson_enterprise(self):
        item_id = uuid.uuid4().hex
        with self.assertRaises(ValueError) as ex:
            ContentManager._get_analyze_params(is_arcgis_online=False, item=item_id, file_type='geojson')
        assert 'ArcGIS Enterprise' in str(ex.exception)
    
    def test_analyze_params_geojson_agol_succeeds(self):
        item_id = uuid.uuid4().hex
        analyze_params = ContentManager._get_analyze_params(is_arcgis_online=True, item=item_id, file_type='geojson')
        assert analyze_params['itemid'] == item_id
        assert analyze_params['fileType'] == 'geojson'

if __name__ == '__main__':
    unittest.main()
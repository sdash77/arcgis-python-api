from arcgis.layers._service_factory._layerfactory import ServiceFactory
from types import LambdaType
import unittest

class TestServiceFactory(unittest.TestCase):
    def test_layer_type_from_url_map_server_layer(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer/0'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'MapServiceLayer')
    
    def test_layer_type_from_url_map_server_no_layer(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'MapImageLayer')
    
    def test_layer_type_from_url_feature_server_layer(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/FeatureServer/0'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'FeatureServiceLayer')
    
    def test_layer_type_from_url_feature_server_no_layer(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/FeatureServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'FeatureLayerCollection')
    
    def test_layer_type_from_url_image_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Elevation/MtBaldy_Elevation/ImageServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'ImageryLayer')

    def test_layer_type_from_url_csv_file(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.csv'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'CSVLayer')
    
    def test_layer_type_from_url_data(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer/1/data'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'DataServiceLayer')
    
    def test_layer_type_from_url_gpserver(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/GPServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertIsInstance(_type, tuple)
        _type_hint, _func = _type
        self.assertEqual(_type_hint, 'GeoprocessingToolbox')
        self.assertIsInstance(_func, LambdaType)
    
    def test_layer_type_from_url_geometry_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Utilities/Geometry/GeometryServer'
        _type = ServiceFactory._layer_type_from_url(url)
        # handle GeometryService impl starting with an underscore
        self.assertIn('GeometryService', _type.__name__)
    
    def test_layer_type_from_url_geocode_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Locators/SanDiego/GeocodeServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertIn('Geocoder', _type.__name__)
    
    def test_layer_type_from_url_geodata_server(self):
        url = 'https://enterprise-arcgis.myorg.com/arcgis/rest/services/GeoData/GeoDataServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'GeoData')
    
    def test_layer_type_from_url_geojson_file(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'GeoJSONLayer')

    def test_layer_type_from_url_geojson_file_query_string(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson?query=1'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'GeoJSONLayer')

    def test_layer_type_from_url_globe_server(self):
        url = 'https://enterprise-arcgis.agency.gov/arcgis/rest/services/Globe/GlobeServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'Layer')
    
    def test_layer_type_from_url_kml_file(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.kml'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'KMLLayer')
    
    def test_layer_type_from_url_kmz_file(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.kmz'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'KMLLayer')

    def test_layer_type_from_url_mobile_server(self):
        url = 'https://enterprise-arcgis.agency.gov/arcgis/rest/services/Mobile/MobileServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'Layer')
    
    def test_layer_type_from_url_network_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/NetworkAnalysis/SanDiego/NAServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'NetworkDataset')
    
    def test_layer_type_from_url_ogc_feature_server(self):
        url = 'https://enterprise-arcgis.agency.gov/arcgis/rest/services/Map/OGCFeatureServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'OGCFeatureService')
    
    def test_layer_type_from_url_scene_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Scene/SceneServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'SceneLayer')
    
    def test_layer_type_from_url_schematic_server(self):
        url = '	https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer/exts/SchematicsServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'SchematicLayers')
    
    def test_layer_type_from_url_vector_tile_server(self):
        url = 'https://basemaps-api.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'VectorTileLayer')
    
    def test_layer_type_from_url_map_server_wmts(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'WMTSLayer')

    def test_layer_type_from_url_wmts_query_string(self):
        url = 'https://cite.deegree.org/deegree-webservices-3.5.0/services/wmts100?SERVICE=WMTS'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'WMTSLayer')

    def test_layer_type_from_url_falls_back_to_layer(self):
        url = 'https://enterprise-arcgis.myorg.com/abcdefghijklmnop'
        _type = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'Layer')
    
    def test_get_url_for_item_kml_returns_data_url(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/CommercialDamageAssessment/FeatureServer/0'
        updated_url = ServiceFactory._get_url_for_item(url, {'type': 'KML'})
        self.assertEqual(f"{url}/data", updated_url)
    
    def test_get_url_for_item_kml_returns_existing_data_url(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/CommercialDamageAssessment/FeatureServer/0/data'
        updated_url = ServiceFactory._get_url_for_item(url, {'type': 'KML Collection'})
        self.assertEqual(url, updated_url)

if __name__ == '__main__':
    unittest.main()

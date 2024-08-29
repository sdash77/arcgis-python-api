from arcgis.layers._service_factory._layerfactory import ServiceFactory
from types import LambdaType
import unittest

class TestServiceFactory(unittest.TestCase):
    def test_layer_type_from_url_map_server_layer(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer/0'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'MapServiceLayer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_map_server_no_layer(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'MapImageLayer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_feature_server_layer(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/FeatureServer/0'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'FeatureServiceLayer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_feature_server_no_layer(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/FeatureServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'FeatureLayerCollection')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_image_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Elevation/MtBaldy_Elevation/ImageServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'ImageryLayer')
        self.assertIsInstance(_, LambdaType)

    def test_layer_type_from_url_csv_file(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.csv'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'CSVLayer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_data(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer/1/data'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'DataServiceLayer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_gpserver(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/GPServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type, 'GeoprocessingToolbox')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_geometry_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Utilities/Geometry/GeometryServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertIn('GeometryService', _type.__name__)
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_geocode_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Locators/SanDiego/GeocodeServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertIn('Geocoder', _type.__name__)
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_geodata_server(self):
        url = 'https://enterprise-arcgis.myorg.com/arcgis/rest/services/GeoData/GeoDataServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'GeoData')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_geojson_file(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'GeoJSONLayer')
        self.assertIsInstance(_, LambdaType)

    def test_layer_type_from_url_geojson_file_query_string(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson?query=1'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'GeoJSONLayer')
        self.assertIsInstance(_, LambdaType)

    def test_layer_type_from_url_globe_server(self):
        url = 'https://enterprise-arcgis.agency.gov/arcgis/rest/services/Globe/GlobeServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'Layer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_kml_file(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.kml'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'KMLLayer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_kmz_file(self):
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.kmz'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'KMLLayer')
        self.assertIsInstance(_, LambdaType)

    def test_layer_type_from_url_mobile_server(self):
        url = 'https://enterprise-arcgis.agency.gov/arcgis/rest/services/Mobile/MobileServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'Layer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_network_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/NetworkAnalysis/SanDiego/NAServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'NetworkDataset')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_ogc_feature_server(self):
        url = 'https://enterprise-arcgis.agency.gov/arcgis/rest/services/Map/OGCFeatureServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'OGCFeatureService')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_scene_server(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Scene/SceneServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'SceneLayer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_schematic_server(self):
        url = '	https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer/exts/SchematicsServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'SchematicLayers')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_vector_tile_server(self):
        url = 'https://basemaps-api.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'VectorTileLayer')
        self.assertIsInstance(_, LambdaType)
    
    def test_layer_type_from_url_map_server_wmts(self):
        url = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/WorldTimeZones/MapServer/WMTS'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'WMTSLayer')
        self.assertIsInstance(_, LambdaType)

    def test_layer_type_from_url_wmts_query_string(self):
        url = 'https://cite.deegree.org/deegree-webservices-3.5.0/services/wmts100?SERVICE=WMTS'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'WMTSLayer')
        self.assertIsInstance(_, LambdaType)

    def test_layer_type_from_url_falls_back_to_layer(self):
        url = 'https://enterprise-arcgis.myorg.com/abcdefghijklmnop'
        _type, _ = ServiceFactory._layer_type_from_url(url)
        self.assertEqual(_type.__name__, 'Layer')
        self.assertIsInstance(_, LambdaType)

if __name__ == '__main__':
    unittest.main()

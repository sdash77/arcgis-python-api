import unittest
from arcgis.map import Scene
from arcgis.map.renderers import SimpleRenderer
from arcgis.map.symbols import PolygonSymbol3D, Material, SolidEdges
from arcgis.features import FeatureLayer
from arcgis.layers import (
    VectorTileLayer,
    MapServiceLayer,
    MapFeatureLayer,
    MapRasterLayer,
    CSVLayer,
    KMLLayer,
    WMSLayer,
    GeoJSONLayer,
)
from arcgis.raster import ImageryLayer
from arcgis.gis import GIS
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestAddLayersToMap(unittest.TestCase):

    def setUp(self):
        # create web scene
        self.wm = Scene(gis=self.gis)
        assert self.wm

        self.drawing_info = {
            "renderer": SimpleRenderer(
                symbol=PolygonSymbol3D(**{
                            "type": "PolygonSymbol3D",
                            "symbolLayers": [
                                {
                                    "type": "Extrude",
                                    "material": Material(color= [255, 0, 0, 0.5]),
                                    "size": 100,
                                    "edges": SolidEdges(color= [50, 50, 50, 0.5]),
                                }
                            ],
                        },)
            )
        }
    def test_feature_layer(self):
        """Test adding a feature layer"""
        # add layer
        layer = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        assert layer
        self.wm.content.add(
            layer,
            drawing_info=self.drawing_info,
        )
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], FeatureLayer)

    def test_add_by_url(self):
        """Test adding a layer by url"""

        # add layer
        url = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        self.wm.content.add(url)
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], MapFeatureLayer)
        
    def test_vector_tile_layer(self):
        """Test adding a vector tile layer"""
        # add layer
        layer = VectorTileLayer(
            "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer",
            gis=self.gis,
        )
        assert layer
        self.wm.content.add(
            layer,
            drawing_info=self.drawing_info,
        )
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], VectorTileLayer)

    def test_csv_layer(self):
        """Test adding a csv layer"""
        # add layer
        layer = CSVLayer(
            "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.csv"
        )
        assert layer
        self.wm.content.add(
            layer,
            drawing_info=self.drawing_info,
        )
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], CSVLayer)

    def test_kml_layer(self):
        """Test adding a kml layer"""
        # add layer
        layer = KMLLayer("http://quickmap.dot.ca.gov/data/lcs.kml")
        assert layer
        self.wm.content.add(layer)
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], KMLLayer)

    def test_wms_layer(self):
        """Test adding a wms layer"""
        # add layer
        layer = WMSLayer("http://ows.mundialis.de/services/service")
        assert layer
        self.wm.content.add(
            layer,
            drawing_info=self.drawing_info,
        )
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], WMSLayer)

    def test_map_service_layer(self):
        """Test adding a map service layer"""
        # add layer
        layer = MapServiceLayer(
            "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/geotagged_tiles/MapServer/0",
            self.gis,
            "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/geotagged_tiles/MapServer",
        )
        assert layer
        self.wm.content.add(
            layer,
            drawing_info=self.drawing_info,
        )
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], MapFeatureLayer)

    def test_geojson_layer(self):
        """Test adding a GeoJSON layer"""
        # add layer
        layer = GeoJSONLayer(
            "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
        )
        assert layer
        self.wm.content.add(
            layer,
            drawing_info=self.drawing_info,
        )
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], GeoJSONLayer)

    def test_map_raster_layer(self):
        layer = MapRasterLayer(
            "https://tiles.arcgis.com/tiles/ULBqC49IEeIR01GF/arcgis/rest/services/BH250-12_PPL/MapServer?cacheKey=82b29e822a144763",
            gis=self.gis,
        )
        assert layer

        self.wm.content.add(
            layer,
            drawing_info=self.drawing_info,
        )
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], MapRasterLayer)

    def test_imagery_layer(self):
        """Test adding an imagery layer"""
        layer = ImageryLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/CharlotteLAS/ImageServer",
            gis=self.gis,
        )
        assert layer

        self.wm.content.add(layer)
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], ImageryLayer)

    def test_add_layer_with_drawing_info(self):
        # add layer
        layer = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        assert layer
        renderer = {
            "renderer": {
                "authoringInfo": {"fadeRatio": 0.2},
                "type": "heatmap",
                "blurRadius": 5.555555555555556,
                "colorStops": [
                    {"color": [133, 193, 200, 0], "ratio": 0},
                    {"color": [133, 193, 200, 0], "ratio": 0.01},
                    {"color": [133, 193, 200, 3], "ratio": 0.01},
                    {"color": [133, 193, 200, 23], "ratio": 0.01},
                    {"color": [144, 161, 190, 212], "ratio": 0.0925},
                    {"color": [156, 129, 132, 255], "ratio": 0.17500000000000002},
                    {"color": [167, 97, 170, 255], "ratio": 0.2575},
                    {"color": [175, 73, 128, 255], "ratio": 0.34},
                    {"color": [184, 48, 85, 255], "ratio": 0.42250000000000004},
                    {"color": [192, 24, 42, 255], "ratio": 0.505},
                    {"color": [200, 0, 0, 255], "ratio": 0.5875},
                    {"color": [211, 51, 0, 255], "ratio": 0.67},
                    {"color": [222, 102, 0, 255], "ratio": 0.7525000000000001},
                    {"color": [233, 153, 0, 255], "ratio": 0.8350000000000001},
                    {"color": [244, 204, 0, 255], "ratio": 0.9175000000000001},
                    {"color": [255, 255, 0, 255], "ratio": 1},
                ],
                "maxDensity": 0.611069562632112,
                "maxPixelIntensity": 139.70497545315783,
                "minDensity": 0,
                "minPixelIntensity": 0,
                "radius": 10,
            }
        }
        self.wm.content.add(layer, drawing_info=renderer)
        assert self.wm.content.layers
        assert len(self.wm.content.layers) == 1
        assert isinstance(self.wm.content.layers[0], FeatureLayer)
        assert (
            self.wm._webscene.operational_layers[
                0
            ].layer_definition.drawing_info.dict()["renderer"]["type"]
            == "heatmap"
        )


if __name__ == "__main__":
    unittest.main()

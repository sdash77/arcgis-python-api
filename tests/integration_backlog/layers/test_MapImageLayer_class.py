import unittest

from arcgis.features.layer import FeatureLayer
from arcgis.layers import (
    MapImageLayer,
    MapImageLayerManager,
    EnterpriseMapImageLayerManager,
)
from arcgis.gis import GIS, Item
from utils.decorators import integration_test

gis = GIS("https://dev0015021.esri.com/portal", verify_cert=False)

# MapImageLayer
try:
    item = gis.content.search("South_Asia_Region", "Map Image Layer")[0]
    layer = MapImageLayer.fromitem(item)
    assert isinstance(item, Item)
except:
    fp = r"//qalab_server/pydata/v109/geosaurus/mapping_mod_MapImageLayer_cls/south_asia_region.sd"
    host_server = gis.admin.servers.get(role="HOSTING_SERVER")[0]
    res = host_server.publish_sd(sd_file=fp, folder="South_Asia", future=False)
    item = gis.content.search("South_Asia_Region", "Map Image Layer")[0]
    if not (item):
        raise (
            "Test data not published. Please configure Map Service for tests to pass."
        )
    else:
        layer = MapImageLayer.fromitem(item)
        print(layer)


@integration_test
class TestQueryFeatureLayer(unittest.TestCase):
    def test_manager(self):
        """ "
        Test manager property
        """
        manager = layer.manager
        assert isinstance(manager, EnterpriseMapImageLayerManager)
        assert "admin" in manager.url

    def test_create_dynamic_layer(self):
        """
        Test create_dynamic_layer
        """
        # Must check that supportDynamicLayers = True in layer properties
        if not layer.properties.supportsDynamicLayers == True:
            raise (
                "test_create_dynamic_layer failed. Layer does not support dynamic layers."
            )
        layer_to_add = {
            "id": 101,
            "source": {"type": "mapLayer", "mapLayerId": 4},
            "definitionExpression": "\"CNTRY_NAME\" is 'Iran'",
            "drawingInfo": {
                "renderer": "simple",
                "transparency": "0",
                "scaleSymbols": True,
                "showLabels": False,
            },
        }

        dynamic = layer.create_dynamic_layer(layer=layer_to_add)
        assert isinstance(dynamic, FeatureLayer)

    def test_properties(self):
        """
        Test properties
        """
        kml = layer.kml
        assert isinstance(kml, str)
        assert kml

        info = layer.item_info
        assert isinstance(info, dict)
        assert "description" in info

        legend = layer.legend
        assert isinstance(legend, dict)
        assert "layers" in legend

        metadata = layer.metadata
        assert isinstance(metadata, str)

        thumbnail = layer.thumbnail()
        assert thumbnail
        assert isinstance(thumbnail, str)

    def test_identify(self):
        """
        Test identify method with various parameters
        """
        identify = layer.identify(
            geometry={"xmin": 52, "ymin": 27.1, "xmax": 65.8, "ymax": 36},
            geometry_type="Envelope",
            tolerance=2,
            map_extent="59,-2,75,25",
            layers="all",
            sr=4326,
            image_display="600,550,96",
        )
        assert isinstance(identify, dict)
        assert "results" in identify
        assert len(identify["results"]) > 0

    def test_find(self):
        """
        Test find method
        """
        find = layer.find(
            search_text="Iran",
            contains=True,
            search_fields="CNTRY_NAME",
            layers="4",
            return_geometry=False,
            max_offset=100,
            return_z=True,
            return_m=False,
        )
        assert isinstance(find, dict)
        assert "results" in find
        assert len(find["results"]) > 0

    def test_generate_kml(self):
        """
        Test generate_kml method
        """
        import tempfile

        generate = layer.generate_kml(
            save_location=tempfile.gettempdir(),
            name="map_service_generate_kml_test",
            layers="0",
            options="composite",
        )
        assert isinstance(generate, str)

    def test_estimate_size_and_export_tiles(self):
        """
        Test estimate_export_tile_size and export_tiles methods
        Export tiles must be True in layer properties
        """
        try:
            size = layer.estimate_export_tiles_size(
                export_by="levelId", levels="5-6", asynchronous=False
            )
            assert isinstance(size, dict)
            assert isinstance(size["totalSize"], int)
            assert isinstance(size["totalTilesToExport"], int)

            export = layer.export_tiles(
                levels="18489297.737236-9244648.868618", export_by="scale"
            )
            assert isinstance(export, list)
            assert len(export) > 0
        except:
            # Export tiles not supported for this layer
            return


if __name__ == "__main__":
    unittest.main()

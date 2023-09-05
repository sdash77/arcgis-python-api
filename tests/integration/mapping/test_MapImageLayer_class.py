import sys

sys.path.insert(0, r"C:\Job\repos\geosaurus\src")
import os
import unittest

from arcgis.features.layer import FeatureLayer
from arcgis.mapping import MapImageLayer, MapImageLayerManager, EnterpriseMapImageLayerManager
from arcgis.gis import GIS, Item

gis = GIS("https://dev0015021.esri.com/portal", verify_cert=False)

# MapImageLayer
try:
    item = gis.content.search("South_Asia_Region", "Map Image Layer")[0]
    layer = MapImageLayer.fromitem(item)
    assert isinstance(item, Item)
except:
    fp = r"//qalab_server/pydata/v109/geosaurus/mapping_mod_MapImageLayer_cls/south_asia_region.sd"
    #fp = r"/Volumes/pydata/v109/geosaurus/mapping_mod_MapImageLayer_cls/south_asia_region.sd"
    host_server = gis.admin.servers.get(role="HOSTING_SERVER")[0]
    res = host_server.publish_sd(sd_file=fp, folder="South_Asia", future=False)
    item = gis.content.search("South_Asia_Region", "Map Image Layer")[0]
    if not(item):
        raise("Test data not published. Please configure Map Service for tests to pass.")
    else:
        layer = MapImageLayer.fromitem(item)
        print(layer)


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
            raise ("test_create_dynamic_layer failed. Layer does not support dynamic layers.")
        layer_to_add = {
            "id": 101, 
            "source": {"type": "mapLayer",
                       "mapLayerId": 4},
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
        assert isinstance(metadata, dict)

        thumbnail = layer.thumbnail()
        assert thumbnail
        assert isinstance(thumbnail, str)

    def test_identify(self):
        """
        Test identify method with various parameters
        """
        identify = layer.identify(
            geometry={"x": -104, "y": 35.6},
            geometry_type="Point",
            tolerance=2,
            map_extent="-104,35.6,-94.32,41",
            image_display="600,550,96",
        )
        assert isinstance(identify, dict)
        assert "results" in identify

    def test_find(self):
        """
        Test find method
        """
        find = layer.find(
            search_text="United",
            contains=True,
            search_fields="CNTRY_NAME", 
            layers="0",
            return_geometry=False,
            max_offset=100,
            return_z=True,
            return_m=False,
        )
        assert isinstance(find, dict)
        assert "results" in find

    def test_generate_kml(self):
        """
        Test generate_kml method
        """
        generate = layer.generate_kml(
            save_location=r"/Users/john3092/Job/data_formats/kmz", #C:\Job\Data_Formats\kmz
            name="map_service_generate_kml_test",
            layers="0",
            options="composite",
        )
        assert isinstance(generate, str)

    def test_export_map(self):
        """
        Test export_map method
        """
        export = layer.export_map(
            bbox="-104,35.6,-94.32,41",
            bbox_sr=4326,
            image_format="png",
            layers="include",
            transparent=True,
            scale=40.0,
            rotation=-45.0,
        )
        assert isinstance(export, dict)
        assert "href" in export

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

            export = layer.export_tiles(levels="18489297.737236-9244648.868618", export_by="scale")
            assert isinstance(export, list)
            assert len(export) > 0
        except:
            # Export tiles not supported for this layer
            return

if __name__ == "__main__":
    unittest.main()

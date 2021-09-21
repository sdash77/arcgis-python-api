import sys
import unittest

from numpy import isin

sys.path.insert(0, r"C:\\ipython_workfolder\\geosaurus_main\src")

from arcgis.features.layer import FeatureLayer
from arcgis.mapping import MapImageLayer, MapImageLayerManager
from arcgis.gis import GIS

gis = GIS(profile="your_online_profile")

# MapImageLayer
item = gis.content.get("977b559f957f4df8a56b28b4311afc36")
layer = MapImageLayer.fromitem(item)
print(layer)


class TestQueryFeatureLayer(unittest.TestCase):
    def test_manager(self):
        """"
        Test manager property
        """
        manager = layer.manager
        assert isinstance(manager, MapImageLayerManager)
        assert "admin" in manager.url

    def test_create_dynamic_layer(self):
        """
        Test create_dynamic_layer
        """
        # Must chech that supportDynamicLayers = True in layer properties
        layer_to_add = {
            "id": "0135e658729c4b55b76a3e556c70a325",
            "source": "https://sampleserver6.arcgisonline.com/arcgis/rest/services/USA/MapServer/2",
            "definitionExpression": "",
            "drawingInfo": {
                "renderer": "Simple Renderer",
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
            search_text="State",
            contains=True,
            layers="top",
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
            save_location=r"C:\\ipython_workfolder",
            name="Map Service Test",
            layers="0,1,3",
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

    def test_export_tiles(self):
        """
        Test estimate_export_tile_size and export_tiles methods
        Export tiles must be True in layer properties
        """
        size = layer.estimate_export_tiles_size(
            export_by="LevelID", levels="0-5", asynchronous=False
        )
        assert isinstance(size, str)

        export = layer.export_tiles(levels="0-5", export_by="LevelID")
        assert isinstance(export, str)


if __name__ == "__main__":
    unittest.main()

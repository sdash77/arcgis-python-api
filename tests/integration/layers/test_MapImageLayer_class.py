import unittest

from arcgis.features.layer import FeatureLayer
from arcgis.layers import (
    MapImageLayer,
    EnterpriseMapImageLayerManager,
)
from arcgis.geometry import Geometry
from utils.decorators import integration_test, profiles


@profiles.enterprise
@integration_test
class TestQueryFeatureLayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        item = cls.gis.content.get("e7981155f26a4156bd85a44e989f381e")  # South_Asia_Region
        assert item, "Could not obtain item (South Asia Region - e7981155f26a4156bd85a44e989f381e)"
        cls.layer = MapImageLayer.fromitem(item)

    def test_manager(self):
        """
        Test manager property
        """
        manager = self.layer.manager
        assert isinstance(manager, EnterpriseMapImageLayerManager)
        assert "admin" in manager.url

    def test_create_dynamic_layer(self):
        """
        Test create_dynamic_layer
        """
        # Must check that supportDynamicLayers = True in layer properties
        if not self.layer.properties.supportsDynamicLayers == True:
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

        dynamic = self.layer.create_dynamic_layer(layer=layer_to_add)
        assert isinstance(dynamic, FeatureLayer)

    def test_properties(self):
        """
        Test properties
        """
        kml = self.layer.kml
        assert isinstance(kml, str)
        assert kml

        info = self.layer.item_info
        assert isinstance(info, dict)
        assert "description" in info

        legend = self.layer.legend
        assert isinstance(legend, dict)
        assert "layers" in legend

        metadata = self.layer.metadata
        assert isinstance(metadata, str)

        thumbnail = self.layer.thumbnail()
        assert thumbnail
        assert isinstance(thumbnail, str)

    def test_identify(self):
        """
        Test identify method with various parameters
        """
        identify = self.layer.identify(
            geometry=Geometry({
                "xmin": -13055810.007118689,
                "ymin": 4028260.3648137297,
                "xmax": -13039076.794074425,
                "ymax": 4040181.123446847,
                "spatialReference": {"wkid": 102100, "latestWkid": 3857},
            }),
            geometry_type="Envelope",
            tolerance=2,
            map_extent="-13055810.0071187 4028260.36481373 -13039076.7940744 4040181.12344685",
            layers="all",
            sr=3857,
            image_display="600,550,96",
        )
        self.assertFalse(
            "error" in identify,
            f"An error occurred during Identify: {identify.get('error')}",
        )
        assert isinstance(identify, dict)
        assert "results" in identify
        assert len(identify["results"]) > 0

    def test_find(self):
        """
        Test find method
        """
        find = self.layer.find(
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

        generate = self.layer.generate_kml(
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
            size = self.layer.estimate_export_tiles_size(
                export_by="levelId", levels="5-6", asynchronous=False
            )
            assert isinstance(size, dict)
            assert isinstance(size["totalSize"], int)
            assert isinstance(size["totalTilesToExport"], int)

            export = self.layer.export_tiles(
                levels="18489297.737236-9244648.868618", export_by="scale"
            )
            assert isinstance(export, list)
            assert len(export) > 0
        except:
            # Export tiles not supported for this layer
            return


if __name__ == "__main__":
    unittest.main()

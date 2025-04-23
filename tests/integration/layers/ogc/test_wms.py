import unittest
from arcgis.layers._ogc import WMSLayer
from utils.decorators import integration_test

wm_url = "https://hydro.nationalmap.gov/arcgis/services/nhd/MapServer/WMSServer?request=GetCapabilities&service=WMS"


@integration_test
class TestWMSLayer(unittest.TestCase):
    """Tests working with a WMS Layer"""

    def test_wms(self):
        """tests the WMS Layer methods and properties"""
        wms = WMSLayer(url=wm_url)
        assert isinstance(wms, WMSLayer)
        assert wms.opacity == 1
        wms.opacity = 0.5
        assert wms.opacity == 0.5
        assert isinstance(wms.scale, tuple)
        wms.scale = (1, 2)
        assert wms.scale == (1, 2)
        assert isinstance(wms.title, str)
        self.assertEqual(
            "WMS Layer", wms.title, f"Unexpected service title. Got {wms.title}"
        )
        wms.title = "test"
        assert wms.title == "test"
        layers = wms.layers
        self.assertEqual(
            13,
            len(layers),
            f"Unexpected quantity of layers in service. Got {len(layers)}",
        )
        layer_1_title = layers[0].get("Title")
        self.assertEqual(
            "Waterbody - Large Scale",
            layer_1_title,
            f"Unexpected layer title. Got: {layer_1_title}",
        )
        assert wms._lyr_json
        assert wms.properties


if __name__ == "__main__":
    unittest.main()

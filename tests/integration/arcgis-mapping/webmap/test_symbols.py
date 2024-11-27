from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from arcgis.map import Map
from arcgis.map.symbols import (
    PictureFillSymbolEsriPFS,
    PictureMarkerSymbolEsriPMS,
    SimpleFillSymbolEsriSFS,
    SimpleLineSymbolEsriSLS,
    SimpleMarkerSymbolEsriSMS,
    TextSymbolEsriTS,
    SimpleLineSymbolStyle,
    SimpleFillSymbolStyle,
    SimpleMarkerSymbolStyle,
)
from arcgis.map.renderers import SimpleRenderer
import unittest
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestSymbols(unittest.TestCase):
    """Test the symbols module"""

    def test_create_picture_fill_symbol(self):
        """Test the create_picture_fill_symbol function"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        symbol = PictureFillSymbolEsriPFS(
            url="https://static.arcgis.com/images/Symbols/Shapes/BluePin1LargeB.png",
            width=20,
            height=20,
        )

        assert symbol
        assert symbol.type == "esriPFS"

        renderer = SimpleRenderer(symbol=symbol)

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriPFS"
        )

    def test_create_picture_marker_symbol(self):
        """Test the create_picture_marker_symbol function"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        symbol = PictureMarkerSymbolEsriPMS(
            url="https://static.arcgis.com/images/Symbols/Shapes/BluePin1LargeB.png",
            width=20,
            height=20,
        )

        assert symbol
        assert symbol.type == "esriPMS"

        renderer = SimpleRenderer(symbol=symbol)

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriPMS"
        )

    def test_create_simple_fill_symbol(self):
        """Test the create_simple_fill_symbol function"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        outline = SimpleLineSymbolEsriSLS(
            color=[0, 0, 0, 255],
            style=SimpleLineSymbolStyle.esri_sls_solid,
            width=1,
        )
        symbol = SimpleFillSymbolEsriSFS(
            color=[255, 0, 0, 255],
            style=SimpleFillSymbolStyle.esri_sfs_solid,
            outline=outline,
        )

        assert symbol
        assert symbol.type == "esriSFS"

        renderer = SimpleRenderer(symbol=symbol)

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriSFS"
        )

    def test_create_simple_line_symbol(self):
        """Test the create_simple_line_symbol function"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        symbol = SimpleLineSymbolEsriSLS(
            color=[255, 0, 0, 255],
            style=SimpleLineSymbolStyle.esri_sls_solid,
            width=1,
        )

        assert symbol
        assert symbol.type == "esriSLS"

        renderer = SimpleRenderer(symbol=symbol)

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriSLS"
        )

    def test_create_simple_marker_symbol(self):
        """Test the create_simple_marker_symbol function"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        outline = SimpleLineSymbolEsriSLS(
            color=[0, 0, 0, 255],
            style=SimpleLineSymbolStyle.esri_sls_solid,
            width=1,
        )

        symbol = SimpleMarkerSymbolEsriSMS(
            color=[255, 0, 0, 255],
            style=SimpleMarkerSymbolStyle.esri_sms_circle,
            size=10,
            outline=outline,
        )

        assert symbol
        assert symbol.type == "esriSMS"

        renderer = SimpleRenderer(symbol=symbol)

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriSMS"
        )

    def test_create_text_symbol(self):
        """Test create_text_symbol function"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        font = {
            "family": "Arial",
            "size": 12,
            "style": "normal",
            "weight": "bold",
        }
        symbol = TextSymbolEsriTS(
            color=[255, 0, 0, 255],
            font=font,
            horizontal_alignment="center",
            vertical_alignment="middle",
            text="Test",
        )

        assert symbol
        assert symbol.type == "esriTS"

        renderer = SimpleRenderer(symbol=symbol)

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriTS"
        )


if __name__ == "__main__":
    unittest.main()

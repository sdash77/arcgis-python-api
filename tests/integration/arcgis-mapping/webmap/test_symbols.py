from arcgis.layers import Service
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
    TextFont
)
from arcgis.map.renderers import SimpleRenderer
import unittest
from utils.decorators import integration_test, profiles


@profiles.all
@integration_test
class TestSymbols(unittest.TestCase):
    """Test the symbols module"""

    def test_create_picture_fill_symbol(self):
        """Test the create_picture_fill_symbol function"""
        fl = Service("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities_/FeatureServer/0")
        assert isinstance(fl, FeatureLayer)

        # create symbol
        symbol = PictureFillSymbolEsriPFS(
            url="https://static.arcgis.com/images/Symbols/Shapes/BluePin1LargeB.png",
            width=20,
            height=20,
        )

        assert isinstance(symbol, PictureFillSymbolEsriPFS)
        assert symbol.type == "esriPFS"
        assert symbol.url == "https://static.arcgis.com/images/Symbols/Shapes/BluePin1LargeB.png"
        assert symbol.width == 20

        # render symbol on map
        renderer = SimpleRenderer(symbol=symbol)
        m = Map(gis=self.gis)
        assert isinstance(m, Map)

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers[0].properties == fl.properties
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriPFS"
        )

    def test_create_picture_marker_symbol(self):
        """Test the create_picture_marker_symbol function"""
        fl = Service("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities_/FeatureServer/0")
        assert isinstance(fl, FeatureLayer)

        # create symbol
        symbol = PictureMarkerSymbolEsriPMS(
            url="https://static.arcgis.com/images/Symbols/Shapes/BluePin1LargeB.png",
            width=20,
            height=20,
        )

        assert isinstance(symbol, PictureMarkerSymbolEsriPMS)
        assert symbol.type == "esriPMS"
        assert symbol.url == "https://static.arcgis.com/images/Symbols/Shapes/BluePin1LargeB.png"
        assert symbol.width == 20

        # render symbol on map
        renderer = SimpleRenderer(symbol=symbol)
        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers[0].properties == fl.properties
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriPMS"
        )

    def test_create_simple_fill_symbol(self):
        """Test the create_simple_fill_symbol function"""
        fl = Service("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities_/FeatureServer/0")
        assert fl

        # create symbols
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

        assert isinstance(outline, SimpleLineSymbolEsriSLS)
        assert isinstance(symbol, SimpleFillSymbolEsriSFS)
        assert outline.style == 'esriSLSSolid'
        assert symbol.style == 'esriSFSSolid'
        assert outline.width == 1
        assert symbol.outline == outline

        # render symbol on map
        renderer = SimpleRenderer(symbol=symbol)
        m = Map(gis=self.gis)
        assert isinstance(m, Map)

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers[0].properties == fl.properties
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriSFS"
        )

    def test_create_simple_line_symbol(self):
        """Test the create_simple_line_symbol function"""
        fl = Service("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities_/FeatureServer/0")
        assert isinstance(fl, FeatureLayer)

        symbol = SimpleLineSymbolEsriSLS(
            color=[255, 0, 0, 255],
            style=SimpleLineSymbolStyle.esri_sls_solid,
            width=1,
        )

        assert isinstance(symbol, SimpleLineSymbolEsriSLS)
        assert symbol.type == "esriSLS"
        assert symbol.style == "esriSLSSolid"
        assert symbol.width == 1

        # render symbol on map
        renderer = SimpleRenderer(symbol=symbol)
        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers[0].properties == fl.properties
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriSLS"
        )

    def test_create_simple_marker_symbol(self):
        """Test the create_simple_marker_symbol function"""
        fl = Service("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities_/FeatureServer/0")
        assert isinstance(fl, FeatureLayer)

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

        assert isinstance(outline, SimpleLineSymbolEsriSLS)
        assert isinstance(symbol, SimpleMarkerSymbolEsriSMS)
        assert outline.style == "esriSLSSolid"
        assert symbol.style == "esriSMSCircle"
        assert outline.type == "esriSLS"
        assert symbol.type == "esriSMS"
        assert outline.width == 1
        assert symbol.size == 10
        assert symbol.outline == outline

        # render symbol on map
        renderer = SimpleRenderer(symbol=symbol)
        m = Map(gis=self.gis)
        assert isinstance(m, Map)

        m.content.add(fl, drawing_info={"renderer": renderer})

        assert m.content.layers[0].properties == fl.properties
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["symbol"]["type"]
            == "esriSMS"
        )

    def test_create_text_symbol(self):
        """Test create_text_symbol function"""
        fl = Service("https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities_/FeatureServer/0")
        assert isinstance(fl, FeatureLayer)

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

        assert isinstance(symbol, TextSymbolEsriTS)
        assert symbol.type == "esriTS"
        assert isinstance(symbol.font, TextFont)
        assert symbol.font.style == "normal"
        assert symbol.horizontal_alignment == "center"

        # render symbol on map
        renderer = SimpleRenderer(symbol=symbol)
        m = Map(gis=self.gis)
        assert isinstance(m, Map)

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

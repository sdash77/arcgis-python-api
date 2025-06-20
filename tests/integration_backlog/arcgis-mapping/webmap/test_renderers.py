from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from arcgis.map import Map
from arcgis.map.renderers import (
    HeatmapRenderer,
    UniqueValueRenderer,
    ClassBreaksRenderer,
    SimpleRenderer,
    DotDensityRenderer,
    AuthoringInfoVisualVariable,
    VisualVariableType,
    LegendOptions,
)
import unittest
import os
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestRenderers(unittest.TestCase):
    """Test the renderers module"""

    def test_create_heatmap(self):
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        renderer = HeatmapRenderer(
            radius=10,
            color_stops=[
                {"ratio": 0, "color": [255, 0, 0, 1]},
                {"ratio": 0.5, "color": [0, 255, 0, 1]},
                {"ratio": 1, "color": [0, 0, 255, 1]},
            ],
        )
        assert renderer
        assert renderer.type == "heatmap"

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})
        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["type"]
            == "heatmap"
        )

    def test_create_unique_value(self):
        """Test generating a unique value renderer"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        renderer = UniqueValueRenderer(
            field1="STATE_NAME",
            unique_value_infos=[
                {
                    "value": "Value1",
                    "symbol": {
                        "type": "esriSMS",
                        "style": "esriSMSCircle",
                        "color": [255, 0, 0, 255],  # Red color (RGB)
                        "size": 6,  # Symbol size
                    },
                },
                {
                    "value": "Value2",
                    "symbol": {
                        "type": "esriSMS",
                        "style": "esriSMSSquare",
                        "color": [0, 255, 0, 255],  # Green color (RGB)
                        "size": 6,  # Symbol size
                    },
                },
                {
                    "value": "Value3",
                    "symbol": {
                        "type": "esriSMS",
                        "style": "esriSMSDiamond",
                        "color": [0, 0, 255, 255],  # Blue color (RGB)
                        "size": 6,  # Symbol size
                    },
                },
                # Add more unique values and symbols as needed
            ],
        )
        assert renderer
        assert renderer.type == "uniqueValue"

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})
        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["type"]
            == "uniqueValue"
        )

    def test_create_classbreaks(self):
        """Test generating a class breaks renderer"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        renderer = ClassBreaksRenderer(
            field="POP2000",
            classification_method="esriClassifyQuantile",
            min_value=0,
            class_break_infos=[
                {
                    "classMinValue": 0,
                    "classMaxValue": 10000,
                    "symbol": {
                        "type": "esriSMS",
                        "style": "esriSMSCircle",
                        "color": [255, 0, 0, 255],  # Red color (RGB)
                        "size": 6,  # Symbol size
                    },
                },
                {
                    "classMinValue": 10001,
                    "classMaxValue": 50000,
                    "symbol": {
                        "type": "esriSMS",
                        "style": "esriSMSSquare",
                        "color": [0, 255, 0, 255],  # Green color (RGB)
                        "size": 6,  # Symbol size
                    },
                },
                {
                    "classMinValue": 50001,
                    "classMaxValue": 100000,
                    "symbol": {
                        "type": "esriSMS",
                        "style": "esriSMSDiamond",
                        "color": [0, 0, 255, 255],  # Blue color (RGB)
                        "size": 6,  # Symbol size
                    },
                },
                # Add more class breaks and symbols as needed
            ],
        )
        assert renderer
        assert renderer.type == "classBreaks"

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})
        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["type"]
            == "classBreaks"
        )

    def test_create_simple(self):
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        renderer = SimpleRenderer(
            symbol={
                "type": "esriSMS",
                "style": "esriSMSCircle",
                "color": [255, 0, 0, 255],  # Red color (RGB)
                "size": 6,  # Symbol size
            }
        )
        assert renderer
        assert renderer.type == "simple"

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer.dict()})
        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["type"]
            == "simple"
        )

    def create_dot_density(self):
        """Test generate dot denisty renderer"""
        fl = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3",
            gis=self.gis,
        )
        assert fl

        renderer = DotDensityRenderer(
            attributes=["POP2000", "POP2007"],
            dot_value=100,
            outline={
                "type": "esriSLS",
                "style": "esriSLSSolid",
                "color": [0, 0, 0, 255],
                "width": 0.5,
            },
            background_color=[255, 255, 255, 255],
            dot_color=[0, 0, 255, 255],
            reference_scale=1000000,
        )
        assert renderer
        assert renderer.type == "dotDensity"

        m = Map(gis=self.gis)
        assert m

        m.content.add(fl, drawing_info={"renderer": renderer})
        assert m.content.layers
        assert len(m.content.layers) == 1
        assert (
            m._webmap.operational_layers[0].layer_definition.drawing_info.dict()[
                "renderer"
            ]["type"]
            == "dotDensity"
        )

    def test_create_visual_variables(self):
        """Test generate visual variables"""
        color_vv = AuthoringInfoVisualVariable(
            field="POP2000",
            normalization_field="SQMI",
            stops=[
                {
                    "value": 0,
                    "color": [255, 255, 255, 255],
                    "label": "< 0",
                },
                {
                    "value": 1000,
                    "color": [255, 0, 0, 255],
                    "label": "1000",
                },
                {
                    "value": 10000,
                    "color": [0, 255, 0, 255],
                    "label": "10000",
                },
                {
                    "value": 100000,
                    "color": [0, 0, 255, 255],
                    "label": "> 100000",
                },
            ],
            type=VisualVariableType.color_info.value,
        )

        assert color_vv
        assert color_vv.type == "colorInfo"

        size_vv = AuthoringInfoVisualVariable(
            field="POP2000",
            max_data_value=100000,
            min_data_value=0,
            stops=[
                {"value": 0, "size": 4},
                {"value": 1000, "size": 8},
                {
                    "value": 10000,
                    "size": 12,
                },
                {
                    "value": 100000,
                    "size": 16,
                },
            ],
            type=VisualVariableType.size_info.value,
        )
        assert size_vv
        assert size_vv.type == "sizeInfo"

        transparency_vv = AuthoringInfoVisualVariable(
            field="POP2000",
            normalization_field="SQMI",
            stops=[
                {
                    "value": 0,
                    "transparency": 0,
                    "label": "< 0",
                },
                {
                    "value": 1000,
                    "transparency": 50,
                    "label": "1000",
                },
                {
                    "value": 10000,
                    "transparency": 75,
                    "label": "10000",
                },
                {
                    "value": 100000,
                    "transparency": 100,
                    "label": "> 100000",
                },
            ],
            type=VisualVariableType.transparency_info.value,
        )
        assert transparency_vv
        assert transparency_vv.type == "transparencyInfo"

    def test_legend_options(self):
        """Test creating legend options"""
        legend_options = LegendOptions(
            title="Test Legend",
            show_legend=True,
            max_label="100000",
            min_label="0",
        )

        heatmap = HeatmapRenderer(
            radius=10,
            color_stops=[
                {"ratio": 0, "color": [255, 0, 0, 1]},
                {"ratio": 0.5, "color": [0, 255, 0, 1]},
                {"ratio": 1, "color": [0, 0, 255, 1]},
            ],
            legend_options=legend_options,
        )

        assert heatmap

    def test_to_template(self):
        """Test creating a template from a renderer"""
        item = self.gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        flayer = item.layers[0]
        df = flayer.query(where="AGE_45_54 < 1500").sdf

        m = Map()

        cbr = ClassBreaksRenderer(
            **{
                "authoringInfo": {
                    "classificationMethod": "esriClassifyEqualInterval",
                    "fadeRatio": 0.0,
                    "type": "classedSize",
                },
                "classBreakInfos": [
                    {
                        "classMaxValue": 5250,
                        "label": "500 - 5,250",
                        "symbol": {
                            "angle": 0.0,
                            "color": [245, 66, 179, 255],
                            "outline": {
                                "color": [255, 255, 255, 64],
                                "style": "esriSLSSolid",
                                "type": "esriSLS",
                                "width": 0.75,
                            },
                            "size": 3,
                            "style": "esriSMSCircle",
                            "type": "esriSMS",
                            "xoffset": 0,
                            "yoffset": 0,
                        },
                    },
                    {
                        "classMaxValue": 10000,
                        "label": "> 5,250 - 10,000",
                        "symbol": {
                            "angle": 0.0,
                            "color": [39, 179, 148, 255],
                            "outline": {
                                "color": [255, 255, 255, 64],
                                "style": "esriSLSSolid",
                                "type": "esriSLS",
                                "width": 0.75,
                            },
                            "size": 16.5,
                            "style": "esriSMSCircle",
                            "type": "esriSMS",
                            "xoffset": 0,
                            "yoffset": 0,
                        },
                    },
                ],
                "defaultLabel": "Other",
                "defaultSymbol": {
                    "angle": 0.0,
                    "color": [128, 128, 128, 255],
                    "outline": {
                        "color": [255, 255, 255, 64],
                        "style": "esriSLSSolid",
                        "type": "esriSLS",
                        "width": 0.75,
                    },
                    "size": 3,
                    "style": "esriSMSCircle",
                    "type": "esriSMS",
                    "xoffset": 0,
                    "yoffset": 0,
                },
                "field": "FAMILIES",
                "minValue": 500,
                "type": "classBreaks",
            }
        )
        m.content.add(df, drawing_info={"renderer": cbr})

        assert m.save(
            {
                "title": "Test Map",
                "tags": "test, map",
                "snippet": "Testing adding a renderer to map resources",
            }
        )

        renderer_manager = m.content.renderer(0)
        assert renderer_manager

        template = renderer_manager.to_template()
        assert template

        # look in map item resources
        resource_manager = m.item.resources
        assert resource_manager

        all_resources = resource_manager.list()

        try:
            for resource in all_resources:
                if resource["resource"] == template:
                    return True
            else:
                raise Exception("Template not found")
        except Exception as e:
            print(e)
        finally:
            assert m.item.delete()

    def test_from_template(self):
        """Test getting a renderer from a template"""
        # Get the current script's directory
        script_dir = os.path.dirname(os.path.realpath(__file__))

        # Construct the path to the renderer.json file in the data folder
        renderer_path = os.path.join(script_dir, "data", "renderers.json")

        item = self.gis.content.get("85d0ca4ea1ca4b9abf0c51b9bd34de2e")
        flayer = item.layers[0]
        df = flayer.query(where="AGE_45_54 < 1500").sdf

        m = Map()

        m.content.add(df)

        renderer_manager = m.content.renderer(0)
        assert renderer_manager

        # Read the renderer from the file
        updated = renderer_manager.from_template(renderer_path)
        assert updated
        assert updated.type == "classBreaks"


if __name__ == "__main__":
    unittest.main()

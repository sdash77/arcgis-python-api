import unittest
from arcgis.map import Map
from arcgis.features import FeatureLayer
from arcgis.gis import GIS
from arcgis.map.popups import (
    PopupElementText,
    PopupElementAttachments,
    PopupElementFields,
    PopupElementMedia,
    PopupElementRelationship,
    PopupElementExpression,
    PopupExpressionInfo,
    MediaInfo,
    MediaType,
    Value,
    FieldInfo,
)
from utils.decorators import integration_test, profiles


@profiles.agol
@integration_test
class TestAddLayersToMap(unittest.TestCase):
    def test_feature_layer(self):
        """Test adding a feature layer"""

        # create webmap
        wm = Map(gis=self.gis)
        assert wm

        # add layer
        layer = FeatureLayer(
            "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3"
        )
        assert layer
        wm.content.add(layer)
        assert wm.content.layers
        assert len(wm.content.layers) == 1
        assert isinstance(wm.content.layers[0], FeatureLayer)

        # popup class
        popup = wm.content.popup(0)
        assert popup

        # edit the popup
        popup.edit(
            title="TestPopup",
            description="TestingEditingAPopup",
            popup_elements=[PopupElementText(text="TestText")],
        )

        assert popup.info

    def test_popup_element_attachments(self):
        """Test create_popup_element_attachments"""
        popup = PopupElementAttachments(
            description="TestDescription",
            type="attachments",
        )
        assert popup

    def test_popup_element_expression(self):
        """Test create_popup_element_expression"""
        popup = PopupElementExpression(
            expression_info=PopupExpressionInfo(
                title="TestPopup",
                expression="TestText",
            ),
            type="expression",
        )
        assert popup

    def test_popup_element_fields(self):
        """Test create_popup_element_fields"""
        popup = PopupElementFields(
            fieldInfos=[
                FieldInfo(
                    fieldName="TestFieldName",
                    label="TestLabel",
                    visible=True,
                    format={"places": 2, "digitSeparator": True},
                )
            ],
            type="fields",
        )
        assert popup

    def test_popup_element_media(self):
        """Test create_popup_element_media"""
        popup = PopupElementMedia(
            description="TestDescription",
            mediaInfos=[
                MediaInfo(
                    caption="TestCaption",
                    title="TestTitle",
                    type=MediaType.image.value,
                    value=Value(sourceURL="www.test.com", linkURL="TestLinkURL"),
                )
            ],
        )
        assert popup

    def test_popup_element_relationship(self):
        """Test create_popup_element_relationship"""
        popup = PopupElementRelationship(
            description="TestDescription",
            display_count=4,
            display_type="list",
            relationship_id=0,
            type="relationship",
        )
        assert popup

    def test_popup_element_text(self):
        """Test create_popup_element_text"""
        popup = PopupElementText(
            text="TestText",
            type="text",
        )
        assert popup


if __name__ == "__main__":
    unittest.main()

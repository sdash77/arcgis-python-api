import sys
import os
import json
import tempfile

from arcgis.gis import GIS

#######################################################################
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

enable_verbose_logging()

_schema: dict = {
    "name": "cmu-classification-schema",
    "version": "2.0",
    "grammarVersion": "2.0",
    "attributeCategories": [],
    "classificationMetadata": {
        "primaryAttribute": "classification",
        "defaultValue": "Public",
        "classificationValueProperties": [
            {
                "value": "Public",
                "acronym": "Pub",
                "backgroundColor": "rgb(31 120 50)",
                "textColor": "Black",
            },
            {
                "value": "Private",
                "acronym": "Pvt",
                "backgroundColor": "#FF5733",
                "textColor": "White",
            },
            {
                "value": "Restricted",
                "acronym": "Res",
                "backgroundColor": "Red",
                "textColor": "White",
            },
            {
                "value": "Restricted-Specific",
                "acronym": "Restricted-Specific",
                "backgroundColor": "Red",
                "textColor": "White",
            },
        ],
    },
    "bannerExpression": "",
    "selectionTextExpression": "",
    "attributes": {
        "classification": {
            "label": "Classification",
            "description": "Classification",
            "type": "string",
            "uiElement": "single-select",
            "validValues": [
                {"label": "Public", "value": "Public"},
                {"label": "Private", "value": "Private"},
                {"label": "Restricted", "value": "Restricted"},
                {
                    "label": "Restricted-Specific",
                    "value": "Restricted-Specific",
                },
            ],
            "selectionDisplayOrder": 1,
            "bannerOrder": 1,
            "labelDelimiter": "",
            "valueDelimiter": "-",
            "attributeDelimiter": ";",
        },
        "field1": {
            "label": "Field 1",
            "description": "Field 1",
            "type": "string",
            "uiElement": "text",
            "selectionDisplayOrder": 2,
            "selectionDisplayLabel": "Field 1",
            "bannerOrder": 2,
            "bannerLabel": "Field 1",
            "labelDelimiter": "-",
            "attributeDelimiter": "//",
        },
        "field2": {
            "label": "Field 2",
            "description": "Field 2",
            "type": "string",
            "uiElement": "multi-select",
            "validValues": [
                {"label": "Option1", "value": "Option1"},
                {"label": "Option2", "value": "Option2"},
                {"label": "Option3", "value": "Option3"},
                {"label": "Option4", "value": "Option4"},
            ],
            "selectionDisplayOrder": 3,
            "selectionDisplayLabel": "Field 2",
            "bannerOrder": 3,
            "bannerLabel": "Field 2",
            "labelDelimiter": "-",
            "valueDelimiter": ",",
            "attributeDelimiter": "//",
        },
    },
    "layouts": {
        "default": {
            "layoutElements": {
                "classification": {"formDisplayOrder": 1},
                "field1": {"formDisplayOrder": 2},
                "field2": {"formDisplayOrder": 3},
            }
        }
    },
}
_item_classification: dict = {
    "classification": "Restricted-Specific",
    "createdUser": "PAPIadmin",
    "createdDate": 1721645568109,
    "banner": "Restricted-Specific//Field 1-FOUO",
    "field1": "FOUO",
    "lastEditedUser": "PAPIadmin",
    "lastEditedDate": 1721654431371,
}


@profiles.enterprise
@integration_test
class TestPortalitemClassification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._item_classification = _item_classification
        cls._classification_schema = _schema
        cls.fp = os.path.join(tempfile.gettempdir(), "schema_1234.txt")

    def test_classification(self):
        if self.gis.version > [10, 3]:
            admin = self.gis.admin
            c = admin.classification
            assert c.properties

    def test_validate_method(self):
        if self.gis.version > [10, 3]:
            admin = self.gis.admin
            c = admin.classification
            assert c.properties
            assert c.delete()  #  should be True

            fp = self.fp
            with open(fp, 'w') as writer:
                writer.write(json.dumps(_schema))
            assert c.add(fp)
            assert c.schema
            assert c.delete()

        assert c.add(fp)
        assert c.schema

        assert c.validate_schema_file(fp)
        assert c.validate_item_schema(classification=_item_classification)

    @classmethod
    def tearDownClass(cls):
        try:
            if os.path.isfile(cls.fp):
                os.remove(cls.fp)
        except:
            pass

    def test_add_schema(self):
        if self.gis.version > [10, 3]:
            admin = self.gis.admin
            c = admin.classification
            assert c.properties
            assert c.delete()  #  should be True

            fp = self.fp
            with open(fp, "w") as writer:
                writer.write(json.dumps(_schema))
            assert c.add(fp)
            assert c.schema
            assert c.delete()


if __name__ == "__main__":
    unittest.main()

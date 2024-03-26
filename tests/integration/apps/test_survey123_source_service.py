import sys
import unittest

import arcgis
from arcgis.gis import GIS
from arcgis.apps.survey123 import Survey
from utils.decorators import integration_test


@integration_test
class Test_Survey_Class(unittest.TestCase):
    """Test instance of Survey class"""
    @classmethod
    def setUpClass(cls):
        cls.gis: GIS = GIS(
            url="https://arcgissolutions.maps.arcgis.com/home",
            username="Survey123Test15",
            password="SurveyS0lutions!",
            verify_cert=False,
        )

        # Survey Item ID with a Source Service that has a non-zero ID for first layer/table
        cls.survey_id = "220d2468ff3a476b9dd5bd3833bcd338"

    def test_survey_init(self):
        """test instance of Survey class"""
        try:
            survey_manager = arcgis.apps.survey123.SurveyManager(self.gis)
            survey = survey_manager.get(self.survey_id)
        except IndexError as indexError:
            self.fail(f"Error while handling indexes in source Service of the Survey: {indexError.__str__()}")
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

        self.assertIsInstance(survey, Survey, f"Item id {self.survey_id} is not of type 'Survey'")

        layer_ids = [layer.properties['id'] for layer in survey._ssi.layers + survey._ssi.tables]
        self.assertNotIn(0, layer_ids, "The Survey's source service should have a non-zero ID for the first layer.")


if __name__ == "__main__":
    unittest.main()

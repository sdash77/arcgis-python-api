# -------------------------------------------------------------------------------
# Name:        Create new Survey123 survey
# Purpose:     Verifies the arcgis.apps.survey123.SurveyManager.publish() method can sucessfully publish a new survey
# -------------------------------------------------------------------------------

import unittest
import arcgis
from utils.decorators import profiles, integration_test
from integration.config import QALAB_ROOT_PATH
import os


QA_LABS_FOLDER = QALAB_ROOT_PATH


@profiles.enterprise_and_agol
@integration_test
class TestPublishSurvey(unittest.TestCase):

    def test_publish_survey(self):
        """
        Test to verify that Survey123 surveys can be published
        """

        survey_manager = arcgis.apps.survey123.SurveyManager(self.gis)
        new_survey = survey_manager.create(
            title="Python Publish Survey",
            tags=["ArcGIS API for Python, Survey123, Form"],
            summary="This survey was created using the ArcGIS API for Python",
        )

        usr = arcgis.gis.User(self.gis, self.gis.users.me.username)
        survey_folder = self.gis.content.folders._get_or_create(
            folder=new_survey.properties["ownerFolder"],
            owner=self.gis.users.me.username,
        ).properties["id"]

        self.survey = new_survey.publish(
            xlsform=os.path.join(
                QA_LABS_FOLDER,
                "survey123",
                "publish_tests",
                "Hydrant_Inspection_init.xlsx",
            ),
            info={
                "queryInfo": {
                    "mode": "manual",
                    "editEnabled": True,
                    "copyEnabled": True,
                },
                "sentInfo": {"enabled": True, "editEnabled": True, "copyEnabled": True},
                "displayInfo": {
                    "map": {
                        "coordinateFormat": "usng",
                        "home": {
                            "latitude": 34.0568,
                            "longitude": -117.1961,
                            "zoomLevel": 20,
                        },
                        "preview": {"coordinateFormat": "usng", "zoomLevel": 0},
                    }
                },
            },
            create_web_form=True,
            enable_delete_protection=False,
            create_coded_value_domains=True,
            enable_sync=False,
            create_web_map=False,
        )
        assert type(self.survey) == arcgis.apps.survey123.Survey

        fldr_items = usr.items(folder=survey_folder)
        fldr_items_types = [x.type for x in fldr_items]

        assert "Form" in fldr_items_types
        assert "Feature Service" in fldr_items_types
        for item in fldr_items:
            if (
                item.type == "Feature Service"
                and item
                == [x for x in fldr_items if x.type == "Form"][0].related_items(
                    "Survey2Service", "forward"
                )[0]
            ):
                assert "View Service" in item.typeKeywords
        usr = arcgis.gis.User(self.gis, self.gis.users.me.username)
        folder = usr.items(folder=self.survey.properties["ownerFolder"])
        [
            x.delete(permanent=True)
            for x in folder
            if x.type != "Feature Service"
            or (x.type == "Feature Service" and "_form" in x.title)
        ]
        [
            x.delete(permanent=True)
            for x in usr.items(folder=self.survey.properties["ownerFolder"])
        ]
        self.gis.content.folders.get(
            folder=self.survey.properties["ownerFolder"],
            owner=self.gis.users.me.username,
        ).delete(permanent=True)


if __name__ == "__main__":
    unittest.main()

# -------------------------------------------------------------------------------
# Name:        Workforce Assignment Attachments tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime
import importlib_resources
from arcgis.gis import GIS, Group, User
from arcgis.features import Feature, FeatureLayer
from arcgis.apps.workforce import *
from arcgis.apps.workforce._schemas import *
from arcgis.apps.workforce.managers import *
from utils.decorators import integration_test, profiles
from integration.config import get_resource_path


@profiles.agol
@integration_test
class Test_Workforce_Assignment_Attachments(unittest.TestCase):
    """
    Test to verify that assignment attachments can be fetched and downloaded
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        t = datetime.datetime.now()
        cls.time_stamp = str.format(
            "Workforce-Ntgrtn-tst: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        cls.project = create_project(cls.time_stamp)
        cls.at = cls.project.assignment_types.add(name="test")
        cls.assignment = cls.project.assignments.add(
            assignment_type=cls.at,
            location="100 Commercial St",
            geometry={"x": -7820308, "y": 5412450},
            status=0,
            description="hello",
            notes="hello",
            priority=0,
        )
        thumbnail = get_resource_path("logo.png")
        cls.assignment.attachments.add(thumbnail)

    def setUp(self):
        # create project for each test
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_"

        t = datetime.datetime.now()
        self.time_stamp = str.format(
            "Workforce-Ntgrtn-tst: {0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.project.delete(permanent=True)
        except Exception as e:
            print("Failed to delete project successfully!")
        print("\n==================================================================")

    def test_attachment_manager(self):
        try:
            assignment = self.project.assignments.search()[0]
            self.assertIsInstance(
                assignment.attachments, AssignmentAttachmentManager, "Incorrect Type"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_download_all(self):
        try:
            assignment = self.project.assignments.search()[0]
            downloaded_paths = assignment.attachments.download()
            self.assertIsInstance(downloaded_paths, list, "Incorrect download type")
            self.assertEqual(
                len(downloaded_paths), 1, "Incorrect number of items downloaded"
            )
            self.assertIsInstance(downloaded_paths[0], str, "Incorrect type")
            self.assertTrue(
                "logo.png" in downloaded_paths[0], "Incorrect download filename"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_download_one(self):
        try:
            assignment = self.project.assignments.search()[0]
            attachment = assignment.attachments.get()[0]
            self.assertIsInstance(attachment, Attachment, "Incorrect download type")
            downloaded_path = attachment.download()
            self.assertIsInstance(downloaded_path, str, "Incorrect type")
            self.assertTrue(
                "logo.png" in downloaded_path, "Incorrect download filename"
            )

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


if __name__ == "__main__":
    unittest.main()

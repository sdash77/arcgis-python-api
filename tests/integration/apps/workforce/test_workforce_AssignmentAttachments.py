# -------------------------------------------------------------------------------
# Name:        Workforce Assignment Attachments tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
import uuid

from arcgis.apps.workforce import *
from arcgis.apps.workforce.managers import *
from integration.config import get_resource_path
from utils.decorators import integration_test, profiles


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
        cls.project_name = f"Workforce-ntgrtn-tst_{uuid.uuid4().hex[:5]}"
        cls.project = create_project(cls.project_name)
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

    @classmethod
    def tearDownClass(cls):
        try:
            cls.project.delete(permanent=True)
        except Exception as e:
            print("Failed to delete project")

    def test_attachment_manager(self):
        try:
            assignment = self.project.assignments.search()[0]
            self.assertIsInstance(
                assignment.attachments, AssignmentAttachmentManager, "Incorrect Type"
            )

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

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


if __name__ == "__main__":
    unittest.main()

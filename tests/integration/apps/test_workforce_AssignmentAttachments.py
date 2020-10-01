#-------------------------------------------------------------------------------
# Name:        Workforce Assignment Attachments tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime
import pkg_resources

#region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if (r1 & r2):
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise(exit())

# Import the module after Precondition checks pass
try:
    from arcgis.gis import GIS, Group, User
    from arcgis.features import Feature, FeatureLayer
    from arcgis.mapping import WebMap
    from arcgis.apps.workforce import *
    from arcgis.apps.workforce._schemas import *
    from arcgis.apps.workforce.managers import *
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Workforce Attachments")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


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
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['workforce_ago']['url']
        cls.portal_username = _conf_reader['workforce_ago']['publisher_user']
        cls.portal_password = _conf_reader['workforce_ago']['publisher_password']
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        t = datetime.datetime.now()
        cls.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
                                     str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        cls.project = create_project(cls.time_stamp)
        cls.at = cls.project.assignment_types.add(name="test")
        cls.assignment = cls.project.assignments.add(assignment_type=cls.at, location="100 Commercial St",
                                                       geometry={'x': -7820308, 'y': 5412450}, status=0,
                                                       description="hello", notes="hello", priority=0)
        resource_package = __name__
        resource_path = '/'.join(('resources', 'logo.png'))
        thumbnail = pkg_resources.resource_filename(resource_package, resource_path)
        cls.assignment.attachments.add(thumbnail)


        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_Workforce_AssignmentManager class")

    def setUp(self):
        # create project for each test
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")
        print("\n==================================================================")

    def test_attachment_manager(self):
        try:
            assignment = self.project.assignments.search()[0]
            self.assertIsInstance(assignment.attachments, AssignmentAttachmentManager, "Incorrect Type")

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
            self.assertEqual(len(downloaded_paths), 1, "Incorrect number of items downloaded")
            self.assertIsInstance(downloaded_paths[0], str, "Incorrect type")
            self.assertTrue("logo.png" in downloaded_paths[0], "Incorrect download filename")


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
            self.assertTrue("logo.png" in downloaded_path, "Incorrect download filename")


        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

#TestModule
def tearDownModule():
    print("**End Workforce AssignmentManager Tests**")
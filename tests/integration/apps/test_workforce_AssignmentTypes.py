#-------------------------------------------------------------------------------
# Name:        Workforce Assignment Types tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime

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
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Workforce Assignment Types")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


class Test_Workforce_Assignment_Types(unittest.TestCase):
    """
    Test to verify that assignments types can be fetched, updated, added, deleted
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


        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_Workforce_AssignmentManager class")

    def setup_project(self):
        self.project.assignment_types.add(name="Inspection")

    def reset_project(self):
        self.project.assignment_types.batch_delete(self.project.assignment_types.search())

    def setUp(self):
        # reset project for each test
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_"
        self.reset_project()
        self.setup_project()

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

    def test_attachment_type_manager(self):
        try:
            assignment_types = self.project.assignment_types.search()
            self.assertIsInstance(assignment_types[0], AssignmentType, "Incorrect type")
            self.assertEqual(assignment_types[0].name, "Inspection", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_assignment_type(self):
        try:
            self.project.assignment_types.add(name="Removal")
            assignment_type = self.project.assignment_types.search()[-1]
            self.assertEqual(assignment_type.name, "Removal", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_assignment_type(self):
        try:
            assignment_type = AssignmentType(
                self.project,
                name="Removal"
            )
            self.project.assignment_types.batch_add([assignment_type])
            assignment_type = self.project.assignment_types.search()[-1]
            self.assertEqual(assignment_type.name, "Removal", "Incorrect name")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_assignment_type(self):
        try:
            assignment_type = self.project.assignment_types.search()[0]
            assignment_type.delete()
            assignment_types = self.project.assignment_types.search()
            self.assertEqual(len(assignment_types), 0, "Incorrect number of assignment types")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_assignment_type(self):
        try:
            assignment_type = self.project.assignment_types.search()[0]
            self.project.assignment_types.batch_delete([assignment_type])
            self.assertEqual(len(self.project.assignment_types.search()), 0, "Incorrect number of assignment types")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_update_assignment_type(self):
        try:
            assignment_type = self.project.assignment_types.search()[0]
            assignment_type.name = "Repair"
            self.project.assignment_types.batch_update([assignment_type])
            assignment_type = self.project.assignment_types.search()[0]
            self.assertEqual(assignment_type.name, "Repair", "Incorrect assignment type")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_assignment_type(self):
        try:
            assignment_type = self.project.assignment_types.search()[0]
            assignment_type.update(name="Repair")
            assignment_type = self.project.assignment_types.search()[0]
            self.assertEqual(assignment_type.name, "Repair", "Incorrect assignment type")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_assignment_type_validation(self):
        try:
            with self.assertRaises(ValidationError):
                self.project.assignment_types.add()

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
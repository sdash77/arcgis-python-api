#-------------------------------------------------------------------------------
# Name:        Workforce Tracks tests
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
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Workforce Tracks")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Workforce_Tracks(unittest.TestCase):
    """
    Test to verify that tracks can be queried, added, updated, and deleted from a project
    """

    def add_track(self):
        self.project.tracks.add(geometry={"x": 123, "y": 456},
                                accuracy=50)

    def reset_project(self):
        self.project.tracks.enabled = True
        self.project.tracks.interval = 30
        self.project.tracks.batch_delete(self.project.tracks.search())

    def setup_project(self):
        self.add_track()

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
        cls.project_id = "0620ee75107747c6ac6ce3d2ac27f36f"
        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        cls.project = Project(cls.gis.content.get(cls.project_id))

        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True
        print("==================================================================")
        print("Beginning tests in Test_Workforce_WorkerManager class")

    def setUp(self):
        # reset project for each test
        self.reset_project()
        self.setup_project()
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
        print("\n==================================================================")

    def test_search_tracks(self):
        try:
            track = self.project.tracks.search()[0]
            self.assertEqual(track.geometry, {"x": 123, "y": 456}, "Incorrect geometry")
            self.assertEqual(track.accuracy, 50, "Incorrect accuracy")

            tracks = self.project.tracks.search("1=0")
            self.assertEqual(len(tracks), 0, "Incorrect number of tracks")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_tracks(self):
        try:
            track = self.project.tracks.search()[0]
            track.update(geometry={"x": 456, "y": 321}, accuracy=30)
            track = self.project.tracks.search()[0]
            self.assertEqual(track.geometry, {"x": 456, "y": 321}, "Incorrect geometry")
            self.assertEqual(track.accuracy, 30, "Incorrect accuracy")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_update_tracks(self):
        try:
            track = self.project.tracks.search()[0]
            track.geometry = {"x": 456, "y": 321}
            track.accuracy = 30
            self.project.tracks.batch_update([track])
            track = self.project.tracks.search()[0]
            self.assertEqual(track.geometry, {"x": 456, "y": 321}, "Incorrect geometry")
            self.assertEqual(track.accuracy, 30, "Incorrect accuracy")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_tracks(self):
        try:
            track = Track(self.project,
                geometry={"x": 456, "y": 321},
                accuracy=50
            )
            self.project.tracks.batch_add([track])
            tracks = self.project.tracks.search()
            self.assertEqual(tracks[1].geometry, {"x": 456, "y": 321}, "Incorrect geometry")
            self.assertEqual(tracks[1].accuracy, 50, "Incorrect accuracy")
            self.assertEqual(len(tracks), 2, "Incorrect number of tracks")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_tracks(self):
        try:
            self.project.tracks.add(
                geometry={"x": 456, "y": 321},
                accuracy=50
            )
            tracks = self.project.tracks.search()
            self.assertEqual(tracks[1].geometry, {"x": 456, "y": 321}, "Incorrect geometry")
            self.assertEqual(tracks[1].accuracy, 50, "Incorrect accuracy")
            self.assertEqual(len(tracks), 2, "Incorrect number of tracks")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_tracks(self):
        try:
            tracks = self.project.tracks.search()
            self.assertEqual(len(tracks), 1, "Incorrect number of tracks")
            tracks[0].delete()
            tracks = self.project.tracks.search()
            self.assertEqual(len(tracks), 0, "Incorrect number of tracks")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_tracks(self):
        try:
            tracks = self.project.tracks.search()
            self.assertEqual(len(tracks), 1, "Incorrect number of tracks")
            self.project.tracks.batch_delete(tracks)
            tracks = self.project.tracks.search()
            self.assertEqual(len(tracks), 0, "Incorrect number of tracks")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_tracking_changes(self):
        try:
            self.assertEqual(self.project.tracks.enabled, True, "Incorrect tracking state")
            self.assertEqual(self.project.tracks.interval, 30, "Incorrect tracking interval")
            self.project.tracks.enabled = False
            self.project.tracks.interval = 50
            self.assertEqual(self.project.tracks.enabled, False, "Incorrect tracking state")
            self.assertEqual(self.project.tracks.interval, 50, "Incorrect tracking interval")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

#TestModule
def tearDownModule():
    print("**End Workforce WorkerManager Tests**")
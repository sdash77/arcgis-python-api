# -------------------------------------------------------------------------------
# Name:        Workforce Tracks tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import datetime
import unittest
from configparser import ConfigParser

from arcgis.apps.workforce import *
from arcgis.apps.workforce.managers import *
from arcgis.gis import GIS
from integration.dino_utils.dino_configs import DinoConfigs
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from utils.decorators import integration_test, profiles


@profiles.admin_agol
@integration_test
class Test_Workforce_Tracks(unittest.TestCase):
    """
    Test to verify that tracks can be queried, added, updated, and deleted from a project
    """

    def add_track(self):
        self.project.tracks.add(geometry={"x": 123, "y": 456}, accuracy=50)

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
        cls.project = create_project(cls.time_stamp, major_version=1)

    def setUp(self):
        # reset project for each test
        self.reset_project()
        self.setup_project()
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
            cls.project.delete()
        except Exception as e:
            print("Failed to delete project successfully!")
        print("\n==================================================================")

    def test_search_tracks(self):
        try:
            track = self.project.tracks.search()[0]
            self.assertEqual(track.geometry["x"], 123, "Incorrect x")
            self.assertEqual(track.geometry["y"], 456, "Incorrect y")
            self.assertEqual(track.accuracy, 50, "Incorrect accuracy")

            tracks = self.project.tracks.search("1=0")
            self.assertEqual(len(tracks), 0, "Incorrect number of tracks")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_update_tracks(self):
        try:
            track = self.project.tracks.search()[0]
            track.update(geometry={"x": 456, "y": 321}, accuracy=30)
            track = self.project.tracks.search()[0]
            self.assertEqual(track.geometry["x"], 456, "Incorrect x")
            self.assertEqual(track.geometry["y"], 321, "Incorrect y")
            self.assertEqual(track.accuracy, 30, "Incorrect accuracy")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_update_tracks(self):
        try:
            track = self.project.tracks.search()[0]
            track.geometry = {"x": 456, "y": 321}
            track.accuracy = 30
            self.project.tracks.batch_update([track])
            track = self.project.tracks.search()[0]
            self.assertEqual(track.geometry["x"], 456, "Incorrect x")
            self.assertEqual(track.geometry["y"], 321, "Incorrect y")
            self.assertEqual(track.accuracy, 30, "Incorrect accuracy")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_add_tracks(self):
        try:
            track = Track(self.project, geometry={"x": 456, "y": 321}, accuracy=50)
            self.project.tracks.batch_add([track])
            tracks = self.project.tracks.search()
            self.assertEqual(tracks[1].geometry["x"], 456, "Incorrect x")
            self.assertEqual(tracks[1].geometry["y"], 321, "Incorrect y")
            self.assertEqual(tracks[1].accuracy, 50, "Incorrect accuracy")
            self.assertEqual(len(tracks), 2, "Incorrect number of tracks")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_add_tracks(self):
        try:
            self.project.tracks.add(geometry={"x": 456, "y": 321}, accuracy=50)
            tracks = self.project.tracks.search()
            self.assertEqual(tracks[1].geometry["x"], 456, "Incorrect x")
            self.assertEqual(tracks[1].geometry["y"], 321, "Incorrect y")
            self.assertEqual(tracks[1].accuracy, 50, "Incorrect accuracy")
            self.assertEqual(len(tracks), 2, "Incorrect number of tracks")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_delete_tracks(self):
        try:
            tracks = self.project.tracks.search()
            self.assertEqual(len(tracks), 1, "Incorrect number of tracks")
            tracks[0].delete()
            tracks = self.project.tracks.search()
            self.assertEqual(len(tracks), 0, "Incorrect number of tracks")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_batch_delete_tracks(self):
        try:
            tracks = self.project.tracks.search()
            self.assertEqual(len(tracks), 1, "Incorrect number of tracks")
            self.project.tracks.batch_delete(tracks)
            tracks = self.project.tracks.search()
            self.assertEqual(len(tracks), 0, "Incorrect number of tracks")

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_tracking_changes(self):
        try:
            self.assertEqual(
                self.project.tracks.enabled, True, "Incorrect tracking state"
            )
            self.assertEqual(
                self.project.tracks.interval, 30, "Incorrect tracking interval"
            )
            self.project.tracks.enabled = False
            self.project.tracks.interval = 50
            self.assertEqual(
                self.project.tracks.enabled, False, "Incorrect tracking state"
            )
            self.assertEqual(
                self.project.tracks.interval, 50, "Incorrect tracking interval"
            )

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


if __name__ == "__main__":
    unittest.main()

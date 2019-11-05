#-------------------------------------------------------------------------------
# Name:        GIS 
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
import os
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import tempfile
import datetime

try:
    from arcgis.gis import GIS
except ImportError:
    print("API import error. Quitting test")
    raise(exit())

class Test_GIS_home_homde(unittest.TestCase):
    """
    Test to check if a GIS('home') object is created correctly
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up proper GIS credentials for when we need them
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['teamportal']['url']
        cls.portal_username = _conf_reader['teamportal']['admin_user']
        cls.portal_password = _conf_reader['teamportal']['admin_password']

    def setUp(self):
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

    def _make_nb_auth_file(self, private_portal_url, public_portal_url,
                           token, referer):
        """Make a temporary file with the above args, returns the path string"""
        temp_file_path = tempfile.tempdir + "temp.json"
        with open(temp_file_path, "w") as file_:
            file_.write('{' + \
                        '"privatePortalUrl": "{}",'.format(private_portal_url) + \
                        '"publicPortalUrl": "{}",'.format(public_portal_url) + \
                        '"token": "{}",'.format(token) + \
                        '"referer": "{}"'.format(referer) + \
                        '}')
        return temp_file_path

    def test_private_public_url(self):
        valid_gis = GIS(self.portal_url,
                        self.portal_username,
                        self.portal_password,
                        verify_cert=False)
        nb_auth_file_path = self._make_nb_auth_file(
            private_portal_url = valid_gis._url,
            public_portal_url = "https://testfakeurl.com",
            token = valid_gis._portal.con._token,
            referer = "http://localhost/")
        os.environ["NB_AUTH_FILE"] = nb_auth_file_path

        #Assert that the URLS and such are set correctly, can connect
        home_gis = GIS('home', verify_cert=False)
        self.assertTrue(home_gis._is_hosted_nb_home)
        self.assertEqual(home_gis._url, valid_gis._url)
        self.assertIsNotNone(home_gis.users.me)

        #assert that the public url is in the notebook display for items
        random_item = home_gis.content.search("*", item_type="Web Map")[0]
        self.assertIn("testfakeurl", random_item._repr_html_())

        #assert that the public url is in the notebook display for user
        me = home_gis.users.me
        self.assertIn("testfakeurl", me._repr_html_())

        #assert that the public url is in the notebook display for user
        random_group = home_gis.groups.search("*")[0]
        self.assertIn("testfakeurl", random_group._repr_html_())

        #assert that a widget instance uses the public url
        widget = home_gis.map()
        self.assertIn("testfakeurl", widget._portal_url)

#TestModule
def tearDownModule():
    print("**End GIS hosted NB module Tests**")

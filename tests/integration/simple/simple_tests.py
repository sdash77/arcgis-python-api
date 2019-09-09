import os
import sys

import unittest
import pytest
import arcgis
from arcgis.gis import GIS

"""
This is a list of Portals to test connecting
with using the Portal_QA Machines

gis = GIS('https://www.arcgis.com', 'arcgis_python', 'P@ssword123')
gis = GIS(profile="your_online_profile")
gis = GIS('https://pythonapi.playground.esri.com/portal', 'arcgis_python', 'amazing_arcgis_123')
gis = GIS(profile="your_enterprise_portal")
"""


# DEBUGGING ONLY
PROXY_HOST = None
PROXY_PORT = None
VERIFY_CERT = False

LARGE_FILE_URL = r"https://www2.census.gov/geo/tiger/TGRGDB18/tlgdb_2018_a_us_rails.gdb.zip"
LARGE_FILE = r"./{fp}".format(fp=os.path.basename(LARGE_FILE_URL))
SMALL_FILE_URL = r"https://www2.census.gov/geo/tiger/TIGER2017/STATE/tl_2017_us_state.zip"
SMALL_FILE = r"./{fp}".format(fp=os.path.basename(SMALL_FILE_URL))

PORTALS_QA = {
    "BUILTIN" : {
        "url" : "https://portalhostds.ags.esri.com/gis",
        "username" : "gisproadv2",
        "password" : "portalaccount1",
    },
    "WINDOWS" : {
        "url" : "https://portaliwads.ags.esri.com/gis",
        "username" : None,
        "password" : None,
    },
    "KERBEROS" : {
        "url" : "https://portalkerberos.ags.esri.com/gis",
        "username" : None,
        "password" : None,
    },
    "BASIC" : {
        "url" : "https://portallxldapds.esri.com/gis",
        "username" : "sharing1",
        "password" : "sharing.1",
    },
    "DOUBLE_IWA" : {
        "url" : "https://prtldualiwads.ags.esri.com/gis",
        "username" : "publisher",
        "password" : "publisher.account",
    },
    "IWA" : {
        "url" : "https://portaliwads.ags.esri.com/gis",
        "username" : None,
        "password" : None
    },
    "PROFILE_AGOL" : "your_online_profile",
    "PROFILE_PORTAL" : "your_enterprise_portal",
    "PROFILE_NBS" : {"url" : "https://datascienceadv.esri.com/portal",
                     "username" : "arcgis_python",
                     "password" : "P@ssword123",
                     "profile" : "hosted_notebook_profile"
                    },
    "PKI" : {
        "url" : "https://portalpkids.ags.esri.com/gis",
        "cert" : r"./gisproadv2.pfx",
        "password" : "portalaccount1",
    },
    "PKI_JAVA" : {
        "url" : "https://portalpkids.ags.esri.com/gis",
        "cert" : r"./gisproadv2.pfx",
        "password" : "portalaccount1",
    }

}
###########################################################################
#@unittest.SkipTest
class TestGISConnection(unittest.TestCase):
    """Tests the various GIS Connection methods"""
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_builtin(self):
        """tests logging in via builtin"""
        info = PORTALS_QA["BUILTIN"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_anon_user_portal(self):
        """tests logging in without credentials"""
        info = PORTALS_QA["BUILTIN"]

        gis = GIS(url=info['url'],
                  username=None,
                  password=None,
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me is None
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_anon_user_agol(self):
        """tests logging in agol without credentials"""
        info = None
        gis = GIS(url=None,
                  username=None,
                  password=None,
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me is None
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_profile_user_portal(self):
        """tests logging in portal without credentials"""

        gis = GIS(profile=PORTALS_QA["PROFILE_PORTAL"],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_profile_user_agol(self):
        """tests logging in agol without credentials"""

        gis = GIS(profile=PORTALS_QA["PROFILE_AGOL"],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_BASIC(self):
        """tests logging in BASIC"""
        info = PORTALS_QA["BASIC"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_DOUBLEIWA(self):
        """tests logging in DOUBLE IWA"""
        info = PORTALS_QA["DOUBLE_IWA"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_IWA(self):
        """tests logging in IWA"""
        info = PORTALS_QA["IWA"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_KERBEROS(self):
        """tests logging in KERBEROS"""
        info = PORTALS_QA["KERBEROS"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_WINDOWS(self):
        """tests logging in WINDOWS AUTH"""
        info = PORTALS_QA["WINDOWS"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_PKI(self):
        """tests logging in PKI"""
        info = PORTALS_QA["PKI"]
        gis = GIS(url=info['url'],
                  cert_file=info['cert'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT)
        assert gis.users.me
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_PKI_JAVA(self):
        """tests logging in PKI"""
        info = PORTALS_QA["PKI_JAVA"]
        gis = GIS(url=info['url'],
                  cert_file=info['cert'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT)
        assert gis.users.me
###########################################################################
#@unittest.SkipTest
class TestAddingSmallItem(unittest.TestCase):
    """Tests uploading items to Portal/AGOL"""
    #--------------------------------------------------------------------------
    def setUp(self):
        if os.path.isfile(SMALL_FILE) == False:
            import requests
            r = requests.get(SMALL_FILE_URL)
            with open(SMALL_FILE, 'wb') as writer:
                writer.write(r.content)
                del writer
    #--------------------------------------------------------------------------
    @staticmethod
    def teardown():
        if os.path.isfile(path=SMALL_FILE):
            os.remove(SMALL_FILE)
    @classmethod
    def tearDownClass(cls):
        cls.teardown()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_builtin(self):
        """tests logging in via builtin"""
        info = PORTALS_QA["BUILTIN"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_profile_user_portal(self):
        """tests logging in portal without credentials"""

        gis = GIS(profile=PORTALS_QA["PROFILE_PORTAL"],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_profile_user_agol(self):
        """tests logging in agol without credentials"""

        gis = GIS(profile=PORTALS_QA["PROFILE_AGOL"],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_BASIC(self):
        """tests logging in BASIC"""
        info = PORTALS_QA["BASIC"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_DOUBLEIWA(self):
        """tests logging in DOUBLE IWA"""
        info = PORTALS_QA["DOUBLE_IWA"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_IWA(self):
        """tests logging in IWA"""
        info = PORTALS_QA["IWA"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_KERBEROS(self):
        """tests logging in KERBEROS"""
        info = PORTALS_QA["KERBEROS"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_WINDOWS(self):
        """tests logging in WINDOWS AUTH"""
        info = PORTALS_QA["WINDOWS"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_PKI(self):
        """tests logging in PKI"""
        info = PORTALS_QA["PKI"]
        gis = GIS(url=info['url'],
                  cert_file=info['cert'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_PKI_JAVA(self):
        """tests logging in PKI"""
        info = PORTALS_QA["PKI_JAVA"]
        gis = GIS(url=info['url'],
                  cert_file=info['cert'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'Shapefile'
            },
            data=SMALL_FILE
        )
        assert item
        assert item.delete()
###########################################################################
#@unittest.SkipTest
class TestAddingLargeItem(unittest.TestCase):
    """Tests uploading items to Portal/AGOL"""
    #--------------------------------------------------------------------------
    def setUp(self):
        if os.path.isfile(LARGE_FILE) == False:
            import requests
            r = requests.get(LARGE_FILE_URL, allow_redirects=True)
            open(LARGE_FILE, 'wb').write(r.content)
    #--------------------------------------------------------------------------
    @staticmethod
    def teardown():
        if os.path.isfile(path=LARGE_FILE):
            os.remove(LARGE_FILE)
    #--------------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        cls.teardown()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_builtin(self):
        """tests logging in via builtin"""
        info = PORTALS_QA["BUILTIN"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'File Geodatabase'
            },
            data=LARGE_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_BASIC(self):
        """tests logging in BASIC"""
        info = PORTALS_QA["BASIC"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'File Geodatabase'
            },
            data=LARGE_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_DOUBLEIWA(self):
        """tests logging in DOUBLE IWA"""
        info = PORTALS_QA["DOUBLE_IWA"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'File Geodatabase'
            },
            data=LARGE_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_IWA(self):
        """tests logging in IWA"""
        info = PORTALS_QA["IWA"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'File Geodatabase'
            },
            data=LARGE_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_KERBEROS(self):
        """tests logging in KERBEROS"""
        info = PORTALS_QA["KERBEROS"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'File Geodatabase'
            },
            data=LARGE_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_WINDOWS(self):
        """tests logging in WINDOWS AUTH"""
        info = PORTALS_QA["WINDOWS"]
        gis = GIS(url=info['url'],
                  username=info['username'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'File Geodatabase'
            },
            data=LARGE_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_PKI(self):
        """tests logging in PKI"""
        info = PORTALS_QA["PKI"]
        gis = GIS(url=info['url'],
                  cert_file=info['cert'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'File Geodatabase'
            },
            data=LARGE_FILE
        )
        assert item
        assert item.delete()
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_portal_PKI_JAVA(self):
        """tests logging in PKI"""
        info = PORTALS_QA["PKI_JAVA"]
        gis = GIS(url=info['url'],
                  cert_file=info['cert'],
                  password=info['password'],
                  verify_cert=VERIFY_CERT)
        item = gis.content.add(
            item_properties={
                'title' : "erase_me_noww",
                'tags' : "a,b,c",
                "type" : 'File Geodatabase'
            },
            data=LARGE_FILE
        )
        assert item
        assert item.delete()
###########################################################################
#@unittest.SkipTest
class TestAdminFunctionality(unittest.TestCase):
    """
    These tests REQUIRE the user to be of type org_admin
    """
    def test_has_admin_portal(self):
        """tests if admin property exists"""
        gis = GIS(profile=PORTALS_QA["PROFILE_PORTAL"],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert hasattr(gis, 'admin')
        assert gis.admin.servers
        servers = gis.admin.servers.list()
        assert len(servers) >= 0
        for s in servers:
            assert s.services
            assert len(s.services.list()) >= 0
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_profile_user_agol(self):
        """tests logging in agol without credentials"""

        gis = GIS(profile=PORTALS_QA["PROFILE_AGOL"],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert hasattr(gis, 'admin')
        assert gis.admin.license.all()
        assert gis.version > [7,1]
    #--------------------------------------------------------------------------
    #@unittest.SkipTest
    def test_profile_nb_server(self):
        """tests logging in agol without credentials"""

        gis = GIS(url=PORTALS_QA["PROFILE_NBS"]['url'],
                  username=PORTALS_QA["PROFILE_NBS"]['username'],
                  password=PORTALS_QA["PROFILE_NBS"]['password'],
                  verify_cert=VERIFY_CERT,
                  proxy_host=PROXY_HOST,
                  proxy_port=PROXY_PORT)
        assert hasattr(gis, 'admin')

        for s in gis.admin.servers.list():
            if isinstance(s, arcgis.gis.nb.NotebookServer):
                q = s.logs.query()
                assert q
        assert gis.version >= [7,1]


#--------------------------------------------------------------------------
if __name__ == "__main__":
    print("... STARTING ALL TESTS ...")
    unittest.main()
    print("... ALL TESTS FINISHED ...")
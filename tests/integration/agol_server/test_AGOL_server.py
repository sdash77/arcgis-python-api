import sys

sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_7467\src")
from arcgis.auth.tools import LazyLoader

logging = LazyLoader("logging")
_isd = LazyLoader("arcgis._impl.common._isd")
_service = LazyLoader("arcgis.gis.server._service")
from arcgis.gis import GIS, agoserver, server
import unittest

PROFILES = ['your_dev_online_profile', 'your_online_profile']


class TestAgolServer(unittest.TestCase):
    def test_get_hosting_servers(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            assert isinstance(gis.hosting_servers, list)

    def test_server_is_AGOServicesDirectory(self):
        """tests that the right classes are returned"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            for server in gis.hosting_servers:
                assert isinstance(server, agoserver.AGOLServicesDirectory)

    def test_server_properties(self):
        """tests the AGO Server Properties"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            for server in gis.hosting_servers:
                assert isinstance(server, agoserver.AGOLServicesDirectory)
                assert server.properties
                assert isinstance(server.services, list)
                assert server.is_tile_server in [True, False]
                assert len(server.folders) == 0


class TestAGOLAdminManager(unittest.TestCase):
    """Tests that the Manager returns the proper things"""

    def test_gis_admin_servers(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            assert isinstance(gis.admin.servers, agoserver.AGOLServersManager)
            assert gis.admin.servers.properties
            assert gis.admin.servers.tile_server
            assert gis.admin.servers.feature_server


class TestAGOLAdminServerTileManager(unittest.TestCase):
    """Tests that ensure the Feature Server Admin Functionality Works"""

    def test_single_admin_servers(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            assert gis.admin.servers.feature_server
            assert isinstance(
                gis.admin.servers.tile_server[0], agoserver.AGOLServerManager
            )

    def test_services(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            sm = gis.admin.servers.tile_server[0]
            assert sm.services

    def test_get(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            sm = gis.admin.servers.tile_server[0]
            if len(sm.properties['services']) > 0:
                name = sm.properties['services'][0]
                assert sm.get(sm.properties['services'][0]['name'])

    def test_status(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            sm = gis.admin.servers.tile_server[0]
            if len(sm.properties['services']) > 0:
                name = sm.properties['services'][0]
                assert sm.status(sm.properties['services'][0]['name'])

    def test_is_tile_service(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            sm = gis.admin.servers.tile_server[0]
            assert sm.is_tile_server in [True, False]


class TestAGOLAdminServerFeatureManager(unittest.TestCase):
    """Tests that ensure the Feature Server Admin Functionality Works"""

    def test_single_admin_servers(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            assert gis.admin.servers.feature_server
            assert isinstance(
                gis.admin.servers.feature_server[0], agoserver.AGOLServerManager
            )

    def test_services(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            sm = gis.admin.servers.feature_server[0]
            assert sm.services

    def test_get(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            sm = gis.admin.servers.feature_server[0]
            if len(sm.properties['services']) > 0:
                name = sm.properties['services'][0]
                assert sm.get(name['adminServiceInfo']['name'])

    def test_status(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            sm = gis.admin.servers.feature_server[0]
            if len(sm.properties['services']) > 0:
                name = sm.properties['services'][0]
                assert sm.status(name['adminServiceInfo']['name'])


class TestHostingServerProperty(unittest.TestCase):
    def setUp(self):
        from arcgis.gis import ProfileManager

        if not 'gpportal' in ProfileManager().list():
            GIS(
                profile='gpportal',
                username='admin',
                password='esri.agp',
                url='https://gpportal.esri.com/portal',
            )

    def test_enterprise_hosting_servers(self):
        """tests if a list of hosting servers is returns"""
        gis = GIS(profile='gpportal', verify_cert=False)
        assert isinstance(gis.hosting_servers, list)
        if len(gis.hosting_servers) > 0:
            assert isinstance(gis.hosting_servers[0], server.ServicesDirectory)

    def test_AGOL_hosting_servers(self):
        """tests if a list of hosting servers is returns"""
        gis = GIS(profile='your_online_profile', verify_cert=False)
        assert isinstance(gis.hosting_servers, list)
        if len(gis.hosting_servers) > 0:
            assert isinstance(gis.hosting_servers[0], agoserver.AGOLServicesDirectory)


if __name__ == "__main__":
    unittest.main()

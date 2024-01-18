from arcgis.auth.tools import LazyLoader

logging = LazyLoader("logging")
from arcgis.gis import GIS, agoserver, server
import unittest
from utils.decorators import admin_agol_profile, admin_enterprise_and_agol_profiles, default_timeout

@admin_agol_profile
class TestAgolServer(unittest.TestCase):
    @default_timeout
    def test_get_hosting_servers(self):
        gis = self.gis
        assert isinstance(gis.hosting_servers, list)

    @default_timeout
    def test_list_servers(self):
        gis = self.gis
        assert isinstance(gis.admin.servers.list(), list)

    @default_timeout
    def test_server_is_AGOServicesDirectory(self):
        """tests that the right classes are returned"""
        gis = self.gis
        for server in gis.hosting_servers:
            assert isinstance(server, agoserver.AGOLServicesDirectory)

    @default_timeout
    def test_server_properties(self):
        """tests the AGO Server Properties"""
        gis = self.gis
        for server in gis.hosting_servers:
            assert isinstance(server, agoserver.AGOLServicesDirectory)
            assert server.properties
            assert isinstance(server.properties["services"], list)
            assert len(server.folders) == 0

@admin_agol_profile
class TestAGOLAdminManager(unittest.TestCase):
    """Tests that the Manager returns the proper things"""

    @default_timeout
    def test_gis_admin_servers(self):
        gis = self.gis
        assert isinstance(gis.admin.servers, agoserver.AGOLServersManager)
        assert gis.admin.servers.properties
        assert gis.admin.servers.tile_server
        assert gis.admin.servers.feature_server
        for ts in gis.admin.servers.tile_server:
            assert ts.is_tile_server in [True, False]
        for fs in gis.admin.servers.feature_server:
            assert fs.is_tile_server in [True, False]

@admin_agol_profile
class TestAGOLAdminServerTileManager(unittest.TestCase):
    """Tests that ensure the Feature Server Admin Functionality Works"""

    @default_timeout
    def test_single_admin_servers(self):
        gis = self.gis
        assert gis.admin.servers.feature_server
        assert isinstance(
            gis.admin.servers.tile_server[0], agoserver.AGOLServerManager
        )

    @default_timeout
    def test_services(self):
        gis = self.gis
        sm = gis.admin.servers.tile_server[0]
        assert sm.services

    @default_timeout
    def test_get(self):
        gis = self.gis
        sm = gis.admin.servers.tile_server[0]
        if len(sm.properties["services"]) > 0:
            name = sm.properties["services"][0]
            assert sm.get(sm.properties["services"][0]["name"])

    @default_timeout
    def test_status(self):
        gis = self.gis
        sm = gis.admin.servers.tile_server[0]
        if len(sm.properties["services"]) > 0:
            name = sm.properties["services"][0]
            assert sm.status(sm.properties["services"][0]["name"])

    @default_timeout
    def test_is_tile_service(self):
        gis = self.gis
        sm = gis.admin.servers.tile_server[0]
        assert sm.is_tile_server in [True, False]


@admin_agol_profile
class TestAGOLAdminServerFeatureManager(unittest.TestCase):
    """Tests that ensure the Feature Server Admin Functionality Works"""

    @default_timeout
    def test_single_admin_servers(self):
        gis = self.gis
        assert gis.admin.servers.feature_server
        assert isinstance(
            gis.admin.servers.feature_server[0], agoserver.AGOLServerManager
        )

    @default_timeout
    def test_services(self):
        gis = self.gis
        sm = gis.admin.servers.feature_server[0]
        assert sm.services

    @default_timeout
    def test_get(self):
        gis = self.gis
        sm = gis.admin.servers.feature_server[0]
        if len(sm.properties["services"]) > 0:
            name = sm.properties["services"][0]
            assert sm.get(name["adminServiceInfo"]["name"])

    @default_timeout
    def test_status(self):
        gis = self.gis
        sm = gis.admin.servers.feature_server[0]
        if len(sm.properties["services"]) > 0:
            name = sm.properties["services"][0]
            assert sm.status(name["adminServiceInfo"]["name"])


@admin_enterprise_and_agol_profiles
class TestHostingServerProperty(unittest.TestCase):
    @default_timeout
    def test_hosting_servers(self):
        """tests if a list of hosting servers is returns"""
        gis = self.gis
        assert isinstance(gis.hosting_servers, list)
        if len(gis.hosting_servers) > 0:
            expected_type = agoserver.AGOLServicesDirectory if gis._is_agol else server.ServicesDirectory
            assert isinstance(gis.hosting_servers[0], expected_type)
        else:
            self.skipTest("No hosting servers found")

if __name__ == "__main__":
    unittest.main()

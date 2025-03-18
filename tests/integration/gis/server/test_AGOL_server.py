import unittest

from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging
from integration.config import get_resource_path

from arcgis.gis import agoserver, server

enable_verbose_logging()


@profiles.admin_agol
@integration_test
class TestAgolServicesDirectory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_get_service_directories(self):
        gis = self.gis
        assert isinstance(gis.hosting_servers, list)
        assert len(gis.hosting_servers) > 1
        for server in gis.hosting_servers:
            assert isinstance(server, agoserver.AGOLServicesDirectory)

    def test_list_folders(self):
        gis = self.gis
        for server in gis.hosting_servers:
            self.assertFalse(server.folders, "Folders should be empty")

    def test_service_directory_properties(self):
        """tests the AGO Server Properties"""
        gis = self.gis
        for server in gis.hosting_servers:
            assert "services" in server.properties
            assert "currentVersion" in server.properties
            assert len(server.properties.services) > 0

    # def test_service_directory_services(self):
    # gis = self.gis
    # for server in gis.hosting_servers:
    # assert isinstance(server.services, list)
    # assert len(server.services) > 0


# @profiles.admin_agol
# @integration_test
# class TestAGOLAdminManager(unittest.TestCase):
# """Tests that the Manager returns the proper things"""

# def test_gis_admin_servers(self):
# gis = self.gis
# assert isinstance(gis.admin.servers, agoserver.AGOLServersManager)
# assert gis.admin.servers.properties
# assert gis.admin.servers.tile_server
# assert gis.admin.servers.feature_server
# for ts in gis.admin.servers.tile_server:
# assert ts.is_tile_server in [True, False]
# for fs in gis.admin.servers.feature_server:
# assert fs.is_tile_server in [True, False]


# @profiles.admin_agol
# @integration_test
# class TestAGOLAdminServerTileManager(unittest.TestCase):
# """Tests that ensure the Feature Server Admin Functionality Works"""

# def test_single_admin_servers(self):
# gis = self.gis
# assert gis.admin.servers.feature_server
# assert isinstance(
# gis.admin.servers.tile_server[0], agoserver.AGOLServerManager
# )

# def test_services(self):
# gis = self.gis
# sm = gis.admin.servers.tile_server[0]
# assert sm.services

# def test_get(self):
# gis = self.gis
# sm = gis.admin.servers.tile_server[0]
# if len(sm.properties["services"]) > 0:
# name = sm.properties["services"][0]
# assert sm.get(sm.properties["services"][0]["name"])

# def test_status(self):
# gis = self.gis
# sm = gis.admin.servers.tile_server[0]
# if len(sm.properties["services"]) > 0:
# name = sm.properties["services"][0]
# assert sm.status(sm.properties["services"][0]["name"])

# def test_is_tile_service(self):
# gis = self.gis
# sm = gis.admin.servers.tile_server[0]
# assert sm.is_tile_server in [True, False]


# @profiles.admin_agol
# @integration_test
# class TestAGOLAdminServerFeatureManager(unittest.TestCase):
# """Tests that ensure the Feature Server Admin Functionality Works"""

# def test_single_admin_servers(self):
# gis = self.gis
# assert gis.admin.servers.feature_server
# assert isinstance(
# gis.admin.servers.feature_server[0], agoserver.AGOLServerManager
# )

# def test_services(self):
# gis = self.gis
# sm = gis.admin.servers.feature_server[0]
# assert sm.services

# def test_get(self):
# gis = self.gis
# sm = gis.admin.servers.feature_server[0]
# if len(sm.properties["services"]) > 0:
# name = sm.properties["services"][0]
# assert sm.get(name["adminServiceInfo"]["name"])

# def test_status(self):
# gis = self.gis
# sm = gis.admin.servers.feature_server[0]
# if len(sm.properties["services"]) > 0:
# name = sm.properties["services"][0]
# assert sm.status(name["adminServiceInfo"]["name"])


# @profiles.admin_enterprise_and_agol
# @integration_test
# class TestHostingServerProperty(unittest.TestCase):
# def test_hosting_servers(self):
# """tests if a list of hosting servers is returns"""
# gis = self.gis
# assert isinstance(gis.hosting_servers, list)
# if len(gis.hosting_servers) > 0:
# expected_type = (
# agoserver.AGOLServicesDirectory
# if gis._is_agol
# else server.ServicesDirectory
# )
# assert isinstance(gis.hosting_servers[0], expected_type)
# else:
# self.skipTest("No hosting servers found")

if __name__ == "__main__":
    unittest.main()

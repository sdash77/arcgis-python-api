"""
Tests Related to Server API Frame
"""
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import unittest
import pandas as pd
import os, shutil, arcpy
from arcgis.server import Server, Service
from arcgis import server as arcgisserver
URLS = [
    "http://sampleserver1.arcgisonline.com/ArcGIS/rest/services", # 10.1
    "http://sampleserver2.arcgisonline.com/ArcGIS/rest/services", # 9.31
    "http://sampleserver3.arcgisonline.com/ArcGIS/rest/services", # 10.05
    "http://sampleserver4.arcgisonline.com/ArcGIS/rest/services", # 10.02
    "https://sampleserver6.arcgisonline.com/arcgis/rest", # 10.41
    "http://acpythondev.esri.com/arcgis/rest" # 10.5
]
import os
import arcgis
from arcgis.server import Server
from arcgis.gis import GIS
from arcgis import SpatialDataFrame
from arcgis.server import Service
from arcgis.data.geodataset import from_layer, to_featureclass, to_sqlite, from_featureclass
############################################################################
#@unittest.SkipTest
class ServerAGOLTest(unittest.TestCase):
    """test the AGOL Server functionality"""
    def setUp(self):
        self._gis = GIS('https://devext.arcgis.com', 'geodev', '12345fish')
    def test_portal_agol(self):
        from arcgis.gis import GIS
        self.assertTrue(len(self._gis.servers)>0)
    def test_all_agol_server(self):
        from arcgis.server._view import Catalog
        res = []
        for server in self._gis.servers:
            isinstance(server, Server)
            res.append(isinstance(server.catalog, Catalog))
        self.assertTrue(all(res))
############################################################################
#@unittest.SkipTest
class ServerPortalTest(unittest.TestCase):
    """tests the connection to arcgis server object from portal"""
    def setUp(self):
        self._gis = GIS('https://dev003246.esri.com/portal', 'andrew', 'password1')
    def test_portal_105(self):
        from arcgis.gis import GIS
        gis = GIS('https://dev003246.esri.com/portal', 'andrew', 'password1')
        self.assertTrue(len(gis.servers)>0)
    def test_all_agol_server(self):
        from arcgis.server._view import Catalog
        res = []
        for server in self._gis.servers:
            isinstance(server, Server)
            server.catalog
            res.append(isinstance(server.catalog, Catalog))
        self.assertTrue(all(res))
    def test_services(self):
        from arcgis.server._view import Catalog
        res = []
        server = self._gis.servers[0]
        isinstance(server, Server)
        server.services
        for service in server.services:
            res.append(service is not None)
        self.assertTrue(all(res))
############################################################################
#@unittest.SkipTest
class ServerCatalogTests(unittest.TestCase):
    """
    test server login
    """
    #----------------------------------------------------------------------
    def setUp(self):
        self._username = "arcgis_python_api"
        self._password = "password1"
    #----------------------------------------------------------------------
    #@unittest.SkipTest
    def test_931_catalog(self):
        """catalog 931"""
        url_931 = URLS[1]
        server = Server(url=url_931)
        self.assertIsInstance(server, Server)
    #----------------------------------------------------------------------
    def test_101_catalog(self):
        """catalog 931"""
        url_101 = URLS[0]
        server = Server(url=url_101)
        self.assertIsInstance(server, Server)
    #----------------------------------------------------------------------
    def test_1005_catalog(self):
        """catalog 931"""
        url_1005 = URLS[2]
        server = Server(url=url_1005)
        self.assertIsInstance(server, Server)
    #----------------------------------------------------------------------
    def test_1002_catalog(self):
        """catalog 931"""
        url_1002 = URLS[3]
        server = Server(url=url_1002)
        self.assertIsInstance(server, Server)
    #----------------------------------------------------------------------
    def test_1041_catalog(self):
        """catalog 931"""
        url_1041 = URLS[4]
        server = Server(url=url_1041)
        self.assertIsInstance(server, Server)
    #----------------------------------------------------------------------
    def test_105_catalog(self):
        """catalog 931"""
        url_105 = URLS[5]
        server = Server(url=url_105)
        self.assertIsInstance(server, Server)
    #----------------------------------------------------------------------
    def test_105_catalog_token_login(self):
        """catalog 931"""
        url_105 = URLS[5]

        server = Server(url=url_105,
                        username=self._username,
                        password=self._password,
                        tokenurl="http://acpythondev.esri.com/arcgis/admin/generateToken")
        content = server.catalog
        idx = -1
        for f in content.folders:
            if f.lower() == 'system':
                idx = content.folders.index(f)
        content.folder = content.folders[idx]
        if idx == -1:
            self.assertGreater(idx, -1, 'Login failed for local server')
        self.assertIsInstance(server, Server)
        self.assertGreaterEqual(len(content.services), 1)
    #----------------------------------------------------------------------
    def test_105_catalog_ANON(self):
        """catalog 931"""
        url_105 = URLS[5]
        server = Server(url=url_105)
        self.assertIsInstance(server, Server)
############################################################################
#@unittest.SkipTest
class ServerPropertyTest(unittest.TestCase):
    """
    test server login & properties on class
    """
    #----------------------------------------------------------------------
    def setUp(self):
        self._username = "arcgis_python_api"
        self._password = "password1"
    #----------------------------------------------------------------------
    def test_connection(self):
        """catalog 10.5 connection"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                        username=self._username,
                        password=self._password)
        self.assertIsInstance(server.connection, arcgisserver._common.ServerConnection)
    #----------------------------------------------------------------------
    def test_content(self):
        """catalog 10.5 content"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                        username=self._username,
                        password=self._password)

        self.assertIsInstance(server.catalog,
                              arcgisserver._view.Catalog)
    def test_data(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        self.assertIsInstance(server.data,
                              arcgisserver.admin._data.Data)
    def test_data_store(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.datastore
        self.assertIsInstance(server.datastore,
                              arcgisserver.admin._data.Data)
    def test_info(self):
        """catalog 10.5 info"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.info
        self.assertIsInstance(ds,
                              arcgisserver.admin._info.Info)
    def test_kml(self):
        """catalog 10.5 kml"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.kml
        self.assertIsInstance(ds,
                              arcgisserver.admin._kml.KML)
    def test_me(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        from arcgis.server._server import User
        ds = server.me
        self.assertIsInstance(ds,
                              (str, User))
    def test_log(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.logs
        self.assertIsInstance(ds,
                              arcgisserver.admin._logs.Log)
    def test_services(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.services
        self.assertIsInstance(ds,
                              arcgisserver.admin._services.ServiceManager)
    def test_usage(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.usage
        self.assertIsInstance(ds,
                              arcgisserver.admin._usagereports.UsageReports)
    def test_users(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.users
        self.assertIsInstance(ds,
                              arcgisserver._server.UserManager)
############################################################################
#@unittest.SkipTest
class catalog_servermanager_test(unittest.TestCase):
    """
    test server catalog view for a server
    """
    #----------------------------------------------------------------------
    def setUp(self):
        self._username = "arcgis_python_api"
        self._password = "password1"
        url_105 = URLS[5]
        self._server_auth = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        self._server_noauth = Server(url=URLS[0])
    #----------------------------------------------------------------------
    def test_content_auth(self):
        """test the functions that can be created"""
        content = self._server_auth.catalog
        self.assertIsInstance(content, arcgisserver._view.catalog.Catalog)
    def test_location_auth(self):
        location = self._server_auth.catalog.location
        self.assertIsInstance(location, str)
    def test_current_version(self):
        c = self._server_auth.catalog.current_version
        self.assertIsInstance(c, (str, float, int))
    def test_user_auth(self):
        user = self._server_auth.catalog.user
        self.assertEqual(user['user']['username'], self._username)
    def test_services_auth(self):
        services = self._server_auth.catalog.services
        self.assertIsInstance(services, (list, tuple))
    def test_folders_auth(self):
        folders = self._server_auth.catalog.folders
        self.assertIsInstance(folders, (list, tuple))
    def test_folder_get_auth(self):
        folder = self._server_auth.catalog.folder
        self.assertEqual(folder.lower(), 'root')
    def test_folder_set_auth(self):
        if len(self._server_auth.catalog.folders) > 1:
            self._server_auth.catalog.folder = \
                self._server_auth.catalog.folders[1]
            self.assertEqual(self._server_auth.catalog.folder,
                             self._server_auth.catalog.folders[1])

    #--- Begin No Anonymous Tests -----------------------------------------
    def test_content_no_auth(self):
        """"""
        content = self._server_noauth.catalog
        self.assertIsInstance(content, arcgisserver._view.catalog.Catalog)
    def test_location_noauth(self):
        location = self._server_noauth.catalog.location
        self.assertIsInstance(location, str)
    def test_services_noauth(self):
        services = self._server_noauth.catalog.services
        self.assertIsInstance(services, (list, tuple))
    def test_folders_noauth(self):
        folders = self._server_noauth.catalog.folders
        self.assertIsInstance(folders, (list, tuple))
    def test_folder_get_noauth(self):
        folder = self._server_noauth.catalog.folder
        self.assertEqual(folder.lower(), 'root')
    def test_folder_set_noauth(self):
        if len(self._server_noauth.catalog.folders) > 1:
            self._server_auth.catalog.folder = self._server_auth.catalog.folders[1]
            self.assertEqual(self._server_auth.catalog.folder,
                             self._server_auth.catalog.folders[1])
############################################################################
#@unittest.SkipTest
class catalog_info_test(unittest.TestCase):
    """
    test server catalog view for a server
    """
    #----------------------------------------------------------------------
    def setUp(self):
        self._username = "arcgis_python_api"
        self._password = "password1"
        url_105 = URLS[5]
        self._server_auth = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        self._server_noauth = Server(url=URLS[0])
    #----- No Auth Test ---------------------------------------------------
    def test_info_noauth(self):
        info = self._server_noauth.info
        self.assertIs(info, None)
    #-------- Auth Test ---------------------------------------------------
    def test_info_auth(self):
        info = self._server_auth.info
        self.assertIsInstance(info, arcgisserver.admin._info.Info)
    def test_info_auth_timezones(self):
        info = self._server_auth.info
        self.assertIsInstance(info.available_time_zones(), dict)
############################################################################
#@unittest.SkipTest
class server_logs_test(unittest.TestCase):
    """
    test server catalog view for a server
    """
    #----------------------------------------------------------------------
    def setUp(self):
        self._username = "arcgis_python_api"
        self._password = "password1"
        url_105 = URLS[5]
        self._server_auth = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        self._server_noauth = Server(url=URLS[0])
    #----- No Auth Test ---------------------------------------------------
    def test_logs_noauth(self):
        info = self._server_noauth.logs
        self.assertIs(info, None)
    #-------- Auth Test ---------------------------------------------------
    def test_logs_auth(self):
        logs = self._server_auth.logs
        self.assertIsInstance(logs,
                              arcgisserver.admin._logs.Log)
    def test_query_logs(self):
        logs = self._server_auth.logs
        results = logs.query()
        self.assertIsInstance(results, dict)
############################################################################
#@unittest.SkipTest
class server_machines_test(unittest.TestCase):
    """
    test server machines module
    """
    #----------------------------------------------------------------------
    def setUp(self):
        url_105 = URLS[5]
        self._username = "arcgis_python_api"
        self._password = "password1"
        self._server_auth = Server(url=url_105,
                            username=self._username,
                            password=self._password)
    #-------- Auth Test ---------------------------------------------------
    def test_machines_auth(self):

        machines = self._server_auth._sm.machines
        isinstance(machines, arcgisserver.admin._machines.Machines)
        self.assertIsInstance(machines,
                              arcgisserver.admin._machines.Machines)
    def test_machines(self):
        machines = self._server_auth._sm.machines
        isinstance(machines, arcgisserver.admin._machines.Machines)
        self.assertIsInstance(machines.machines, (list, tuple))
    def test_get_machine(self):
        machines = self._server_auth._sm.machines
        isinstance(machines, arcgisserver.admin._machines.Machines)
        self.assertIsInstance(machines.getMachine(machineName=machines.machines[0].machineName),
                              arcgisserver.admin._machines.Machine)
############################################################################
#@unittest.SkipTest
class server_usagereports_test(unittest.TestCase):
    """
    test server usage module
    """
    #----------------------------------------------------------------------
    def setUp(self):
        url_105 = URLS[5]
        self._username = "arcgis_python_api"
        self._password = "password1"
        self._server_auth = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        self.usagereports = self._server_auth.usage
    #-------- Auth Test ---------------------------------------------------
    def test_reports(self):
        isinstance(self.usagereports, arcgisserver.admin._usagereports.UsageReports)
        self.assertIsInstance(self.usagereports.reports, (list, tuple))
    def test_metrics(self):
        self.assertIsNotNone(self.usagereports.metrics)
    def test_usage_settings(self):
        self.assertIsNotNone(self.usagereports.usage_settings)
    def test_report(self):
        report = self.usagereports.reports[0]
        self.assertIsInstance(report, arcgisserver.admin._usagereports.UsageReport)
    def test_report_query(self):
        report = self.usagereports.reports[0]
        isinstance(report, arcgisserver.admin._usagereports.UsageReport)
        res = report.query()
        self.assertIsInstance(res, dict)
############################################################################
#@unittest.SkipTest
class server_userandusers_test(unittest.TestCase):
    """
    test server usage module
    """
    #----------------------------------------------------------------------
    def setUp(self):
        url_105 = URLS[5]
        self._username = "arcgis_python_api"
        self._password = "password1"
        self._server_auth = Server(url=url_105,
                            username=self._username,
                            password=self._password)
        self.users = self._server_auth.users

    #-------- Auth Test ---------------------------------------------------
    def test_users(self):
        from arcgis.server._server import UserManager, User
        self.assertIsInstance(self.users, UserManager)
        isinstance(self.users, UserManager)
    def test_create_user(self):
        from arcgis.server._server import UserManager, User
        if len(self.users.search("BobSmith1")) > 0:
            self.users.search("BobSmith1")[0].delete()
        user = self.users.create(username="BobSmith1", password="lovetheapi1",
                          firstname="B", lastname="d", email="d@esri.com", description="account")

        self.assertIsInstance(user, User)
    def test_get(self):
        from arcgis.server._server import UserManager, User
        isinstance(self.users, UserManager)
        user = self.users.get(username="BobSmith1")
        self.assertIsInstance(user, (list, User))
    def test_me(self):
        from arcgis.server._server import UserManager, User
        self.assertIsInstance(self.users.me, User)
    def test_search(self):
        from arcgis.server._server import UserManager, User
        self.assertIsInstance(self.users.search(username="Bob"), list)
    def test_roles(self):
        from arcgis.server._server import UserManager, User, RoleManager
        roles = self.users.roles
        self.assertIsInstance(roles, RoleManager)

    def test_roles_all(self):
        from arcgis.server._server import UserManager, User, RoleManager, Role
        roles = self.users.roles
        isinstance(roles, RoleManager)
        theroles = roles.all()
        self.assertIsInstance(theroles, list)
    def test_roles_get_role(self):
        from arcgis.server._server import UserManager, User, RoleManager, Role
        roles = self.users.roles
        isinstance(roles, RoleManager)
        role = roles.get_role(role_id='admin')
        self.assertIsInstance(role, (list, Role))
    def test_role_create(self):
        from arcgis.server._server import UserManager, User, RoleManager, Role
        roles = self.users.roles
        isinstance(roles, RoleManager)
        if len(roles.get_role(role_id='role1')) == 1:
            roles.get_role(role_id='role1')[0].delete()
        role = roles.create(name='role1', description='role description')
        self.assertTrue(role['status'] == 'success')
    def test_role_update(self):
        from arcgis.server._server import UserManager, User, RoleManager, Role
        roles = self.users.roles
        isinstance(roles, RoleManager)
        role = roles.get_role(role_id='role1')[0]
        isinstance(role, Role)

        self.assertIsInstance(role.update(description="New Description"), (dict, Role))
    def test_set_privileges(self):
        from arcgis.server._server import UserManager, User, RoleManager, Role
        roles = self.users.roles
        isinstance(roles, RoleManager)
        role = roles.get_role(role_id='role1')[0]
        isinstance(role, Role)
        self.assertIsInstance(role.set_privileges("publish"), (dict, Role))
    #----------------------------------------------------------------------
    def test_user(self):
        from arcgis.server._server import UserManager, User
        user = self.users.search(username="BobSmith1")[0]
        self.assertIsInstance(user, (dict, User))
    #----------------------------------------------------------------------
    def test_user_update(self):
        from arcgis.server._server import UserManager, User
        user = self.users.search(username="BobSmith1")[0]
        isinstance(user, User)
        res = user.update(password="pw12356", full_name="Jane Doe", description="description new", email=None)
        self.assertTrue(res['status'] == 'success')
    def test_user_assign_role(self):
        from arcgis.server._server import UserManager, User, Role, RoleManager
        roles = self.users.roles
        user = self.users.search(username="BobSmith1")[0]
        isinstance(user, User)
        role = roles.get_role(role_id='role1')[0]
        res = user.add_role(role.rolename)
        self.assertTrue(res['status'] == 'success')


#--------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()


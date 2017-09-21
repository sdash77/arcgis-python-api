"""
Tests Related to Server API Frame
"""
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import unittest
import pandas as pd
import os, shutil
try:
    import arcpy
    HAS_ARCPY = True
except:
    HAS_ARCPY = False
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
from arcgis.gis import GIS
from arcgis.gis.server import  ServicesDirectory
from arcgis.gis.server import ServerManager
from arcgis.gis.server import Server

from arcgis.gis.server.admin._clusters import Cluster, ClusterProtocol, Clusters
from arcgis.gis.server.admin._data import Datastore, DataStoreManager
from arcgis.gis.server.admin._info import Info
from arcgis.gis.server.admin._kml import KML
from arcgis.gis.server.admin._logs import LogManager
from arcgis.gis.server.admin._machines import Machine, MachineManager
from arcgis.gis.server.admin._mode import Mode
from arcgis.gis.server.admin._security import Role, RoleManager, Security, User, UserManager
from arcgis.gis.server.admin._services import Extension, Service, ServiceManager
from arcgis.gis.server.admin._uploads import Uploads
from arcgis.gis.server.admin._usagereports import Report, ReportManager
#############################################################################
AGOL_URL = None
AGOL_USERNAME = None
AGOL_PASSWORD = None

if AGOL_USERNAME and AGOL_PASSWORD:
    #@unittest.SkipTest
    class ServerAGOLTest(unittest.TestCase):
        """test the AGOL Server functionality"""
        def setUp(self):
            self._gis = GIS(url=AGOL_URL,
                            username=AGOL_USERNAME,
                            password=AGOL_PASSWORD)
        #@unittest.SkipTest
        def test_reports(self):
            res = []
            urls = self._gis._con.get(path="%s/portals/%s/urls" % (self._gis._portal.resturl,
                                                                   self._gis.properties.id),
                                      params={'f': 'json'})
            url = ["%s://%s/%s/arcgis/rest/services" % ("https", urls['urls']['features']['https'][0],
                                               self._gis.properties.id)]
            for server in url:
                c =  ServicesDirectory(url=server, portal_connection=self._gis, is_agol=True)
                break
            html = c.report()
            res.append(isinstance(html, str))
            df = c.report(as_html=False)
            res.append(isinstance(df, pd.DataFrame))
            self.assertTrue(all(res))
        #@unittest.SkipTest
        def test_get_found(self):
            from arcgis.features import FeatureLayerCollection
            res = []
            urls = self._gis._con.get(path="%s/portals/%s/urls" % (self._gis._portal.resturl,
                                                                   self._gis.properties.id),
                                      params={'f': 'json'})
            url = ["%s://%s/%s/arcgis/rest/services" % ("https", urls['urls']['features']['https'][0],
                                               self._gis.properties.id)]
            for server in url:
                c =  ServicesDirectory(url=server, portal_connection=self._gis, is_agol=True)
                break
            s = c.get(name="06_14_2016__Info_Lookup_Link")
            if s is None:
                s = c.get(name="02_2016__Gas_Transmission_Facility_Layers_PD")
            self.assertIsInstance(s, FeatureLayerCollection)
        #@unittest.SkipTest
        def test_get_not_found(self):
            from arcgis.features import FeatureLayerCollection
            res = []
            urls = self._gis._con.get(path="%s/portals/%s/urls" % (self._gis._portal.resturl, self._gis.properties.id), params={'f': 'json'})
            url = ["%s://%s/%s/arcgis/rest/services" % ("https", urls['urls']['features']['https'][0], self._gis.properties.id)]
            for server in url:
                c =  ServicesDirectory(url=server, portal_connection=self._gis, is_agol=True)
                break
            s = c.get(name="IDONTEXIST")
            self.assertIsNone(s)
        #@unittest.SkipTest
        def test_agol_server(self):
            res = []
            urls = self._gis._con.get(path="%s/portals/%s/urls" % (self._gis._portal.resturl, self._gis.properties.id), params={'f': 'json'})
            url = ["%s://%s/%s/arcgis/rest/services" % ("https", urls['urls']['features']['https'][0], self._gis.properties.id)]
            for server in url:
                res.append(isinstance( ServicesDirectory(url=server, portal_connection=self._gis, is_agol=True), ServicesDirectory))
            self.assertTrue(all(res))

#############################################################################
#@unittest.SkipTest
class ServerPortalTest(unittest.TestCase):
    """tests the connection to arcgis server object from portal"""
    def setUp(self):
        self._gis = GIS('https://dev003246.esri.com/portal', 'andrew', 'password1')
    def test_server_portal_not_gis(self):
        """tests creating a Server object"""
        from arcgis.gis.server import Server
        s = Server(url="https://dev003247.esri.com:6443/arcgis", gis=None,
               username="admin", password="esri.agp",
               tokenurl="https://dev003247.esri.com:6443/arcgis/admin/generateToken")
        self.assertIsInstance(s, Server)
    #@unittest.SkipTest
    def test_portal_get_server_manager(self):
        """tests getting server manager object"""
        from arcgis.gis import GIS
        from arcgis.gis.server import ServerManager, Server
        gis = self._gis
        self.assertIsInstance(gis.admin.servers, ServerManager)
    #@unittest.SkipTest
    def test_list_servers(self):
        """tests the server listing function on server manager"""
        sm = self._gis.admin.servers

        self.assertTrue(all(sm.list()))
    #@unittest.SkipTest
    def test_validate(self):
        """tests validate servers"""
        sm = self._gis.admin.servers
        self.assertIsInstance(sm.validate(), (bool, int))
############################################################################
#@unittest.SkipTest
class ServerCatalogCreationTests(unittest.TestCase):
    """
    test server login
    """
    #----------------------------------------------------------------------
    def setUp(self):
        self._username = "arcgis_python_api"
        self._password = "password1"
    #----------------------------------------------------------------------
    def test_931_catalog(self):
        """catalog 931"""
        url_931 = URLS[1]
        server =  ServicesDirectory(url=url_931)
        self.assertIsInstance(server,  ServicesDirectory)
    #----------------------------------------------------------------------
    def test_101_catalog(self):
        """catalog 10.1 Anonymous"""
        url_101 = URLS[0]
        server =  ServicesDirectory(url=url_101)
        self.assertIsInstance(server,  ServicesDirectory)
    #----------------------------------------------------------------------
    def test_1005_catalog(self):
        """catalog 10.05 Anonymous """
        url_1005 = URLS[2]
        server =  ServicesDirectory(url=url_1005)
        self.assertIsInstance(server,  ServicesDirectory)
    #----------------------------------------------------------------------
    def test_1002_catalog(self):
        """catalog 10.02 Anonymous"""
        url_1002 = URLS[3]
        server =  ServicesDirectory(url=url_1002)
        self.assertIsInstance(server,  ServicesDirectory)
    #----------------------------------------------------------------------
    def test_1041_catalog(self):
        """catalog 10.41"""
        url_1041 = URLS[4]
        server =  ServicesDirectory(url=url_1041)
        self.assertIsInstance(server,  ServicesDirectory)
    #----------------------------------------------------------------------
    def test_105_catalog(self):
        """catalog 10.5"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105)
        self.assertIsInstance(server,  ServicesDirectory)
    #----------------------------------------------------------------------
    def test_105_catalog_token_login(self):
        """catalog 10.5"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                        username=self._username,
                        password=self._password,
                        tokenurl="http://acpythondev.esri.com/arcgis/admin/generateToken")
        self.assertIsInstance(server,  ServicesDirectory)
        self.assertGreaterEqual(len(server.list()), 1)
    #---------------------------------------------------------------------
    def test_105_catalog_admin(self):
        """test getting the admin object to server from direct connection"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                             username=self._username,
                            password=self._password,
                            tokenurl="http://acpythondev.esri.com/arcgis/admin/generateToken")
        self.assertIsInstance(server.admin, Server)
    #----------------------------------------------------------------------
    def test_105_catalog_ANON(self):
        """catalog 10.5 Anonymous"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105)
        self.assertIsInstance(server,  ServicesDirectory)
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
    def test_content(self):
        """catalog 10.5 content"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                        username=self._username,
                        password=self._password).admin

        self.assertIsInstance(server,
                              Server)
    def test_data_storemanager(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.admin.datastores
        self.assertIsInstance(ds,
                              DataStoreManager)
    def test_info(self):
        """catalog 10.5 info"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.admin._info
        self.assertIsInstance(ds,
                              Info)
    def test_kml(self):
        """catalog 10.5 kml"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.admin._kml
        self.assertIsInstance(ds,
                              KML)
    def test_log(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.admin.logs
        self.assertIsInstance(ds,
                              LogManager)
    def test_services(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.admin.services
        self.assertIsInstance(ds,
                              ServiceManager)
    def test_usage(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password).admin
        ds = server.usage
        self.assertIsInstance(ds,
                              ReportManager)
    def test_users(self):
        """catalog 10.5 data"""
        url_105 = URLS[5]
        server =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password)
        ds = server.admin.users
        self.assertIsInstance(ds,
                              UserManager)
############################################################################

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
        self._server_auth =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password).admin
        self._server_noauth =  ServicesDirectory(url=URLS[0])
    #----- No Auth Test ---------------------------------------------------
    def test_info_noauth(self):
        if hasattr(self._server_noauth, 'admin'):
            self.assertTrue(False)
        self.assertTrue(True)
    #-------- Auth Test ---------------------------------------------------
    #@unittest.SkipTest
    def test_info_auth(self):
        info = self._server_auth._info
        self.assertIsInstance(info, Info)
    #@unittest.SkipTest
    def test_info_auth_timezones(self):
        info = self._server_auth._info
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
        self._server_auth =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password).admin
        self._server_noauth =  ServicesDirectory(url=URLS[0])
    #-------- Auth Test ---------------------------------------------------
    def test_logs_auth(self):
        logs = self._server_auth.logs
        self.assertIsInstance(logs,
                              LogManager)
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
        self._server_auth =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password).admin
    #-------- Auth Test ---------------------------------------------------
    def test_machines_auth(self):

        machines = self._server_auth.machines
        isinstance(machines, MachineManager)
        self.assertIsInstance(machines,
                              MachineManager)
    def test_machines(self):
        machines = self._server_auth.machines
        isinstance(machines, MachineManager)
        self.assertIsInstance(machines.list(), (list, tuple))
    def test_get_machine(self):
        machines = self._server_auth.machines
        isinstance(machines, MachineManager)
        self.assertIsInstance(machines.get(machine_name=machines.list()[0].properties.machineName),
                              Machine)
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
        self._server_auth =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password).admin
        self.usage = self._server_auth.usage
    #-------- Auth Test ---------------------------------------------------
    def test_reports(self):
        isinstance(self.usage, ReportManager)
        self.assertIsInstance(self.usage.list(), (list, tuple))
    def test_metrics(self):
        self.assertIsNotNone(self.usage.properties.metrics)
    def test_usage_settings(self):
        self.assertIsNotNone(self.usage.settings)
    def test_report(self):
        report = self.usage.list()[0]
        self.assertIsInstance(report, Report)
    def test_report_query(self):
        report = self.usage.list()[0]
        isinstance(report, Report)
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
        self._server_auth =  ServicesDirectory(url=url_105,
                            username=self._username,
                            password=self._password).admin
        self.users = self._server_auth.users

    #-------- Auth Test ---------------------------------------------------
    #@unittest.SkipTest
    def test_users(self):

        self.assertIsInstance(self.users, UserManager)
        isinstance(self.users, UserManager)
    #@unittest.SkipTest
    def test_create_user(self):

        if len(self.users.search("BobSmith1")) > 0:
            self.users.search("BobSmith1")[0].delete()
        user = self.users.create(username="BobSmith1", password="lovetheapi1",
                          fullname="b d", email="d@esri.com", description="account")

        self.assertIsInstance(user, User)
    #@unittest.SkipTest
    def test_get(self):

        isinstance(self.users, UserManager)
        user = self.users.get(username="arcgis_python_api")
        self.assertIsInstance(user, (list, User))
    #@unittest.SkipTest
    def test_me(self):

        self.assertIsInstance(self.users.me, User)
    #@unittest.SkipTest
    def test_search(self):
        self.assertIsInstance(self.users.search(username="Bob"), list)
    #@unittest.SkipTest
    def test_roles(self):
        roles = self.users.roles
        self.assertIsInstance(roles, RoleManager)
    #@unittest.SkipTest
    def test_roles_all(self):
        roles = self.users.roles
        isinstance(roles, RoleManager)
        theroles = roles.all()
        self.assertIsInstance(theroles, list)
    #@unittest.SkipTest
    def test_roles_get_role(self):

        roles = self.users.roles
        isinstance(roles, RoleManager)
        role = roles.get_role('admin')

        self.assertIsInstance(role, (list, Role))
    #@unittest.SkipTest
    def test_role_create(self):

        roles = self.users.roles
        isinstance(roles, RoleManager)
        if len(roles.get_role('role1')) == 1:
            roles.get_role('role1')[0].delete()
        role = roles.create(name='role1', description='role description')
        self.assertTrue(role)
    #@unittest.SkipTest
    def test_role_update(self):

        roles = self.users.roles
        isinstance(roles, RoleManager)
        role = roles.get_role('role1')[0]
        isinstance(role, Role)

        self.assertIsInstance(role.update(description="New Description"), (dict, Role, bool))
    #@unittest.SkipTest
    def test_set_privileges(self):

        roles = self.users.roles
        isinstance(roles, RoleManager)
        role = roles.get_role('role1')[0]
        isinstance(role, Role)
        self.assertIsInstance(role.set_privileges("publish"), (dict, Role, bool))
    #----------------------------------------------------------------------
    #@unittest.SkipTest
    def test_user(self):

        user = self.users.search(username="BobSmith1")[0]
        self.assertIsInstance(user, (dict, User))
    #----------------------------------------------------------------------
    #@unittest.SkipTest
    def test_user_update(self):

        user = self.users.search(username="BobSmith1")[0]
        isinstance(user, User)
        res = user.update(password="pw12356", full_name="Jane Doe", description="description new", email=None)
        self.assertTrue(res)
    #@unittest.SkipTest
    def test_user_assign_role(self):

        roles = self.users.roles
        user = self.users.search(username="BobSmith1")[0]
        isinstance(user, User)
        role = roles.get_role('role1')[0]
        res = user.add_role(role.rolename)
        self.assertTrue(res)


#--------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()


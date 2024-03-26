"""
Tests Related to Server API Frame
"""
import unittest
import pandas as pd
import os, shutil

unittest.TestLoader.sortTestMethodsUsing = None

try:
    import arcpy

    HAS_ARCPY = True
except:
    HAS_ARCPY = False
URLS = [
    "http://sampleserver1.arcgisonline.com/ArcGIS/rest/services",  # 10.1
    "http://sampleserver2.arcgisonline.com/ArcGIS/rest/services",  # 9.31
    "http://sampleserver3.arcgisonline.com/ArcGIS/rest/services",  # 10.05
    "http://sampleserver4.arcgisonline.com/ArcGIS/rest/services",  # 10.02
    "https://sampleserver6.arcgisonline.com/arcgis/rest",  # 10.41
    # "https://pythonapi.playground.esri.com/server/rest/",  # 10.91
    # "https://rextapilnxsvr01.esri.com/server/rest/services",  # 11.1
]
ENT_SETS = [
    {
        "url": "https://pythonapi.playground.esri.com/server/rest/",
        "portal": "https://pythonapi.playground.esri.com/portal",
        "username": "ServerTestAdmin",
        "password": "y0ugot$erved!",
        "server": "10.9.1 federated",
        "token": "https://pythonapi.playground.esri.com/portal/sharing/rest/generateToken",
    },
    {
        "url": "https://rextapilnxsvr01.esri.com/server/rest/services",
        "portal": "",
        "username": "siteadmin",
        "password": "esri.agp2",
        "server": "11.1 standalone",
        "token": "https://rextapilnxsvr01.esri.com/server/tokens/",
    },
]
ALT_SETS = [
    # requires built-in admin credentials for Esri public servers
    {
        "url": "https://rqawinbi01sv.ags.esri.com:6443/arcgis/rest/services",
        "portal": "https://rqawinbi01pt.ags.esri.com/gis/home/",
        "username": "",
        "password": "",
        "server": "11.1 federated built-in",
        "token": "https://rqawinbi01pt.ags.esri.com/gis/sharing/rest/generateToken",
    },
    # requires IWA authentication for Esri public servers
    {
        "url": "https://rqawiniwa02sv.ags.esri.com:6443/arcgis/rest/services",
        "portal": "https://rqawiniwa02pt.ags.esri.com/gis/home/",
        "username": "",  # use 'AVWORLD\\<username>'
        "password": "",
        "server": "11.1 federated IWA",
        "token": "https://rqawiniwa02pt.ags.esri.com/gis/sharing/rest/generateToken",
    },
    # dummy set to test things are failing properly
    {
        "url": "this shouldn't work",
        "portal": "duloc",
        "username": "donkey",
        "password": "shrek",
        "server": "lord farquaad",
        "token": "token? you're jokin!",
    },
]

# ENT_SETS.append(ALT_SETS[0])
# ENT_SETS.append(ALT_SETS[1])
# ENT_SETS = [ALT_SETS[2]]

import os
import arcgis
from arcgis.gis import GIS
from arcgis.gis.server import ServicesDirectory
from arcgis.gis.server import ServerManager
from arcgis.gis.server import Server

from arcgis.gis.server.admin._clusters import Cluster, ClusterProtocol, Clusters
from arcgis.gis.server.admin._data import Datastore, DataStoreManager
from arcgis.gis.server.admin._info import Info
from arcgis.gis.server.admin._kml import KML
from arcgis.gis.server.admin._logs import LogManager
from arcgis.gis.server.admin._machines import Machine, MachineManager
from arcgis.gis.server.admin._mode import Mode
from arcgis.gis.server.admin._security import (
    Role,
    RoleManager,
    Security,
    User,
    UserManager,
)
from arcgis.gis.server.admin._services import Extension, Service, ServiceManager
from arcgis.gis.server.admin._uploads import Uploads
from arcgis.gis.server.admin._usagereports import Report, ReportManager
from utils.decorators import integration_test

#############################################################################
AGOL_URL = None
AGOL_USERNAME = None
AGOL_PASSWORD = None

if AGOL_USERNAME and AGOL_PASSWORD:

    # @unittest.SkipTest
    @integration_test
    class ServerAGOLTest(unittest.TestCase):
        """test the AGOL Server functionality"""

        @classmethod
        def setUpClass(cls):
            cls._gis = GIS(
                url=AGOL_URL,
                username=AGOL_USERNAME,
                password=AGOL_PASSWORD,
                verify_cert=False,
            )

        # @unittest.SkipTest
        def test_reports(self):
            res = []
            urls = self._gis._con.get(
                path="%s/portals/%s/urls"
                % (self._gis._portal.resturl, self._gis.properties.id),
                params={"f": "json"},
            )
            url = [
                "%s://%s/%s/arcgis/rest/services"
                % (
                    "https",
                    urls["urls"]["features"]["https"][0],
                    self._gis.properties.id,
                )
            ]
            for server in url:
                c = ServicesDirectory(
                    url=server, portal_connection=self._gis, is_agol=True
                )
                break
            html = c.report()
            res.append(isinstance(html, str))
            df = c.report(as_html=False)
            res.append(isinstance(df, pd.DataFrame))
            self.assertTrue(all(res))

        # @unittest.SkipTest
        def test_get_found(self):
            from arcgis.features import FeatureLayerCollection

            res = []
            urls = self._gis._con.get(
                path="%s/portals/%s/urls"
                % (self._gis._portal.resturl, self._gis.properties.id),
                params={"f": "json"},
            )
            url = [
                "%s://%s/%s/arcgis/rest/services"
                % (
                    "https",
                    urls["urls"]["features"]["https"][0],
                    self._gis.properties.id,
                )
            ]
            for server in url:
                c = ServicesDirectory(
                    url=server, portal_connection=self._gis, is_agol=True
                )
                break
            s = c.get(name="06_14_2016__Info_Lookup_Link")
            if s is None:
                s = c.get(name="02_2016__Gas_Transmission_Facility_Layers_PD")
            if s:

                self.assertIsInstance(s, FeatureLayerCollection)

        # @unittest.SkipTest
        def test_get_not_found(self):
            from arcgis.features import FeatureLayerCollection

            res = []
            urls = self._gis._con.get(
                path="%s/portals/%s/urls"
                % (self._gis._portal.resturl, self._gis.properties.id),
                params={"f": "json"},
            )
            url = [
                "%s://%s/%s/arcgis/rest/services"
                % (
                    "https",
                    urls["urls"]["features"]["https"][0],
                    self._gis.properties.id,
                )
            ]
            for server in url:
                c = ServicesDirectory(
                    url=server, portal_connection=self._gis, is_agol=True
                )
                break
            s = c.get(name="IDONTEXIST")
            self.assertIsNone(s)

        # @unittest.SkipTest
        def test_agol_server(self):
            res = []
            urls = self._gis._con.get(
                path="%s/portals/%s/urls"
                % (self._gis._portal.resturl, self._gis.properties.id),
                params={"f": "json"},
            )
            url = [
                "%s://%s/%s/arcgis/rest/services"
                % (
                    "https",
                    urls["urls"]["features"]["https"][0],
                    self._gis.properties.id,
                )
            ]
            for server in url:
                res.append(
                    isinstance(
                        ServicesDirectory(
                            url=server, portal_connection=self._gis, is_agol=True
                        ),
                        ServicesDirectory,
                    )
                )
            self.assertTrue(all(res))


#############################################################################
# @unittest.SkipTest
@integration_test
class ServerPortalTest(unittest.TestCase):
    """tests the connection to arcgis server object from portal"""

    def test_server_portal_not_gis(self):
        """tests creating a Server object"""
        from arcgis.gis.server import Server

        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                s = Server(
                    url=ent["url"],
                    gis=None,
                    username=ent["username"],
                    password=ent["password"],
                    tokenurl=ent["token"],
                )
                self.assertIsInstance(s, Server)

    # @unittest.SkipTest
    def test_portal_get_server_manager(self):
        """tests getting server manager object"""
        from arcgis.gis import GIS
        from arcgis.gis.server import ServerManager, Server

        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                gis = GIS(
                    url=ent["portal"],
                    username=ent["username"],
                    password=ent["password"],
                )
                self.assertIsInstance(gis.admin.servers, ServerManager)

    # @unittest.SkipTest
    def test_list_servers(self):
        """tests the server listing function on server manager"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                gis = GIS(
                    url=ent["portal"],
                    username=ent["username"],
                    password=ent["password"],
                )
                sm = gis.admin.servers
                self.assertTrue(all(sm.list()))

    # @unittest.SkipTest
    def test_validate(self):
        """tests validate servers"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                gis = GIS(
                    url=ent["portal"],
                    username=ent["username"],
                    password=ent["password"],
                )
                sm = gis.admin.servers
                self.assertIsInstance(sm.validate(), (bool, int))


############################################################################
# @unittest.SkipTest
@integration_test
class ServerCatalogCreationTests(unittest.TestCase):
    """
    test server login
    """

    # ----------------------------------------------------------------------
    def test_931_catalog(self):
        """catalog 931"""
        url_931 = URLS[1]
        server = ServicesDirectory(url=url_931)
        assert server.properties
        self.assertIsInstance(server, ServicesDirectory)

    # ----------------------------------------------------------------------
    @unittest.skip("url broken")
    def test_101_catalog(self):
        """catalog 10.1 Anonymous"""
        url_101 = URLS[0]
        server = ServicesDirectory(url=url_101)
        assert server.properties
        self.assertIsInstance(server, ServicesDirectory)

    # ----------------------------------------------------------------------
    @unittest.skip("url broken")
    def test_1005_catalog(self):
        """catalog 10.05 Anonymous"""
        url_1005 = URLS[2]
        server = ServicesDirectory(url=url_1005)
        assert server.properties
        self.assertIsInstance(server, ServicesDirectory)

    # ----------------------------------------------------------------------
    def test_1041_catalog(self):
        """catalog 10.41"""
        url_1041 = URLS[4]
        server = ServicesDirectory(url=url_1041)
        assert server.properties
        self.assertIsInstance(server, ServicesDirectory)

    # ----------------------------------------------------------------------
    def test_ent_catalog_anon(self):
        """catalog of recent enterprise versions anonymous"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                ent_url = ent["url"]
                server = ServicesDirectory(url=ent_url)
                self.assertIsInstance(server, ServicesDirectory)

    # ----------------------------------------------------------------------
    def test_ent_catalog_token_login(self):
        """catalog of recent enterprise versions with token"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"],
                    username=ent["username"],
                    password=ent["password"],
                    tokenurl=ent["token"],
                )
                self.assertIsInstance(server, ServicesDirectory)

    # ---------------------------------------------------------------------
    def test_ent_catalog_admin(self):
        """test getting the admin object to server from direct connection"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"],
                    username=ent["username"],
                    password=ent["password"],
                    tokenurl=ent["token"],
                )
                self.assertIsInstance(server.admin, Server)


############################################################################
# @unittest.SkipTest
@integration_test
class ServerPropertyTest(unittest.TestCase):
    """
    test server login & properties on class
    """

    # ----------------------------------------------------------------------
    def test_content(self):
        """catalog enterprise content"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                # print(ent["username"])
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                ).admin
                self.assertIsInstance(server, Server)

    def test_data_storemanager(self):
        """catalog enterprise data"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                ds = server.admin.datastores
                self.assertIsInstance(ds, DataStoreManager)

    def test_info(self):
        """catalog enterprise info"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                ds = server.admin._info
                self.assertIsInstance(ds, Info)

    def test_kml(self):
        """catalog enterprise kml"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                ds = server.admin._kml
                self.assertIsInstance(ds, KML)

    def test_log(self):
        """catalog enterprise data"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                ds = server.admin.logs
                self.assertIsInstance(ds, LogManager)

    def test_services(self):
        """catalog enterprise data"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                ds = server.admin.services
                self.assertIsInstance(ds, ServiceManager)

    def test_usage(self):
        """catalog enterprise data"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                ).admin
                ds = server.usage
                self.assertIsInstance(ds, ReportManager)

    def test_users(self):
        """catalog enterprise data"""
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                ds = server.admin.users
                self.assertIsInstance(ds, UserManager)


############################################################################

############################################################################
# @unittest.SkipTest
@integration_test
class catalog_info_test(unittest.TestCase):
    """
    test server catalog view for a server
    """

    # ----- No Auth Test ---------------------------------------------------
    def test_info_noauth(self):
        if hasattr(ServicesDirectory(url=URLS[0]), "admin"):
            self.assertTrue(False)
        self.assertTrue(True)

    # -------- Auth Test ---------------------------------------------------
    # @unittest.SkipTest
    def test_info_auth(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                info = server.admin._info
                self.assertIsInstance(info, Info)

    # @unittest.SkipTest
    def test_info_auth_timezones(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                info = server.admin._info
                self.assertIsInstance(info.available_time_zones(), dict)


############################################################################
# @unittest.SkipTest
@integration_test
class server_logs_test(unittest.TestCase):
    """
    test server catalog view for a server
    """

    # -------- Auth Test ---------------------------------------------------
    def test_logs_auth(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                logs = server.admin.logs
                self.assertIsInstance(logs, LogManager)

    def test_query_logs(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                logs = server.admin.logs
                results = logs.query()
                self.assertIsInstance(results, dict)
                results2 = logs.query(max_records_return=5002)
                self.assertIsInstance(results2, dict)


############################################################################
# @unittest.SkipTest
@integration_test
class server_machines_test(unittest.TestCase):
    """
    test server machines module
    """

    # -------- Auth Test ---------------------------------------------------
    def test_machines_auth(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                machines = server.admin.machines
                isinstance(machines, MachineManager)
                self.assertIsInstance(machines, MachineManager)

    def test_machines(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                machines = server.admin.machines
                isinstance(machines, MachineManager)
                self.assertIsInstance(machines.list(), (list, tuple))

    def test_get_machine(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                machines = server.admin.machines
                isinstance(machines, MachineManager)
                self.assertIsInstance(
                    machines.get(
                        machine_name=machines.list()[0].properties.machineName
                    ),
                    Machine,
                )


############################################################################
# @unittest.SkipTest
@integration_test
class server_usagereports_test(unittest.TestCase):
    """
    test server usage module
    """

    # -------- Auth Test ---------------------------------------------------
    def test_reports(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                usage = server.admin.usage
                isinstance(usage, ReportManager)
                self.assertIsInstance(usage.list(), (list, tuple))

    def test_metrics(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                usage = server.admin.usage
                self.assertIsNotNone(usage.properties.metrics)

    def test_usage_settings(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                usage = server.admin.usage
                self.assertIsNotNone(usage.settings)

    def test_report(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                usage = server.admin.usage
                report = usage.list()[0]
                self.assertIsInstance(report, Report)

    def test_report_query(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                usage = server.admin.usage
                report = usage.list()[0]
                isinstance(report, Report)
                res = report.query()
                self.assertIsInstance(res, dict)


############################################################################
# @unittest.SkipTest
@integration_test
class server_userandusers_test(unittest.TestCase):
    """
    test server usage module
    """

    # -------- Auth Test ---------------------------------------------------
    # @unittest.SkipTest
    def test_users(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                self.assertIsInstance(users, UserManager)
                isinstance(users, UserManager)

    # @unittest.SkipTest
    def test_create_user(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users

                if len(users.search("PyAPIServerTest123")) > 0:
                    users.search("PyAPIServerTest123")[0].delete()
                user = users.create(
                    username="PyAPIServerTest123",
                    password="lovetheapi1",
                    fullname="b d",
                    email="d@esri.com",
                    description="account",
                )

                self.assertIsInstance(user, User)

    # @unittest.SkipTest
    def test_get(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                isinstance(users, UserManager)
                user = users.get(username="PyAPIServerTest123")
                self.assertIsInstance(user, (list, User))

    # @unittest.SkipTest
    def test_me(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                self.assertIsInstance(users.me, (str, User))

    # @unittest.SkipTest
    def test_search(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                self.assertIsInstance(users.search(username="Py"), list)

    # @unittest.SkipTest
    def test_roles(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                roles = users.roles
                self.assertIsInstance(roles, RoleManager)

    # @unittest.SkipTest
    def test_roles_all(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                roles = users.roles
                isinstance(roles, RoleManager)
                theroles = roles.all()
                self.assertIsInstance(theroles, list)

    # @unittest.SkipTest
    def test_roles_get_role(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                roles = users.roles
                isinstance(roles, RoleManager)
                role = roles.get_role("admin")
                self.assertIsInstance(role, (list, Role))

    # @unittest.SkipTest
    def test_role_create(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                roles = users.roles
                isinstance(roles, RoleManager)
                if len(roles.get_role("role1")) == 1:
                    roles.get_role("role1")[0].delete()
                role = roles.create(name="role1", description="role description")
                self.assertTrue(role)

    # @unittest.SkipTest
    def test_role_update(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                roles = users.roles
                isinstance(roles, RoleManager)
                role = roles.get_role("role1")[0]
                isinstance(role, Role)
                self.assertIsInstance(
                    role.update(description="New Description"), (dict, Role, bool)
                )

    # @unittest.SkipTest
    def test_set_privileges(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                roles = users.roles
                isinstance(roles, RoleManager)
                role = roles.get_role("role1")[0]
                isinstance(role, Role)
                self.assertIsInstance(
                    role.set_privileges("publish"), (dict, Role, bool)
                )

    # ----------------------------------------------------------------------
    # @unittest.SkipTest
    def test_user(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                user = users.search(username="PyAPIServerTest123")[0]
                self.assertIsInstance(user, (dict, User))

    # ----------------------------------------------------------------------
    # @unittest.SkipTest
    def test_user_update(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                user = users.search(username="PyAPIServerTest123")[0]
                isinstance(user, User)
                res = user.update(
                    password="pw12356",
                    full_name="Jane Doe",
                    description="description new",
                    email=None,
                )
                self.assertTrue(res)

    # @unittest.SkipTest
    def test_user_assign_role(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users
                roles = users.roles
                user = users.search(username="PyAPIServerTest123")[0]
                isinstance(user, User)
                role = roles.get_role("role1")[0]
                res = user.add_role(role.rolename)
                self.assertTrue(res)

    # --------------------------------------------------------------------------
    # @unittest.SkipTest
    def test_user_zdelete(self):
        for ent in ENT_SETS:
            with self.subTest(msg="enterprise " + ent["server"]):
                server = ServicesDirectory(
                    url=ent["url"], username=ent["username"], password=ent["password"]
                )
                users = server.admin.users

                if len(users.search("PyAPIServerTest123")) > 0:
                    resp = users.search("PyAPIServerTest123")[0].delete()
                    self.assertTrue(resp)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()

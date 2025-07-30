import unittest
import pandas as pd
import uuid

from arcgis.gis.server import ServicesDirectory
from arcgis.gis.server import ServerManager
from arcgis.gis.server import Server
from arcgis.gis.server.admin._data import Datastore, DataStoreManager
from arcgis.gis.server.admin._info import Info
from arcgis.gis.server.admin._kml import KML
from arcgis.gis.server.admin._logs import LogManager
from arcgis.gis.server.admin._machines import Machine, MachineManager
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
from arcgis.features import FeatureLayerCollection
from arcgis._impl.common._isd import InsensitiveDict
from utils.decorators import server_credentials, integration_test, profiles
from utils._logging import enable_verbose_logging
from integration.config import get_resource_path

enable_verbose_logging()


@profiles.agol
@integration_test
class TestServerAGOL(unittest.TestCase):
    """test the AGOL Server functionality"""

    def setUp(self):
        self.urls = self.gis._con.get(
            path="%s/portals/%s/urls"
            % (self.gis._portal.resturl, self.gis.properties.id),
            params={"f": "json"},
        )

        self.url = [
            "%s://%s/%s/arcgis/rest/services"
            % (
                "https",
                self.urls["urls"]["features"]["https"][0],
                self.gis.properties.id,
            )
        ]

        sd_list = []

        for service in self.url:
            sd = ServicesDirectory(
                url=service, portal_connection=self.gis, is_agol=True
            )
            assert isinstance(sd, ServicesDirectory)
            sd_list.append(sd)
            self.sd = sd_list[0]

    def test_reports(self):
        """tests getting html and dataframe reports from ServiceDirectory class"""
        html = self.sd.report()
        assert isinstance(html, str)

        df = self.sd.report(as_html=False)
        assert isinstance(df, pd.DataFrame)

    def test_get_exist_service(self):
        """tests getting existing service"""
        service = self.sd.get(name="NYCHotels")
        if not service:
            self.skipTest("Service does not exist.")
            assert isinstance(service, FeatureLayerCollection)

    def test_get_service_not_found(self):
        """tests getting non-existing service"""
        service = self.sd.get(name="IDONTEXIST")
        self.assertIsNone(service)


@profiles.admin_enterprise
@integration_test
class TestServerFederated(unittest.TestCase):
    """Tests arcgis server object (federated)"""

    def test_get_server_from_server_manager(self):
        """tests getting server object through gis.server.ServerManager"""

        sm = self.gis.admin.servers
        self.assertIsInstance(sm, ServerManager)

        server = sm.get(role="hosting_server")[0]
        self.assertIsInstance(server, Server)

    def test_get_server_from_server(self):
        """tests getting server object through gis.server.Server with gis param"""

        server = Server(
            url=self.gis._url.replace("/portal/", "/server/admin"), gis=self.gis
        )
        self.assertIsInstance(server, Server)

    def test_get_server_from_portal_connection(self):
        """tests getting server object through gis.server.Server with gis connection param"""

        server = Server(
            url=self.gis._url.replace("/portal/", "/server/admin"),
            portal_connection=self.gis,
        )
        self.assertIsInstance(server, Server)


@profiles.admin_enterprise
@integration_test
class TestServerManager(unittest.TestCase):
    """tests ServerManager class"""

    def test_server_manager(self):
        """tests getting server manager object"""
        self.assertIsInstance(self.gis.admin.servers, ServerManager)

    def test_list_servers(self):
        """tests listing servers"""
        sm = self.gis.admin.servers
        server_list = sm.list()
        self.assertIsInstance(server_list, list)
        self.assertTrue(any([isinstance(s, Server) for s in server_list]))

    ## @unittest.SkipTest
    def test_validate(self):
        """tests validating servers"""
        sm = self.gis.admin.servers
        validation = sm.validate()
        self.assertIsInstance(validation, (bool, int))

    def test_properties(self):
        """tests ServerManager properties"""
        sm = self.gis.admin.servers
        properties = sm.properties
        self.assertIsInstance(properties, InsensitiveDict)
        self.assertTrue("servers" in list(sm.properties.keys()))
        self.assertTrue(
            "HOSTING_SERVER" in [s["serverRole"] for s in sm.properties["servers"]]
        )
        sroles = set(s["serverRole"] for s in sm.properties["servers"])
        self.assertTrue(sroles, {"FEDERATED_SERVER", "HOSTING_SERVER"})


@profiles.admin_enterprise_and_agol
@integration_test
class TestServiceDirectory(unittest.TestCase):
    """
    Tests ServiceDirectory class
    """

    @classmethod
    def setUpClass(cls):
        cls.online_urls = [
            "https://sampleserver5.arcgisonline.com/arcgis/rest/",  # 10.91
            "https://sampleserver6.arcgisonline.com/arcgis/rest/",  # 10.91
        ]

    def test_service_directory(self):
        """test service directories for online and enterprise"""
        if self.gis._is_agol:
            server = ServicesDirectory(url=f"{self.gis.url}/arcgis/rest")
            self.assertIsInstance(server, ServicesDirectory)
        else:
            url = self.gis.url.replace("portal/", "server/")
            server = ServicesDirectory(url=url)
            self.assertIsInstance(server, ServicesDirectory)

    def test_ent_service_directory_anonymous(self):
        """tests access enterprise ServiceDirectory anonymously"""
        if not self.gis._is_agol:
            server = ServicesDirectory(url=self.gis.url)
            self.assertIsInstance(server, ServicesDirectory)

    def test_ent_service_directory_token(self):
        """access enterprise ServiceDirectory catalog token"""
        if not self.gis._is_agol:
            server = ServicesDirectory(
                url=self.gis.url.replace("portal/", "server/"),
                username=self.gis._username,
                password=self.gis._password,
                tokenurl=self.gis.resturl + "generateToken/",
            )
            self.assertIsInstance(server, ServicesDirectory)

    def test_ent_service_directory_admin(self):
        """test getting the admin object to server from direct connection"""
        if not self.gis._is_agol:
            server = ServicesDirectory(
                url=self.gis.url.replace("portal/", "server/"),
                username=self.gis._username,
                password=self.gis._password,
                tokenurl=self.gis.resturl + "generateToken/",
            )
            self.assertIsInstance(server.admin, Server)


@profiles.admin_enterprise
@integration_test
class TestServerProperty(unittest.TestCase):
    """
    test server login & properties on class
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server"),
            username=cls.gis._username,
            password=cls.gis._password,
            tokenurl=cls.gis.resturl + "generateToken/",
        ).admin

    def test_service_directory(self):
        """enterprise server services"""
        server_content = self.server_manager.content
        self.assertIsInstance(server_content, ServicesDirectory)

    def test_datastore_manager(self):
        """enterprise server datastore manager"""
        ds = self.server_manager.datastores
        self.assertIsInstance(ds, DataStoreManager)

    def test_info(self):
        """enterprise server info"""
        info = self.server_manager._info
        self.assertIsInstance(info, Info)

    def test_kml(self):
        """enterprise server kml"""
        kml = self.server_manager._kml
        self.assertIsInstance(kml, KML)

    def test_log(self):
        """enterprise server logs"""
        lm = self.server_manager.logs
        self.assertIsInstance(lm, LogManager)

    def test_services(self):
        """enterprise server service manager"""
        service_mgr = self.server_manager.services
        self.assertIsInstance(service_mgr, ServiceManager)
        self.assertIsInstance(service_mgr.folders, list)
        assert {"Hosted", "System", "Utilities"}.issubset(service_mgr.folders)

    def test_usage(self):
        """enterprise server report manager"""
        report_mgr = self.server_manager.usage
        self.assertIsInstance(report_mgr, ReportManager)

    def test_users(self):
        """enterprise server user manager"""
        user_mgr = self.server_manager.users
        self.assertIsInstance(user_mgr, UserManager)


@profiles.admin_enterprise
@integration_test
class TestServerInfo(unittest.TestCase):
    """
    Tests Server Info property
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server"),
            username=cls.gis._username,
            password=cls.gis._password,
        ).admin

    def test_get_info(self):
        """tests getting server info"""
        info = self.server_manager._info
        self.assertIsInstance(info, Info)

    def test_info_auth_timezones(self):
        """tests get available time zones"""
        info = self.server_manager._info
        available_time_zones = info.available_time_zones()
        self.assertIsInstance(available_time_zones, dict)

    def test_info_properties(self):
        info = self.server_manager._info
        info_props = dict(info.properties)
        self.assertIsInstance(info_props, dict)
        self.assertIn("currentversion", info.properties)
        self.assertIn("currentbuild", info.properties)
        self.assertEqual(
            info.properties["loggedInUserPrivilege"],
            "ADMINISTER",
            "Logged in User should be administrator.",
        )
        self.assertIn("supportedFonts", info.properties)


@profiles.admin_enterprise
@integration_test
class TestServerLog(unittest.TestCase):
    """
    Tests Server Log Manager class
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server"),
            username=cls.gis._username,
            password=cls.gis._password,
        ).admin

    def test_log_manager(self):
        """tests getting log manager object"""
        logs = self.server_manager.logs
        self.assertIsInstance(logs, LogManager)

    def test_query_logs(self):
        """tests querying logs with specific parameters"""
        logs = self.server_manager.logs

        results = logs.query()
        self.assertIsInstance(results, dict)

        results_max_record = logs.query(max_records_return=5002)
        self.assertIsInstance(results_max_record, dict)

        results_debug = logs.query(
            start_time="2025-03-11T14:00:00",
            end_time="2025-02-11T14:00:00",
            codes=["20000-24000"],
            level="WARNING",
        )

        self.assertIsNot(
            [], results_debug["logMessages"], "This log query should have results"
        )
        self.assertFalse(
            any([c["code"] < 20000 for c in results_debug["logMessages"]]),
            "Result codes are outside range.",
        )
        self.assertFalse(
            any([c["code"] > 24000 for c in results_debug["logMessages"]]),
            "Result codes are outside range.",
        )


@profiles.admin_enterprise
@integration_test
class TestServerMachine(unittest.TestCase):
    """
    Tests Server Machine Manager class
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server"),
            username=cls.gis._username,
            password=cls.gis._password,
        ).admin

    def test_machine_manager(self):
        """tests getting machine manager object"""
        machines = self.server_manager.machines
        self.assertIsInstance(machines, MachineManager)
        self.assertEqual(
            ["machines", "DatastoreMachines", "Protocol"],
            list(machines.properties.keys()),
            "MachineManger properties does not have appropriate keys.",
        )

    def test_list_machines(self):
        """tests listing machines"""
        machines = self.server_manager.machines
        machine_list = machines.list()
        self.assertIsInstance(machine_list, (list, tuple))
        self.assertGreaterEqual(len(machine_list), 1, "Server must have a machine.")
        self.assertIsInstance(machine_list[0], Machine)

    def test_get_machine(self):
        """tests getting one of the machines"""
        machines = self.server_manager.machines
        machine_name = machines.list()[0].properties.machineName
        machine = machines.get(machine_name=machine_name)
        self.assertIsInstance(machine, Machine)
        self.assertEquals(machine.properties.machineName, machine_name)
        assert machine.properties["adminURL"].endswith(":6443/arcgis/admin")


@profiles.admin_enterprise
## TODO: add standalone server
@integration_test
class TestServerReport(unittest.TestCase):
    """
    Tests Server Report class
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server"),
            username=cls.gis._username,
            password=cls.gis._password,
        ).admin

    def test_reports(self):
        """tests listing server usage report"""
        usage = self.server_manager.usage
        self.assertIsInstance(usage, ReportManager)

        report_list = usage.list()
        self.assertIsInstance(report_list, (list, tuple))

    def test_usage_metrics(self):
        """tests getting server usage report metrics"""
        usage = self.server_manager.usage
        metrics = usage.properties.metrics
        self.assertIsNotNone(metrics)

    def test_usage_settings(self):
        """tests getting server usage report settings"""
        usage = self.server_manager.usage
        settings = usage.settings
        self.assertIsNotNone(settings)

    def test_get_report(self):
        """tests listing reports"""
        usage = self.server_manager.usage
        report = usage.list()[0]
        self.assertIsInstance(report, Report)

    def test_report_query(self):
        """tests querying report"""
        usage = self.server_manager.usage
        report = usage.list()[0]
        res = report.query()
        self.assertIsInstance(res, dict)


@server_credentials.standalone_enterprise
@integration_test
class TestServerStandAloneConnect(unittest.TestCase):
    """tests the connection to arcgis server object (standalone)"""

    @classmethod
    def setUpClass(cls):
        cls.url = cls.url
        cls.username = cls.username
        cls.password = cls.password
        cls.web_adaptor = "server"

        cls.svc_dir = ServicesDirectory(
            url=cls.url, username=cls.username, password=cls.password
        )
        cls.server = cls.svc_dir.admin

    def test_standalone_server_service_directory(self):
        """tests creating a Server object - standalone server"""
        sa_server = self.server
        self.assertIsInstance(sa_server, Server)

    def test_standalone_server_sharing_endpoint(self):
        surl = self.url
        susername = self.username
        spassword = self.password
        stoken = f"{self.url}/tokens/"

        stnd_alone_server = Server(
            url=surl,
            username=susername,
            password=spassword,
            token=stoken,
        )

        self.assertIsInstance(stnd_alone_server, Server)

    def test_standalone_server_admin_gentoken(self):
        gurl = f"{self.url}/admin"
        gusername = f"{self.username}"
        gpassword = f"{self.password}"
        gtoken_url = f"{self.url}/tokens/generateToken"

        stnd_alone_server = Server(
            url=gurl,
            username=gusername,
            password=gpassword,
            token_url=gtoken_url,
        )

        self.assertIsInstance(stnd_alone_server, Server)
        self.assertIsInstance(stnd_alone_server.content, ServicesDirectory)


@server_credentials.standalone_enterprise
@integration_test
class TestServerStandAloneUser(unittest.TestCase):
    """
    Tests Server User Manager class
    """

    @classmethod
    def setUpClass(cls):
        from arcgis.gis.server import ServicesDirectory

        cls.server_sdir = ServicesDirectory(
            url=cls.url,
            username=cls.username,
            password=cls.password,
        )

        cls.server_manager = cls.server_sdir.admin

        cls.server_manager.users.roles.create(
            name="ntgrtn-tst-user-role",
            description="Setup role for ntgrtn-tst verification.",
        )

        cls.test_role = cls.server_manager.users.roles.get_role("ntgrtn-tst-user-role")[
            0
        ]
        if (
            not cls.test_role._security._get_privilege_for_role(cls.test_role.rolename)[
                "privilege"
            ]
            == "ACCESS"
        ):
            cls.test_role.set_privileges("ACCESS")

        cls.test_user = cls.server_manager.users.create(
            username="ntgrtn-tst-user",
            password="lovetheapi1",
            fullname="Stand-alone ntgrtn-tst",
            email="ntgrtn-tstr@esri.com",
            description="Test account on stand alone server.",
        )
        cls.test_user.add_role(cls.test_role.rolename)

    def test_user_manager(self):
        """tests getting UserManager object"""
        users = self.server_manager.users
        self.assertIsInstance(users, UserManager)
        self.assertIn("search", dir(users), "Search method missing on UserManager")

    def test_create_user(self):
        """tests creating user"""
        users = self.server_manager.users
        user_search = users.search("PyAPIServerTest123")
        if not user_search:
            sa_user = users.create(
                username="PyAPIServerTest123",
                password="lovetheapi1",
                fullname="Ntgrtn Tst",
                email="d@esri.com",
                description="account",
            )
        else:
            sa_user = user_search[0]
            self.assertIsInstance(sa_user, User)
            self.assertEqual(sa_user.username, "PyAPIServerTest123")
            self.assertFalse(
                bool(users.roles._get_user_roles(sa_user.username)["roles"])
            )
            sa_user.add_role(self.test_role.rolename)
            self.assertIn(
                "ntgrtn-tst-user-role",
                users.roles._get_user_roles(sa_user.username)["roles"],
                "Role not assigned",
            )

    def test_get_user(self):
        """tests getting user"""
        users = self.server_manager.users
        user_get = users.get(username="ntgrtn-tst-user")
        if not user_get.username:
            self.skipTest("Create user failed in setup, skipping.")
            assert isinstance(user_get, User)
            self.assertIn(
                "ntgrtn-tst-user-role",
                users.roles._get_user_roles(user_get.username)["roles"],
                "add_role failed in test setup.",
            )
            self.assertIn("add_role", dir(user_get), "User missing add_role method.")

    def test_me(self):
        """tests getting current authenticated user"""
        users = self.server_manager.users
        self.assertIsInstance(users.me, str)
        self.assertEqual(users.me, self.server_manager.users.me)

    def test_search_user(self):
        """tests search user by username"""
        users = self.server_manager.users
        self.assertGreaterEqual(
            len(users.search(username="Py")), 1, "No username starts with Py"
        )
        self.assertTrue(users.search(username="ntgrtn-tst"))

    def test_role_manager(self):
        """tests getting RoleManager object"""
        users = self.server_manager.users
        roles = users.roles
        self.assertIsInstance(roles, RoleManager)
        self.assertGreaterEqual(
            len(roles.all()), 1, "At least one role should have been created"
        )

    def test_roles_all(self):
        """tests getting all roles"""
        users = self.server_manager.users
        roles = users.roles
        assert isinstance(roles, RoleManager)
        roles_list = roles.all()
        if not roles_list:
            self.skipTest("No user-defined roles on server, skipping")
            self.assertIsInstance(roles_list, list)
            self.assertIsInstance(roles_list[0], Role)

    def test_get_role(self):
        """tests getting a role"""
        users = self.server_manager.users
        roles = users.roles
        role_list = roles.get_role("ntgrtn-tst-user-role")
        self.assertIsInstance(role_list, list)
        self.assertIsInstance(role_list[0], Role)
        role = role_list[0]
        self.assertEqual(role.rolename, "ntgrtn-tst-user-role")
        self.assertEqual(
            roles._get_privilege_for_role(role.rolename)["privilege"],
            "ACCESS",
            "Role returned incorrect privilege.",
        )

    def test_create_role(self):
        """tests creating a role"""
        users = self.server_manager.users
        roles = users.roles
        if not roles.get_role("ntgrtn-tst-publisher-role"):
            role = roles.create(
                name="ntgrtn-tst-publisher-role",
                description="Role created for ntgrtn-tst RoleManager.create verification.",
            )
        self.assertIsInstance(role, bool)
        role_list = roles.get_role("ntgrtn-tst-publisher-role")
        if not role_list:
            self.skipTest("Role not created on server, skipping")
        self.assertIsInstance(role_list, list)
        role = role_list[0]
        self.assertIsInstance(role, Role)
        self.assertEqual(
            role.rolename,
            "ntgrtn-tst-publisher-role",
            "Role should be named ntgrtn-tst-publisher-role.",
        )
        self.assertEqual(
            roles._get_privilege_for_role(role.rolename)["privilege"], "ACCESS"
        )
        role.set_privileges(privilege="PUBLISH")
        self.assertEqual(
            roles._get_privilege_for_role(role.rolename)["privilege"], "PUBLISH"
        )

    def test_role_update(self):
        """tests update a role"""
        users = self.server_manager.users
        roles = users.roles
        role = roles.get_role("ntgrtn-tst-user-role")[0]
        orig_desc = role.description
        role.update(description="Test updated description for ntgrtn-tst-user-role.")
        upd_desc = role.description
        self.assertNotEqual(orig_desc, upd_desc, "Update role description failed")

    def test_set_privileges(self):
        """tests set role privileges"""
        users = self.server_manager.users
        roles = users.roles
        role = roles.get_role("ntgrtn-tst-user-role")[0]
        current_priv = roles._get_privilege_for_role(role.rolename)["privilege"]
        role.set_privileges("PUBLISH")
        pub_priv = roles._get_privilege_for_role(role.rolename)["privilege"]
        self.assertNotEqual(current_priv, pub_priv, "Privilege was not set.")

    def test_update_user_update(self):
        """tests update a user"""
        users = self.server_manager.users
        user = users.get(self.test_user.username)
        self.assertEqual(
            user.fullname,
            "Stand-alone ntgrtn-tst",
            "Unexpected full_name for server user.",
        )
        new_fullname = "Stand-alone ntgrtn-tst-updated"
        res = user.update(
            password="pw12356",
            full_name=new_fullname,
            description="Updated description for stand-alone test user.",
            email=None,
        )
        self.assertTrue(res)
        self.assertEqual(user.fullname, new_fullname, "Updating user failed.")

    def test_user_assign_role(self):
        """tests assigning a role to a user"""
        users = self.server_manager.users
        roles = users.roles
        user = users.get("ntgrtn-tst-user")
        role = roles.get_role("ntgrtn-tst-publisher-role")[0]
        res = user.add_role(role.rolename)
        self.assertTrue(res)
        self.assertIn(
            "ntgrtn-tst-publisher-role",
            roles._get_user_roles(user.username)["roles"],
            "The add_role method did not add role to user.",
        )

    def test_user_delete(self):
        """tests deleting a user"""
        users = self.server_manager.users
        if not users.search("PyAPIServerTest123"):
            self.skipTest("User does not exist to delete")
        resp = users.search("PyAPIServerTest123")[0].delete()
        self.assertTrue(resp)

    @classmethod
    def tearDownClass(cls):
        cls.test_user.delete()
        cls.test_role.delete()

        role_mgr = cls.server_manager.users.roles
        role_mgr.get_role("ntgrtn-tst-publisher-role")[0].delete()


if __name__ == "__main__":
    unittest.main()

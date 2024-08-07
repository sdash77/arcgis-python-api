import unittest
import pandas as pd
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
from utils.decorators import integration_test, profiles


ENT_SETS = [
    {
        "url": "https://pythonapitest.playground.esri.com/server/rest/",
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
        "server": "11.4 standalone",
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


@profiles.admin_agol
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
            sd = ServicesDirectory(url=service, portal_connection=self.gis, is_agol=True)
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
        assert isinstance(service, FeatureLayerCollection)

    def test_get_service_not_found(self):
        """tests getting non-existing service"""
        service = self.sd.get(name="IDONTEXIST")
        self.assertIsNone(service)


@unittest.skip("waiting for standalone server setup")
@integration_test
class TestServerStandalone(unittest.TestCase):
    """tests the connection to arcgis server object (standalone)"""

    def test_server_portal_not_gis(self):
        """tests creating a Server object without gis - standalone server"""

        # TODO: get standalone server url and generateToken url, create Server object, and assert Server object


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

        server = Server(url=self.gis._url.replace("/portal/", "/server/admin"), gis=self.gis)
        self.assertIsInstance(server, Server)

    def test_get_server_from_server_connection(self):
        """tests getting server object through gis.server.Server with gis connection param"""

        server = Server(url=self.gis._url.replace("/portal/", "/server/admin"), portal_connection=self.gis._portal.con)
        self.assertIsInstance(server, Server)


@profiles.admin_enterprise
# TODO: add stand-alone credentials
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

    # @unittest.SkipTest
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


@profiles.admin_enterprise_and_agol
# TODO: add stand-alone credentials
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
            for url in self.online_urls:
                server = ServicesDirectory(url=url)
                self.assertIsInstance(server, ServicesDirectory)
        else:
            url = self.gis.url.replace("portal/", "server/rest/")
            server = ServicesDirectory(url=url)
            self.assertIsInstance(server, ServicesDirectory)

    def test_ent_service_directory_anonymous(self):
        """tests access enterprise ServiceDirectory anonymously"""
        server = ServicesDirectory(url=self.gis.url)
        self.assertIsInstance(server, ServicesDirectory)

    def test_ent_service_directory_token(self):
        """access enterprise ServiceDirectory catalog token"""
        if not self.gis._is_agol:
            server = ServicesDirectory(
                url=self.gis.url.replace("portal/", "server/rest/"),
                username=self.gis._username,
                password=self.gis._password,
                tokenurl=self.gis.resturl + "generateToken/",
            )
            self.assertIsInstance(server, ServicesDirectory)

    # ---------------------------------------------------------------------
    def test_ent_service_directory_admin(self):
        """test getting the admin object to server from direct connection"""
        if not self.gis._is_agol:
            server = ServicesDirectory(
                url=self.gis.url.replace("portal/", "server/rest/"),
                username=self.gis._username,
                password=self.gis._password,
                tokenurl=self.gis.resturl + "generateToken/",
            )
            self.assertIsInstance(server.admin, Server)


@profiles.admin_enterprise
# TODO: add standalone server credentials
@integration_test
class TestServerProperty(unittest.TestCase):
    """
    test server login & properties on class
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server/rest/"),
            username=cls.gis._username,
            password=cls.gis._password,
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

    def test_usage(self):
        """enterprise server report manager"""
        report_mgr = self.server_manager.usage
        self.assertIsInstance(report_mgr, ReportManager)

    def test_users(self):
        """enterprise server user manager"""
        user_mgr = self.server_manager.users
        self.assertIsInstance(user_mgr, UserManager)


@profiles.admin_enterprise
# TODO: add standalone credentials
# TODO: test online?
@integration_test
class TestServerInfo(unittest.TestCase):
    """
    Tests Server Info property
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server/rest/"),
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


@profiles.admin_enterprise
# TODO: add standalone server
@integration_test
class TestServerLog(unittest.TestCase):
    """
    Tests Server Log Manager class
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server/rest/"),
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


@profiles.admin_enterprise
# TODO: add standalone server
@integration_test
class TestServerMachine(unittest.TestCase):
    """
    Tests Server Machine Manager class
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server/rest/"),
            username=cls.gis._username,
            password=cls.gis._password,
        ).admin

    def test_machine_manager(self):
        """tests getting machine manager object"""
        machines = self.server_manager.machines
        self.assertIsInstance(machines, MachineManager)

    def test_list_machines(self):
        """tests listing machines"""
        machines = self.server_manager.machines
        machine_list = machines.list()
        self.assertIsInstance(machine_list, (list, tuple))

    def test_get_machine(self):
        """tests getting one of the machines"""
        machines = self.server_manager.machines
        machine_name = machines.list()[0].properties.machineName
        machine = machines.get(machine_name=machine_name)
        self.assertIsInstance(machine, Machine)
        self.assertEquals(machine.properties.machineName, machine_name)


@profiles.admin_enterprise
# TODO: add standalone server
@integration_test
class TestServerReport(unittest.TestCase):
    """
    Tests Server Report class
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server/rest/"),
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


@profiles.admin_enterprise
# TODO: add standalone server
@integration_test
class TestServerSecurity(unittest.TestCase):
    """
    Tests Server Security module - User Manager and Role Manager classes
    """

    @classmethod
    def setUpClass(cls):
        cls.server_manager = ServicesDirectory(
            url=cls.gis.url.replace("portal", "server/rest/"),
            username=cls.gis._username,
            password=cls.gis._password,
        ).admin

    def test_user_manager(self):
        """tests getting UserManager object"""
        users = self.server_manager.users
        self.assertIsInstance(users, UserManager)

    def test_create_and_delete_user(self):
        """tests creating user"""
        users = self.server_manager.users

        # create user
        user = users.create(
            username="PyAPIServerTest123",
            password="lovetheapi1",
            fullname="b d",
            email="d@esri.com",
            description="account",
        )

        self.assertIsInstance(user, User)

        # delete user
        users.search("PyAPIServerTest123")[0].delete()

    def test_get_user(self):
        """tests getting user"""
        users = self.server_manager.users

        # create user
        res = users.create(
            username="PyAPIServerTest123",
            password="lovetheapi1",
            fullname="b d",
            email="d@esri.com",
            description="account",
        )

        # get user
        user = users.get(username="PyAPIServerTest123")
        self.assertIsInstance(user, (list, User))

        # delete user
        users.search("PyAPIServerTest123")[0].delete()

    def test_me(self):
        """tests getting current authenticated user"""
        users = self.server_manager.users
        self.assertIsInstance(users.me, (str, User))

    def test_search_user(self):
        """tests search user by username"""
        users = self.server_manager.users

        # create user
        res = users.create(
            username="PyAPIServerTest123",
            password="lovetheapi1",
            fullname="b d",
            email="d@esri.com",
            description="account",
        )
        self.assertIsInstance(users.search(username="Py"), list)

        # delete user
        users.search("PyAPIServerTest123")[0].delete()

    def test_update_user(self):
        """tests update a user"""
        users = self.server_manager.users

        # create user
        user = users.create(
            username="PyAPIServerTest123",
            password="lovetheapi1",
            fullname="b d",
            email="d@esri.com",
            description="account",
        )

        # update user
        res = user.update(
            password="pw12356",
            full_name="Jane Doe",
            description="description new",
            email=None,
        )
        self.assertTrue(res)

        # delete user
        users.search("PyAPIServerTest123")[0].delete()

    def test_role_manager(self):
        """tests getting RoleManager object"""
        users = self.server_manager.users
        roles = users.roles
        self.assertIsInstance(roles, RoleManager)

    def test_list_roles(self):
        """tests getting all roles """
        users = self.server_manager.users
        roles = users.roles
        roles_list = roles.all()
        self.assertIsInstance(roles_list, list)

    def test_get_role(self):
        """tests getting a role"""
        users = self.server_manager.users
        roles = users.roles
        role = roles.get_role("admin")
        self.assertIsInstance(role, (list, Role))

    def test_create_role(self):
        """tests creating a role"""
        users = self.server_manager.users
        roles = users.roles

        # create role
        if len(roles.get_role("role1")) == 1:
            roles.get_role("role1")[0].delete()
        role = roles.create(name="role1", description="role description")
        self.assertIsInstance(role, Role)

        # delete role
        roles.get_role("role1")[0].delete()

    def test_update_role(self):
        """tests update a role"""
        users = self.server_manager.users
        roles = users.roles

        # create role
        if len(roles.get_role("role1")) == 1:
            roles.get_role("role1")[0].delete()
        role = roles.create(name="role1", description="role description")
        self.assertIsInstance(role, Role)

        # update role
        self.assertIsInstance(
            role.update(description="New Description"), (dict, Role, bool)
        )

        # delete role
        roles.get_role("role1")[0].delete()

    def test_set_role_privileges(self):
        """tests set role privileges"""
        users = self.server_manager.users
        roles = users.roles

        # create role
        role = roles.create(name="role1", description="role description")
        self.assertIsInstance(role, Role)

        # set privileges
        role = roles.get_role("role1")[0]
        self.assertIsInstance(
            role.set_privileges("publish"), (dict, Role, bool)
        )

        # delete role
        roles.get_role("role1")[0].delete()

    def test_assign_role_to_user(self):
        """tests assigning a role to a user"""
        users = self.server_manager.users
        roles = users.roles

        # create user
        user = users.create(
            username="PyAPIServerTest123",
            password="lovetheapi1",
            fullname="b d",
            email="d@esri.com",
            description="account",
        )

        # create role
        role = roles.create(name="role1", description="role description")

        # assign role to user
        role = roles.get_role("role1")[0]
        res = user.add_role(role.rolename)
        self.assertTrue(res)

        # delete user and role
        users.search("PyAPIServerTest123")[0].delete()
        roles.get_role("role1")[0].delete()


if __name__ == "__main__":
    unittest.main()

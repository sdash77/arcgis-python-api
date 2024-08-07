import unittest
from arcgis._impl.common._mixins import PropertyMap
from arcgis.gis.nb import NotebookServer
from arcgis.gis.nb import LogManager
from arcgis.gis.nb import Machine, MachineManager
from arcgis.gis.nb import Runtime, NotebookManager
from arcgis.gis.nb import SecurityManager
from arcgis.gis.nb import SystemManager, WebAdaptor, WebAdaptorManager
from arcgis.gis.nb import Container, DirectoryManager
from utils.decorators import integration_test, profiles


def _find_nb_server(gis):
    nbs = [
        server
        for server in gis.admin.servers.list()
        if isinstance(server, NotebookServer)
    ]
    if len(nbs) > 0:
        return nbs[0]
    return None


@profiles.admin_enterprise
@integration_test
class TestNotebookServer(unittest.TestCase):
    """Tests the base level to the notebook server"""

    def setUp(self):
        self.nbs = _find_nb_server(self.gis)
        if not self.nbs:
            self.skipTest("Portal not configured with notebook server.")

    def test_root_getters(self):
        """tests that the proper types are returning for the root getters"""
        assert isinstance(self.nbs, NotebookServer)
        assert isinstance(self.nbs.info, PropertyMap)
        assert isinstance(self.nbs.logs, LogManager)
        assert isinstance(self.nbs.machine, MachineManager)
        assert isinstance(self.nbs.notebooks, NotebookManager)
        assert isinstance(self.nbs.properties, PropertyMap)
        assert isinstance(self.nbs.security, SecurityManager)
        assert isinstance(self.nbs.system, SystemManager)

    def test_str_repr_method(self):
        """tests notebook server name"""
        assert "< NotebookServer @" in str(self.nbs)


@profiles.admin_enterprise
@integration_test
class TestLogManager(unittest.TestCase):
    """Tests the LogManager class"""

    def setUp(self):
        self.nbs = _find_nb_server(self.gis)
        if not self.nbs:
            self.skipTest("Portal not configured with notebook server.")

        self.logs = self.nbs.logs
        assert isinstance(self.logs, LogManager)

    def test_get_log_manager(self):
        """tests getting the log manager"""
        assert isinstance(self.nbs.logs, LogManager)

    def test_get_settings(self):
        """tests getting the log settings"""
        assert isinstance(self.logs.settings, PropertyMap)
        assert len(dict(self.logs.settings)) > 0

    def test_updating_settings(self):
        """tests updating the log settings"""
        settings = self.logs.settings
        self.logs.settings = settings
        assert isinstance(self.logs.settings, PropertyMap)

    def test_query_settings(self):
        """tests query the log settings"""
        val = self.logs.query()
        assert isinstance(val, dict)

    def test_clean_settings(self):
        """tests clean the log settings"""
        assert self.logs.clean()


@profiles.admin_enterprise
@integration_test
class TestSecurityManager(unittest.TestCase):
    """Tests the SecurityManager class"""

    def setUp(self):
        self.nbs = _find_nb_server(self.gis)
        if not self.nbs:
            self.skipTest("Portal not configured with notebook server.")

        self.security = self.nbs.security
        assert isinstance(self.security, SecurityManager)

    def test_get_configuration(self):
        """test get security configuration through notebook server Security Manager """
        assert isinstance(self.security.configuration, (dict, PropertyMap))

    def test_set_configuration(self):
        """test set security configuration through notebook server Security Manager"""
        vals = dict(self.security.configuration)
        self.security.configuration = vals
        assert isinstance(self.security.configuration, (dict, PropertyMap))


@profiles.admin_enterprise
@integration_test
class TestMachineManager(unittest.TestCase):
    """Tests the Machine and MachineManager class"""

    def setUp(self):
        self.nbs = _find_nb_server(self.gis)
        if not self.nbs:
            self.skipTest("Portal not configured with notebook server.")

        self.machine = self.nbs.machine
        assert isinstance(self.machine, MachineManager)

    def test_machine_manager(self):
        """tests getting the machine list and machine properties"""
        assert isinstance(self.machine.list(), list)
        assert isinstance(self.machine.properties, (PropertyMap, dict))

    def test_get_machine(self):
        """tests getting one of the machines"""
        m = self.machine.list()[0]
        assert isinstance(m, Machine)

    def test_get_machine_properties(self):
        """tests getting one of the machine's properties"""
        m = self.machine.list()[0]
        assert isinstance(m, Machine)
        assert isinstance(m.properties, (dict, PropertyMap))

    def test_set_machine_properties(self):
        """tests setting machine properties"""
        m = self.machine.list()[0]
        assert isinstance(m, Machine)
        v = dict(m.properties)
        m.properties = v
        assert isinstance(m.properties, (dict, PropertyMap))

    def test_get_machine_hardware(self):
        """tests getting the hardware property of a machine"""
        m = self.machine.list()[0]
        assert isinstance(m, Machine)
        assert isinstance(m.hardware, dict)

    def test_get_machine_status(self):
        """tests getting machine status"""
        m = self.machine.list()[0]
        assert isinstance(m, Machine)
        assert isinstance(m.status, dict)

    def test_create_self_signed_cert(self):
        m = self.machine.list()[0]
        assert isinstance(m, Machine)
        cert = m.create_self_signed_cert(
                alias="aliastest",
                keysize=2048,
                common_name="common",
                org_unit="org_unit",
                organization="orgtest",
                city="city",
                state="state",
                country="US",
            )
        assert "success" in cert


@profiles.admin_enterprise
@integration_test
class TestNotebookManager(unittest.TestCase):
    """Tests the NotebookManager Class"""

    def setUp(self):
        self.nbs = _find_nb_server(self.gis)
        if not self.nbs:
            self.skipTest("Portal not configured with notebook server.")

        self.notebook = self.nbs.notebooks
        assert isinstance(self.notebook, NotebookManager)

    def test_nb_manager(self):
        """tests getting notebook manager properties and runtimes"""
        assert isinstance(self.notebook.properties, (dict, PropertyMap))
        assert isinstance(self.notebook.runtimes, list)

    def test_runtime(self):
        """tests the runtime class operations"""
        rts = self.notebook.runtimes
        if len(rts) > 0:
            runtime = rts[0]
            assert isinstance(runtime, Runtime)
            assert isinstance(runtime.manifest, list)
            assert isinstance(runtime.properties, (dict, PropertyMap))
            assert runtime.update(max_cpu=2)


@profiles.admin_enterprise
@integration_test
class TestSystemManager(unittest.TestCase):
    """Tests the SystemManager Class"""

    def setUp(self):
        self.nbs = _find_nb_server(self.gis)
        if not self.nbs:
            self.skipTest("Portal not configured with notebook server.")

        self.system = self.nbs.system
        assert isinstance(self.system, SystemManager)

    def test_system_manager(self):
        """tests getting system manager properties"""
        assert isinstance(self.system.containers, list)
        assert isinstance(self.system.directories, DirectoryManager)
        assert isinstance(self.system.jobs, list)
        assert isinstance(self.system.properties, (dict, PropertyMap))
        assert isinstance(self.system.config_store, (dict, PropertyMap))
        assert isinstance(self.system.web_adaptors, WebAdaptorManager)

    def test_job_details(self):
        """tests getting the job details"""
        if not self.system.jobs:
          self.skipTest("No notebook server system jobs configured.")
        job = self.system.jobs[0]
        job_details = self.system.job_details(job_id=job['jobId'])
        assert isinstance(job_details, dict)
        assert job_details

    def test_recent_statistics(self):
        """tests recent_statistics method, enterprise must be 10.8.1+"""
        if self.gis.version < [10, 8, 1]:
            self.skipTest("Portal version must be 10.8.1 or higher")

        assert self.system.recent_statistics
        assert "machineName" in self.system.recent_statistics.get("mostRecentStatistics")[0].keys()

    def test_list_jobs(self):
        """tests list_jobs method, enterprise must be 10.9+"""
        if self.gis.version < [10, 9]:
            self.skipTest("Portal version must be 10.9 or higher")

        assert isinstance(self.system.list_jobs(), list)

        jobs = self.system.list_jobs(details=False)
        assert isinstance(jobs, list)
        assert "status" not in jobs[0].keys()

        detailed_jobs = self.system.list_jobs(details=True)
        assert isinstance(detailed_jobs, list)
        assert "status" in detailed_jobs[0].keys()

        num_jobs = self.system.list_jobs(details=False, num=5)
        assert len(num_jobs) <= 5


@profiles.admin_enterprise
@integration_test
class TestWebAdaptorManager(unittest.TestCase):
    """Tests the WebAdaptor, WebAdaptorManager Classes"""

    def setUp(self):
        self.nbs = _find_nb_server(self.gis)
        if not self.nbs:
            self.skipTest("Portal not configured with notebook server.")

        self.webadaptor = self.nbs.system.web_adaptors
        assert isinstance(self.webadaptor, WebAdaptorManager)

    def test_webadaptor_manager(self):
        """tests getting web adaptor manager properties"""
        assert isinstance(self.webadaptor.config, (dict, PropertyMap))
        assert len(self.webadaptor.list()) > 0
        assert isinstance(self.webadaptor.properties, PropertyMap)
        wa = self.webadaptor.list()[0]
        assert isinstance(wa, WebAdaptor)


@profiles.admin_enterprise
@integration_test
class TestDirectoryManager(unittest.TestCase):
    """Tests the DirectoryManager Classes"""

    def setUp(self):
        self.nbs = _find_nb_server(self.gis)
        if not self.nbs:
            self.skipTest("Portal not configured with notebook server.")

        self.directory = self.nbs.system.directories
        assert isinstance(self.directory, DirectoryManager)

    def test_dir_manager(self):
        """tests the directory manager and its properties"""
        assert isinstance(self.directory.list(), (list, tuple))
        assert isinstance(self.directory.properties, (dict, PropertyMap))

    def test_register_unregister_server_directory(self):
        """tests register and unregister server directory through DirectoryManager"""
        d = [d["id"] for d in self.directory.list() if d["name"] == "amazingdirtest"]
        if len(d) > 0:
            self.directory.unregister(d[0])

        assert self.directory.register(
            name="amazingdirtest",
            path=r"/net/FILESERVER/gisdata/notebookserver/directories/directories/",
            directory_type="DATA",
        )

        d = [d["id"] for d in self.directory.list() if d["name"] == "amazingdirtest"]
        assert len(d) == 1
        assert self.directory.unregister(d[0])


if __name__ == "__main__":
    unittest.main()
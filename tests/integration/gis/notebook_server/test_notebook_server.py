import unittest
from arcgis._impl.common._mixins import PropertyMap
from arcgis.gis.nb import NotebookServer  #
from arcgis.gis.nb._logs import LogManager  #
from arcgis.gis.nb._machines import Machine, MachineManager  #
from arcgis.gis.nb._nbm import Runtime, NotebookManager  #
from arcgis.gis.nb._security import SecurityManager  #
from arcgis.gis.nb._system import SystemManager, WebAdaptor, WebAdaptorManager
from arcgis.gis.nb._system import Container, DirectoryManager
from utils.decorators import integration_test, profiles


@profiles.admin_enterprise
@integration_test
class TestNBLogManager(unittest.TestCase):
    """tests the log functionality of the notebook server"""

    _server = None

    def _find_nb_server(self, gis):
        nbs = [
            server
            for server in self.gis.admin.servers.list()
            if isinstance(server, NotebookServer)
        ]
        if len(nbs) > 0:
            return nbs[0]
        return None

    def test_get_log_manager(self):
        """tests getting the log manager"""
        nb = self._find_nb_server(gis=self.gis)
        if nb:
            isinstance(nb, NotebookServer)
            assert isinstance(nb.logs, LogManager)

    def test_settings_get(self):
        """tests getting the settings"""
        nb = self._find_nb_server(gis=self.gis)
        logs = nb.logs
        isinstance(logs, LogManager)
        assert isinstance(logs.settings, PropertyMap)
        assert len(dict(logs.settings)) > 0

    def test_updating_settings(self):
        """tests getting the settings"""
        nb = self._find_nb_server(gis=self.gis)
        logs = nb.logs
        isinstance(logs, LogManager)
        v = nb.logs.settings
        logs.settings = v

    def test_query(self):
        """tests getting the settings"""
        nb = self._find_nb_server(gis=self.gis)
        logs = nb.logs
        isinstance(logs, LogManager)
        val = logs.query()
        print(val)

    def test_clean(self):
        """tests getting the settings"""
        nb = self._find_nb_server(gis=self.gis)
        logs = nb.logs
        isinstance(logs, LogManager)
        assert logs.clean()


@profiles.admin_enterprise
@integration_test
class TestNotebookServer(unittest.TestCase):
    """tests the base level to the notebook server"""

    def _find_nb_server(self, gis):
        nbs = [
            server
            for server in self.gis.admin.servers.list()
            if isinstance(server, NotebookServer)
        ]
        if len(nbs) > 0:
            return nbs[0]
        return None

    def test_root_getters(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)
        if nbs:
            assert isinstance(nbs, NotebookServer)
            assert isinstance(nbs.info, PropertyMap)
            assert isinstance(nbs.logs, LogManager)
            assert isinstance(nbs.machine, MachineManager)
            assert isinstance(nbs.notebooks, NotebookManager)
            assert isinstance(nbs.properties, PropertyMap)
            assert isinstance(nbs.security, SecurityManager)
            assert isinstance(nbs.system, SystemManager)

    def test_str_repr_method(self):
        nbs = self._find_nb_server(gis=self.gis)
        if nbs:
            assert str(nbs).find("<NotebookServer @") > -1
            assert str(nbs.__repr__()).find("<NotebookServer @") > -1


@profiles.admin_enterprise
@integration_test
class TestNBSecurityModule(unittest.TestCase):
    """
    Tests the Security Module for the ArcGIS Notebook Server
    """

    def _find_nb_server(self, gis):
        nbs = [
            server
            for server in self.gis.admin.servers.list()
            if isinstance(server, NotebookServer)
        ]
        if len(nbs) > 0:
            return nbs[0]
        return None

    def test_configuration_get(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)

        if nbs:
            security = nbs.security
            isinstance(security, SecurityManager)
            assert isinstance(security.configuration, (dict, PropertyMap))

    def test_configuration_set(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)

        if nbs:
            security = nbs.security

            isinstance(security, SecurityManager)
            vals = dict(security.configuration)
            security.configuration = vals


@profiles.admin_enterprise
@integration_test
class TestNBMachineManager(unittest.TestCase):
    """tests the MachineManager methods"""

    def _find_nb_server(self, gis):
        nbs = [
            server
            for server in self.gis.admin.servers.list()
            if isinstance(server, NotebookServer)
        ]
        if len(nbs) > 0:
            return nbs[0]
        return None

    def test_machine_manager(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)

        if nbs:
            mm = nbs.machine
            assert isinstance(mm, MachineManager)
            assert isinstance(mm.list(), list)
            assert isinstance(mm.properties, (PropertyMap, dict))

    def test_machine(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)

        if nbs:
            mm = nbs.machine
            assert isinstance(mm, MachineManager)
            m = mm.list()[0]
            assert isinstance(m, Machine)

    def test_machine_properties_get(self):
        """tests the property get operation"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)

        if nbs:
            mm = nbs.machine
            assert isinstance(mm, MachineManager)
            m = mm.list()[0]
            assert isinstance(m, Machine)
            assert isinstance(m.properties, (dict, PropertyMap))

    @unittest.skip("Skipped due to REST API error")
    def test_machine_properties_set(self):
        """tests the property get operation"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)

        if nbs:
            mm = nbs.machine
            assert isinstance(mm, MachineManager)
            m = mm.list()[0]
            assert isinstance(m, Machine)
            v = dict(m.properties)
            m.properties = v

    def test_machine_hardware(self):
        """tests the hardware property"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)

        if nbs:
            mm = nbs.machine
            assert isinstance(mm, MachineManager)
            m = mm.list()[0]
            assert isinstance(m, Machine)
            assert isinstance(m.hardware, dict)

    def test_status(self):
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)

        if nbs:
            mm = nbs.machine
            assert isinstance(mm, MachineManager)
            m = mm.list()[0]
            assert isinstance(m, Machine)
            assert isinstance(m.status, dict)

    def test_create_ss_cert(self):
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)

        if nbs:
            mm = nbs.machine
            assert isinstance(mm, MachineManager)
            m = mm.list()[0]
            assert isinstance(m, Machine)
            print(
                m.create_self_signed_cert(
                    alias="aliastest",
                    keysize=2048,
                    common_name="common",
                    org_unit="org_unit",
                    organization="orgtest",
                    city="city",
                    state="state",
                    country="US",
                )
            )


@profiles.admin_enterprise
@integration_test
class TestNBNotebookManager(unittest.TestCase):
    """Tests the Notebook Manager Class"""

    def _find_nb_server(self, gis):
        nbs = [
            server
            for server in self.gis.admin.servers.list()
            if isinstance(server, NotebookServer)
        ]
        if len(nbs) > 0:
            return nbs[0]
        return None

    def test_nb_manager(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)
        if nbs:  # property tests
            nbm = nbs.notebooks
            assert isinstance(nbm, NotebookManager)
            assert isinstance(nbm.properties, (dict, PropertyMap))
            assert isinstance(nbm.runtimes, list)

    def test_runtime(self):
        """tests the runtime class operations"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)
        if nbs:  # property tests
            nbm = nbs.notebooks
            assert isinstance(nbm, NotebookManager)
            rts = nbm.runtimes
            if len(rts) > 0:
                runtime = nbm.runtimes[0]
                assert isinstance(runtime, Runtime)
                assert isinstance(runtime.manifest, list)
                assert isinstance(runtime.properties, (dict, PropertyMap))
                assert runtime.update(max_cpu=2)


@profiles.admin_enterprise
@integration_test
class TestSystemManager(unittest.TestCase):
    """Tests the SystemManager Class"""

    def _find_nb_server(self, gis):
        nbs = [
            server
            for server in self.gis.admin.servers.list()
            if isinstance(server, NotebookServer)
        ]
        if len(nbs) > 0:
            return nbs[0]
        return None

    def test_sys_manager(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)
        if nbs:  # property tests
            nbm = nbs.notebooks
            isinstance(nbs, NotebookServer)
            system = nbs.system
            assert isinstance(system, SystemManager)
            assert isinstance(system.containers, list)
            assert isinstance(system.directories, DirectoryManager)
            assert isinstance(system.jobs, list)
            assert isinstance(system.properties, (dict, PropertyMap))
            assert isinstance(system.config_store, (dict, PropertyMap))
            assert isinstance(system.web_adaptors, WebAdaptorManager)

    def test_job_details(self):
        """tests getting the job details"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)
        if nbs:  # property tests
            nbm = nbs.notebooks
            isinstance(nbs, NotebookServer)
            system = nbs.system

            isinstance(system, SystemManager)
            for job in system.jobs:
                assert system.job_details(job_id=job)
                break


@profiles.admin_enterprise
@integration_test
class TestWebAdaptorManager(unittest.TestCase):
    """Tests the WebAdaptor, WebAdaptorManager Classes"""

    def _find_nb_server(self, gis):
        nbs = [
            server
            for server in self.gis.admin.servers.list()
            if isinstance(server, NotebookServer)
        ]
        if len(nbs) > 0:
            return nbs[0]
        return None

    def test_wa_manager(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)
        if nbs:  # property tests
            nbm = nbs.notebooks
            isinstance(nbs, NotebookServer)
            system = nbs.system
            isinstance(system, SystemManager)
            assert isinstance(system.web_adaptors, WebAdaptorManager)
            wam = system.web_adaptors
            isinstance(wam, WebAdaptorManager)
            assert isinstance(wam.config, (dict, PropertyMap))
            assert len(wam.list()) > 0
            assert isinstance(wam.properties, PropertyMap)
            wa = wam.list()[0]
            assert isinstance(wa, WebAdaptor)


@profiles.admin_enterprise
@integration_test
class TestDirectoryManager(unittest.TestCase):
    """Tests the DirectoryManager Classes"""

    def _find_nb_server(self, gis):
        nbs = [
            server
            for server in self.gis.admin.servers.list()
            if isinstance(server, NotebookServer)
        ]
        if len(nbs) > 0:
            return nbs[0]
        return None

    def test_dir_manager(self):
        """ensures that the proper types are returning for the root getters"""
        nbs = self._find_nb_server(gis=self.gis)
        isinstance(nbs, NotebookServer)
        if nbs:  # property tests
            system = nbs.system
            isinstance(system, SystemManager)
            sd = system.directories
            assert isinstance(sd, DirectoryManager)
            assert isinstance(sd.list(), (list, tuple))
            assert isinstance(sd.properties, (dict, PropertyMap))
            d = [d["id"] for d in sd.list() if d["name"] == "amazingdirtest"]
            if len(d) > 0:
                sd.unregister(d[0])
            assert sd.register(
                name="amazingdirtest",
                path=r"/data/arcgis/notebookserver/usr/directories",
                directory_type="WORKSPACE",
            )
            d = [d["id"] for d in sd.list() if d["name"] == "amazingdirtest"]
            assert len(d) == 1
            assert sd.unregister(d[0])


if __name__ == "__main__":
    unittest.main()

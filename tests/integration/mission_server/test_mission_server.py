import sys
#sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_issue_mission_admin_api\src")
from arcgis.gis import GIS
from arcgis.gis.mission import MissionServer

import unittest
import pytest

profiles = ['your_test_machine']
URL = "https://ragsebtest01.esri.com/portal" 
username = "APITeam" 
password = "APIletmein01"

###########################################################################
#@unittest.SkipTest
class TestMissionServerMACHINE(unittest.TestCase):
    """Tests the machine Functionality"""
    #----------------------------------------------------------------------
    def setUp(self):
        self._gis = GIS(url=URL, username=username, password=password, verify_cert=False)
        self._mss = [server for server in self._gis.admin.servers.list() if isinstance(server, MissionServer)]
    #----------------------------------------------------------------------
    def test_access_mission_MACHINE(self):
        """tests the logic to get a mission server  machine property"""
        from arcgis.gis.mission._machines import MachineManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.machine
            machine = m.machine
            assert isinstance(machine, MachineManager)
            
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_MACHINE_properties_list(self):
        """tests the logic to get a mission server  machine property"""
        from arcgis.gis.mission._machines import MachineManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.machine
            machine = m.machine
            assert isinstance(machine, MachineManager)
            assert isinstance(machine.list(), (list, tuple))
            assert machine.properties
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_MACHINE_properties_list(self):
        """tests the logic to get a mission server  machine property"""
        from arcgis.gis.mission._machines import MachineManager, Machine
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.machine
            machine = m.machine
            assert isinstance(machine, MachineManager)
            machines = machine.list()
            if len(machines) > 0:
                mach = machines[0]
                isinstance(mach, Machine)
                assert mach.hardware
                assert mach.properties
                assert mach.ssl_certificates

            assert isinstance(machine.list(), (list, tuple))
            assert machine.properties
        else:
            raise Exception("No Mission Server to test with.")            
###########################################################################
#@unittest.SkipTest
class TestMissionServerSYSTEM(unittest.TestCase):
    """Tests the system Functionality"""
    #----------------------------------------------------------------------
    def setUp(self):
        self._gis = GIS(url=URL, username=username, password=password, verify_cert=False)
        self._mss = [server for server in self._gis.admin.servers.list() if isinstance(server, MissionServer)]
    #----------------------------------------------------------------------
    def test_access_mission_SYSTEM(self):
        """tests the logic to get a mission server system property"""
        from arcgis.gis.mission._system import SystemManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.system
            system = m.system
            assert isinstance(system, SystemManager)
            
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_SYSTEM_properties(self):
        """tests the logic to get a mission server system property"""
        from arcgis.gis.mission._system import SystemManager
        from arcgis._impl.common._mixins import PropertyMap
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.system
            system = m.system
            assert isinstance(system, SystemManager)
            assert isinstance(system.properties, PropertyMap)
            system.properties = system.properties
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_SYSTEM_license(self):
        """tests the logic to get a mission system.license"""
        from arcgis.gis.mission._system import SystemManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.system
            system = m.system
            assert system.licenses            
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_SYSTEM_directories(self):
        """tests the logic to get a mission system.license"""
        from arcgis.gis.mission._system import SystemManager, DirectoryManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.system
            system = m.system
            assert system.directories
            assert isinstance(system.directories, DirectoryManager)
            d = system.directories
            dirs = d.list()
            assert dirs[0]
            
        else:
            raise Exception("No Mission Server to test with.")            
        
    #----------------------------------------------------------------------
    def test_SYSTEM_WebAdaptorManager(self):
        """tests the logic to get a mission system.license"""
        from arcgis.gis.mission._system import SystemManager, WebAdaptorManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.system
            system = m.system
            assert system.web_adaptors
            assert isinstance(system.web_adaptors, WebAdaptorManager)
            d = system.web_adaptors
            was = d.list()
            assert d.config
            assert d.properties
            
            
        else:
            raise Exception("No Mission Server to test with.")  
###########################################################################
#@unittest.SkipTest
class TestMissionServerSECURITY(unittest.TestCase):
    """Tests the security Functionality"""
    #----------------------------------------------------------------------
    def setUp(self):
        self._gis = GIS(url=URL, username=username, password=password, verify_cert=False)
        self._mss = [server for server in self._gis.admin.servers.list() if isinstance(server, MissionServer)]
    #----------------------------------------------------------------------
    def test_access_mission_SECURITY(self):
        """tests the logic to get a mission server security property"""
        from arcgis.gis.mission._security import SecurityManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.security
            security = m.security
            assert isinstance(security, SecurityManager)
            
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_access_mission_CONFIGURATION(self):
        """tests the logic to get a mission server security config"""
        from arcgis.gis.mission._security import SecurityManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.security
            security = m.security
            assert isinstance(security, SecurityManager)
            assert security.configuration
            security.configuration = security.configuration
        else:
            raise Exception("No Mission Server to test with.")     
    
###########################################################################
#@unittest.SkipTest
class TestMissionServerLOGS(unittest.TestCase):
    """Tests the Log Functionality"""
    #----------------------------------------------------------------------
    def setUp(self):
        self._gis = GIS(url=URL, username=username, password=password, verify_cert=False)
        self._mss = [server for server in self._gis.admin.servers.list() if isinstance(server, MissionServer)]
    #----------------------------------------------------------------------
    def test_access_mission_LOGS(self):
        """tests the logic to get a mission server logs property"""
        from arcgis.gis.mission._logs import LogManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.logs
            logs = m.logs
            assert isinstance(logs, LogManager)
            
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_LOGS_properties(self):
        """tests the logic to get a mission server logs property"""
        from arcgis.gis.mission._logs import LogManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.logs
            logs = m.logs
            assert isinstance(logs, LogManager)
            assert logs.properties
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_LOGS_query(self):
        """tests the logic to get a mission server logs property"""
        from arcgis.gis.mission._logs import LogManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.logs
            logs = m.logs
            assert isinstance(logs, LogManager)
            res = logs.query()
            assert res is not None
        else:
            raise Exception("No Mission Server to test with.")            
    #----------------------------------------------------------------------
    def test_LOGS_settings(self):
        """tests the logic to get a mission server logs property"""
        from arcgis.gis.mission._logs import LogManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.logs
            logs = m.logs
            assert isinstance(logs, LogManager)
            res = dict(logs.settings)
            assert res
            logs.settings = logs.settings
        else:
            raise Exception("No Mission Server to test with.")                
    #----------------------------------------------------------------------
    def test_LOGS_clean(self):
        """tests the logic to get a mission server logs property"""
        from arcgis.gis.mission._logs import LogManager
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.logs
            logs = m.logs
            assert isinstance(logs, LogManager)
            assert logs.clean()
            
        else:
            raise Exception("No Mission Server to test with.")                
#@unittest.SkipTest
class TestMissionServer(unittest.TestCase):
    #----------------------------------------------------------------------
    def setUp(self):
        self._gis = GIS(url=URL, username=username, password=password, verify_cert=False)
        self._mss = [server for server in self._gis.admin.servers.list() if isinstance(server, MissionServer)]
    #----------------------------------------------------------------------
    def test_access_mission_server(self):
        """tests the GIS logic to get a mission server"""
        found = False        
        for server in self._gis.admin.servers.list():
            if isinstance(server, MissionServer):
                found = True
                break
        assert found
    #---------------------------------------------------------------------- 
    def test_properties(self):
        """tests the logic to get the properties of the mission server"""
        if len(self._mss) > 0:
            assert self._mss[0].properties
        else:
            raise Exception("No Mission Server to test with.")
    #----------------------------------------------------------------------
    def test_access_mission_INFO(self):
        """tests the logic to get a mission server info property"""
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.info
        else:
            raise Exception("No Mission Server to test with.")
    #----------------------------------------------------------------------
    def test_access_mission_LOGS(self):
        """tests the logic to get a mission server logs property"""
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.logs
        else:
            raise Exception("No Mission Server to test with.")        
    #----------------------------------------------------------------------
    def test_access_mission_SYSTEM(self):
        """tests the logic to get a mission server system property"""
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.system
        else:
            raise Exception("No Mission Server to test with.")        
    #----------------------------------------------------------------------
    def test_access_mission_MACHINE(self):
        """tests the logic to get a mission server machines property"""
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.machine
        else:
            raise Exception("No Mission Server to test with.")        
    #----------------------------------------------------------------------
    def test_access_mission_SECURITY(self):
        """tests the logic to get a mission server security property"""
        if len(self._mss) > 0:
            m = self._mss[0]
            isinstance(m, MissionServer)
            assert m.security
        else:
            raise Exception("No Mission Server to test with.")                
if __name__ == "__main__":
    unittest.main()
    
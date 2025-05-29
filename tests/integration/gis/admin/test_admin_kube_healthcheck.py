import sys
import os
import json
import tempfile

from arcgis.gis import GIS
from arcgis.gis.kubernetes._admin._healthcheck import HealthCheckManager, Suite, SuitesManager,  ReportManager,  Report, ReportJob

#######################################################################
import unittest
from utils.decorators import profiles, integration_test
from utils._logging import enable_verbose_logging

enable_verbose_logging()

def update_question():
    username = "PAPIadmin"
    password = "PAPIletmein01"
    url="https://1150pubbi-1150pubbi.apps.openshift416release.esri.com/web"
    gis = GIS(url=url, username=username, password=password, verify_cert=False, trust_env=True, use_gen_token=True)
    user = gis.users.me
    user.update(security_question='1', security_answer="Amazing_Answer")
    

@integration_test
class TestKubernetesHealthCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        update_question()
        username = "PAPIadmin"
        password = "PAPIletmein01"

        cls.gis = GIS(url="https://1150pubbi-1150pubbi.apps.openshift416release.esri.com/web", username=username, password=password, verify_cert=False, trust_env=True)

    def test_healthcheck_mgr(self):
        admin = self.gis.admin
        assert isinstance(admin.health_check, HealthCheckManager)

    def test_suite_mgr(self):
        admin = self.gis.admin
        hc: HealthCheckManager =  admin.health_check

        assert isinstance(hc.suites, SuitesManager)

    def test_report_mgr(self):
        admin = self.gis.admin
        hc: HealthCheckManager =  admin.health_check

        assert isinstance(hc.reports, ReportManager)

@integration_test
class TestKubernetesSuiteManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        update_question()
        username = "PAPIadmin"
        password = "PAPIletmein01"

        gis = GIS(url="https://1150pubbi-1150pubbi.apps.openshift416release.esri.com/web", username=username, password=password, verify_cert=False, trust_env=True)
        cls.suitemgr = gis.admin.health_check.suites


    def test_manager_list(self):
        for suite in self.suitemgr.list():
            assert isinstance(suite, Suite)
    def test_manager_get_by_id(self):
        suite = self.suitemgr.get("BSHC-001")
        assert isinstance(suite, Suite)
    def test_manager_get_by_name(self):
        suite = self.suitemgr.get("Basic health checks")
        assert isinstance(suite, Suite)    
    def test_suite_id(self):
        suite = self.suitemgr.get("BSHC-001")
        assert isinstance(suite, Suite)
        assert suite.suite_id
    def test_suite_name(self):
        suite = self.suitemgr.get("BSHC-001")
        assert isinstance(suite, Suite)
        assert suite.name

    def test_suite_properties(self):
        suite = self.suitemgr.get("BSHC-001")
        assert isinstance(suite, Suite)
        assert suite.properties        

@integration_test
class TestKubernetesReportManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        update_question()
        username = "PAPIadmin"
        password = "PAPIletmein01"

        gis = GIS(url="https://1150pubbi-1150pubbi.apps.openshift416release.esri.com/web", username=username, password=password, verify_cert=False, trust_env=True)
        cls.reportmgr = gis.admin.health_check.reports
        cls.suitemgr = gis.admin.health_check.suites
    def test_query(self):
        """tests the query operation"""
        rm: ReportManager = self.reportmgr
        for report in rm.query():
            assert isinstance(report, Report)

    def test_run(self):
        import uuid
        rm: ReportManager = self.reportmgr
        sm = self.suitemgr
        suite = sm.get("BSHC-001")
        rm.run(suite=suite, name=f"AmazingTest{uuid.uuid4().hex[:3]}")
        

    def test_run_and_delete(self):
        import uuid
        unique_name = uuid.uuid4().hex[:3]
        rm: ReportManager = self.reportmgr
        sm = self.suitemgr
        suite = sm.get("BSHC-001")
        job = rm.run(suite=suite, name=f"AmazingTest{unique_name}")
        assert isinstance(job, ReportJob)
        report = list(rm.query())[-1]
        assert report.delete()



if __name__ == "__main__":
    unittest.main()
    
import unittest
import unittest.mock
from unittest.mock import MagicMock
import sys, datetime


from arcgis.gis import GIS
profiles = [ 'your_kubernetes_profile']  # profile names go here #'your_online_profile', 'your_enterprise_profile',
VERIFY_CERT = False # Boolean T/F

class TestLogsAdminTemplate(unittest.TestCase):
    """
    Tests the Kubernetes Admin Logs Functions
    """

    def test_admin_logs(self):
        """runs the admin.logs tests for Kubernetes"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            admin = gis.admin
            assert admin.logs
            logs = admin.logs
            assert logs
            res = logs.query(start_time=datetime.datetime.now() - datetime.datetime.now() - datetime.timedelta(days=1))
            assert res
            assert logs.edit('DEBUG')
            assert logs.settings
            assert admin.logs.clean()
        pass


if __name__ == "__main__":
    unittest.main()

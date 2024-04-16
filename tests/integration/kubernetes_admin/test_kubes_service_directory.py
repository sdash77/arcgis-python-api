import unittest
import unittest.mock
from unittest.mock import MagicMock
import datetime
from utils.decorators import integration_test

from arcgis.gis import GIS

profiles = [
    "your_kubernetes_profile"
]  # profile names go here #'your_online_profile', 'your_enterprise_profile',
VERIFY_CERT = False  # Boolean T/F


@integration_test
class TestLogsAdminTemplate(unittest.TestCase):
    """
    Tests the Kubernetes Admin Logs Functions
    """

    def test_services_directory(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            admin = gis.admin
            assert admin.services_catalog

    def test_services_directory_folder(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            admin = gis.admin
            assert admin.services_catalog.folders

    def test_services_directory_list(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            admin = gis.admin
            assert admin.services_catalog.list("System")

    def test_services_directory_get_find(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            admin = gis.admin
            assert admin.services_catalog.get(name="PublishingTools", folder="System")
            assert admin.services_catalog.find("PublishingTools", "System")

    def test_admin_sd(self):
        """runs the admin.logs tests for Kubernetes"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            sc = gis.admin.services_catalog
            result = sc.publish_sd(
                r"\\qalab_server\seleniumdata\v109\GPServer11\sd\Release\CWT_ByVal_s11_FileParamTest.sd"
            )
            assert result


if __name__ == "__main__":
    unittest.main()

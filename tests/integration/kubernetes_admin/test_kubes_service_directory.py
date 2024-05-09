import os
import unittest
from utils.decorators import integration_test, profiles
from integration.config import get_resource_path
from arcgis.gis import GIS
from utils._logging import enable_verbose_logging


enable_verbose_logging()


@profiles.admin_k8s
@integration_test
class TestLogsAdminTemplate(unittest.TestCase):
    """
    Tests the Kubernetes Admin Logs Functions
    """

    def test_services_directory(self):
        admin = self.gis.admin
        assert admin.services_catalog

    def test_services_directory_folder(self):
        admin = self.gis.admin
        assert admin.services_catalog.folders

    def test_services_directory_list(self):
        admin = self.gis.admin
        assert admin.services_catalog.list("System")

    def test_services_directory_get_find(self):
        admin = self.gis.admin
        assert admin.services_catalog.get(name="PublishingTools", folder="System")
        assert admin.services_catalog.find("PublishingTools", "System")

    def test_admin_sd(self):
        """tests publishing a service definition on k8s"""
        sd_path = get_resource_path('seleniumdata/sd/CWT_ByVal_s11_SimpleParamTest.sd')

        sc = self.gis.admin.services_catalog
        result = sc.publish_sd(sd_path)
        assert result

        if result is True:
            try:
                item = self.gis.content.search('ByVal_s11_SimpleParamTest')[0]
                item.delete()
            except Exception:
                print("Cannot delete sd service.")


if __name__ == "__main__":
    unittest.main()

import os
import unittest
from utils.decorators import integration_test, profiles
from arcgis.gis import GIS
from integration.config import K8S_LICENSES_PATH


@profiles.admin_k8s
@integration_test
class TestLicense(unittest.TestCase):
    """tests the license manager"""

    @classmethod
    def setUpClass(cls):
        """
        Get class test asset location and data
        Setup GIS connection
        Store License information for an org
        """
        cls.K8S_LICENSE_PATH = K8S_LICENSES_PATH
        cls.lic_file1_path = 'AllUTs_AllAddOnApps_K8S.json'
        cls.lic_file1 = os.path.join(K8S_LICENSES_PATH, cls.lic_file1_path)
        cls.lic_file2_path = 'CreatorViewerUTs_NoAddOnApps_K8S.json'
        cls.lic_file2 = os.path.join(K8S_LICENSES_PATH, cls.lic_file2_path)

        cls.org = cls.gis.admin.organizations.orgs[0]
        cls.lic1 = cls.org.license

    def test_import_license(self):
        """tests the license file import"""
        res1 = self.lic1.import_license(self.lic_file1)
        assert bool(res1)

    def test_license_properties(self):
        """tests license properties"""
        assert bool(self.lic1)
        assert self.lic1.properties
        assert isinstance(self.lic1.properties, dict)
        assert bool(self.lic1.properties)
        prop = ["licenseManagerInfo", "maximumRegisteredMembers", "version"]
        assert [p in self.lic1.properties.keys() for p in prop]

    def test_validate_license(self):
        """tests license file validation"""
        res2 = self.lic1.validate(self.lic_file2)
        assert isinstance(res2, dict)
        assert bool(res2)

        res3 = self.lic1.validate(self.lic_file2, list_ut=True)
        assert isinstance(res3, dict)
        assert bool(res3)
        self.assertEqual(*res3, "userTypes")

    def test_update_license_manager(self):
        """tests updates to license manager"""
        config = {"hostname": "change.me1", "port": 1234}
        assert self.lic1.update_license_manager(config=config)
        org2 = self.gis.admin.organizations.orgs[0]
        lic2 = org2.license
        info = lic2.properties["licenseManagerInfo"]
        self.assertDictEqual(config, info)


if __name__ == "__main__":
    unittest.main()

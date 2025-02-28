import os
import unittest
from utils.decorators import integration_test, profiles
from arcgis.gis import GIS
from integration.config import get_resource_path


@unittest.skip("Skip until get back to our own k8s environment")
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
        cls.resources_root = get_resource_path('authorization_files/k8s')
        cls.lic_file1 = get_resource_path(f'{cls.resources_root}/AllUTs_AllAddOnApps_K8S.json')
        cls.lic_file2 = get_resource_path(f'{cls.resources_root}/CreatorViewerUTs_NoAddOnApps_K8S.json')

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

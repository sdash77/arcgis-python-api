import unittest
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser

# Import the module
try:
    import arcgis
    from arcgis.gis import GIS
except ImportError:
    print("API import error. Quitting test")
    raise(exit())


class TestLicense(unittest.TestCase):
    """tests the license manager"""

    @classmethod
    def setUpClass(cls):
        """
        Get class test asset location and data
        Setup GIS connection
        Store License information for an org
        :return:
        """
        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.data_folder_path = _conf_reader2['license_data']['data_folder']
        cls.lic_file1 = cls.data_folder_path + _conf_reader2['license_data']['lic_file1']
        cls.lic_file2 = cls.data_folder_path + _conf_reader2['license_data']['lic_file2']

        _profiles = ['your_kubernetes_profile']  # profile names go here #'your_online_profile', 'your_enterprise_profile',
        cls.k_gis = GIS(profile=_profiles[0], verify_cert=False, trust_env=True)
        cls.org = cls.k_gis.admin.organizations.orgs[0]
        cls.lic1 = cls.org.license

    def test_import_license(self):
        """tests the license file import"""
        res1 = self.lic1.import_license(self.lic_file2)
        assert bool(res1)

    def test_license_properties(self):
        """tests license properties"""
        assert bool(self.lic1)
        assert self.lic1.properties
        assert isinstance(self.lic1.properties, dict)
        assert bool(self.lic1.properties)
        prop = ['licenseManagerInfo', 'maximumRegisteredMembers', 'version']
        assert [p in self.lic1.properties.keys() for p in prop]

    def test_validate_license(self):
        """tests license file validation"""
        res2 = self.lic1.validate(self.lic_file1)
        assert isinstance(res2, dict)
        assert bool(res2)

        res3 = self.lic1.validate(self.lic_file1, list_ut=True)
        assert isinstance(res3, dict)
        assert bool(res3)
        self.assertEqual(*res3, 'userTypes')

    def test_update_license_manager(self):
        """tests updates to license manager"""
        config = {"hostname": "change.me1", "port": 1234}
        assert self.lic1.update_license_manager(config=config)
        org2 = self.k_gis.admin.organizations.orgs[0]
        lic2 = org2.license
        info = lic2.properties['licenseManagerInfo']
        self.assertDictEqual(config, info)


if __name__ == "__main__":
    unittest.main()
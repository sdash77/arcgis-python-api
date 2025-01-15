import sys

sys.path.insert(0, r"C:\SVN\geosaurus_issue_12518\tests")
sys.path.insert(1, r"C:\SVN\geosaurus_issue_12518\src")
import unittest
from utils.decorators import profiles, integration_test
from arcgis.gis.admin import AGOLAdminManager, PortalAdminManager


@profiles.admin_enterprise_and_agol
@integration_test
class TestLicenseClass(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if self.gis._is_agol:
            self.admin = AGOLAdminManager(gis=self.gis)
        else:
            self.admin = PortalAdminManager(
                url=f"{self.gis.url}/sharing/rest/", gis=self.gis
            )

    @unittest.skip("said so")
    def test_offline_report(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert lic.offline_report

    @unittest.skip("said so")
    def test_get_license(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert lic

    @unittest.skip("said so")
    def test_properties(self):
        assert self.admin.license.properties

    @unittest.skip("said so")
    def test_report(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert lic.report

    @unittest.skip("said so")
    def test_check(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert isinstance(lic.check(self.gis._username), list)

    @unittest.skip("said so")
    def test_user_entitlement(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert isinstance(lic.user_entitlement(self.gis._username), dict)

    def test_user_entitlement_check(self):
        user = self.gis.users.me
        lm = self.admin.license
        lic = lm.get("ArcGIS Pro")
        assert lic.check(user) == lic.user_entitlement(user)['entitlements']


if __name__ == "__main__":
    unittest.main()

import unittest
from utils.decorators import profiles, integration_test
from arcgis.gis.admin import AGOLAdminManager, PortalAdminManager
import pandas as pd


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

    def test_offline_report(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert isinstance(lic.offline_report, pd.DataFrame)
            assert "Username" in lic.offline_report.columns

    def test_get_license(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert lic

    def test_properties(self):
        assert self.admin.license.properties

    def test_report(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert isinstance(lic.report, pd.DataFrame)

    def test_expired_license(self):
        assert self.admin.license.expired_licenses

    def test_check(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert isinstance(lic.check(self.gis._username), list)

    def test_user_entitlement(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert isinstance(lic.user_entitlement(self.gis._username), dict)

    def test_user_entitlement_check(self):
        user = self.gis.users.me
        lm = self.admin.license
        lic = lm.get("ArcGIS Pro")
        if lic is None:
            self.skipTest("The ArcGIS Pro license is not available, skipping.")
        assert lic.check(user) == lic.user_entitlement(user)['entitlements']


if __name__ == "__main__":
    unittest.main()

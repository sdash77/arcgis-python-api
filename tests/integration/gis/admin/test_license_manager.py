import unittest
from utils.decorators import profiles
from arcgis.gis.admin import AGOLAdminManager, PortalAdminManager

@profiles.admin_enterprise_and_agol
# @integration_test
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
            assert lic.offline_report

    def test_get_license(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert lic
    
    def test_properties(self):
        assert self.admin.license.properties
    
    def test_report(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert lic.report

    def test_check(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert lic.check(self.gis.username)
    
    def test_user_entitlement(self):
        licenses = self.admin.license.all()
        for lic in licenses:
            assert isInstance(lic.user_entitlement(self.gis._username), dict)
   
   
   if __name__ == "__main__":
            unittest.main()
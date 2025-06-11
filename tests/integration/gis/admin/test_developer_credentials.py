import sys
sys.path.insert(0, r"C:\svn\geosaurus_master\src")
sys.path.insert(1, r"C:\svn\geosaurus_master\tests")
import unittest
import datetime as _dt
from utils.decorators import integration_test, from_to_profiles, profiles
from utils._logging import enable_verbose_logging

from arcgis.gis.admin._stokenmgr import DeveloperCredentialManager, DeveloperCredential,  TokenPrivilege


enable_verbose_logging()


@profiles.admin_enterprise
@integration_test
class TestDeveloperCredentialsEnterprise(unittest.TestCase):
    """tests developer credentials"""
    def test_manager(self):
        if self.gis.version >= [2025, 1]:
            assert isinstance(self.gis.admin.developer_credentials, DeveloperCredentialManager)
        else:
            assert self.gis.admin.developer_credentials is None
    
    def test_list(self):
        dc: DeveloperCredentialManager =  self.gis.admin.developer_credentials
        if dc:
            for token in mgr.list():
                assert isinstance(token, DeveloperCredential)
                break
    
    def test_developer_credential(self):
        mgr: DeveloperCredentialManager =  self.gis.admin.developer_credentials
        if mgr:
            expiration = _dt.datetime.now() + _dt.timedelta(weeks=35)
            credential: DeveloperCredential = mgr.create(title="ArcGIS Python API Token",
                       privileges=[TokenPrivilege.FEATURES_USER_EDIT,
                                   TokenPrivilege.PORTAL_ADMIN_CREATEGPWEBHOOK],
                       referers=['http'],
                       expiration=expiration)
            assert isinstance(credential, DeveloperCredential)
            token = credential.generate_token()
            assert token
            assert credential.revoke(1)
            assert credential.delete()

@profiles.admin_agol
@integration_test
class TestDeveloperCredentialsAGOL(unittest.TestCase):
    """tests developer credentials"""
    def test_manager(self):
        if self.gis.version >= [2025, 1]:
            assert isinstance(self.gis.admin.developer_credentials, DeveloperCredentialManager)
        else:
            assert self.gis.admin.developer_credentials is None
    
    def test_list(self):
        mgr: DeveloperCredentialManager =  self.gis.admin.developer_credentials
        if mgr:
            for token in mgr.list():
                assert isinstance(token, DeveloperCredential)
                break
    
    def test_developer_credential(self):
        mgr: DeveloperCredentialManager =  self.gis.admin.developer_credentials
        if mgr:
            expiration = _dt.datetime.now() + _dt.timedelta(weeks=35)
            credential: DeveloperCredential = mgr.create(title="ArcGIS Python API Token",
                       privileges=[TokenPrivilege.FEATURES_USER_EDIT,
                                   TokenPrivilege.PORTAL_ADMIN_CREATEGPWEBHOOK],
                       referers=['http'],
                       expiration=expiration)
            assert isinstance(credential, DeveloperCredential)
            token = credential.generate_token()
            assert token
            assert credential.revoke(1)
            assert credential.delete()

    
if __name__ == "__main__":
    unittest.main()
"""
GIS Connection Testing for Pro and NBAUTH files
"""
import os
import sys
sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork\src")
import imp
import json
import tempfile 
import unittest
import unittest.mock
from unittest.mock import MagicMock

class ArcPyMock(object):
    """mocking the arcpy module (ha ha ha)"""
    @staticmethod
    def GetActivePortalURL(*args, **kwargs):
        return "DO I EXIST?"
    @staticmethod
    def GetSigninToken(*args, **kwargs):
        return "DO I EXIST?"    
try:
    raise ImportError("missing")
    import imp
    imp.find_module('arcpy')
    _HAS_ARCPY = True
except ImportError:
    sys.modules['arcpy'] = ArcPyMock()
    import arcpy
    _HAS_ARCPY = True
import arcgis
import pytest
from arcgis.gis import GIS
from arcgis.gis import ProfileManager

###########################################################################
@unittest.mock.patch(target='__main__.arcpy', new=ArcPyMock, create=True)
class TestProHomeLogic(unittest.TestCase):
    """Tests the 'home' logic"""
    #----------------------------------------------------------------------
    def test_home_pro_login(self, *args,**kwargs):
        """tests the login method using the Pro login method from `home`"""
        import arcpy
        gis_source = GIS(profile='your_enterprise_profile', verify_cert=False)
        url = gis_source._url
        token_resp = (
            gis_source
            ._con
            .post(gis_source._con._token_url, {
                "username" : gis_source.users.me.username,
                "password" : ProfileManager()._securely_get_password('your_enterprise_profile'),
                "referer" : "http",
                "expiration" : 1440,
                "f" : 'json'
                }, add_token=False))
        
        if token_resp is None:
            raise Exception("Could not authenticate, please verify `your_enterprise_profile` exists on the system.")
        token_response = {'token': f"{token_resp['token']}", 
                          'referer': 'http', 
                          'expires': token_resp['expires']}
        del gis_source
        with unittest.mock.patch.object(arcpy, "GetActivePortalURL", return_value=url):
            with unittest.mock.patch.object(arcpy, "GetSigninToken", return_value=token_response):
                gis = GIS(url='home', verify_cert=False) 
                assert gis.users.me 
                del gis
    #----------------------------------------------------------------------
    def test_pro_login(self, *args,**kwargs):
        """tests the login method using the Pro """
        import arcpy
        gis_source = GIS(profile='your_enterprise_profile', verify_cert=False)
        url = gis_source._url
        token_resp = (
            gis_source
            ._con
            .post(gis_source._con._token_url, {
                "username" : gis_source.users.me.username,
                "password" : ProfileManager()._securely_get_password('your_enterprise_profile'),
                "referer" : "http",
                "expiration" : 1440,
                "f" : 'json'
                }, add_token=False))
        
        if token_resp is None:
            raise Exception("Could not authenticate, please verify `your_enterprise_profile` exists on the system.")
        token_response = {'token': f"{token_resp['token']}", 
                          'referer': 'http', 
                          'expires': token_resp['expires']}
        del gis_source
        with unittest.mock.patch.object(arcpy, "GetActivePortalURL", return_value=url):
            with unittest.mock.patch.object(arcpy, "GetSigninToken", return_value=token_response):
                gis = GIS(url='pro', verify_cert=False) 
                assert gis.users.me    
                del gis
###########################################################################
class TestHomeNBAUTHLogic(unittest.TestCase):
    """Test the 'home' logic for NBAUTH file"""
    def test_home_nbauth_login(self):
        """tests the login method using the NBAUTH logic (pre-10.8.1 style of NB_AUTH_FILE"""
        gis_source = GIS(profile='your_enterprise_profile', verify_cert=False)
        private_url = gis_source._url
        public_url = gis_source._url
        referer = ""
        token_resp = (
            gis_source
            ._con
            .post(gis_source._con._token_url, {
                "username" : gis_source.users.me.username,
                "password" : ProfileManager()._securely_get_password('your_enterprise_profile'),
                "referer" : json.dumps(referer),
                "expiration" : 1440,
                "f" : 'json'
                }, add_token=False)
            .get("token", None)
        )
        if token_resp is None:
            raise Exception("Could not authenticate, please verify `your_enterprise_profile` exists on the system.")
        del gis_source
        
        with tempfile.TemporaryDirectory() as d:
            token = json.dumps(
                {"token":f"{token_resp}",
                 "referer":"",
                 "privatePortalUrl": public_url,
                 "publicPortalUrl": public_url})
            f = open(os.path.join(d, ".nbauth.json"), 'w')
            f.write(token)
            f.close()
            del f            
            os.getenv
            with unittest.mock.patch.dict('os.environ', {'NB_AUTH_FILE': os.path.join(d, ".nbauth.json")}, clear=True):
                with unittest.mock.patch.object(os, "getenv", return_value=os.path.join(d, ".nbauth.json")):
                    self.assertEqual(os.environ.get('NB_AUTH_FILE'), os.path.join(d, ".nbauth.json"))
                    self.assertEqual(len(os.environ), 1)                  
                    gis = GIS(url='home', verify_cert=False)
                    assert gis._con._expiration == 10080 
                    assert gis.users.me
                    del gis
    #----------------------------------------------------------------------
    def test_home_nbauth_login_expiration_stated(self):
        """
        tests the login method using the NBAUTH logic with expiration key 
        present (new style 10.8.1+)
        """
        gis_source = GIS(profile='your_enterprise_profile', verify_cert=False)
        private_url = gis_source._url
        public_url = gis_source._url
        referer = ""
        token_resp = (
            gis_source
            ._con
            .post(gis_source._con._token_url, {
                "username" : gis_source.users.me.username,
                "password" : ProfileManager()._securely_get_password('your_enterprise_profile'),
                "referer" : json.dumps(referer),
                "expiration" : 1440,
                "f" : 'json'
                }, add_token=False)
            .get("token", None)
        )
        if token_resp is None:
            raise Exception("Could not authenticate, please verify `your_enterprise_profile` exists on the system.")
        del gis_source
        
        with tempfile.TemporaryDirectory() as d:
            token = json.dumps(
                {"token":f"{token_resp}",
                 "referer":"",
                 "privatePortalUrl": public_url,
                 "publicPortalUrl": public_url,
                 "expiration": 20160})
            f = open(os.path.join(d, ".nbauth.json"), 'w')
            f.write(token)
            f.close()
            del f            
            os.getenv
            with unittest.mock.patch.dict('os.environ', {'NB_AUTH_FILE': os.path.join(d, ".nbauth.json")}, clear=True):
                with unittest.mock.patch.object(os, "getenv", return_value=os.path.join(d, ".nbauth.json")):
                    self.assertEqual(os.environ.get('NB_AUTH_FILE'), os.path.join(d, ".nbauth.json"))
                    self.assertEqual(len(os.environ), 1)                  
                    gis = GIS(url='home', verify_cert=False)
                    assert gis._con._expiration == 20160
                    assert gis.users.me
                    del gis

if __name__ == "__main__":
    unittest.main()
"""profile testing"""
import os
import uuid
import unittest
import pytest
from arcgis.gis import GIS
from arcgis.gis._impl._profile import ProfileManager
import pandas as pd
PROFILES = ['your_online_profile', 'your_enterprise_profile']
DUMMY_PROFILE = "FAKE" + uuid.uuid4().hex[:5]

class TestProfileManager(unittest.TestCase):
    """tests the profile manager"""
    def test_accessing(self):
        """tests getting the manager"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            assert isinstance(gis.profiles, ProfileManager)
    def test_list(self):
        """tests list method"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            assert isinstance(gis.profiles, ProfileManager)    
            pm = gis.profiles
            assert isinstance(pm.list(), list)
            assert isinstance(pm.list(as_df=True), pd.DataFrame)
    def test_create_delete_profiles(self):
        """tests creating/deleting a profile"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            assert isinstance(gis.profiles, ProfileManager)    
            pm = gis.profiles           
            pm.create(profile=DUMMY_PROFILE, 
                      url=gis._url, 
                      username=gis._username, 
                      password=gis._password, 
                      key_file=gis._key_file, 
                      cert_file=gis._cert_file, 
                      client_id=gis._client_id)
            assert DUMMY_PROFILE in pm.list()
            pm.delete(DUMMY_PROFILE)
            assert DUMMY_PROFILE not in pm.list()
    def test_update(self):
        """tests the update logic"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False)
            assert isinstance(gis.profiles, ProfileManager)    
            pm = gis.profiles       
            pm.create(profile=DUMMY_PROFILE, 
                      url=gis._url, 
                      username=gis._username, 
                      password=gis._password, 
                      key_file=gis._key_file, 
                      cert_file=gis._cert_file, 
                      client_id=gis._client_id)            
            pm.update(profile=DUMMY_PROFILE,
                      url="AFAKEVALUE")
            assert pm.get(profile=DUMMY_PROFILE)['url'] == "AFAKEVALUE"
            pm.delete(DUMMY_PROFILE)
            assert DUMMY_PROFILE not in pm.list()            

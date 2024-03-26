"""
Tests the ability to specify the Generate Token Authentication Handler
"""
import sys
import unittest
from arcgis.gis import GIS, ProfileManager
from arcgis.auth import EsriBuiltInAuth, EsriGenTokenAuth
from utils.decorators import integration_test

PROFILES = ["your_online_profile", "your_enterprise_profile"]


@integration_test
class TestUseGenTokenGIS(unittest.TestCase):
    def test_use_gen_token_true_enterprise(self):
        """tests using the generate token"""
        gis = GIS(profile=PROFILES[1], verify_cert=False, use_gen_token=True)
        assert isinstance(gis._portal.con._session.auth, EsriGenTokenAuth)

    def test_use_gen_token_true_agol(self):
        """tests using the generate token"""
        gis = GIS(profile=PROFILES[0], verify_cert=False, use_gen_token=True)
        assert isinstance(gis._portal.con._session.auth, EsriGenTokenAuth)

    def test_use_gen_token_false(self):
        """tests using the generate token"""
        gis = GIS(profile=PROFILES[0], verify_cert=False, use_gen_token=False)
        assert isinstance(gis._portal.con._session.auth, EsriBuiltInAuth)


if __name__ == "__main__":
    unittest.main()

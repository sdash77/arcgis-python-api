import unittest
from arcgis.gis import GIS
###########################################################################
class TestGISExpiration(unittest.TestCase):
    """Tests the setting of the expiration value"""
    #----------------------------------------------------------------------
    def test_set_expiration(self):
        """setting the expiration value"""
        gis = GIS(profile='your_enterprise_profile', expiration=7)
        assert gis._con._expiration == 7
        gis._con.token
        assert gis._con._create_time
    #----------------------------------------------------------------------
    def test_setting_expiration_none(self):
        """set if expiration is set to None"""
        gis = GIS(profile='your_enterprise_profile', expiration=None)
        assert gis._con._expiration == 60
    #----------------------------------------------------------------------
    def test_default_setting_expiration_less_than_6(self):
        """set if expiration is less than 6, it should set it to 6"""
        gis = GIS(profile='your_enterprise_profile', expiration=1)
        assert gis._con._expiration > 5
    #----------------------------------------------------------------------
    def test_default_setting_expiration(self):
        """ensures the default expiration is 60"""
        gis = GIS(profile='your_enterprise_profile')
        assert gis._con._expiration == 60

if __name__ == '__main__':
    unittest.main()
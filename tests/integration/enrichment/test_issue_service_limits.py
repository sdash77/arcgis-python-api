import os
import sys

import unittest
import pytest
import pandas as pd
from pandas import Timestamp
from arcgis.gis import GIS
from arcgis.geoenrichment import service_limits
   
###########################################################################
class TestGEHorizontalScaling(unittest.TestCase):
    def test_get_service_limits(self):
        """tests getting the service limits"""
        
        for profile in ['your_online_profile', 'your_enterprise_profile']:
            gis = GIS(profile=profile, verify_cert=False)
            info = service_limits()
            assert isinstance(info, pd.DataFrame)
    
if __name__ == "__main__":
    unittest.main()
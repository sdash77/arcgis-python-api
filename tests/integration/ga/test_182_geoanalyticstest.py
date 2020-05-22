import os
import sys

import unittest
import pytest
import pandas as pd
from pandas import Timestamp

from arcgis.gis import GIS
import arcgis.geoanalytics
from arcgis.geoanalytics.manage_data import copy_to_data_store

try:
    url = "https://gplinux.esri.com/portal"
    username = "admin"
    password = 'esri.agp'
    ITEMID = "340be039723244db9e0f3bc10246e1ce"
    gis = GIS(url=url, username=username, password=password, verify_cert=False)
    SKIP_TESTS = False
except:
    SKIP_TESTS = True
###########################################################################
@unittest.skipIf(SKIP_TESTS == True,
                 reason='Cannot connect to the GIS')
class TestIssue1224BDSPrevention(unittest.TestCase):
    #----------------------------------------------------------------------
    def test_bsd_item_error_raised(self):
        """
        Tests that a BDS Item raises an error when given.
        """
        if len(gis.content.search("the_output_that_should_fail")) > 0:
            for i in gis.content.search("the_output_that_should_fail"):
                i.delete()
        big_data_file_share_name = "bigDataFileShares_pyTest"
        bigdata_fileshares = gis.content.search("*", item_type = "big data file share", max_items=20)
        data_item = next(x for x in bigdata_fileshares if x.title=="bigDataFileShares_pyTest")
        with self.assertRaises(Exception) as context:
            copy_to_data_store(data_item)
        assert type(context.exception) == ValueError
        assert context.exception.args[0].lower().find("please pass the layer") > -1
    #----------------------------------------------------------------------
    def test_bsd_layer_no_error_raised(self):
        """
        Tests that a BDS Item's Layer does not raises an error when given.
        """
        if len(gis.content.search("the_output_that_should_fail")) > 0:
            for i in gis.content.search("the_output_that_should_fail"):
                i.delete()
        big_data_file_share_name = "bigDataFileShares_pyTest"
        bigdata_fileshares = gis.content.search("*", item_type = "big data file share", max_items=20)
        data_item = next(x for x in bigdata_fileshares if x.title=="bigDataFileShares_pyTest")
        data_item = data_item.layers[0]
        item = copy_to_data_store(data_item)
        assert item.delete()

    #----------------------------------------------------------------------

        
if __name__ == "__main__":
    unittest.main()
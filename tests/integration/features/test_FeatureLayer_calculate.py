import os
import sys
import unittest
import concurrent.futures

import pytest

#sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_fl_108_calculate\src")
from arcgis.gis import GIS, ContentManager
from arcgis.features import FeatureLayer



profiles = ['your_online_profile']


class TestFeatureLayerCalculate(unittest.TestCase):
    
    def test_calculate_basic(self):
        """tests a simple calculate method"""
        fp = "./calculate_sd.zip"
        if os.path.isfile(path=fp):
            for profile in profiles:
                gis = GIS(profile=profile, verify_cert=False)
                items = gis.content.search("calculate_sd.zip")
                if len(items) > 0:
                    for item in items:
                        try:
                            item.delete()
                        except:
                            pass
                cm = gis.content
                isinstance(cm, ContentManager)
                add_item = cm.add(item_properties={'title' : "calculate_sd", "type" : "File Geodatabase"}, data=fp)
                pitem = add_item.publish()
                fl = pitem.layers[0]
                res = fl.calculate(where="ObjectID < 519",
                                   calc_expression={"field": "FIPS_CNTRY", "value" : "R1"},
                                   future=False)                
                assert res
                assert pitem.delete()
                assert add_item.delete()
                del gis

    def test_calculate_async(self):
        """tests a simple calculate method using the asynchronous method"""
        fp = "./calculate_sd.zip"
        if os.path.isfile(path=fp):
            for profile in profiles:
                gis = GIS(profile=profile, verify_cert=False)
                items = gis.content.search("calculate_sd.zip")
                if len(items) > 0:
                    for item in items:
                        try:
                            item.delete()
                        except:
                            pass
                items = gis.content.search("calculate_sd")
                if len(items) > 0:
                    for item in items:
                        try:
                            item.delete()
                        except:
                            pass
                cm = gis.content
                isinstance(cm, ContentManager)
                add_item = cm.add(item_properties={'title' : "calculate_sd", "type" : "File Geodatabase"}, data=fp)
                pitem = add_item.publish()
                fl = pitem.layers[0]
                res = fl.calculate(where="ObjectID < 519",
                                   calc_expression={"field": "FIPS_CNTRY", "value" : "R1"},
                                   future=True)                
                assert res
                assert isinstance(res, concurrent.futures.Future)
                assert res.result()
                assert pitem.delete()
                assert add_item.delete()
                del gis

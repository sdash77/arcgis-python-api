import os
import sys
import string
import random
import unittest
import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.features.analysis import aggregate_points



def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class TestPassingDictionaries(unittest.TestCase):
    """Tests passing in output names as dictionaries to WebGIS Tools"""
    def test_analysis_on_existing_fl(self):
        """tests adding to an existing feature layer"""
        gis = GIS("https://deldev.maps.arcgis.com", "demos_deldev", "DelDevs12", verify_cert=False)
        point_item = gis.content.get('1923d4e74ac947dab4f8c94d2c2a7a9c')
        polygon_item = gis.content.get('78778fe9e4244f71b8194122d1f228ae')
        point_layer = point_item.layers[0]
        polygon_layer = polygon_item.layers[3]
        # 1). Step 1 - create an initial output:
        agg_init = aggregate_points(point_layer=point_layer,
                                    polygon_layer=polygon_layer,
                                    keep_boundaries_with_no_points=False,
                                    summary_fields=["DeclValNu mean","DeclValNu2 mean"],
                                    group_by_field='Declared_V',
                                    output_name="agg"+id_generator())
        existing_lyr = agg_init.layers[0]
        # 2). Step 2. Take output from step 1 and pass in the feature layer.
        agg_add_item = aggregate_points(point_layer=point_layer,
                                        polygon_layer=polygon_layer,
                                        keep_boundaries_with_no_points=False,
                                        summary_fields=["DeclValNu mean","DeclValNu2 mean"],
                                        group_by_field='Declared_V',
                                        output_name=existing_lyr) 
        assert agg_add_item.itemid == agg_init.itemid
        assert agg_add_item.layers[0].url == agg_init.layers[0].url
        assert agg_add_item.delete()
        
if __name__ == "__main__":
    unittest.main()
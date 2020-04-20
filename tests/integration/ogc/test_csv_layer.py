import os
import sys
import unittest
import pytest
import pandas as pd
from arcgis.gis import GIS
from arcgis.gis._ogc import CSVLayer

csv_url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.csv'


class TestCSVLayer(unittest.TestCase):
    """Runs the tests for the CSV Layer"""
    def test_csv_layer_url(self):
        csv = CSVLayer(csv_url)
        assert isinstance(csv, CSVLayer)
        assert csv.fields
        assert csv.latitude
        assert csv.longitude

        assert isinstance(csv.df, pd.DataFrame)
        assert csv.delimiter
        assert csv.copyright is None
        assert csv.sql_expression is None
        assert csv.renderer
        assert str(csv).find("<CSV") > -1
        assert csv.title
        assert csv.__webmap__
    def test_csv_layer_item(self):
        gis = GIS()
        items = [gis.content.get("3f0f20ae77c0447cb5fa2a15038d0520")]
        if len(items) > 0:


            csv = CSVLayer(items[0])
            assert isinstance(csv, CSVLayer)
            assert csv.fields
            assert csv.latitude is None or csv.latitude
            assert csv.longitude is None or csv.longitude
            assert isinstance(csv.df, pd.DataFrame)
            assert csv.delimiter
            assert csv.copyright is None
            assert csv.sql_expression is None
            assert csv.renderer
            assert str(csv).find("<CSV") > -1
            assert csv.title
            assert csv.__webmap__




if __name__ == "__main__":
    unittest.main()
"""
Performs Unittests on GeoEnrichment

WARNING THESE UNIT TESTS WILL COST CREDITS ON AGOL
"""
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import unittest
import pandas as pd
import os, shutil
from arcgis.gis import GIS
from arcgis import geoenrichment
from arcgis.features import SpatialDataFrame
########################################################################
## SETUP VALUES                                                       ##
########################################################################
USERNAME = None
PASSWORD = None
URL = None
VERIFY = False
########################################################################


if USERNAME is not None and PASSWORD is not None:
    ########################################################################
    class ge_unittest(unittest.TestCase):
        """
        AGOL GeoEnrichment Tests
        """
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_ge_coutry_df(self):
            """tests if countries returned as a Pandas' DataFrame"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)
            res = geoenrichment.list_countries(gis=gis)
            self.assertIsInstance(res, pd.DataFrame)
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_ge_report_metadata(self):
            """tests report metadata"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)

            df_countries = geoenrichment.list_countries(gis=gis)
            cc = df_countries.iloc[0]['Country_Code']
            fn = df_countries.iloc[0]['Full_Name']
            self.assertIsInstance(geoenrichment.report_metadata(cc), pd.DataFrame)
            self.assertIsInstance(geoenrichment.report_metadata(fn), pd.DataFrame)
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_find_report(self):
            """test the find report"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)
            self.assertIsInstance(geoenrichment.find_report(country="CA"), pd.DataFrame)
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_get_variables(self):
            """tests get variables"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)

            self.assertIsInstance(geoenrichment.get_variables(country="US"), pd.DataFrame)
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_data_collections(self):
            """tests data collections"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)

            r = geoenrichment.data_collections(country="US", dataset="EducationalAttainment", variables=["percent"])
            self.assertIsInstance(r, pd.DataFrame)
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_select_businesses(self):
            """tests select businesses"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)

            r = geoenrichment.select_businesses(search_string="Fireproofing",
                              return_geometry=True,
                        spatial_filter={"Locations":["NY,TONAWANDA,14150","KY,LOUISVILLE,40204","WA,SEATTLE,98108"]})
            self.assertIsInstance(r, (SpatialDataFrame, pd.DataFrame))
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_standard_geography_query(self):
            """tests standard_geography_query"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)

            r = geoenrichment.standard_geography_query(source_country='US',
                                      layers=['US.States'],
                                      ids=['06'],
                                      return_geometry=True)
            self.assertIsInstance(r, (SpatialDataFrame, pd.DataFrame))
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_enrich(self):
            """tests enrich dataset"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)

            r = geoenrichment.enrich(study_areas=[{"geometry":{"x":-122.435,"y":37.785},"attributes":{"id":"1"}},{"geometry":{"x":-122.433,"y":37.734},"attributes":{"id":"2"}},
                           {"sourceCountry":"US","layer":"US.ZIP5","ids":["92373","92129"]},
                           {"geometry":{"x": -122.435, "y": 37.785},"areaType": "NetworkServiceArea","bufferUnits": "Hours","bufferRadii": [1],"travel_mode":"Driving"},
                           {"address":{"text":"12 Concorde Place Toronto ON M3C 3R8","sourceCountry":"Canada"}},{"address":{"text":"380 New York St Redlands CA 92373","sourceCountry":"US"}},
                           {"geometry":{"rings":[[[-117.185412,34.063170],[-122.81,37.81],[-117.200570,34.057196],[-117.185412,34.063170]]],
                                        "spatialReference":{"wkid":4326}},"attributes":{"id":"3","name":"optional polygon area name"}}])
            self.assertIsInstance(r, (SpatialDataFrame, pd.DataFrame))
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_create_report(self):
            """tests enrich dataset"""
            gis = GIS(url=URL, username=USERNAME, password=PASSWORD, verify_cert=VERIFY)

            r = geoenrichment.create_report(study_areas=[{"geometry":{"x":-117.1956,"y":34.0572}}])
            import os
            self.assertTrue(os.path.isfile(r))

if __name__ == "__main__":
    unittest.main()


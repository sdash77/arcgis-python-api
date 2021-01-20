"""
Performs Unittests on GeoEnrichment

WARNING THESE UNIT TESTS WILL COST CREDITS ON AGOL
"""
import sys
#sys.path.insert(0, r"c:\SVN\geosaurus_master_kubernetes\src")
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import unittest
import pandas as pd
import os, shutil
from arcgis.gis import GIS, ProfileManager
from arcgis import geoenrichment
from arcgis.features import SpatialDataFrame
########################################################################
## SETUP VALUES                                                       ##
########################################################################
PROFILES = ['your_kubernetes_profile', 'your_online_profile', 'your_enterprise_profile']#
VERIFY = False
########################################################################
if not 'your_kubernetes_profile' in ProfileManager().list():
    from arcgis.gis import GIS
    gis = GIS(url="https://devent.esri.com/gis",
              username='admin',
              password='esri.agp',
              profile='your_kubernetes_profile')

if len(PROFILES) > 0:
    ########################################################################
    class ge_unittest(unittest.TestCase):
        """
        AGOL GeoEnrichment Tests
        """
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_ge_coutry_list(self):
            """tests if country as list"""
            for profile in PROFILES:
                gis = GIS(profile=profile, verify_cert=VERIFY, trust_env=True)
                res = geoenrichment.get_countries(gis=gis)
                self.assertIsInstance(res, list)
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_standard_geography_query(self):
            """tests standard_geography_query"""
            for profile in PROFILES:
                gis = GIS(profile=profile, verify_cert=VERIFY, trust_env=True)
                r = geoenrichment.standard_geography_query(source_country='US',
                                                           layers=['US.States'],
                                                           ids=['06'],
                                                           return_geometry=True)
                self.assertIsInstance(r, (SpatialDataFrame, pd.DataFrame))
        ##----------------------------------------------------------------------
        #@unittest.SkipTest
        def test_enrich(self):
            """tests enrich dataset"""
            for profile in PROFILES:
                gis = GIS(profile=profile, verify_cert=VERIFY, trust_env=True)
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
            for profile in PROFILES:
                gis = GIS(profile=profile, verify_cert=VERIFY, trust_env=True)
                import tempfile
                with tempfile.TemporaryDirectory() as tdir:
                    r = geoenrichment.create_report(study_areas=[{"geometry":{"x":-117.1956,"y":34.0572}}], out_name="report.pdf", out_folder=tdir)
                    import os
                    self.assertTrue(os.path.isfile(r))
                    os.remove(r)

if __name__ == "__main__":
    unittest.main()


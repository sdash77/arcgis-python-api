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
_ADD_ITEM_SETUP = {}
########################################################################
if not 'your_kubernetes_profile' in ProfileManager().list():
    from arcgis.gis import GIS
    gis = GIS(url="https://devent.esri.com/gis",
              username='admin',
              password='esri.agp',
              profile='your_kubernetes_profile')
def _setup_ge_service(gis:GIS):
    """configures the site's GeoEnrichment if not present"""
    item_properties = {
        "type": "Geoenrichment Service",
        "url": "https://geoenrich.arcgis.com/arcgis/rest/services/World/GeoenrichmentServer",
        "title": "AGO World GeoEnrichment (demos_deldev)",
        "tags": "Tool, Service, Geoenrichment Service, ArcGIS Server",
        "serviceUsername": "demos_deldev",
        "servicePassword": "DelDevs.123"
    }
    from arcgis.gis import ContentManager
    cm = gis.content
    isinstance(cm, ContentManager)
    item = cm.add(item_properties=item_properties)
    item.share(org=True)
    item.protect(True)
    gis.update_properties({
        "geoenrichmentService": {"url": item.url}
    })
    return item

def _delete_setup_ge_service(item, gis):
    """configures the site's GeoEnrichment if not present"""

    item.protect(False)
    item.delete()
    gis.update_properties({
        "clearEmptyFields": True,
        "geoenrichmentService": ""
    })
    return None
if len(PROFILES) > 0:
    ########################################################################
    class ge_unittest(unittest.TestCase):
        """
        AGOL GeoEnrichment Tests
        """
        ##----------------------------------------------------------------------
        @classmethod
        def setUpClass(self):
            for profile in PROFILES:
                gis = GIS(profile=profile, verify_cert=False, trust_env=True)
                if ('geoenrichment' in gis.properties.helperServices and gis.properties.helperServices.geoenrichment.url is None) or \
                   'geoenrichment' not in gis.properties.helperServices:
                    item = _setup_ge_service(gis)
                    _ADD_ITEM_SETUP[profile] = (item, GIS(profile=profile, verify_cert=False, trust_env=True))
        @classmethod
        def tearDownClass(self):
            for profile in PROFILES:
                if profile in _ADD_ITEM_SETUP:
                    item, gis = _ADD_ITEM_SETUP[profile]
                    _delete_setup_ge_service(item, gis)
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


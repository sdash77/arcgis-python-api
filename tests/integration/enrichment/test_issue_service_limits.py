import os
import sys
#sys.path.insert(0, r"C:\SVN\geosaurus_master_kubernetes\src")
import unittest
import pytest
import pandas as pd
from pandas import Timestamp
from arcgis.gis import GIS
from arcgis.geoenrichment import service_limits


#gis = GIS(profile='your_kubernetes_profile')
###########################################################################
class TestGEHorizontalScaling(unittest.TestCase):

    def setup_ge_service(self, gis:GIS):
        """configures the site's GeoEnrichment if not present"""
        item_properties = {
            "type": "Geoenrichment Service",
            "url": "https://geoenrich.arcgis.com/arcgis/rest/services/World/GeoenrichmentServer",
            "title": "AGO World GeoEnrichment (kubes_deldev)",
            "tags": "Tool, Service, Geoenrichment Service, ArcGIS Server",
            "serviceUsername": "kubes_deldev",
            "servicePassword": "Sharing.esri.agp1"
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

    def delete_setup_ge_service(self, item, gis):
        """configures the site's GeoEnrichment if not present"""

        item.protect(False)
        item.delete()
        gis.update_properties({
            "clearEmptyFields": True,
            "geoenrichmentService": ""
        })
        return None

    def test_get_service_limits(self):
        """tests getting the service limits"""

        for profile in ['your_kubernetes_profile', 'your_online_profile', 'your_enterprise_profile']:
            gis = GIS(profile=profile, verify_cert=False)
            item = None
            if ('geoenrichment' in gis.properties.helperServices and gis.properties.helperServices.geoenrichment.url is None) or \
               'geoenrichment' not in gis.properties.helperServices:
                item = self.setup_ge_service(gis)
            info = service_limits()
            assert isinstance(info, pd.DataFrame)
            if item:
                item = self.delete_setup_ge_service(item=item, gis=gis)
                del item
                item = None


if __name__ == "__main__":
    unittest.main()
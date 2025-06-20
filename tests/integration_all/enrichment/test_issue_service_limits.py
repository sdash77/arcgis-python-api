import unittest
import pandas as pd
from arcgis.gis import GIS
from arcgis.geoenrichment import service_limits
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

enable_verbose_logging()

###########################################################################
@integration_test
@profiles.enterprise_and_agol
class TestGEHorizontalScaling(unittest.TestCase):
    def setup_ge_service(self, gis: GIS):
        """configures the site's GeoEnrichment if not present"""
        item_properties = {
            "type": "Geoenrichment Service",
            "url": "https://geoenrich.arcgis.com/arcgis/rest/services/World/GeoenrichmentServer",
            "title": "AGO World GeoEnrichment (kubes_deldev)",
            "tags": "Tool, Service, Geoenrichment Service, ArcGIS Server",
            "serviceUsername": "kubes_deldev",
            "servicePassword": "Sharing.esri.agp1",
        }
        from arcgis.gis import ContentManager

        cm = gis.content
        isinstance(cm, ContentManager)
        item = cm.add(item_properties=item_properties)
        item.sharing.sharing_level = "ORGANIZATION"
        item.protect(True)
        gis.update_properties({"geoenrichmentService": {"url": item.url}})
        return item

    def delete_setup_ge_service(self, item, gis):
        """configures the site's GeoEnrichment if not present"""

        item.protect(False)
        item.delete()
        gis.update_properties({"clearEmptyFields": True, "geoenrichmentService": ""})
        return None

    def test_get_service_limits(self):
        """tests getting the service limits"""

        gis = self.gis
        item = None
        if (
            "geoenrichment" in gis.properties.helperServices
            and gis.properties.helperServices.geoenrichment.url is None
        ) or "geoenrichment" not in gis.properties.helperServices:
            item = self.setup_ge_service(gis)
        info = service_limits()
        assert isinstance(info, pd.DataFrame)
        if item:
            item = self.delete_setup_ge_service(item=item, gis=gis)
            del item
            item = None


if __name__ == "__main__":
    unittest.main()

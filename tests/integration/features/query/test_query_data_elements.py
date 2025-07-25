import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis.server.catalog import ServicesDirectory
from arcgis.features import FeatureLayerCollection
from utils.decorators import integration_test

from utils._logging import enable_verbose_logging

enable_verbose_logging()


@integration_test
class TestQueryDataElements(unittest.TestCase):
    def test_query_data_elements(self):
        sd = ServicesDirectory(
            url="https://sampleserver7.arcgisonline.com/server/rest/services",
            username="viewer01",
            password="I68VGU^nMurF",
        )
        services = sd.list("UtilityNetwork")
        for service in services:
            if (
                isinstance(service, FeatureLayerCollection)
                and "supportsQueryDataElements" in service.properties
                and service.properties.supportsQueryDataElements
                and len(service.layers) > 0
            ):
                break

        resp = service.query_data_elements(
            [lyr.properties.id for lyr in service.layers]
        )
        assert isinstance(resp, dict)


if __name__ == "__main__":
    unittest.main()

import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging

PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging()


@integration_test
@profiles.admin_enterprise_and_agol
class Test_RuntimeInstancesMethod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._gis = cls.gis

    def test_runtime(self):
        gis = self._gis
        from arcgis.notebook import list_runtimes

        res = list_runtimes(gis)
        assert isinstance(res, list)


if __name__ == "__main__":
    unittest.main()

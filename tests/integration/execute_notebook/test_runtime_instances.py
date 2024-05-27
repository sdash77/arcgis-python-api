import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from utils.decorators import integration_test, profiles

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


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

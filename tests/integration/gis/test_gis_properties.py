import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestNewProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_agol = GIS(
            profile='your_online_profile', verify_cert=False, proxy=PROXIES
        )
        cls.gis_ent = GIS(
            profile='your_enterprise_profile',
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_gis_properties(self):
        """tests the new properties on the GIS object"""
        assert self.gis_agol._is_arcgisonline in [True, False]
        assert self.gis_agol._is_kubernetes in [True, False]
        assert self.gis_agol._is_multitenant in [True, False]
        assert self.gis_agol.session
        assert self.gis_ent._is_arcgisonline in [True, False]
        assert self.gis_ent._is_kubernetes in [True, False]
        assert self.gis_ent._is_multitenant in [True, False]
        assert self.gis_ent.session


if __name__ == "__main__":
    unittest.main()

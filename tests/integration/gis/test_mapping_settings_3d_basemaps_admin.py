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
class TestMapSettings3DBasemaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile="your_online_admin_profile",
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_get_3dbasemaps(self):
        admin = self.gis.admin
        ux = admin.ux
        assert ux.map_settings.use_3D_basemaps in [True, False]

    def test_set_3dBasemaps(self):
        admin = self.gis.admin
        ux = admin.ux
        original_value = ux.map_settings.use_3D_basemaps
        not_orignal_value = not original_value
        ux.map_settings.use_3D_basemaps = not_orignal_value
        assert ux.map_settings.use_3D_basemaps == not_orignal_value
        ux.map_settings.use_3D_basemaps = original_value
        assert ux.map_settings.use_3D_basemaps == original_value


if __name__ == "__main__":
    unittest.main()

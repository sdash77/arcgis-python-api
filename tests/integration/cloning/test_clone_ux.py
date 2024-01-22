import sys

#
#  Update the Path to set the test area
import os
import logging
import unittest
import concurrent.futures
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


profiles = ['your_online_admin_profile', 'your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
# enable_verbose_logging(__logger__)


@integration_test
class TestCloneWorkflows(unittest.TestCase):
    """tests the cloning offline workflows"""

    @classmethod
    def setUpClass(cls):
        cls.result_files = []
        cls.source_gis_online = GIS(
            profile=profiles[0],
            verify_cert=False,
            proxy=PROXIES,
        )
        cls.source_gis_ent = GIS(
            url="https://rextapilnx02eb.esri.com/portal",
            username="PAPIadmin",
            password="PAPIletmein01",
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_offline_defaults_ago(self):
        gis_source = self.source_gis_online
        ux = gis_source.admin.ux
        fp = ux.clone()
        assert len(fp) >= 0
        assert fp[0].result()
        self.result_files.append(fp[0].result())

    def test_offline_package_loading(self):
        gis_source = self.source_gis_online
        gis_source.update_properties(
            {
                "allowedOrigins": "http://localhost:8888,http://localhost:8889,http://*.esri.com,http://*,https://*"
            }
        )
        ux = gis_source.admin.ux
        fp = ux.clone()
        assert len(fp) >= 0
        fp = fp[0].result()
        ux_dest = self.source_gis_ent.admin.ux
        assert ux_dest.load_offline_configuration(fp)

    def test_offline_defaults_ent(self):
        gis_source = self.source_gis_ent
        gis_source.update_properties(
            {
                "allowedOrigins": "http://localhost:8888,http://localhost:8889,http://*.esri.com,http://*,https://*"
            }
        )
        ux = gis_source.admin.ux
        fp = ux.clone()
        assert len(fp) >= 0
        assert fp[0].result()
        self.result_files.append(fp[0].result())

    def test_online_to_ent(self):
        gis = self.source_gis_online
        gis.update_properties(
            {
                "allowedOrigins": "http://localhost:8888,http://localhost:8889,http://*.esri.com,http://*,https://*"
            }
        )
        ux = gis.admin.ux
        result = ux.clone(targets=[self.source_gis_ent])
        assert len(result) == 1
        assert isinstance(result[0], concurrent.futures.Future)
        assert result[0].result()

    def test_ent_to_online(self):
        gis = self.source_gis_ent
        gis.update_properties(
            {
                "allowedOrigins": "http://localhost:8888,http://localhost:8889,http://*.esri.com,http://*,https://*"
            }
        )
        ux = gis.admin.ux
        result = ux.clone(targets=[self.source_gis_online])
        assert len(result) == 1
        assert isinstance(result[0], concurrent.futures.Future)
        assert result[0].result()

    @classmethod
    def tearDownClass(cls):
        for fp in cls.result_files:
            if os.path.isfile(fp):
                os.remove(fp)


if __name__ == "__main__":
    unittest.main()

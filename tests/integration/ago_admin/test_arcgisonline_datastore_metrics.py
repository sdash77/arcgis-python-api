import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\SVN\geosaurus_issue_10226\src")
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis.admin._dsmgr import DataStoreMetricsManager

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class Test_DatastoreMetrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile='your_online_profile', verify_cert=False, proxy=PROXIES
        )

    def test_dmm(self):
        """tests the admin endpoint for the metric manager"""
        assert self.gis.admin.datastore_metrics
        assert isinstance(
            self.gis.admin.datastore_metrics, DataStoreMetricsManager
        )

    def test_dmm_feature_storage(self):
        """tests the admin endpoint for the metric manager feature storage"""
        assert self.gis.admin.datastore_metrics
        assert isinstance(
            self.gis.admin.datastore_metrics, DataStoreMetricsManager
        )
        dmm = self.gis.admin.datastore_metrics
        assert dmm.feature_storage

    def test_dmm_query_resource_usage(self):
        """tests the admin endpoint for the metric manager query resource usage"""
        dmm = self.gis.admin.datastore_metrics
        assert dmm.query_resource_usage(query_period='day')
        assert dmm.query_resource_usage(query_period='hour')
        assert dmm.query_resource_usage(query_period='week')

    def test_dmm_query_resource_usage_failure(self):
        """tests the admin endpoint for the metric manager query resource usage"""
        dmm = self.gis.admin.datastore_metrics
        with self.assertRaises(AssertionError) as context:
            dmm.query_resource_usage(query_period='dog')


if __name__ == "__main__":
    unittest.main()

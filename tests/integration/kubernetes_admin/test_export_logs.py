import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\SVN\geosaurus_master\src")
import os
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ["your_kubernetes_profile"]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


class TestKubernetesExportLogs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile=profiles[0], verify_cert=False, proxy=PROXIES)

    def test_export_log(self):
        admin = self.gis.admin
        lm = admin.logs
        res = lm.export()
        assert isinstance(res, str)
        assert os.path.isfile(res)
        os.remove(res)

    def test_export_log_parameters(self):
        admin = self.gis.admin
        lm = admin.logs
        res = lm.export(
            query="error",
            start_time=None,
            end_time=None,
            level="VERBOSE",
            log_code=None,
            users=None,
            request_ids=None,
            service_types=None,
            source=None,
            stack_traces=True,
            out_folder=None,
        )
        assert isinstance(res, str)
        assert os.path.isfile(res)
        os.remove(res)


if __name__ == "__main__":
    unittest.main()

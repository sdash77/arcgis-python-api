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


profiles = ['your_enterprise_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestEnterpriseLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        username = "PAPIadmin"

        password = "PAPIletmein01"

        cls.gis = GIS(
            url="https://rqawinbi01pt.ags.esri.com/gis",
            username=username,
            password=password,
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_get_limits(self):
        system = self.gis.admin.system
        assert system.limits

    def test_set_limits(self):
        result = self.gis.admin.system.set_limits(
            properties=[{'limitName': 'TaskRunHistoryCount', 'numLimit': 50}]
        )
        assert result


if __name__ == "__main__":
    unittest.main()

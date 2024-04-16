import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
import datetime as _dt
import os
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


profiles = ['your_online_admin_profile']
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestAGOLHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(profile=profiles[0], verify_cert=False, proxy=PROXIES)
        cls.admin = cls.gis.admin

    def test_get_history_df(self):
        start_time = _dt.datetime(2022, 11, 10, 19, 0)
        res = self.admin.history(
            start_date=start_time,
            num=10000,
            data_format='csv',
        )
        assert res
        assert os.path.isfile(res)
        os.remove(res)

    def test_get_history_filters(self):
        start_time = _dt.datetime(2023, 8, 10)
        res = self.admin.history(
            start_date=start_time,
            num=10,
            data_format='df',
            event_types="i,g,u",
        )
        assert len(res) > 0

    def test_get_history_filters_json(self):
        start_time = _dt.datetime(2023, 8, 10)
        res = self.admin.history(
            start_date=start_time,
            num=10,
            data_format='raw',
            event_types="i,g,u",
        )
        assert len(res) > 0

    def test_get_history(self):
        """
        tests if receive login history
        """
        today = _dt.datetime.now()
        history = self.admin.history(start_date=today)
        assert isinstance(history, str)
        assert history
        os.remove(history)


if __name__ == "__main__":
    unittest.main()

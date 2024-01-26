import sys

import logging
import unittest
import datetime as _dt
import pandas as pd
from arcgis.features.geo._extarray import (
    ArrowTimeAccessor,
    ArrowTimeArray,
    ArrowTimeDtype,
)

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


enable_verbose_logging(__logger__)


class TestDtypeArray(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = pd.Series(
            [
                _dt.time(8, 30),
                _dt.time(12, 45),
                _dt.time(17, 15),
                None,
            ],
            dtype=ArrowTimeDtype(),
        )

    def test_to_numpy(self):
        self.data.to_numpy()

    def test_properties(self):
        self.data.time.hour
        self.data.time.minute
        self.data.time.second
        self.data.time.microsecond
        self.data.time.tzinfo

    def test_set_value(self):
        v = _dt.time(hour=1, minute=10, second=0, microsecond=0)
        self.data[1] = v
        assert self.data[1] == v

    def test_isoformat_2(self):
        s = self.data.time.isoformat("microseconds")
        assert s[0] == '08:30:00.000000'

    def test_isoformat(self):
        s = self.data.time.isoformat()
        assert s[0] == '08:30:00'

    def test_replace_method(self):
        assert all(
            [
                hour == 17
                for hour in self.data.time.replace(hour=17).time.hour
                if (not hour is None and not hour is pd.NA)
            ]
        )

    def test_strftime(self):
        s = self.data.time.strformat('%I:%M %p')
        assert isinstance(s[0], str)
        assert s[0] == '08:30 AM'


if __name__ == "__main__":
    unittest.main()

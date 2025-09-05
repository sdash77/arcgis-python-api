import unittest
import datetime as dt
from dateutil.relativedelta import relativedelta

from utils.decorators import integration_test, profiles
from utils.data_utils import INTEGRATION_TEST_ITEM_TAG

from arcgis.auth.tools import LazyLoader

VERIFY_CERT = False
TRUST_ENV = True


@integration_test
@profiles.agol
class TestItemUsage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Get a hosted feature layer known to contain usage at 6M and 1Y ranges.
        A new item will not be helpful to evaluate usage results, so making
        use of an existing item allows for checking values of returns.
        """

        cls.now = dt.datetime.now()
        cls.less_six_months = cls.now - relativedelta(months=3)
        cls.six_months_ago = cls.now - relativedelta(months=6)

        cls.item_id = "d5986892a770415ba724692b56019214"
        cls.hosted_flyr_item = cls.gis.content.get(cls.item_id)
        cls.assertIsNotNone(cls.hosted_flyr_item, "No feature layer item to test.")

    def test_preset(self):
        """tests the preset times we can use for date range"""
        item = self.hosted_flyr_item

        # use the item so you do not get empty dataframe
        date_ranges = ["24H", "7D", "14D", "30D", "60D", "6M", "1Y"]

        non_empty = []

        for date in date_ranges:
            result = item.usage(date_range=date)
            self.assertIsNotNone(
                result, "Usage returning None when should return dataframe"
            )
            self.assertIn(
                "Usage",
                list(result.columns),
                "DataFrame should have a column named Usage.",
            )
            if not result[result["Usage"] != 0].empty:
                non_empty.append(f"{date} contained non-empty rows")

        self.assertGreater(
            len(non_empty),
            0,
            "At least one date range should have returned non-zero rows for this feature layer.",
        )

    def test_custom_less_6_months(self):
        item = self.hosted_flyr_item

        result = item.usage(date_range=(self.less_six_months, self.now))

        self.assertIsNotNone(result, "usage method should return a dataframe.")
        self.assertIn(
            "Usage", list(result.columns), "DataFrame should have a column named Usage."
        )
        self.assertGreater(
            len(result[result["Usage"] != 0]),
            0,
            "This hosted feature layer has been queried within 3 months.",
        )

    def test_custom_more_6_months(self):
        item = self.hosted_flyr_item

        result = item.usage(date_range=(self.six_months_ago, self.now))

        self.assertIsNotNone(
            result, "Item usage method should always return a dataframe."
        )
        self.assertIn(
            "Usage", list(result.columns), "DataFrame should have a column named Usage."
        )
        self.assertGreater(
            len(result[result["Usage"] != 0]),
            0,
            "This hosted feature layer has been queried within 6 months.",
        )

    def test_custom_11_days(self):
        item = self.hosted_flyr_item

        # use the item so you do not get empty dataframe
        date_1 = self.now - relativedelta(days=11)

        result = item.usage(date_range=(date_1, self.now))

        self.assertIsNotNone(
            result, "Item usage method should always return a dataframe."
        )
        self.assertIn(
            "Usage", list(result.columns), "DataFrame should have a column named Usage."
        )
        self.assertGreater(
            len(result[result["Usage"] != 0]),
            0,
            "This hosted feature layer has been queried within last 11 days.",
        )


if __name__ == "__main__":
    unittest.main()

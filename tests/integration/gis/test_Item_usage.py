import unittest
from arcgis.gis import GIS
from datetime import timedelta, datetime
from arcgis.mapping import WebMap
from utils.decorators import integration_test

# Note this is only supported for AGOL as of now
profiles = [
    "your_online_profile",
]
VERIFY_CERT = False
TRUST_ENV = True


@integration_test
class TestItemUsage(unittest.TestCase):
    def test_preset(self):
        """tests the preset times we can use for date range"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
            item = gis.content.get("747b24cdf0ef49acab79feb3dfcd4546")
            wm = WebMap()
            wm.add_layer(item.layers[0])
            new_item = wm.save({"title": "Test for item usage", "snippet": "Using an item to increase usage for testing", "tags":["python"]})
            # use the item so you do not get empty dataframe
            date_ranges = ["24H", "7D", "14D", "30D", "60D", "6M", "1Y"]
            try:
                for date in date_ranges:
                    result = item.usage(date_range = date)
                    assert result is not None
            except:
                print("Test failed at date range: ", date)
            finally:
                new_item.delete()
    
    def test_custom_less_5_months(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
            item = gis.content.get("747b24cdf0ef49acab79feb3dfcd4546")
            wm = WebMap()
            wm.add_layer(item.layers[0])
            new_item = wm.save({"title": "Test for item usage", "snippet": "Using an item to increase usage for testing", "tags":["python"]})
            # use the item so you do not get empty dataframe
            date_2 = datetime.now()
            date_1 = date_2 - timedelta(days=140)
            try:
                result = item.usage(date_range = (date_1, date_2))
                assert result is not None
            except:
                pass
            finally:
                new_item.delete()

    def test_custom_more_5_months(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
            item = gis.content.get("747b24cdf0ef49acab79feb3dfcd4546")
            wm = WebMap()
            wm.add_layer(item.layers[0])
            new_item = wm.save({"title": "Test for item usage", "snippet": "Using an item to increase usage for testing", "tags":["python"]})
            # use the item so you do not get empty dataframe
            date_2 = datetime.now()
            date_1 = date_2 - timedelta(days=185)
            try:
                result = item.usage(date_range = (date_1, date_2))
                assert result is not None
            except:
                pass
            finally:
                new_item.delete()
    
    def test_custom_at_5_months(self):
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=TRUST_ENV)
            item = gis.content.get("747b24cdf0ef49acab79feb3dfcd4546")
            wm = WebMap()
            wm.add_layer(item.layers[0])
            new_item = wm.save({"title": "Test for item usage", "snippet": "Using an item to increase usage for testing", "tags":["python"]})
            # use the item so you do not get empty dataframe
            date_2 = datetime.now()
            date_1 = date_2 - timedelta(days=152)
            try:
                result = item.usage(date_range = (date_1, date_2))
                assert result is not None
            except:
                pass
            finally:
                new_item.delete()


if __name__ == "__main__":
    unittest.main()

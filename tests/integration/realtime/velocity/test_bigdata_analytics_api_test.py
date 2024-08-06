import unittest

from arcgis.gis import GIS
from arcgis.realtime.velocity.bigdata_analytics_manager import BigDataAnalytics
from utils.decorators import integration_test

try:
    # Use your ArcGIS enterprise url and credentials to run the test
    url = "https://devext.arcgis.com"
    username = "pythontest_a4iot"
    password = "v3locity.pyth0n"
    gis = GIS(url, username, password)
    SKIP_TESTS = False
    # Skip task start/stop/delete tests by default. Set as false to run
    SKIP_SOME_TESTS = True
except:
    SKIP_TESTS = True


@unittest.skipIf(SKIP_TESTS, reason="GIS connection failed")
@integration_test
class TestBigDataAnalyticsMethods(unittest.TestCase):
    velocity = gis.velocity
    bigdata_analytics = velocity.bigdata_analytics
    bigdata_analytics_item = bigdata_analytics.get("28d7fc935b3043d58069cec2abc265a9")

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_get_all_bigdata_analytics skipping")
    def test_get_all_bigdata_analytics(self):
        print("\n ---- test_get_all_bigdata_analytics ----")

        try:
            items = self.bigdata_analytics.items
            for item in items:
                assert isinstance(item, BigDataAnalytics)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    def test_get_bigdata_analytics(self):
        print("\n ---- test_get_bigdata_analytics ----")

        try:
            response = self.bigdata_analytics.get("28d7fc935b3043d58069cec2abc265a9")
            assert isinstance(response, BigDataAnalytics)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_start_bigdata_analytics skipping")
    def test_start_bigdata_analytics(self):
        print("\n ---- test_start_bigdata_analytics ----")

        try:
            response = self.bigdata_analytics_item.start()
            assert response and response.get("status") == "success"

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_stop_bigdata_analytics skipping")
    def test_stop_bigdata_analytics(self):
        print("\n ---- test_stop_bigdata_analytics ----")

        try:
            response = self.bigdata_analytics_item.stop()
            assert response and response.get("status") == "success"

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    def test_bigdata_analytics_status(self):
        print("\n ---- test_bigdata_analytics_status ----")

        try:
            response = self.bigdata_analytics_item.status
            assert response and response.get("status")

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_bigdata_analytics_metrics skipping")
    def test_bigdata_analytics_metrics(self):
        print("\n ---- test_bigdata_analytics_metrics ----")

        try:
            response = self.bigdata_analytics_item.metrics
            assert response and response.get("itemId")

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_delete_bigdata_analytics skipping")
    def test_delete_bigdata_analytics(self):
        print("\n ---- test_delete_bigdata_analytics ----")
        try:
            bigdata_analytics_to_delete = self.bigdata_analytics.get(
                "3302845ecb68466ea4aa4f98b27ec51e"
            )
            try:
                response = bigdata_analytics_to_delete.delete()
                assert response and response.get("id")

            except AssertionError as assertErrorException:
                self.SKIP_TESTS = True
                raise assertErrorException

            except unittest.SkipTest as skipException:
                raise skipException

            except Exception as testException:
                self.fail("Error during test: " + testException.__str__())

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


if __name__ == "__main__":
    unittest.main()

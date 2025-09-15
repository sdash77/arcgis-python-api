import unittest

from arcgis.gis import GIS
from arcgis.realtime.velocity.feeds_manager import Feed
from arcgis.realtime.velocity.feeds import RSS, HttpReceiver
from arcgis.realtime.velocity.http_authentication_type import (
    NoAuth,
    BasicAuth,
    CertificateAuth,
)
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


@unittest.skip("Test portal not ready yet")
#TODO: update profile and set decorator for velocity tests when portal is ready
@unittest.skipIf(SKIP_TESTS, reason="GIS connection failed")
@integration_test
class TestFeedsApiMethods(unittest.TestCase):
    velocity = gis.velocity
    feeds = velocity.feeds

    # @unittest.skipIf(SKIP_SOME_TESTS, "test_get_all_feeds skipping")
    def test_get_all_feeds(self):
        print("\n ---- test_get_all_feeds ----")

        try:
            items = self.feeds.items
            for item in items:
                assert isinstance(item, Feed)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    def test_get_feed(self):
        print("\n ---- test_get_feed ----")
        try:
            feed = self.feeds.get("9b346d664c244adea79ee11942de38c5")
            assert isinstance(feed, Feed)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_start_feed skipping")
    def test_start_feed(self):
        print("\n ---- test_start_feed ----")
        try:
            response = self.feed_item.start()
            assert response and response.get("status") == "success"

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_stop_feed skipping")
    def test_stop_feed(self):
        print("\n ---- test_stop_feed ----")
        try:
            response = self.feed_item.stop()
            assert response and response.get("status") == "success"

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------

    @unittest.skipIf(SKIP_SOME_TESTS, "test_feed_metrics skipping")
    def test_feed_status(self):
        print("\n ---- test_feed_status ----")
        try:
            response = self.feed_item.status
            assert response and response.get("status")

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_feed_metrics skipping")
    def test_feed_metrics(self):
        print("\n ---- test_feed_metrics ----")
        try:
            response = self.feed_item.metrics
            assert response and response.get("itemId")

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, "test_delete_feed skipping")
    def test_delete_feed(self):
        print("\n ---- test_delete_feed ----")
        try:
            feed_to_delete = self.feeds.get("b4b439a0d1f240949835a79b4e919a6d")
            try:
                response = feed_to_delete.delete()
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

    @unittest.skipIf(SKIP_SOME_TESTS, "create a feed")
    def test_create_a_feed(self):

        # HTTP Receiver Properties
        name = "http_receiver_feed_1"
        description = "some description about the HTTP Receiver feed"
        sample_data = """name,age
        dan,23"""

        http_receiver = HttpReceiver(
            label=name,
            description=description,
            authentication_type="none",
            sample_message=sample_data,
            data_format=None,
        )

        http_receiver.rename_field("name", "name1")

        # set track id for an existing field
        http_receiver.set_track_id("name")

        self.feeds.create(http_receiver)
        self.feeds.items

        # rss_feed = feeds._sample_message(input_type="feed")
        # print(rss_feed)
        # feed_item = feeds.get("7392333e5ab0406abaa67cc75a214b98")


if __name__ == "__main__":
    unittest.main()

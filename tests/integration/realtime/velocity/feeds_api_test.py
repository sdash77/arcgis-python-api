import unittest

from arcgis.gis import GIS
from arcgis.realtime.velocity.feeds_manager import Feed

try:
    # Use your ArcGIS enterprise url and credentials to run the test
    url = ''
    username = ''
    password = ''
    gis = GIS(url, username, password)
    SKIP_TESTS = False
    # Skip task start/stop/delete tests by default. Set as false to run
    SKIP_SOME_TESTS = True
except:
    SKIP_TESTS = True


@unittest.skipIf(SKIP_TESTS,
                 reason='GIS connection failed')
class TestFeedsApiMethods(unittest.TestCase):
    velocity = gis.velocity
    feed_manager = velocity.feeds_manager
    feed_item = feed_manager.get('334dfcf1d7184dcc8c92207643bfe65d')

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_get_all_feeds skipping')
    def test_get_all_feeds(self):
        print('\n ---- test_get_all_feeds ----')

        try:
            items = self.feed_manager.items
            for item in items:
                assert isinstance(item, Feed)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    def test_get_feed(self):
        print('\n ---- test_get_feed ----')
        try:
            feed = self.feed_manager.get('334dfcf1d7184dcc8c92207643bfe65d')
            assert isinstance(feed, Feed)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_start_feed skipping')
    def test_start_feed(self):
        print('\n ---- test_start_feed ----')
        try:
            response = self.feed_item.start()
            assert response and response.get('status') == 'success'

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_stop_feed skipping')
    def test_stop_feed(self):
        print('\n ---- test_stop_feed ----')
        try:
            response = self.feed_item.stop()
            assert response and response.get('status') == 'success'

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    def test_feed_status(self):
        print('\n ---- test_feed_status ----')
        try:
            response = self.feed_item.status()
            assert response and response.get('status')

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_feed_metrics skipping')
    def test_feed_metrics(self):
        print('\n ---- test_feed_metrics ----')
        try:
            response = self.feed_item.metrics()
            assert response and response.get('itemId')

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_delete_feed skipping')
    def test_delete_feed(self):
        print('\n ---- test_delete_feed ----')
        try:
            feed_to_delete = self.feed_manager.get('3a3ef00fce904fe78f014243241b0da6')
            try:
                response = feed_to_delete.delete()
                assert response and response.get('id')

            except AssertionError as assertErrorException:
                self.SKIP_TESTS = True
                raise assertErrorException

            except unittest.SkipTest as skipException:
                raise skipException

            except Exception as testException:
                self.fail('Error during test: ' + testException.__str__())

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())


def print_result(response):
    if type(response) == str:
        print(response)
    else:
        for key in response:
            print(key + ' : ' + format(response[key]))


if __name__ == '__main__':
    unittest.main()

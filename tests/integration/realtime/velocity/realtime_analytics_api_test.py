import unittest

from arcgis.gis import GIS

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
class TestRealTimeAnalyticsMethods(unittest.TestCase):
    velocity = gis.velocity
    realtime_analytics_manager = velocity.realtime_analytics_manager
    realtime_analytics_item = realtime_analytics_manager.get('7a8f2100aedb47be85d57d4969757a16')

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_get_all_realtime_analytics skipping')
    def test_get_all_realtime_analytics(self):
        print('\n ---- test_get_all_realtime_analytics ----')
        realtime_tasks = self.realtime_analytics_manager.tasks
        try:
            print(realtime_tasks)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    def test_get_realtime_analytics(self):
        print('\n ---- test_get_realtime_analytics ----')

        response = self.realtime_analytics_manager.get('7a8f2100aedb47be85d57d4969757a16')
        try:
            print(response)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_start_realtime_analytics skipping')
    def test_start_realtime_analytics(self):
        print('\n ---- test_start_realtime_analytics ----')

        response = self.realtime_analytics_item.start()
        try:
            print_result(response)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_stop_realtime_analytics skipping')
    def test_stop_realtime_analytics(self):
        print('\n ---- test_stop_realtime_analytics ----')

        response = self.realtime_analytics_item.stop()
        try:
            print_result(response)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    def test_realtime_analytics_status(self):
        print('\n ---- test_realtime_analytics_status ----')
        response = self.realtime_analytics_item.status()
        try:
            print_result(response)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_realtime_analytics_metrics skipping')
    def test_realtime_analytics_metrics(self):
        print('\n ---- test_realtime_analytics_metrics ----')
        response = self.realtime_analytics_item.metrics()
        try:
            print_result(response)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_delete_realtime_analytics skipping')
    def test_delete_realtime_analytics(self):
        print('\n ---- test_delete_realtime_analytics ----')
        try:
            realtime_analytics_to_delete = self.realtime_analytics_manager.get('e6a8caa0e38f44fab569cebbaf5fea2a')
            try:
                response = realtime_analytics_to_delete.delete()
                print_result(response)

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

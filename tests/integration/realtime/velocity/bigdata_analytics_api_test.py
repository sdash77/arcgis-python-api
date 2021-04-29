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
class TestBigDataAnalyticsMethods(unittest.TestCase):
    velocity = gis.velocity
    bigdata_analytics_manager = velocity.bigdata_analytics_manager
    bigdata_analytics_item = bigdata_analytics_manager.get('7a49c634c09f4e558f842db06c76a346')

    # ----------------------------------------------------------------------
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_get_all_bigdata_analytics skipping')
    def test_get_all_bigdata_analytics(self):
        print('\n ---- test_get_all_bigdata_analytics ----')
        bigdata_tasks = self.bigdata_analytics_manager.tasks
        try:
            print(bigdata_tasks)

        except AssertionError as assertErrorException:
            self.SKIP_TESTS = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail('Error during test: ' + testException.__str__())

    # ----------------------------------------------------------------------
    def test_get_bigdata_analytics(self):
        print('\n ---- test_get_bigdata_analytics ----')

        response = self.bigdata_analytics_manager.get('7a49c634c09f4e558f842db06c76a346')
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
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_start_bigdata_analytics skipping')
    def test_start_bigdata_analytics(self):
        print('\n ---- test_start_bigdata_analytics ----')

        response = self.bigdata_analytics_item.start()
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
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_stop_bigdata_analytics skipping')
    def test_stop_bigdata_analytics(self):
        print('\n ---- test_stop_bigdata_analytics ----')

        response = self.bigdata_analytics_item.stop()
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
    def test_bigdata_analytics_status(self):
        print('\n ---- test_bigdata_analytics_status ----')
        response = self.bigdata_analytics_item.status()
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
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_bigdata_analytics_metrics skipping')
    def test_bigdata_analytics_metrics(self):
        print('\n ---- test_bigdata_analytics_metrics ----')
        response = self.bigdata_analytics_item.metrics()
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
    @unittest.skipIf(SKIP_SOME_TESTS, 'test_delete_bigdata_analytics skipping')
    def test_delete_bigdata_analytics(self):
        print('\n ---- test_delete_bigdata_analytics ----')
        try:
            bigdata_analytics_to_delete = self.bigdata_analytics_manager.get('f34d3a7c899f4c178c9a0ff9dfc24bf9')
            try:
                response = bigdata_analytics_to_delete.delete()
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

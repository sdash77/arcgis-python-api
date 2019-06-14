#-------------------------------------------------------------------------------
# Name:        ContentManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime

#region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if (r1 & r2):
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise(exit())

# Import the module after Precondition checks pass
try:
    import arcgis
    from arcgis.gis import GIS
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.gis module GIS class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_ContentManager_portal_builtin(unittest.TestCase):
    """
    Test to check if a ContentManager object works with builtin portal
    """
    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        #region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['teamportal']['url']
        cls.portal_username = _conf_reader['teamportal']['admin_user']
        cls.portal_password = _conf_reader['teamportal']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_ContentManager_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_ContentManager_portal_builtin class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_ContentManager_"

        #region delete old outputs
        self.test_case_name = self.namePrefix + self._testMethodName
        search_result = PortalUtils.search_portal_item(self.gis, self.test_case_name, "Feature Service")

        if search_result is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, search_result)
            if not delete_result[0]:
                test_skip = True #cannot run test case if old output is not deleted
                print("Failed to delete old test output: " + str(delete_result[1]))
            else:
                print("setUp : deleted old output. Proceeding to test case")
        else:
            print("setUp: not old outputs found. Proceeding to test case")
        #endregion

        t = datetime.datetime.now()
        self.time_stamp_numerals= str.format("{0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        self.time_stamp = "Time stamp: " + self.time_stamp_numerals
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_import_data_geocode(self):
        try:
            #read input data
            file_path = self.qalab_cls_path + self.test_case_name + ".csv"
            import pandas as pd
            df = pd.read_csv(file_path)

            #geocode and publish
            publish_output = self.gis.content.import_data(df, {'Address':'LOCATION'})

            #validate
            if publish_output is None:
                self.fail("Failed to geocode a known data frame")
            else:
                #validate return type
                self.assertIsInstance(publish_output, arcgis.features.FeatureCollection, "import_data does not return "
                                        "a Feature Collection upon success. Instead it returns: " + str(type(publish_output)))

                #validate item can be found
                self.assertTrue(len(publish_output.layer.featureSet.features) > 0, "No features found in geocoded"
                                                                                   "feature collection")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(class_skip, "Test preconditions not met, skipping")
    def test_create_service_defaults(self):
        """
        Calling gis.content.create_service("test","test service") shouls create a feature service.
        :return:
        """
        #region old previous output
        old_output_sr = PortalUtils.search_portal_item(self.gis, "dino_ContentManager_test_create_service_defaults", "Feature Service")
        if old_output_sr:
            try:
                old_output_delete_result = old_output_sr.delete()
                print("Deleted old output: " + str(old_output_delete_result))
            except:
                pass #not a failure, deleting is just for housekeeping as this service does not have any data associated.
        #endregion

        try:
            #create default feature service
            service_title = self.test_case_name +"_" + self.time_stamp_numerals
            print("Creating service titled: " + service_title)

            service_item = self.gis.content.create_service(name=service_title, service_description="Dino test default service")
            print(service_item.title)
            self.assertEqual(service_item.type, "Feature Service",
                             "Default service type created when calling create_service is not a feature service")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

class Test_ContentManager_ago_builtin(unittest.TestCase):
    """
    Test to check if a ContentManager object works with ArcGIS Online
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if portal builtin can be reached
        Get class test asset location
        :return:
        """

        # region Read config data
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        cls.portal_url = _conf_reader['arcgiscom']['url']
        cls.portal_username = _conf_reader['arcgiscom']['admin_user']
        cls.portal_password = _conf_reader['arcgiscom']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_ContentManager_cls']
        # endregion

        # region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_ContentManager_portal_builtin class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_ContentManager_"

        # region delete old outputs
        self.test_case_name = self.namePrefix + self._testMethodName
        search_result = PortalUtils.search_portal_item(self.gis, self.test_case_name, "Feature Service")

        if search_result is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, search_result)
            if not delete_result[0]:
                test_skip = True  # cannot run test case if old output is not deleted
                print("Failed to delete old test output: " + str(delete_result[1]))
            else:
                print("setUp : deleted old output. Proceeding to test case")
        else:
            print("setUp: not old outputs found. Proceeding to test case")
        # endregion

        t = datetime.datetime.now()
        self.time_stamp_numerals = str.format("{0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
                                              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        self.time_stamp = "Time stamp: " + self.time_stamp_numerals
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_import_data_geocode(self):
        try:
            # read input data
            file_path = self.qalab_cls_path + self.test_case_name + ".csv"
            import pandas as pd
            df = pd.read_csv(file_path)

            # geocode and publish
            publish_output = self.gis.content.import_data(df, {'Address': 'LOCATION'})

            # validate
            if publish_output is None:
                self.fail("Failed to geocode a known data frame")
            else:
                # validate return type
                self.assertIsInstance(publish_output, arcgis.features.FeatureCollection,
                                      "import_data does not return "
                                      "a Feature Collection upon success. Instead it returns: " + str(
                                          type(publish_output)))

                # validate item can be found
                self.assertTrue(len(publish_output.layer.featureSet.features) > 0,
                                "No features found in geocoded"
                                "feature collection")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


    def test_import_data_table_geocode(self):
        try:
            #read input data
            import pandas as pd
            df = pd.read_html("https://en.wikipedia.org/wiki/Number_of_guns_per_capita_by_country")[0]

            #pre-process
            df.columns = df.iloc[0]
            df = df.reindex(df.index.drop(0))
            df = df.reindex(df.index.drop(1))
            df = df.drop(df.columns[0], axis=1)
            df.iloc[0, 1] = 120.5

            converted_column = pd.to_numeric(df["Estimate of civilian firearms per 100 persons"], errors='coerce')
            df['Estimate of civilian firearms per 100 persons'] = converted_column

            # df.rename(columns={'Country__or_dependent_territory__subnational_area__etc__': 'Country'},
            #           inplace=True)

            #geocode and publish
            publish_output = self.gis.content.import_data(df, {"CountryCode":"Country__or_dependent_territory__subnational_area__etc__"})

            #validate
            if publish_output is None:
                self.fail("Failed to geocode a known data frame")
            else:
                #validate return type
                self.assertIsInstance(publish_output, arcgis.features.FeatureCollection, "import_data does not return "
                                        "a Feature Collection upon success. Instead it returns: " + str(type(publish_output)))

                #validate item can be found
                self.assertTrue(len(publish_output.layer.featureSet.features) > 0, "No features found in geocoded"
                                                                                   "feature collection")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(class_skip, "Test preconditions not met, skipping")
    def test_create_service_defaults(self):
        """
        Calling gis.content.create_service("test","test service") shouls create a feature service.
        :return:
        """
        # region old previous output
        old_output_sr = PortalUtils.search_portal_item(self.gis, "dino_ContentManager_test_create_service_defaults",
                                                       "Feature Service")
        if old_output_sr:
            try:
                old_output_delete_result = old_output_sr.delete()
                print("Deleted old output: " + str(old_output_delete_result))
            except:
                pass  # not a failure, deleting is just for housekeeping as this service does not have any data associated.
        # endregion

        try:
            # create default feature service
            service_title = self.test_case_name + "_" + self.time_stamp_numerals
            print("Creating service titled: " + service_title)

            service_item = self.gis.content.create_service(name=service_title,
                                                           service_description="Dino test default service")
            print(service_item.title)
            self.assertEqual(service_item.type, "Feature Service",
                             "Default service type created when calling create_service is not a feature service")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
#TestModule
def tearDownModule():
    print("**End GIS module Tests**")
#-------------------------------------------------------------------------------
# Name:        DatastoreManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
import datetime
import os

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

class Test_DatastoreManager_portal_builtin(unittest.TestCase):
    """
    Test to check if a GroupManager object works with builtin portal
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

        cls.portal_url = _conf_reader['teamportal105']['url']
        cls.portal_username = _conf_reader['teamportal105']['admin_user']
        cls.portal_password = _conf_reader['teamportal105']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_DatastoreManager_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_DatastoreManager_portal_builtin class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_DatastoreManager_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

        #remove previous outputs
        if self._testMethodName == "test_geoanalyticsDM_add_BDFS_winUNC":
            print("Test setUp: Remove old outputs")
            try:
                from arcgis import geoanalytics
                ga_DM = geoanalytics.get_datastores(self.gis)
                DS_list = ga_DM.search()
                search_list = [ds for ds in DS_list if ds.datapath.__contains__("unittest_fortune500")]
                if len(search_list) > 0:
                    ds = DS_list[0]
                    delete_result = ds.delete()
                    print("Old BDFS found, delete result: " + str(delete_result))
                else:
                    print("No Old BDFS can be found. proceeding to test")
            except:
                print("Exception trying to search and delete old BDFS")

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_is_supported(self):
        """
        Test if geoanalytics is supported in GIS
        :return:
        """
        try:
            from arcgis import geoanalytics
            self.assertTrue(geoanalytics.is_supported(self.gis), "GIS does not support geoanalytics")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test, most likely cannot import geoanalytics: "
                      + testException.__str__())

    def test_geoanalytics_get_datastores(self):
        """
        Test to DatastoreManager running geoanalytics
        :return:
        """
        try:
            from arcgis import geoanalytics
            ga_DM = geoanalytics.get_datastores(self.gis)

            self.assertIsNotNone(ga_DM, "geoanalytics.get_datastores() returns None")
            self.assertIsInstance(ga_DM, arcgis.gis.DatastoreManager,
                                  "geoanalytics.get_datastores() does not return a DM object")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_gis_get_datastores(self):
        """
        Test to get all DatastoreManager for all servers
        :return:
        """
        try:
            DM_list = self.gis._datastores

            self.assertGreaterEqual(len(DM_list), 1,
                                    "gis._datastores returns less than 1 DM obj")

            DM1 = DM_list[0]
            self.assertIsInstance(DM1, arcgis.gis.DatastoreManager,
                                  "gis._datastores does not return DM objects")
            print("Datastores in self.gis: ")
            for dm in DM_list:
                print(str(dm))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_hostingDM_search_noparams(self):
        """
        Test use DatastoreManager obj to search for Datastore objects
        :return:
        """
        try:
            #get the datastore manager of the hosting server
            DM_list = self.gis._datastores
            DM_t1 = [DM for DM in DM_list if DM._server['serverFunction'] == '']
            DM_hosted_server = DM_t1[0]

            #run the search method
            DS_list = DM_hosted_server.search()
            self.assertIsNotNone(DS_list, "Calling search() on hosting server DataStoreManager returns NOne")
            self.assertGreaterEqual(len(DS_list), 1, "No Datastore objs were returned by search() method")

            #ensure search returns obj of type DAtastore
            DS1 = DS_list[0]
            self.assertIsInstance(DS1, arcgis.gis.Datastore,
                                  "search() of DatastoreManager does not return Datastore objs")

            print("List of datastores in hosting server:")
            for ds in DS_list:
                print(str(ds))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_geoanalyticsDM_search_noparams(self):
        """
        Test use DatastoreManager obj of Geoanalytics server to search for Datastore objects
        :return:
        """
        try:
            # get the datastore manager of the geoanalytics server
            from arcgis import geoanalytics
            ga_DM = geoanalytics.get_datastores(self.gis)

            # run the search method
            DS_list = ga_DM.search()
            self.assertIsNotNone(DS_list, "Calling search() on ga server DataStoreManager returns NOne")
            self.assertGreaterEqual(len(DS_list), 1, "No Datastore objs were returned by search() method")

            # ensure search returns obj of type DAtastore
            DS1 = DS_list[0]
            self.assertIsInstance(DS1, arcgis.gis.Datastore,
                                  "search() of DatastoreManager does not return Datastore objs")

            print("List of datastores in ga server:")
            for ds in DS_list:
                print(str(ds))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_geoanalyticsDM_add_BDFS_winUNC(self):
        """
        Test use DatastoreManager obj of Geoanalytics server to add Big Data File Share data stores from a Windows
        UNC location
        :return:
        """
        try:
            # get the datastore manager of the geoanalytics server
            from arcgis import geoanalytics
            ga_DM = geoanalytics.get_datastores(self.gis)

            # add unittest_ChicagoCrime BDFS
            bdfs_title = "unittest_fortune500"
            data_path = os.path.join(self.qalab_cls_path, "fortune500_BDFS")
            print("Registering datastore from: " + data_path)

            registered_ds = ga_DM.add_bigdata(bdfs_title, data_path)

            #ensure BDFS was added
            self.assertIsNotNone(registered_ds, "add_bigdata() returns none")
            self.assertIsInstance(registered_ds, arcgis.gis.Datastore,
                                  "add_bigdata() does not return a Datastore obj on success")

            print("Successfully registered BDFS using add_bigdata()")

            #ensure BDFS can be searched
            DS_list = ga_DM.search()
            search_list = [ds for ds in DS_list if ds.datapath.__contains__(bdfs_title)]
            self.assertGreaterEqual(len(search_list), 1,
                                    "Newly added BDFS cannot be searched")

            print("Added BDFS can be successfully searched using DatastoreManager.search()")

            # ensure added BDFS creates and item
            # TODO finish this

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

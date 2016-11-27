#-------------------------------------------------------------------------------
# Name:        Item class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
import os
from dino_utils.dino_precondition_checks import PreconditionChecks
from dino_utils.dino_precondition_checks import PortalUtils
from dino_utils.dino_configs import DinoConfigs
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
    Set up code for full arcgis.gis module Item class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Item_portal_builtin(unittest.TestCase):
    """
    Test to check if a Item object works with builtin portal
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
        cls.portal_username = _conf_reader['teamportal']['publisher1']
        cls.portal_password = _conf_reader['teamportal']['publisher1_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_data_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_dataprep']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_dataprep']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_Item_portal_builtin class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_Item_"

        #region delete old outputs
        self.test_case_name = self.namePrefix + self._testMethodName
        search_result = PortalUtils.search_portal_item(self.gis, self.test_case_name, None)

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
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_publish_vtpk(self):
        vtpk_package_name = "set2_vtpk_worldgreen.vtpk"

        #region delete old service on portal
        service_title = os.path.splitext(vtpk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(self.gis, service_title, 'Vector Tile Service')
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail('Cannot delete old service output. Skipping test.')
        #endregion

        try:
            # search for vtpk item
            sr = self.gis.content.search(vtpk_package_name, item_type = 'Vector Tile Package', max_items = 1)
            if sr is not None and len(sr) > 0:
                vtpk_item = sr[0]
                print("Old VTPK item found and will be used")

            else:
                print("Old VTPK not found on portal. Adding new")
                file_path = os.path.join(self.qalab_data_path, "packages", vtpk_package_name)
                vtpk_item = self.gis.content.add({'type': 'Vector Tile Package'}, file_path)

            # publish vtpk item
            publish_output = vtpk_item.publish()

            #validate
            if publish_output is None:
                self.fail("Failed to publish VTPK item")
            else:
                #validate return type
                self.assertIsInstance(publish_output, arcgis.gis.Item, "item.publish does not return "
                                        "an Item upon success. Instead it returns: " + str(type(publish_output)))

                # validate item's type is vector tile service
                self.assertEqual(publish_output.type, 'Vector Tile Service', 'Publishing VPTK does not create an item '
                                                                             'of type Vector Tile Service')

                #validate service item has layers
                self.assertTrue(len(publish_output.layers) > 0, "No layers found in Vector Tile Service")
                print("Passed: VTPK successfully published as VTS")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_publish_spk(self):
        spk_package_name = "set2_spk_SD3dbuildings.spk"

        #region delete old service on portal
        service_title = os.path.splitext(spk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(self.gis, service_title, 'Scene Service')
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail('Cannot delete old service output. Skipping test.')
        #endregion

        try:
            # search for spk item
            sr = self.gis.content.search(spk_package_name, item_type='Scene Package', max_items=1)
            if sr is not None and len(sr) > 0:
                spk_item = sr[0]
                print("Old SPK item found and will be used")

            else:
                print("Old SPK not found on portal. Adding new")
                file_path = os.path.join(self.qalab_data_path, "packages", spk_package_name)
                spk_item = self.gis.content.add({'type': 'Scene Package'}, file_path)

            # publish vtpk item
            publish_output = spk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish SPK item")
            else:
                # validate return type
                self.assertIsInstance(publish_output, arcgis.gis.Item, "item.publish does not return "
                                                                       "an Item upon success. Instead it returns: " + str(
                    type(publish_output)))

                # validate item's type is vector tile service
                self.assertEqual(publish_output.type, 'Scene Service', 'Publishing SPK does not create an item '
                                                                             'of type Scene Service')

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Scene Service")
                print("Passed: SPK successfully published as WSL")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_publish_tpk(self):
        tpk_package_name = "set2_tpk_SD.tpk"

        #region delete old service on portal
        service_title = os.path.splitext(tpk_package_name)[0]
        old_sr = PortalUtils.search_portal_item(self.gis, service_title, 'Map Service')
        if old_sr is not None:
            delete_result = PortalUtils.delete_portal_item(self.gis, old_sr)
            if not delete_result:
                self.fail('Cannot delete old service output. Skipping test.')
        #endregion

        try:
            # search for spk item
            sr = self.gis.content.search(tpk_package_name, item_type='Tile Package', max_items=1)
            if sr is not None and len(sr) > 0:
                tpk_item = sr[0]
                print("Old TPK item found and will be used")

            else:
                print("Old TPK not found on portal. Adding new")
                file_path = os.path.join(self.qalab_data_path, "packages", tpk_package_name)
                tpk_item = self.gis.content.add({'type': 'Tile Package'}, file_path)

            # publish tpk item
            publish_output = tpk_item.publish()

            # validate
            if publish_output is None:
                self.fail("Failed to publish TPK item")
            else:
                # validate return type
                self.assertIsInstance(publish_output, arcgis.gis.Item, "item.publish does not return "
                                                                       "an Item upon success. Instead it returns: " + str(
                    type(publish_output)))

                # validate item's type is vector tile service
                self.assertEqual(publish_output.type, 'Map Service', 'Publishing TPK does not create an item '
                                                                             'of type Map Service')

                # # validate service item has layers
                # self.assertTrue(len(publish_output.layers) > 0, "No layers found in Map Service")
                print("Passed: TPK successfully published as WTL")

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
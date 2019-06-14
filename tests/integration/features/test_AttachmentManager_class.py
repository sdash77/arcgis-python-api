#-------------------------------------------------------------------------------
# Name:        AttachmentManager class tests
# Purpose:     Tests for reading, editing FeatureLayer definitions
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
    from arcgis import features
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Features module")
def setUpModule():
    """
    Set up code for full arcgis.features module Featurelayer class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_AttachmentManager_portal(unittest.TestCase):
    """
    Test to check if a FeatureLayer object works with builtin portal
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
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureLayerManager_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False)
        if cls.gis is None:
            cls.class_skip = True
        #endregion

        #region print banner
        print("==================================================================")
        print("Beginning tests in Test_FeatureLayer_portal class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        # self.namePrefix = "dino_FeatureLayer_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(test_skip, "Precondition error, skipping test.")
    def test_create_AttachmentManager_object(self):
        """
        Purpose of this test is to create instances of AttachmentManager class in multiple ways
        :return:
        """
        try:
            test_item = PortalUtils.search_portal_item(self.gis, "dino_AttachmentManager_basic", "Feature Layer")
            self.assertIsInstance(test_item, arcgis.gis.Item, "Input item is not of type Item, cannot run rest of the test case")

            #check Item.layers property yields a list of FeatureLayer objects
            flayers = test_item.layers
            self.assertIsInstance(flayers, list, "Item.layers property does not return a list")
            self.assertIsInstance(flayers[0], arcgis.features.FeatureLayer,
                                  "Item.layers property does not return a list of FeatureLayer objects")

            #check a FeatureLayerManager object can be created from FeatureLayer object
            flayer0 = flayers[0]
            flayer0_amgr = flayer0.attachments
            self.assertIsInstance(flayer0_amgr, arcgis.features.managers.AttachmentManager,
                                  "Cannot create a AttachmentManager obj from FeatureLayer Item")

            #check FeatureLayerManager object can be created from item
            am2 = features.managers.AttachmentManager(test_item)
            self.assertIsInstance(am2, arcgis.features.managers.AttachmentManager,
                                  "AttachmentManager constructor does not create a manager object")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Precondition error, skipping test.")
    def test_download_png_attachment(self):
        """
        Download png to default dir and given dir
        """
        try:
            test_item = PortalUtils.search_portal_item(self.gis, "dino_AttachmentManager_basic", "Feature Layer")

            #get attachment list
            flayer = test_item.layers[0]
            attch_list = flayer.attachments.get_list(1)
            self.assertGreaterEqual(len(attch_list), 1, "At least 1 attchment should be found")
            self.assertEqual(attch_list[0]['id'], 1, 'attachment id mismatch')
            self.assertEqual(attch_list[0]['name'], 'img_png.png', "attachment name mismatch")

            #download
            download_result = flayer.attachments.download(1,1)
            self.assertIsInstance(download_result, str, "download does not return a str path")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Precondition error, skipping test.")
    def test_download_pdf_attachment(self):
        """
        Download png to default dir and given dir
        """
        try:
            test_item = PortalUtils.search_portal_item(self.gis, "dino_AttachmentManager_basic", "Feature Layer")

            # get attachment list
            flayer = test_item.layers[0]
            attch_list = flayer.attachments.get_list(3)
            self.assertGreaterEqual(len(attch_list), 1, "At least 1 attchment should be found")
            self.assertEqual(attch_list[0]['id'], 3, 'attachment id mismatch')
            self.assertEqual(attch_list[0]['name'], 'crime_pdf.pdf', "attachment name mismatch")

            # download
            download_result = flayer.attachments.download(3, 3)
            self.assertIsInstance(download_result, str, "download does not return a str path")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Precondition error, skipping test.")
    def test_download_multiple_attachments(self):
        """
        Download png to default dir and given dir
        """
        try:
            test_item = PortalUtils.search_portal_item(self.gis, "dino_AttachmentManager_basic", "Feature Layer")

            # get attachment list
            flayer = test_item.layers[0]
            attch_list = flayer.attachments.get_list(6)
            self.assertGreaterEqual(len(attch_list), 3, "At least 3 attachments should be found")
            self.assertEqual(attch_list[0]['id'], 6, 'attachment id mismatch')
            self.assertEqual(attch_list[0]['name'], 'crime_pdf.pdf', "attachment name mismatch")

            # download
            download_result = flayer.attachments.download(6, 6)
            self.assertIsInstance(download_result, str, "download does not return a str path")

            download_result2 = flayer.attachments.download(6, 7)
            self.assertIsInstance(download_result2, str, "download does not return a str path")

            download_result3 = flayer.attachments.download(6, 8)
            self.assertIsInstance(download_result3, str, "download does not return a str path")

            print(download_result3)

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

class Test_AttachmentManager_online(unittest.TestCase):
    """
    Test to check if a FeatureLayer object works with AGO
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
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureLayerManager_cls']
        # endregion

        # region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False)
        if cls.gis is None:
            cls.class_skip = True
        # endregion

        # region print banner
        print("==================================================================")
        print("Beginning tests in Test_FeatureLayer_portal class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        # self.namePrefix = "dino_FeatureLayer_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
                                     str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(test_skip, "Precondition error, skipping test.")
    def test_create_AttachmentManager_object(self):
        """
        Purpose of this test is to create instances of AttachmentManager class in multiple ways
        :return:
        """
        try:
            test_item = PortalUtils.search_portal_item(self.gis, "dino_AttachmentManager_basic",
                                                       "Feature Layer")
            self.assertIsInstance(test_item, arcgis.gis.Item,
                                  "Input item is not of type Item, cannot run rest of the test case")

            # check Item.layers property yields a list of FeatureLayer objects
            flayers = test_item.layers
            self.assertIsInstance(flayers, list, "Item.layers property does not return a list")
            self.assertIsInstance(flayers[0], arcgis.features.FeatureLayer,
                                  "Item.layers property does not return a list of FeatureLayer objects")

            # check a FeatureLayerManager object can be created from FeatureLayer object
            flayer0 = flayers[0]
            flayer0_amgr = flayer0.attachments
            self.assertIsInstance(flayer0_amgr, arcgis.features.managers.AttachmentManager,
                                  "Cannot create a AttachmentManager obj from FeatureLayer Item")

            # check FeatureLayerManager object can be created from item
            am2 = features.managers.AttachmentManager(test_item)
            self.assertIsInstance(am2, arcgis.features.managers.AttachmentManager,
                                  "AttachmentManager constructor does not create a manager object")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Precondition error, skipping test.")
    def test_download_png_attachment(self):
        """
        Download png to default dir and given dir
        """
        try:
            test_item = PortalUtils.search_portal_item(self.gis, "dino_AttachmentManager_basic",
                                                       "Feature Layer")

            # get attachment list
            flayer = test_item.layers[0]
            attch_list = flayer.attachments.get_list(1)
            self.assertGreaterEqual(len(attch_list), 1, "At least 1 attchment should be found")
            self.assertEqual(attch_list[0]['id'], 1, 'attachment id mismatch')
            self.assertEqual(attch_list[0]['name'], 'img_png.png', "attachment name mismatch")

            # download
            download_result = flayer.attachments.download(1, 1)
            self.assertIsInstance(download_result, str, "download does not return a str path")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Precondition error, skipping test.")
    def test_download_pdf_attachment(self):
        """
        Download png to default dir and given dir
        """
        try:
            test_item = PortalUtils.search_portal_item(self.gis, "dino_AttachmentManager_basic",
                                                       "Feature Layer")

            # get attachment list
            flayer = test_item.layers[0]
            attch_list = flayer.attachments.get_list(3)
            self.assertGreaterEqual(len(attch_list), 1, "At least 1 attchment should be found")
            self.assertEqual(attch_list[0]['id'], 3, 'attachment id mismatch')
            self.assertEqual(attch_list[0]['name'], 'crime_pdf.pdf', "attachment name mismatch")

            # download
            download_result = flayer.attachments.download(3, 3)
            self.assertIsInstance(download_result, str, "download does not return a str path")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Precondition error, skipping test.")
    def test_download_multiple_attachments(self):
        """
        Download png to default dir and given dir
        """
        try:
            test_item = PortalUtils.search_portal_item(self.gis, "dino_AttachmentManager_basic",
                                                       "Feature Layer")

            # get attachment list
            flayer = test_item.layers[0]
            attch_list = flayer.attachments.get_list(6)
            self.assertGreaterEqual(len(attch_list), 3, "At least 3 attachments should be found")
            self.assertEqual(attch_list[0]['id'], 6, 'attachment id mismatch')
            self.assertEqual(attch_list[0]['name'], 'crime_pdf.pdf', "attachment name mismatch")

            # download
            download_result = flayer.attachments.download(6, 6)
            self.assertIsInstance(download_result, str, "download does not return a str path")

            download_result2 = flayer.attachments.download(6, 7)
            self.assertIsInstance(download_result2, str, "download does not return a str path")

            download_result3 = flayer.attachments.download(6, 8)
            self.assertIsInstance(download_result3, str, "download does not return a str path")

            print(download_result3)

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
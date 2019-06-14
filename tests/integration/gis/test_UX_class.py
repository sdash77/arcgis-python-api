#-------------------------------------------------------------------------------
# Name:        UX class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
import os
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
from pathlib import Path
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
    Set up code for full arcgis.gis module ResourceManager class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_UX_portal(unittest.TestCase):
    """
    Test to check if a ResourceManager object works with builtin portal
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
        cls.qalab_data_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_dataprep']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_UX_cls']
        cls.qalab_output_root = cls.qalab_base_path + _conf_reader2['test_data']['qalab_output_root']
        cls.qalab_cls_name = _conf_reader2['test_data']['qalab_UX_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False)
        print("Connected to : " + str(cls.gis))
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_UX_portal class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_UX_"

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
        self.time_stamp = str.format("{0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_set_banner_html(self):
        """
        Change the banner of arcgis enterprise using html
        :return:
        """
        try:
            banner = "<div> Hello </div>"
            change_result = self.gis.admin.ux.set_banner(None, False, banner)
            self.assertTrue(change_result, "Cannot set html as banner")


            #reset the banner
            # reset_result = self.gis.admin.ux.set_banner('banner-1')

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_get_summary(self):
        """
        gets the summary as string
        """
        try:
            res = self.gis.admin.ux.summary
            if res is None or \
               len(res) == 0:
                self.gis.admin.ux.summary = "random string"
            res2 = self.gis.admin.ux.summary
            self.assertTrue(isinstance(res2, str), "Summary should be a string")
            self.gis.admin.ux.summary = res

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_set_summary_null(self):
        """
        resets the summary as string
        """
        try:
            summary = self.gis.admin.ux.summary
            self.gis.admin.ux.summary = None
            res = self.gis.admin.ux.summary
            self.assertTrue((isinstance(res, str) or res is None), "Summary is not None")
            self.gis.admin.ux.summary = summary

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_set_summary_empty(self):
        """
        resets the summary as string using empty string
        """
        try:
            summary = self.gis.admin.ux.summary
            self.gis.admin.ux.summary = ""
            res = self.gis.admin.ux.summary
            self.assertTrue(res is None, "Summary is not None")
            self.gis.admin.ux.summary = summary
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_set_summary_random(self):
        """
        resets the summary as string
        """
        try:
            # store the default
            summary = self.gis.admin.ux.summary
            self.gis.admin.ux.summary = 'random string'
            res = self.gis.admin.ux.summary
            self.assertTrue(isinstance(res, str), "Summary is not a string")
            self.assertTrue(res == 'random string', "Summary should be 'random string' not %s" % res)
            # reset to test default
            self.gis.admin.ux.summary = summary
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())



    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_set_banner_built_in_image(self):
        """
        Change the banner of arcgis enterprise using html
        :return:
        """
        try:
            change_result = self.gis.admin.ux.set_banner('banner-1', True)
            self.assertTrue(change_result, "Cannot set banner using built in image")


            # reset the banner
            # reset_result = self.gis.admin.ux.set_banner('banner-1')

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_set_banner_built_in_image_custom_html(self):
        """
        Change the banner of arcgis enterprise using html
        :return:
        """
        try:
            banner_file = 'banner-1'
            custom_html = "<img src='images/{}.jpg' " \
                                                   "style='-webkit-border-radius:0 0 10px 10px; -moz-border-radius:0 0 10px 10px; "\
                                                   "-o-border-radius:0 0 10px 10px; border-radius:0 0 10px 10px; margin-top:0; "\
                                                   "width:960px; height:180px;'/><div style='position:absolute; bottom:80px; "\
                                                   "left:80px; max-height:65px; width:660px; margin:0;'>"\
                                                   "<img src='{}/portals/self/resources/thumbnail.png?token=SECURITY_TOKEN' "\
                                                   "class='esriFloatLeading esriTrailingMargin025' style='margin-bottom:0; "\
                                                   "max-height:100px;'/><span style='position:absolute; bottom:0; margin-bottom:0; "\
                                                   "line-height:normal; font-family:HelveticaNeue,Verdana; font-weight:300; "\
                                                   "font-size:16px; color:#369;'>{}</span></div>".format(banner_file,
                                                                                                         self.gis._con.baseurl,
                                                                                                         self.gis.properties.name)
            change_result = self.gis.admin.ux.set_banner(banner_file, True, custom_html)

            self.assertTrue(change_result, "Cannot set banner using built in image and custom html")


            # reset the banner
            # reset_result = self.gis.admin.ux.set_banner('banner-1')

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_set_banner_custom_image(self):
        """
        Change the banner of arcgis enterprise using custom image
        :return:
        """
        try:
            banner_file = os.path.join(self.qalab_cls_path, 'fire_banner.png')
            change_result = self.gis.admin.ux.set_banner(banner_file)

            self.assertTrue(change_result, "Cannot set banner using built in image and custom html")


            # reset the banner
            # reset_result = self.gis.admin.ux.set_banner('banner-1')

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_remove_banner(self):
        """
        Change the banner of arcgis enterprise using html
        :return:
        """
        try:
            change_result = self.gis.admin.ux.set_banner(None)
            self.assertTrue(change_result, "Cannot remove banner")
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
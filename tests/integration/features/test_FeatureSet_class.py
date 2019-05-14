#-------------------------------------------------------------------------------
# Name:        Feature class tests
# Purpose:     Tests for checking the save function of the feature class works properly.
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

class Test_Feature_class(unittest.TestCase):
    """
    Test to check if a UserManager object works with builtin portal
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
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureSet_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_Feature_class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_NetworkAnalysis_"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def test_save_featureSet_withFeatures_to_csv_method(self):
        """
        Test to check if the save function operates successfully when a non-empty featureSet is to be saved to a CSV file
        :return:
        """
        try:

            temp = None
            gis = GIS()
            #calling a feature layer corresponding to the USA Freeway System in arcgis online
            content = gis.content.get('91c6a5f6410b4991ab0db1d7c26daacb')

            layer = content.layers[0]
            features_req = layer.query(where='OBJECTID = 1')

            csv_file = r'generatedCSVfile.csv'
            path = os.path.join(self.qalab_cls_path, csv_file)
            temp = features_req.save(self.qalab_cls_path, csv_file)

            print(temp)

            self.assertEqual(temp, path, "CSV file not created successfully")



        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_save_featureSet_withoutFeatures_to_csv_method(self):
        """
        Test to check if the save function operates successfully when an empty featureSet is to be saved to a CSV file
        :return:
        """
        try:

            temp = None

            gis = GIS()
            # calling a feature layer corresponding to the USA Freeway System in arcgis online
            content = gis.content.get('91c6a5f6410b4991ab0db1d7c26daacb')

            layer = content.layers[0]
            features_req = layer.query(where='OBJECTID = -1')

            csv_file = r'generatedCSVfile.csv'
            path = os.path.join(self.qalab_cls_path, csv_file)
            temp = features_req.save(self.qalab_cls_path, csv_file)

            print(temp)

            self.assertEqual(temp, path, "CSV file not created successfully")



        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


    def tearDown(self):
        print("------------------------------------------------------------------\n")


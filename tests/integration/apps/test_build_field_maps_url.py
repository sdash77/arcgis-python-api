#-------------------------------------------------------------------------------
# Name:        Field Maps Integration Tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
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
    from arcgis.apps import build_field_maps_url
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in Field Maps Integration")
def setUpModule():
    """
    Run checks for host system
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_Field_Maps_Integrations(unittest.TestCase):
    """
    Test the creation of app url schemes
    """

    @classmethod
    def setUpClass(cls):
        """
        Check if ArcGIS.com can be reached
        :return:
        """
        _conf_reader = ConfigParser()
        _conf_reader.read(DinoConfigs.portal_list_file, 'UTF-8')

        print("==================================================================")
        print("Beginning tests in Test_Field_Maps_Integrations class")

    def setUp(self):
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_"
        self.portal_url = "https://rags19003.ags.esri.com/portal"
        self.webmap = "7584d0ac469748339004a01c80b55fc1"
        self.center = "41.780618,-88.179449"
        self.center_address = "100 Commercial St, Portland, ME 04101"
        self.scale = 3000
        self.bookmark = "Esri Portland Office"
        self.wkid = 4326
        self.search = "75 Washington Ave, Portland, ME 04101"
        self.geometry = {"rings":[[[-117.1961714,34.0547155],[-117.1961714,34.0587155],[-117.2001714,34.0587155],[-117.2001714,34.0547155]]],"spatialReference":{"wkid":4326}}
        self.feature_layer = "https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0"
        self.fields = {"name": "Mayor of Portland"}
        self.feature_id = "0000000-0000-0000-0000-0000000000000"
        self.callback = "arcgis-explorer://"
        self.callback_prompt = "Explore At Location"

        t = datetime.datetime.now()
        self.time_stamp = str.format("Time stamp: {0}_{1}_{2}_{3}_{4}_{5}", str(t.year),
              str(t.month), str(t.day), str(t.hour), str(t.minute), str(t.second))
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    def test_field_maps_open_map(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                      action="open")
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext={}&itemID={}".format(
                "open",
                self.webmap,
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_only_portal(self):
        try:
            url = build_field_maps_url(portal=self.portal_url)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?portalURL={}".format(
                self.portal_url
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_portal_url(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                      portal=self.portal_url,
                                      action="open")
            self.assertEqual(url, "https://fieldmaps.arcgis.app?portalURL={}&referenceContext={}&itemID={}".format(
                self.portal_url,
                "open",
                self.webmap
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_center_scale_map(self):
        try:
            url = build_field_maps_url(action="center", webmap=self.webmap, center=[41.780618, -88.179449], scale=self.scale)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=center&itemID={}&scale={}&center={}".format(
                self.webmap,
                self.scale,
                self.center
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_center_scale_map_wkid(self):
        try:
            url = build_field_maps_url(action="center", webmap=self.webmap, center="41.780618,-88.179449", scale=self.scale, wkid=self.wkid)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=center&itemID={}&scale={}&wkid={}&center={}".format(
                self.webmap,
                self.scale,
                self.wkid,
                self.center
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_center_geocoded_address(self):
        try:
            url = build_field_maps_url(action="center", webmap=self.webmap, center=self.center_address, scale=self.scale)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=center&itemID={}&scale={}&center={}".format(
                self.webmap,
                self.scale,
                "100+Commercial+St,+Portland,+ME+04101"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_search_address(self):
        try:
            url = build_field_maps_url(action="search", webmap=self.webmap, search=self.search)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=search&itemID={}&search={}".format(
                self.webmap,
                "75+Washington+Ave,+Portland,+ME+04101"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_search_asset(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                      action="search",
                                      search=43141)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=search&itemID={}&search={}".format(
                self.webmap,
                "43141"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_view_bookmark(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                      action="open",
                                      bookmark=self.bookmark)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=open&itemID={}&bookmark={}".format(
                self.webmap,
                "Esri+Portland+Office"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_initiate_capture(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                      action="addFeature",
                                      feature_layer=self.feature_layer)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=addFeature&itemID={}&featureSourceURL={}".format(
                self.webmap,
                self.feature_layer
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_initiate_capture_with_geometry(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                       action="addFeature",
                                       feature_layer=self.feature_layer,
                                       geometry=self.geometry)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=addFeature"
                                  "&itemID=7584d0ac469748339004a01c80b55fc1"
                                  "&featureSourceURL=https://examples.esri.com/server/rest/services/Hosted/test_service/FeatureServer/0"
                                  "&geometry={%22rings%22:%5B%5B%5B-117.1961714,34.0547155%5D,%5B-117.1961714,34.0587155%5D,%5B-117.2001714,34.0587155%5D,%5B-117.2001714,34.0547155%5D%5D%5D,%22spatialReference%22:{%22wkid%22:4326}}")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_use_antenna(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                      action="addFeature",
                                      use_antenna_height=True,
                                      use_loc_profile=True,
                                      geometry="34.058030,-117.195940, 1200",
                                      feature_layer=self.feature_layer)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=addFeature&itemID={}&featureSourceURL={}"
                                  "&geometry=34.058030,-117.195940,1200&useAntennaHeight=true&useLocationProfile=true".format(
                self.webmap,
                self.feature_layer
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_callback(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                      action="addFeature",
                                      feature_layer=self.feature_layer,
                                      callback=self.callback,
                                      callback_prompt=self.callback_prompt)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=addFeature&itemID={}"
                                  "&featureSourceURL={}&callback={}&callbackPrompt={}".format(
                self.webmap,
                self.feature_layer,
                self.callback,
                "Explore%20At%20Location"
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_update_feature(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                      action="updateFeature",
                                      feature_layer=self.feature_layer,
                                      feature_id=self.feature_id)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=updateFeature&itemID={}"
                                  "&featureSourceURL={}&featureID={}".format(
                self.webmap,
                self.feature_layer,
                self.feature_id
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_anonymous(self):
        try:
            url = build_field_maps_url(webmap=self.webmap,
                                       action="open",
                                       anonymous=True)
            self.assertEqual(url, "https://fieldmaps.arcgis.app?referenceContext=open&itemID={}"
                                  "&anonymousAccess=true".format(
                self.webmap,
            ))
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_url_bad_action(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="blah")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
    
    def test_field_maps_url_no_action(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(webmap=self.webmap)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_url_invalid_webmap(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="center", webmap=123)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_search_without_webmap(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="search", search="100 Commercial St")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_bookmark_without_webmap(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="open", bookmark="100 Commercial St")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_center_without_webmap(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="center", center="100 Commercial St")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_invalid_scale(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="center", scale=123)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_wkid_without_center(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="center", webmap=self.webmap, wkid=4326)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_invalid_wkid(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="center", webmap=self.webmap, center="100 Commercial St", wkid="4326")
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    def test_field_maps_feature_layer_bad_action(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="open", webmap=self.webmap, feature_layer=self.feature_layer)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_fields_without_feature_layer(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="addFeature", webmap=self.webmap, fields={"name": "John Smith"})
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_geometry_without_feature_layer(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="addFeature", webmap=self.webmap, geometry=self.geometry)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
    
    def test_field_maps_use_antenna_height_without_feature_layer(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="addFeature", webmap=self.webmap, geometry=self.geometry, use_antenna_height=True)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_use_location_profile_bad_action(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="open", webmap=self.webmap, geometry=self.geometry,
                                     use_loc_profile=True, feature_layer=self.feature_layer)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
            
    def test_field_maps_feature_id_bad_action(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="addFeature", webmap=self.webmap, feature_id=self.feature_id)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
    
    def test_field_maps_callback_without_webmap(self):
        try:
            with self.assertRaises(ValueError):
                build_field_maps_url(action="addFeature", callback=self.callback)
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException
    
        except unittest.SkipTest as skipException:
            raise skipException
    
        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())
        
#TestModule
def tearDownModule():
    print("**End Field Maps Integration Tests Tests**")

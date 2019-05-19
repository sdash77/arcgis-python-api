#-------------------------------------------------------------------------------
# Name:        Feature class tests
# Purpose:     Tests for checking the save function of the feature class works properly.
#-------------------------------------------------------------------------------
import unittest
from dino_utils.dino_precondition_checks import PreconditionChecks
from dino_utils.dino_precondition_checks import PortalUtils
from dino_utils.dino_configs import DinoConfigs
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

        cls.portal_url = _conf_reader['datascienceqa']['url']
        cls.portal_username = _conf_reader['datascienceqa']['admin_user']
        cls.portal_password = _conf_reader['datascienceqa']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_FeatureSet_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False)
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

    def test_create_featureSet_withFeatures_from_geojson_method(self):
        """
        Test to check if the from_geojson function operates successfully when a non-empty featureSet is to be created
        from GeoJSON file
        :return:
        """
        try:
            geojson = {
                       "type": "FeatureCollection",
                       "features": [
                           {
                               "type": "Feature",
                               "id": "EONET_4176",
                               "geometry": {
                                   'type': 'LineString',
                                   'coordinates': [[128.9, -8.7], [129.1, -8.7], [128.9, -9.1], [129.1, -9.4], [129, -9.6], [128.8, -9.4], [128.5, -9.3]],
                                   'date': ['2019-05-09T00:00:00Z', '2019-05-09T06:00:00Z', '2019-05-09T12:00:00Z', '2019-05-09T18:00:00Z', '2019-05-10T00:00:00Z', '2019-05-10T06:00:00Z', '2019-05-10T12:00:00Z'],
                                   'spatialReference': {'wkid': 4326}
                               },
                               "properties": {
                                   'id': 'EONET_4176',
                                   'title': 'Tropical Cyclone Lili',
                                   'date': '2019-05-09T00:00:00Z',
                                   'OBJECTID': 7,
                                   'SHAPE': {'paths': [[[128.9, -8.7], [129.1, -8.7], [128.9, -9.1], [129.1, -9.4], [129, -9.6], [128.8, -9.4], [128.5, -9.3]]],
                                             'spatialReference': {'wkid': 4326}}
                               }
                           },
                           {
                               "type": "Feature",
                               "id": "EONET_4178",
                               "geometry": {
                                   'type': 'Point',
                                   'coordinates': [24.7758, 56.08683],
                                   'date': '2019-05-07T16:27:00Z'
                               },
                               "properties": {
                                   'id': 'EONET_4178',
                                   'title': 'Wildfires - Lithuania and Latvia',
                                   'date': '2019-05-07T16:27:00Z',
                                   'OBJECTID': 8,
                                   'SHAPE': {'x': 24.7758, 'y': 56.08683,
                                             'spatialReference': {'wkid': 4326}}
                               }
                           },
                           {
                               "type": "Feature",
                               "id": "EONET_354",
                               "geometry": {
                                   'type': 'Polygon',
                                   'coordinates': [[[127.84286499023438, 1.6633016286241373], [127.84286499023438, 1.7379700300000804], [127.91641235351562, 1.7379700300000804], [127.91641235351562, 1.6633016286241373], [127.84286499023438, 1.6633016286241373]]],
                                   'date': ['2016-03-16T00:00:00Z']
                               },
                               "properties": {
                                   'id': 'EONET_354',
                                   'title': 'Dukono Volcano, Indonesia',
                                   'date': '2016-03-16T00:00:00Z',
                                   'OBJECTID': 114,
                                   'SHAPE': {'rings': [[[127.84286499023438, 1.6633016286241373], [127.84286499023438, 1.7379700300000804], [127.91641235351562, 1.7379700300000804], [127.91641235351562, 1.6633016286241373], [127.84286499023438, 1.6633016286241373]]],
                                             'spatialReference': {'wkid': 4326}}
                               }
                           }
                       ]
                    }

            from arcgis.features import Feature, FeatureSet, FeatureCollection
            from arcgis.geometry import Geometry
            f_set = FeatureSet.from_geojson(geojson)
            self.assertIsNotNone(f_set, "from_geojson failed!")

            fc = FeatureCollection.from_featureset(f_set, symbol=None,
                                                   name="Natural Disaster Feed Events Feature Collection")
            self.assertEqual(len(fc.query()), 3, "from_featureset failed!")

            df = fc.query().sdf
            map_g = self.gis.map()
            for ea in fc.query():
                msg = "Failed to get geoextent from ", ea.geometry_type, \
                      " - ", ea.get_value('title'), " - ", ea.geometry, " - ", ea.get_value('date')
                self.assertIsInstance(Geometry(ea.geometry).extent, tuple, msg)

                if ea.get_value('type') == 'LineString':
                    df_sel = df[df['OBJECTID'] == ea.attributes['OBJECTID']]
                    df_sel.spatial.plot(map_widget=map_g,
                                        name=ea.get_value('title'),
                                        symbol_type='simple',
                                        symbol_style='s.')

                elif ea.get_value('type') == 'Point':
                    df_sel = df[df['OBJECTID'] == ea.attributes['OBJECTID']]
                    df_sel.spatial.plot(map_widget=map_g,
                                        name=ea.get_value('title'),
                                        symbol_type='simple',
                                        symbol_style='x')
                else:  # Polygon
                    df_sel = df[df['OBJECTID'] == ea.attributes['OBJECTID']]
                    df_sel.spatial.plot(map_widget=map_g,
                                        name=ea.get_value('title'),
                                        cmap='RdPu',
                                        symbol_type='simple',
                                        symbol_style='s',
                                        outline_style='s',
                                        outline_color=[0, 0, 0, 255],
                                        line_width=1.0)

            wm_title = "Unit Test Natural Disasters (FC only) Collection"
            wm_item = self.gis.content.search(wm_title, item_type = 'Web Map')
            if wm_item:
                wm_item[0].delete()
            web_map_properties = {'title': wm_title,
                                  'snippet': 'This web map contains multiple FC',
                                  'tags': 'ArcGIS Python API, Unit Test'}

            wm_item = map_g.save(item_properties=web_map_properties)
            self.assertIsNotNone(wm_item, "save failed!")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


    def tearDown(self):
        print("------------------------------------------------------------------\n")


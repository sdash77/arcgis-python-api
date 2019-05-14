#-------------------------------------------------------------------------------
# Name:        WebMap class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import unittest
import os
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
from integration.dino_utils.dino_configs import DinoConfigs
from configparser import ConfigParser
from pathlib import Path
import json
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
    from arcgis.mapping import WebMap
except ImportError:
    print("API import error. Quitting test")
    raise(exit())
#endregion PreCondition Check

#TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.raster module ImageryLayer class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: " , PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())

class Test_WebMap_AGO(unittest.TestCase):
    """
    Test to check if a ImageryLayer object works with builtin portal
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

        cls.portal_url = _conf_reader['arcgiscom']['url']
        cls.portal_username = _conf_reader['arcgiscom']['admin_user']
        cls.portal_password = _conf_reader['arcgiscom']['admin_password']

        _conf_reader2 = ConfigParser()
        _conf_reader2.read(DinoConfigs.root_init_file, 'UTF-8')

        cls.qalab_base_path = _conf_reader2['test_data']['qalab_base_path']
        cls.qalab_data_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_dataprep']
        cls.qalab_cls_path = cls.qalab_base_path + _conf_reader2['test_data']['qalab_WebMap_cls']
        cls.qalab_output_root = cls.qalab_base_path + _conf_reader2['test_data']['qalab_output_root']
        cls.qalab_cls_name = _conf_reader2['test_data']['qalab_WebMap_cls']
        #endregion

        #region precondition checks and sign in
        r1 = PreconditionChecks.can_ping_portal(cls.portal_url)
        if not r1:
            cls.class_skip = True

        cls.gis = GIS(cls.portal_url, cls.portal_username, cls.portal_password, verify_cert=False)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_WebMap_portal class")
        #endregion

    def setUp(self):
        test_skip = False #reset the skip flag
        print("Test: "+self._testMethodName)
        self.namePrefix = "dino_WebMap_"

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
    def test_WebMap_obj_from_item(self):
        try:
            #search for a web map and test instantiating a WebMap object
            search_result = PortalUtils.search_portal_item(self.gis, "dinotests_sample_demographic_map", "Web Map")
            if search_result:
                wm_item = search_result
            else:
                self.skipTest('Unable to find required webmap item')

            wm_obj = WebMap(wm_item)
            #assert
            self.assertIsInstance(wm_obj,arcgis.mapping.WebMap, "Cannot create WebMap object from item")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_create_empty_WebMap_obj(self):
        try:
            wm_obj = WebMap()
            # assert
            self.assertIsInstance(wm_obj, arcgis.mapping.WebMap, "Cannot create empty WebMap")
            self.assertTrue(hasattr(wm_obj.definition, 'baseMap'), 'Empty WebMap obj is missing baseMap')

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_add_layer_simple_FL(self):
        """
        Compose a new web map with one operational layer.
        :return: 
        """
        try:
            wm_obj = WebMap()
            # assert
            self.assertIsInstance(wm_obj, arcgis.mapping.WebMap, "Cannot create empty WebMap")
            self.assertTrue(hasattr(wm_obj.definition, 'baseMap'), 'Empty WebMap obj is missing baseMap')

            #use a hosted feature service layer for operational layer
            from arcgis.features import FeatureLayer
            fl = FeatureLayer(url='https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities/FeatureServer/0',
                              gis=self.gis)

            #add operational layer
            wm_obj.add_layer(fl)
            self.assertTrue(hasattr(wm_obj.definition, 'operationalLayers'), 'Adding a layer does not create operationalLayers')

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_add_table(self):
        """
        Compose a new web map with one table
        """
        # Set up the WebMap and Table instances
        wm_obj = WebMap()
        from arcgis.features import Table
        table_service_url = 'https://services2.arcgis.com/PWJUSsdoJDp7SgLj/arcgis/rest/services/DavidVsMap_WFL1/FeatureServer/1'
        table = Table(table_service_url, self.gis)
        wm_obj.add_table(table)

        # Assert that the table was set up correctly
        self.assertTrue('tables' in wm_obj._webmapdict)
        table_added_underlying_dict = wm_obj._webmapdict['tables'][0]
        table_added_public_property_obj = wm_obj.tables[0]
        self.assertEqual(table_service_url, table_added_underlying_dict['url'])
        self.assertEqual(table_service_url, table_added_public_property_obj.url)
        self.assertEqual(len(wm_obj.tables), 1)
        self.assertTrue('popupInfo' in table_added_underlying_dict)

        # Remove the table
        wm_obj.remove_table(table_added_public_property_obj)

        # Assert that the table was removed correctly
        self.assertEqual(len(wm_obj.tables), 0)

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_add_layer_simple_FL_existing_wm(self):
        """
        Compose a new web map with one operational layer.
        :return:
        """
        try:
            # get existing web map with 2 layers.
            search_result = PortalUtils.search_portal_item(self.gis, "dinotests_sample_demographic_map2", "Web Map")
            if search_result:
                wm_item = search_result
            else:
                self.skipTest('Unable to find required webmap item')

            wm_obj = WebMap(wm_item)

            # region: Bug: Call add layers without inspecting list of layers

            # use a hosted feature service layer for operational layer
            from arcgis.features import FeatureLayer
            fl = FeatureLayer(
                url='https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities/FeatureServer/0',
                gis=self.gis)

            #add operational layer
            wm_obj.add_layer(fl)
            self.assertEqual(3, len(wm_obj.layers), "Error adding layer to existing web map")
            #endregion

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_add_multilayer_FLC_Item(self):
        """
        Compose a new web map and add an Item with multiple feature layers
        :return: 
        """
        try:
            wm_obj = WebMap()
            # assert
            self.assertIsInstance(wm_obj, arcgis.mapping.WebMap, "Cannot create empty WebMap")
            self.assertTrue(hasattr(wm_obj.definition, 'baseMap'), 'Empty WebMap obj is missing baseMap')

            # flc_item = self.gis.content.get('99fd67933e754a1181cc755146be21ca')
            flc_item = self.gis.content.get('36ed2b2b92bc4131af4a08634bbfa115')

            # add item
            wm_obj.add_layer(flc_item)
            self.assertTrue(hasattr(wm_obj.definition, 'operationalLayers'),
                            'Adding a layer does not create operationalLayers')
            self.assertEqual(3,len(wm_obj.definition.operationalLayers))
            self.assertEqual(3, len(wm_obj.layers))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_save_with_correct_extent(self):
        """
        Compose a new web map and add an Item with multiple feature layers
        :return: 
        """
        try:
            wm_obj = WebMap()
            # assert
            self.assertIsInstance(wm_obj, arcgis.mapping.WebMap, "Cannot create empty WebMap")
            self.assertTrue(hasattr(wm_obj.definition, 'baseMap'), 'Empty WebMap obj is missing baseMap')

            # flc_item = self.gis.content.get('99fd67933e754a1181cc755146be21ca')
            flc_item = self.gis.content.get('36ed2b2b92bc4131af4a08634bbfa115')

            # add item
            wm_obj.add_layer(flc_item)
            self.assertTrue(hasattr(wm_obj.definition, 'operationalLayers'),
                            'Adding a layer does not create operationalLayers')
            self.assertEqual(3,len(wm_obj.definition.operationalLayers))
            self.assertEqual(3, len(wm_obj.layers))

            #save web map
            wmitem = wm_obj.save({'title':self.test_case_name,
                                  'snippet':"automation",
                                  'tags':"dev"})
            self.assertIsInstance(wmitem, arcgis.gis.Item)
            self.assertIsNotNone(wmitem.extent, "Extent came out empty")

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_update_webmap_empty_item_properties(self):
        """
        Update an existing web map with empty item properties dictionary.
        :return:
        """
        try:
            wm_obj = WebMap()

            # flc_item = self.gis.content.get('99fd67933e754a1181cc755146be21ca')
            flc_item = self.gis.content.get('36ed2b2b92bc4131af4a08634bbfa115')

            # add item
            wm_obj.add_layer(flc_item)
            self.assertTrue(hasattr(wm_obj.definition, 'operationalLayers'),
                            'Adding a layer does not create operationalLayers')
            self.assertEqual(len(flc_item.layers), len(wm_obj.definition.operationalLayers))
            self.assertEqual(len(flc_item.layers), len(wm_obj.layers))

            # save web map
            wmitem = wm_obj.save({'title': self.test_case_name,
                                  'snippet': "automation",
                                  'tags': "dev"})
            self.assertIsInstance(wmitem, arcgis.gis.Item)

            # update the web map by removing one of the layers.
            wm_obj2 = WebMap(wmitem)

            original_layers = wm_obj2.layers
            self.assertEqual(len(flc_item.layers), len(original_layers), "Saved Web map does not have 3 layers")

            wm_obj2.remove_layer(wm_obj2.layers[0])
            wm_obj2.update()

            wm_obj3 = WebMap(wmitem)
            updated_layers = wm_obj3.layers
            self.assertEqual(len(flc_item.layers)-1, len(updated_layers), "Web map was not correctly updated")

            # all is well, delete the web map now
            wmitem.delete()

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_add_allsupported_layertypes(self):
        """
        Compose a new web map with many operational layers. Add all supported layer types
        :return: 
        """
        try:
            wm_obj = WebMap()
            # assert
            self.assertIsInstance(wm_obj, arcgis.mapping.WebMap, "Cannot create empty WebMap")
            self.assertTrue(hasattr(wm_obj.definition, 'baseMap'), 'Empty WebMap obj is missing baseMap')

            # use a hosted feature service layer for operational layer
            from arcgis.features import FeatureLayer
            fl = FeatureLayer(
                url='https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities/FeatureServer/0',
                gis=self.gis)

            # add operational layer
            wm_obj.add_layer(fl)
            self.assertTrue(hasattr(wm_obj.definition, 'operationalLayers'),
                            'Adding a layer does not create operationalLayers')

            #add Vector tile service
            vtitem = PortalUtils.search_portal_item(self.gis, 'set2_vtpk_worldgreen','Vector Tile Service')
            if not vtitem:
                self.skipTest('Cannot find needed vector tile layer')
            vtlayer = vtitem.layers[0]
            wm_obj.add_layer(vtlayer)

            #add map image layer
            from arcgis.mapping import MapImageLayer
            mi_item = self.gis.content.get('eaa04af9d8a04554973f2edd0f5921ac')
            if not mi_item:
                self.skipTest('Cannot find needed map image layer')
            mi_layer = MapImageLayer.fromitem(mi_item)
            wm_obj.add_layer(mi_layer)

            #add image service
            il_sr = self.gis.content.get('58a541efc59545e6b7137f961d7de883')
            il_layer = il_sr.layers[0]
            wm_obj.add_layer(il_layer)

            #add feature collection

            #verify
            self.assertGreaterEqual(len(wm_obj.layers), 4, "NUmber of layers added not equal to 4")
            print("Printing added layer name, type")
            for l in wm_obj.layers:
                print(l.title, l.layerType)

            self.assertEqual(wm_obj.layers[3].layerType, 'ArcGISImageServiceLayer')

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_add_imageryLayer_builtin_rf(self):
        """
        Compose a new web, add an imagery layer with built-in raster function
        :return: 
        """
        try:
            wm_obj = WebMap()
            # assert
            self.assertIsInstance(wm_obj, arcgis.mapping.WebMap, "Cannot create empty WebMap")
            self.assertTrue(hasattr(wm_obj.definition, 'baseMap'), 'Empty WebMap obj is missing baseMap')

            # search for world elevation
            il_item = self.gis.content.get('58a541efc59545e6b7137f961d7de883')
            il = il_item.layers[0]

            from arcgis.raster import apply
            tinted_il = apply(il, 'Elevation_Tinted_Hillshade')

            #add to map
            wm_obj.add_layer(tinted_il)

            #verify
            self.assertIsNotNone(wm_obj.layers[0].renderingRule)
            self.assertEqual(wm_obj.layers[0].renderingRule.rasterFunction, 'Elevation_Tinted_Hillshade')

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_add_imageryLayer_chain_custom_rf(self):
        """
        Compose a new web, add an imagery layer with two or more non-built-in raster functions
        :return: 
        """
        try:
            wm_obj = WebMap()
            # assert
            self.assertIsInstance(wm_obj, arcgis.mapping.WebMap, "Cannot create empty WebMap")
            self.assertTrue(hasattr(wm_obj.definition, 'baseMap'), 'Empty WebMap obj is missing baseMap')

            # search for world elevation
            il_item = self.gis.content.get('58a541efc59545e6b7137f961d7de883')
            il = il_item.layers[0]

            from arcgis.raster import apply, hillshade, stretch
            hillshade_stretched = stretch(hillshade(il))

            #add to map
            wm_obj.add_layer(hillshade_stretched)

            #verify
            self.assertIsNotNone(wm_obj.layers[0].renderingRule)
            self.assertEqual(wm_obj.layers[0].renderingRule.rasterFunction, 'Stretch')
            if hasattr(wm_obj.layers[0].renderingRule, 'rasterFunctionArguments'):
                self.assertEqual(wm_obj.layers[0].renderingRule.rasterFunctionArguments.Raster.rasterFunction, 'Hillshade')
            else:
                self.fail('Unable to find inner raster function')
        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_author_and_save_new_web_map(self):
        """
        Compose a new web map with one operational layer and save to disk.
        :return: 
        """
        try:
            wm_obj = WebMap()
            # use a hosted feature service layer for operational layer
            from arcgis.features import FeatureLayer
            fl = FeatureLayer(
                url='https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Major_Cities/FeatureServer/0',
                gis=self.gis)

            # add operational layer
            wm_obj.add_layer(fl)

            wm_item = wm_obj.save({'title':self.test_case_name,
                                   'snippet':'created with Python API unit test',
                                     'tags':['unittest','automation','geosaurus']})

            self.assertIsInstance(wm_item, arcgis.gis.Item, 'save_as() does not return and item')
            self.assertEqual(wm_item.type, "Web Map", "item type created by save_as() is not Web Map")

            #delete the item for future runs
            del_result = wm_item.delete()
            print("delete result " + str(del_result))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_editlayers_and_saveas_web_map(self):
        """
        Read an existing webmap, edit the layer properties and save it as a new item
        :return:
        """
        try:
            wm_item = self.gis.content.get('a4c20b6de07640d0bf022c62003f0a55')
            if not wm_item:
                raise self.skipTest('webmap required for test not found')

            wm_obj = WebMap(wm_item)

            #print all operational layers in web map
            lindex = 0
            for l in wm_obj.layers:
                print(str(lindex) + " " + l.title)
                lindex+=1

            #edit first layer title, itemid, url and save it back to the webGIS
            l1 = wm_obj.layers[0]
            l1.title = self.namePrefix
            l1.url = 'http://teton:8080/jenkins/dinotests'
            l1.itemid = self.portal_username

            #add new property
            l1.newProp = 'this is a new property'

            wm_item_new = wm_obj.save({'title':self.test_case_name,
                                       'snippet':'created with Python API unit test',
                                        'tags':['unittest', 'automation', 'geosaurus']})

            self.assertIsInstance(wm_item_new, arcgis.gis.Item, 'save_as() does not return and item')
            self.assertEqual(wm_item_new.type, "Web Map", "item type created by save_as() is not Web Map")
            print("Saved out the edited webmap as a new item")

            #read the saved webmap into a new obj and print the details
            wm_obj_new = WebMap(wm_item_new)
            print("Printing the saved out webmap's layer0")
            print(wm_obj_new.layers[0].title)
            print(wm_obj_new.layers[0].newProp)
            print(str(wm_obj_new.definition.operationalLayers[0].url))

            #delete the item for future test runs
            del_result = wm_item_new.delete()
            print("delete result: " + str(del_result))

        except AssertionError as assertErrorException:
            test_skip = True
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(test_skip, "Test condition not met. Check if old outputs are present")
    def test_removelayers_and_saveas_web_map(self):
        """
        Read an existing webmap, remove some layers and save it as a new item
        :return:
        """
        try:
            wm_item = self.gis.content.get('a4c20b6de07640d0bf022c62003f0a55')
            if not wm_item:
                raise self.skipTest('webmap required for test not found')

            wm_obj = WebMap(wm_item)

            #get number of layers
            original_layers = wm_obj.layers
            num_layers_original = len(original_layers)
            self.assertGreater(num_layers_original,0,"Number of layers in webmap is less than 0. Cannot proceed with layer removal testcase")

            # print all operational layers in web map
            lindex = 0
            for l in wm_obj.layers:
                print(str(lindex) + " " + l.title)
                lindex += 1

            #remove the first two layers
            wm_obj.remove_layer(original_layers[0])
            wm_obj.remove_layer(original_layers[1])

            self.assertLess(len(wm_obj.layers), num_layers_original, "Number of layers not less than original after removing layers from webmap")

            wm_item_new = wm_obj.save({'title': self.test_case_name,
                                       'snippet': 'created with Python API unit test',
                                       'tags': ['unittest', 'automation', 'geosaurus']})

            self.assertIsInstance(wm_item_new, arcgis.gis.Item, 'save_as() does not return and item')
            self.assertEqual(wm_item_new.type, "Web Map", "item type created by save_as() is not Web Map")
            print("Saved out the edited webmap as a new item")

            # read the saved webmap into a new obj and print the details
            wm_obj_new = WebMap(wm_item_new)
            self.assertEqual(len(wm_obj_new.layers), num_layers_original-2, "Number of layers in saved out webmap is not 2 less than original")

            # delete the item for future test runs
            del_result = wm_item_new.delete()
            print("delete result: " + str(del_result))

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

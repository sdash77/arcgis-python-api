# -------------------------------------------------------------------------------
# Name:        OfflineMapAreaManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
# -------------------------------------------------------------------------------
import unittest
import os
from integration.dino_utils.dino_precondition_checks import PreconditionChecks
from integration.dino_utils.dino_precondition_checks import PortalUtils
import datetime
from utils.decorators import integration_test
from arcgis.auth.tools import LazyLoader

arcgismapping = LazyLoader("arcgis.map")

# region PreCondition check
test_skip = False
class_skip = False
module_skip = False

r1 = PreconditionChecks.check_API_import()
r2 = PreconditionChecks.check_Python_version()

if r1 & r2:
    print("## Precondition checks passed ##")
    module_skip = False
else:
    module_skip = True
    print("Pre condition checks failed. Quitting tests")
    raise (exit())

# Import the module after Precondition checks pass
try:
    import arcgis
    from arcgis.gis import GIS
except ImportError:
    print("API import error. Quitting test")
    raise (exit())
# endregion PreCondition Check


# TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping tests in GIS module")
def setUpModule():
    """
    Set up code for full arcgis.raster module ImageryLayer class tests
    :return:
    """
    # Get environment status
    print("ArcPy on system: ", PreconditionChecks.check_ArcPy_import())
    print("Is Pro installed: ", PreconditionChecks.check_Pro_installed())
    print("Host OS: " + PreconditionChecks.get_OS())


@integration_test
class Test_WebMap_OMA_AGO(unittest.TestCase):
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

        cls.gis = GIS(profile="your_online_profile", verify_cert=False)
        if cls.gis is None:
            cls.class_skip = True

        print("==================================================================")
        print("Beginning tests in Test_OfflineMapAreaManager class")
        # endregion

    def setUp(self):
        test_skip = False  # reset the skip flag
        print("Test: " + self._testMethodName)
        self.namePrefix = "dino_WebMap_"

        # region delete old outputs
        self.test_case_name = self.namePrefix + self._testMethodName
        search_result = PortalUtils.search_portal_item(
            self.gis, self.test_case_name, None
        )

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
        self.time_stamp = str.format(
            "{0}_{1}_{2}_{3}_{4}_{5}",
            str(t.year),
            str(t.month),
            str(t.day),
            str(t.hour),
            str(t.minute),
            str(t.second),
        )
        print("Time stamp: " + self.time_stamp)

    def tearDown(self):
        print("------------------------------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n==================================================================")

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_create_OfflineMapAreaManager(self):
        try:
            wmitem = self.gis.content.get("8d1df5a2b82f406b900f7f623806d36e")
            wm = arcgismapping.Map(item=wmitem)
            try:
                oma_manager = wm.offline_areas
            except Exception as e:
                if (
                    e.__str__()
                    == "You do not have permission to manage offline areas for this map. You must be the owner of the item."
                ):
                    return  # skip this test case

            # assert
            self.assertIsInstance(
                oma_manager,
                arcgis.layers.OfflineMapAreaManager,
                "Cannot create OMA manager object from web map object",
            )

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_list_offline_areas(self):
        try:
            wmitem = self.gis.content.get("7cb38a3325564607a81c0da5733bfbfc")
            wm = arcgismapping.Map(item=wmitem)

            try:
                oma_mgr = wm.offline_areas
            except Exception as e:
                if (
                    e.__str__()
                    == "You do not have permission to manage offline areas for this map. You must be the owner of the item."
                ):
                    return  # skip this test case

            offline_areas = wm.offline_areas.list()

            # assert
            self.assertIsInstance(
                offline_areas,
                list,
                "Cannot list offline areas associated with a WebMap item",
            )
            print(str(offline_areas))

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_create_offline_areas(self):
        """
        Create offline areas
        :return:
        """
        try:
            wmitem = self.gis.content.get("2051a50d9370428297dc08a87db4a43f")

            wm = arcgismapping.Map(item=wmitem)

            bookmark1 = wm.bookmarks.list[-1].name

            import arcgis

            arcgis.env.verbose = True
            try:
                oma_mgr = wm.offline_areas
            except Exception as e:
                if (
                    e.__str__()
                    == "You do not have permission to manage offline areas for this map. You must be the owner of the item."
                ):
                    return  # skip this test case

            item_properties = {
                "title": self.test_case_name,
                "snippet": "automated test",
                "tags": "python api",
            }
            oma_item = wm.offline_areas.create(
                bookmark1, item_properties=item_properties, folder="dino_test"
            )
            arcgis.env.verbose = False

            # assert oma_item
            self.assertIsInstance(
                oma_item, arcgis.gis.Item, "Cannot create offline map area item"
            )

            # assert offline packages for oma_item
            offline_packages = oma_item.related_items("Area2Package", "forward")
            self.assertGreater(len(offline_packages), 0, "Zero packages were created")

            # delete all items created
            for i in offline_packages:
                i.delete()
            oma_item.delete()

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_update_offline_area(self):
        """
        update offline areas
        :return:
        """
        try:
            # wmitem = self.gis.content.get('3d7e3508ccc14d03b9b1b4be134c7a8a')  # old, while in dev cloud.
            # wmitem = self.gis.content.get('89919db1b67547388bdcdf444b4d2cdb')
            # wmitem = self.gis.content.get('2051a50d9370428297dc08a87db4a43f')
            wmitem = self.gis.content.get("7cb38a3325564607a81c0da5733bfbfc")
            wm = arcgismapping.Map(item=wmitem)

            try:
                oma_mgr = wm.offline_areas
            except Exception as e:
                if (
                    e.__str__()
                    == "You do not have permission to manage offline areas for this map. You must be the owner of the item."
                ):
                    return  # skip this test case

            oma_item = wm.offline_areas.list()[0]

            import arcgis

            arcgis.env.verbose = True
            oma_item = wm.offline_areas.update(oma_item)
            arcgis.env.verbose = False

            # assert oma_item
            self.assertIsNotNone(oma_item)
            print(oma_item)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_update_all_offline_areas(self):
        """
        update offline areas
        :return:
        """
        try:
            # wmitem = self.gis.content.get('3d7e3508ccc14d03b9b1b4be134c7a8a')  # old, while in dev cloud.
            # wmitem = self.gis.content.get('89919db1b67547388bdcdf444b4d2cdb')
            # wmitem = self.gis.content.get('2051a50d9370428297dc08a87db4a43f')
            wmitem = self.gis.content.get("7cb38a3325564607a81c0da5733bfbfc")
            wm = arcgismapping.Map(item=wmitem)

            try:
                oma_mgr = wm.offline_areas
            except Exception as e:
                if (
                    e.__str__()
                    == "You do not have permission to manage offline areas for this map. You must be the owner of the item."
                ):
                    return  # skip this test case

            import arcgis

            arcgis.env.verbose = True
            oma_item = wm.offline_areas.update()
            arcgis.env.verbose = False

            # assert oma_item
            self.assertIsNotNone(oma_item)
            print(oma_item)

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())

    @unittest.skipIf(
        test_skip, "Test condition not met. Check if old outputs are present"
    )
    def test_create_offline_areas_min_max_scale(self):
        """
        Create offline areas
        :return:
        """
        try:
            # wmitem = self.gis.content.get('3d7e3508ccc14d03b9b1b4be134c7a8a')  # old, while in dev cloud.
            # wmitem = self.gis.content.get('3e7159ee4c6c4e6faf2ca2bd066ee972')
            wmitem = self.gis.content.get("2051a50d9370428297dc08a87db4a43f")
            wm = arcgismapping.Map(item=wmitem)

            bookmark1 = wm.bookmarks.list[-1].name

            import arcgis

            arcgis.env.verbose = True
            try:
                oma_mgr = wm.offline_areas
            except Exception as e:
                if (
                    e.__str__()
                    == "You do not have permission to manage offline areas for this map. You must be the owner of the item."
                ):
                    return  # skip this test case

            item_properties = {
                "title": self.test_case_name,
                "snippet": "automated test",
                "tags": "python api",
            }
            oma_item = wm.offline_areas.create(
                bookmark1,
                item_properties=item_properties,
                folder="dino_test",
                min_scale=147914000,
                max_scale=73957000,
            )
            arcgis.env.verbose = False

            # assert oma_item
            self.assertIsInstance(
                oma_item, arcgis.gis.Item, "Cannot create offline map area item"
            )

            # assert offline packages for oma_item
            offline_packages = oma_item.related_items("Area2Package", "forward")
            for offline_pkg in offline_packages:
                print(offline_pkg.homepage)
            self.assertGreater(len(offline_packages), 0, "Zero packages were created")

            # delete all items created
            for i in offline_packages:
                i.delete()
            oma_item.delete()
            print(
                "Deleted OMA item and all offline packages created during this test case"
            )

        except AssertionError as assertErrorException:
            raise assertErrorException

        except unittest.SkipTest as skipException:
            raise skipException

        except Exception as testException:
            self.fail("Error during test: " + testException.__str__())


# TestModule
def tearDownModule():
    print("**End GIS module Tests**")


if __name__ == "__main__":
    unittest.main()

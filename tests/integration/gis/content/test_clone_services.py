import unittest
import os
import random
import string
import time
import uuid

from arcgis.gis._impl import ItemTypeEnum
from utils.data_utils import publish_test_item, cleanup_published_items
from utils.decorators import integration_test, from_to_profiles

from integration.config import QALAB_ROOT_PATH, get_resource_path

# QALAB_ROOT_PATH = "/Volumes/pydata/v109/geosaurus"
QA_LABS_FOLDER = os.path.join(QALAB_ROOT_PATH, "clone_services")


@integration_test
@from_to_profiles.all_except_k8s
class TestCloneServices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.items_to_delete = []

    def test_default_cloning(self):
        uid = uuid.uuid4().hex
        created_items = []
        source = self.from_gis
        target = self.to_gis
        layer_item = None
        clone_list = None
        try:
            staging_data_path = "staging_data/cloning"
            test_file = get_resource_path(
                f"{staging_data_path}/normal_service.zip",
                unique_copy=True,
            )

            layer_item = publish_test_item(
                source,
                layer_name=f"normal_service_{uid}",
                source_data_path=test_file,
                item_type=ItemTypeEnum.FILE_GEODATABASE,
                target_url=target.url,
            )
            self.assertIsNotNone(layer_item, "Failed to publish layer item")
            self.items_to_delete.append(layer_item)

            clone_list = target.content.clone_items(
                [layer_item], search_existing_items=False
            )
            created_items.extend(clone_list)
            assert len(clone_list) == 1
            cloned_layer = clone_list[0]
            assert cloned_layer.type == "Feature Service"
            assert cloned_layer.title == layer_item.title
            assert cloned_layer.layers[0].query(
                where="1=1", return_count_only=True
            ) == layer_item.layers[0].query(where="1=1", return_count_only=True)
        finally:
            if clone_list:
                cleanup_published_items(clone_list)
            if layer_item:
                cleanup_published_items([layer_item])

    # @unittest.skip("Skipping test")
    def test_export_cloning(self):
        uid = uuid.uuid4().hex
        created_items = []
        source = self.from_gis
        target = self.to_gis
        layer_item = None
        clone_list = None
        try:
            staging_data_path = "staging_data/cloning"
            test_file = get_resource_path(
                f"{staging_data_path}/normal_service.zip",
                unique_copy=True,
            )

            layer_item = publish_test_item(
                source,
                layer_name=f"normal_service_{uid}",
                source_data_path=test_file,
                item_type=ItemTypeEnum.FILE_GEODATABASE,
                target_url=target.url,
            )
            self.assertIsNotNone(layer_item, "Failed to publish layer item")
            self.items_to_delete.append(layer_item)

            clone_list = target.content.clone_items(
                [layer_item], search_existing_items=False, export_service=True
            )
            created_items.extend(clone_list)
            assert len(clone_list) == 2
            cloned_gdb = clone_list[0]
            assert cloned_gdb.type == "File Geodatabase"
            cloned_layer = clone_list[1]
            assert cloned_layer.type == "Feature Service"
            assert cloned_layer.title == layer_item.title
            assert cloned_layer.layers[0].query(
                where="1=1", return_count_only=True
            ) == layer_item.layers[0].query(where="1=1", return_count_only=True)
        finally:
            if clone_list:
                cleanup_published_items(clone_list)
            if layer_item:
                cleanup_published_items([layer_item])

    # @unittest.skip("Skipping test")
    def test_read_only_cloning(self):
        # covers export and normal
        uid = uuid.uuid4().hex
        created_items = []
        source = self.from_gis
        target = self.to_gis
        layer_item = None
        clone_list = None
        try:
            staging_data_path = "staging_data/cloning"
            test_file = get_resource_path(
                f"{staging_data_path}/normal_service.zip",
                unique_copy=True,
            )

            layer_item = publish_test_item(
                source,
                layer_name=f"normal_service_{uid}",
                source_data_path=test_file,
                item_type=ItemTypeEnum.FILE_GEODATABASE,
                target_url=target.url,
            )
            self.assertIsNotNone(layer_item, "Failed to publish layer item")
            self.items_to_delete.append(layer_item)

            layer = layer_item.layers[0]
            fields = layer.properties["fields"]
            for field in fields:
                field["editable"] = False
            layer.manager.update_definition({"fields": fields})

            clone_list = target.content.clone_items(
                [layer_item], search_existing_items=False
            )
            clone_export_list = target.content.clone_items(
                [layer_item], search_existing_items=False, export_service=True
            )
            created_items.extend(clone_list)
            created_items.extend(clone_export_list)
            assert len(clone_list) == 1
            assert len(clone_export_list) == 2
            cloned_layer = clone_list[0]
            cloned_export_layer = clone_export_list[1]
            assert cloned_layer.type == cloned_export_layer.type == "Feature Service"
            assert cloned_layer.title == cloned_export_layer.title == layer_item.title
            cl = cloned_layer.layers[0]
            cel = cloned_export_layer.layers[0]
            assert (
                cl.query(where="1=1", return_count_only=True)
                == cel.query(where="1=1", return_count_only=True)
                == layer.query(where="1=1", return_count_only=True)
            )
            cl_fields = cl.properties["fields"]
            cel_fields = cel.properties["fields"]
            for i in range(len(fields)):
                assert (
                    cl_fields[i]["editable"]
                    == cel_fields[i]["editable"]
                    == fields[i]["editable"]
                    == False
                )
        finally:
            cleanup_published_items(clone_list)
            if layer_item:
                cleanup_published_items([layer_item])

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items(cls.items_to_delete)


@integration_test
@from_to_profiles.all_except_k8s
class TestCloneEditorTracking(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.items_to_delete = []

    def test_standard_editor(self):
        uid = uuid.uuid4().hex
        created_items = []
        source = self.from_gis
        target = self.to_gis
        layer_item = None
        clone_list = None
        try:
            staging_data_path = "staging_data/cloning"
            test_file = get_resource_path(
                f"{staging_data_path}/editor_tracking_test.zip",
                unique_copy=True,
            )

            layer_item = publish_test_item(
                source,
                layer_name=f"normal_service_{uid}",
                source_data_path=test_file,
                item_type=ItemTypeEnum.FILE_GEODATABASE,
                target_url=target.url,
            )
            self.assertIsNotNone(layer_item, "Failed to publish layer item")
            self.items_to_delete.append(layer_item)
            created_items.append(layer_item)
            edit_field = layer_item.layers[0].properties["editFieldsInfo"][
                "creatorField"
            ]
            og_creator = (
                layer_item.layers[0]
                .query(where="1=1")
                .features[0]
                .get_value(edit_field)
            )

            clone_list = target.content.clone_items(
                [layer_item], search_existing_items=False, preserve_editing_info=True
            )
            created_items.extend(clone_list)
            assert len(clone_list) == 1
            cloned_layer = clone_list[0]
            assert cloned_layer.type == "Feature Service"
            assert cloned_layer.title == layer_item.title
            cloned_edit_field = cloned_layer.layers[0].properties["editFieldsInfo"][
                "creatorField"
            ]
            assert (
                cloned_layer.layers[0]
                .query(where="1=1")
                .features[0]
                .get_value(cloned_edit_field)
                == og_creator
            )

        finally:
            if clone_list:
                cleanup_published_items(clone_list)
            if layer_item:
                cleanup_published_items([layer_item])

    def test_export_editor(self):
        uid = uuid.uuid4().hex
        created_items = []
        source = self.from_gis
        target = self.to_gis
        layer_item = None
        clone_export_list = None
        try:
            staging_data_path = "staging_data/cloning"
            test_file = get_resource_path(
                f"{staging_data_path}/editor_tracking_test.zip",
                unique_copy=True,
            )

            layer_item = publish_test_item(
                source,
                layer_name=f"normal_service_{uid}",
                source_data_path=test_file,
                item_type=ItemTypeEnum.FILE_GEODATABASE,
                target_url=target.url,
            )
            self.assertIsNotNone(layer_item, "Failed to publish layer item")
            self.items_to_delete.append(layer_item)
            created_items.append(layer_item)
            edit_field = layer_item.layers[0].properties["editFieldsInfo"][
                "creatorField"
            ]
            og_creator = (
                layer_item.layers[0]
                .query(where="1=1")
                .features[0]
                .get_value(edit_field)
            )

            clone_export_list = target.content.clone_items(
                [layer_item],
                search_existing_items=False,
                export_service=True,
                preserve_editing_info=True,
            )
            created_items.extend(clone_export_list)
            assert len(clone_export_list) == 2
            cloned_export_layer = clone_export_list[1]
            assert cloned_export_layer.type == "Feature Service"
            assert cloned_export_layer.title == layer_item.title
            cloned_edit_field = cloned_export_layer.layers[0].properties[
                "editFieldsInfo"
            ]["creatorField"]
            if target._is_agol == False:
                assert (
                    cloned_export_layer.layers[0]
                    .query(where="1=1")
                    .features[0]
                    .get_value(cloned_edit_field)
                    == og_creator
                )

        finally:
            if clone_export_list:
                cleanup_published_items(clone_export_list)
            if layer_item:
                cleanup_published_items([layer_item])


@integration_test
class TestCloneApps(unittest.TestCase):
    def test_clone_quick_capture(self):
        """Uses a permanent QuickCapture app owned by api_data_owner.
        ItemID: 50789f80a7f74009889cd4d3971b12ce"""
        from arcgis.gis import GIS

        clone_list = None
        try:
            gis = GIS(profile="your_online_api_data_owner_profile")
            gis2 = GIS(profile="your_ent_admin_profile", verify_cert=False)
            qc = gis.content.get("50789f80a7f74009889cd4d3971b12ce")
            clone_list = gis2.content.clone_items(
                [qc], search_existing_items=False, preserve_item_id=True
            )
            cloned_item = gis2.content.get("50789f80a7f74009889cd4d3971b12ce")
            self.assertIsNotNone(
                cloned_item,
                "No item with that item id",
            )
        finally:
            if clone_list:
                cleanup_published_items(clone_list)


if __name__ == "__main__":
    unittest.main()

import unittest
import os
import random
import string
from utils.decorators import integration_test, from_to_profiles

from integration.config import QALAB_ROOT_PATH
# QALAB_ROOT_PATH = "/Volumes/pydata/v109/geosaurus"
QA_LABS_FOLDER = os.path.join(QALAB_ROOT_PATH, "clone_services")


@integration_test
@from_to_profiles.all_except_k8s
class TestCloneServices(unittest.TestCase):

    # @unittest.skip("Skipping test")
    def test_default_cloning(self):
        created_items = []
        try:
            source = self.from_gis
            target = self.to_gis
            folder = source.content.folders.get()
            test_file = os.path.join(QA_LABS_FOLDER, "normal_service.zip")
            props = {
                "title": "normal_service_"
                + "".join(random.choices(string.ascii_letters, k=5)),
                "type": "File Geodatabase",
                "url": target.url,
            }
            job = folder.add(
                **{
                    "item_properties": props,
                    "file": test_file,
                }
            )
            service_item = job.result()
            assert service_item
            created_items.append(service_item)

            layer_item = service_item.publish()
            assert layer_item
            created_items.append(layer_item)

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
            for item in created_items:
                item.delete()

    # @unittest.skip("Skipping test")
    def test_export_cloning(self):
        created_items = []
        try:
            source = self.from_gis
            target = self.to_gis
            folder = source.content.folders.get()
            test_file = os.path.join(QA_LABS_FOLDER, "normal_service.zip")
            props = {
                "title": "normal_service_"
                + "".join(random.choices(string.ascii_letters, k=5)),
                "type": "File Geodatabase",
                "url": target.url,
            }
            job = folder.add(
                **{
                    "item_properties": props,
                    "file": test_file,
                }
            )
            service_item = job.result()
            assert service_item
            created_items.append(service_item)

            layer_item = service_item.publish()
            assert layer_item
            created_items.append(layer_item)

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
            for item in created_items:
                item.delete()

    # @unittest.skip("Skipping test")
    def test_read_only_cloning(self):
        # covers export and normal
        created_items = []
        try:
            source = self.from_gis
            target = self.to_gis
            folder = source.content.folders.get()
            test_file = os.path.join(QA_LABS_FOLDER, "normal_service.zip")
            props = {
                "title": "normal_service_"
                + "".join(random.choices(string.ascii_letters, k=5)),
                "type": "File Geodatabase",
                "url": target.url,
            }
            job = folder.add(
                **{
                    "item_properties": props,
                    "file": test_file,
                }
            )
            service_item = job.result()
            assert service_item
            created_items.append(service_item)

            layer_item = service_item.publish()
            assert layer_item
            created_items.append(layer_item)

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
            for item in created_items:
                item.delete()


@integration_test
@from_to_profiles.all_except_k8s
class TestCloneEditorTracking(unittest.TestCase):

    # @unittest.skip("Skipping test")
    def test_standard_editor(self):
        created_items = []
        try:
            source = self.from_gis
            target = self.to_gis
            folder = source.content.folders.get()
            test_file = os.path.join(QA_LABS_FOLDER, "editor_tracking_test.zip")
            rand_name = "editor_tracking_test_" + "".join(
                random.choices(string.ascii_letters, k=5)
            )
            props = {
                "title": rand_name,
                "type": "File Geodatabase",
                "url": target.url,
            }
            job = folder.add(
                **{
                    "item_properties": props,
                    "file": test_file,
                }
            )
            service_item = job.result()
            assert service_item
            created_items.append(service_item)
            pub_params = {
                "editorTrackingInfo": {"preserveEditUsersAndTimestamps": True},
                "name": rand_name,
            }

            layer_item = service_item.publish(publish_parameters=pub_params)
            assert layer_item
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
            for item in created_items:
                item.delete()

    # @unittest.skip("Skipping test")
    def test_export_editor(self):
        created_items = []
        try:
            source = self.from_gis
            target = self.to_gis
            folder = source.content.folders.get()
            test_file = os.path.join(QA_LABS_FOLDER, "editor_tracking_test.zip")
            rand_name = "editor_tracking_test_" + "".join(
                random.choices(string.ascii_letters, k=5)
            )
            props = {
                "title": rand_name,
                "type": "File Geodatabase",
                "url": target.url,
            }
            job = folder.add(
                **{
                    "item_properties": props,
                    "file": test_file,
                }
            )
            service_item = job.result()
            assert service_item
            created_items.append(service_item)

            pub_params = {
                "editorTrackingInfo": {"preserveEditUsersAndTimestamps": True},
                "name": rand_name,
            }
            layer_item = service_item.publish(publish_parameters=pub_params)
            assert layer_item
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
            assert (
                cloned_export_layer.layers[0]
                .query(where="1=1")
                .features[0]
                .get_value(cloned_edit_field)
                == og_creator
            )

        finally:
            for item in created_items:
                item.delete()


if __name__ == "__main__":
    unittest.main()

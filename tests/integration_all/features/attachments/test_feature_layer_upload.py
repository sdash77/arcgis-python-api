import json
import os.path
import time
import unittest
from io import StringIO

from utils.data_utils import publish_test_item, cleanup_published_items
from integration.config import QALAB_ROOT_PATH, get_resource_path
from utils._logging import enable_verbose_logging
from utils.decorators import integration_test, profiles

from arcgis.features._uploads.upload import UploadManager, Upload
from arcgis.gis._impl import ItemTypeEnum

enable_verbose_logging()

file_path = get_resource_path(
    "staging_data/USA_Major_Cities.zip",
    unique_copy=True,
)


@profiles.enterprise_and_agol
@integration_test
class TestUploadManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        uid = int(time.time())
        layer_name = f"test_upload_fl_{uid}"
        item_type = ItemTypeEnum.SHAPEFILE
        cls.published_item = publish_test_item(
            gis=cls.gis,
            layer_name=layer_name,
            source_data_path=file_path,
            item_type=item_type,
            prep_for_editing=False,
        )
        cls.item_source = cls.published_item

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.published_item])

    def test_upload_io_obj(self):
        upload_item = None
        data = {"hello": "world"}
        io_obj = StringIO()
        io_obj.write(json.dumps(data))

        fl = self.published_item.layers[0]
        try:
            um = UploadManager(layer=fl)
            upload_item = um.upload(path=io_obj, file_name="data.json")
            self.assertTrue(
                isinstance(upload_item, Upload), "Upload item is not Upload type"
            )
            upload_properties = upload_item.properties
            item_name = upload_properties.get("itemName")
            self.assertTrue(
                "data.json" == item_name, f"Incorrect itemName prop: {item_name}"
            )
            is_committed = upload_properties.get("committed")
            self.assertTrue(is_committed, "Upload not committed")
        finally:
            if upload_item:
                upload_item.delete()

    def test_upload_file(self):
        upload_item = None
        data = {"hello": "world"}
        import os
        import tempfile

        try:
            data_file = os.path.join(tempfile.gettempdir(), "dataset.json")
            with open(data_file, "w") as writer:
                writer.write(json.dumps(data))
            fl = self.published_item.layers[0]
            um = UploadManager(layer=fl)
            upload_item = um.upload(path=data_file)
            self.assertTrue(
                isinstance(upload_item, Upload), "Upload item is not Upload type"
            )
            upload_properties = upload_item.properties
            item_name = upload_properties.get("itemName")
            self.assertTrue(
                "dataset.json" == item_name, f"Incorrect itemName prop: {item_name}"
            )
            is_committed = upload_properties.get("committed")
            self.assertTrue(is_committed, "Upload not committed")
        finally:
            if upload_item:
                upload_item.delete()

    def test_upload_by_parts(self):
        upload_item = None
        data = {"hello": "world"}
        import os
        import tempfile

        try:
            data_file = os.path.join(tempfile.gettempdir(), "datasetparts.json")
            with open(data_file, "w") as writer:
                writer.write(json.dumps(data))
            fl = self.published_item.layers[0]
            um = UploadManager(layer=fl)
            upload_item = um.register("upload_test.json")
            self.assertIsNotNone(upload_item, "Upload item is None")
            self.assertTrue(
                isinstance(upload_item, Upload), "Upload item is not Upload type"
            )
            uploaded = upload_item.upload_by_part(
                part_number=1, part=data_file, part_name="part1.json"
            )
            if isinstance(uploaded, dict) and uploaded.get("error"):
                raise Exception(f"Upload by Part failed: {uploaded}")
            self.assertTrue(uploaded, "Item did not upload")
            commits = upload_item.commit()
            self.assertTrue(isinstance(commits, bool), "Unexpected type for commit")
            if isinstance(commits, dict):
                self.assertIsNone(commits.get("error"))
        finally:
            if isinstance(upload_item, Upload):
                upload_item.delete()


if __name__ == "__main__":
    unittest.main()

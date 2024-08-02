import os.path
import unittest
from arcgis.gis import GIS, ContentManager
from io import StringIO
import json, uuid
from arcgis.features._uploads.upload import UploadManager, Upload
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from integration.config import QALAB_ROOT_PATH


enable_verbose_logging()
FEATURE_CLASS = os.path.join(QALAB_ROOT_PATH, r"esri_requests\issue_9705\USA_Major_Cities.zip")


@profiles.enterprise_and_agol
@integration_test
class TestUploadManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        content: ContentManager = cls.gis.content
        item = content.add(
            item_properties={"title": "test_data_abc", "type": "Shapefile"},
            data=FEATURE_CLASS,
        )
        name = f"mjr{uuid.uuid4().hex[:4]}cty"
        cls.item = item.publish(publish_parameters={"name": name})
        cls.item_source = item

    @classmethod
    def tearDownClass(cls):
        cls.item.delete()
        cls.item_source.delete()

    def test_upload_io_obj(self):
        data = {"hello": "world"}
        io_obj = StringIO()
        io_obj.write(json.dumps(data))
        fl = self.item.layers[0]
        um = UploadManager(layer=fl)
        upload_item = um.upload(path=io_obj, file_name="data.json")
        assert upload_item
        assert upload_item.delete()

    def test_upload_file(self):
        data = {"hello": "world"}
        import os, tempfile

        data = os.path.join(tempfile.gettempdir(), "dataset.json")
        with open(data, 'w') as writer:
            writer.write(json.dumps(data))
        fl = self.item.layers[0]
        um = UploadManager(layer=fl)
        upload_item = um.upload(path=data)
        assert upload_item
        assert upload_item.delete()

    def test_upload_by_parts(self):
        data = {"hello": "world"}
        import os, tempfile

        data = os.path.join(tempfile.gettempdir(), "datasetparts.json")
        with open(data, 'w') as writer:
            writer.write(json.dumps(data))
        fl = self.item.layers[0]
        um = UploadManager(layer=fl)
        upload_item = um.register("amazingtest.json")
        assert upload_item
        assert isinstance(upload_item, Upload)
        uploaded = upload_item.upload_by_part(
            part_number=1, part=data, part_name="part1.json"
        )
        assert uploaded
        commits = upload_item.commit()
        assert commits
        assert upload_item.delete()


if __name__ == "__main__":
    unittest.main()

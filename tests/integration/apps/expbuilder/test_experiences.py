import unittest
from arcgis.gis import GIS, Item
from arcgis.apps.expbuilder import WebExperience
import pathlib
import os
import tempfile
import shutil
import zipfile

from utils.decorators import integration_test, profiles, from_to_profiles

from integration.config import QALAB_ROOT_PATH

# QALAB_ROOT_PATH = "/Volumes/pydata/v109/geosaurus"
QA_LABS_FOLDER = os.path.join(QALAB_ROOT_PATH, "experiences")


@integration_test
@profiles.admin_enterprise_and_agol
class TestExperience(unittest.TestCase):
    """Test Basic WebExperience Methods"""

    # @unittest.skip("focusing elsewhere")
    def test_new_experience(self):
        """Make a new experience, reload, save, save, publish, delete"""
        # establish gis connection
        gis = self.gis
        exp = WebExperience(gis=gis)

        # assert some properties
        with self.subTest(msg=self.profile + " properties"):
            assert exp._gis
            assert exp.item
            assert exp.itemid
            assert exp._expdict["template"] == "blankfullscreen"
            assert exp._draft["template"] == "blankfullscreen"
            assert isinstance(exp._resources, list)

        # test reload save
        with self.subTest(msg=self.profile + " reload save"):
            exp._draft = {"this_is": "bad!"}
            assert exp.reload()
            assert exp._draft == exp._expdict
            assert exp._draft["template"] == "blankfullscreen"

        # test save
        with self.subTest(msg=self.profile + " save"):
            exp._draft["test"] = "we love testing"
            assert exp.save(title="pikachu", tags="ash, misty, brock")
            assert exp._expdict["test"] == "we love testing"
            assert exp.item.title == "pikachu"
            assert exp.item.tags == ["ash", "misty", "brock"]

        # test publish
        with self.subTest(msg=self.profile + " publish"):
            assert exp.item.get_data() == {}
            assert exp.save(publish=True, access="org")
            assert "status: Published" in exp.item.typeKeywords
            # assert exp.item.access == "org"

        # test delete
        with self.subTest(msg=self.profile + " delete"):
            exp_id = exp.itemid
            assert gis.content.get(exp_id)
            assert exp.delete()
            assert not gis.content.get(exp_id)

    # @unittest.skip("focusing elsewhere")
    def test_duplicate_clone(self):
        """Assert existing experiences are able to be duplicated and cloned"""
        gis = self.gis
        exp = WebExperience(template="dart", gis=gis)
        exp2 = exp.save(
            title="rhyperior", tags=["jesse", "james", "meowth"], duplicate=True
        )
        assert exp2
        assert exp2.item.title == "rhyperior"
        assert exp2._expdict == exp._expdict
        assert exp2._draft == exp._draft
        assert exp2.item.get_data() == exp.item.get_data()
        assert exp2.delete()
        assert exp.delete()

    # @unittest.skip("focusing elsewhere")
    def test_views(self):
        """Assert an IFrame is returned for the previewing methods"""
        from IPython.display import IFrame

        gis = self.gis
        exp = WebExperience(gis=gis)
        assert exp

        # test preview method
        with self.subTest(msg=self.profile + " preview"):
            preview = exp.preview()
            assert isinstance(preview, IFrame)

        # test view method
        with self.subTest(msg=self.profile + " view"):
            assert exp.save(publish=True)
            view = exp.view()
            assert isinstance(view, IFrame)

        assert exp.delete()

    # @unittest.skip("focusing elsewhere")
    def test_local_experience(self):
        """Make a new experience from local JSON and test properties/methods"""
        path_root = str(pathlib.Path(__file__).parent.resolve())
        path = path_root + "/testconfig.json"
        # path = "/Users/cowboy/GitHub/geosaurus/tests/integration/apps/expbuilder/testconfig.json"
        gis = self.gis

        with self.subTest(msg=self.profile + " creating"):
            exp = WebExperience(path=path, gis=gis)
            assert exp._draft
            assert exp._gis
            assert exp.item == None
            assert exp.itemid == None

        with self.subTest(msg=self.profile + " adding to portal"):
            exp = WebExperience(path=path, gis=gis)
            item = exp.upload(gis=gis, title="test exp")
            assert isinstance(item, Item)
            assert item["title"] == "test exp"
            assert exp._draft["attributes"]["portalUrl"] == gis.url
            assert exp.item == item
            assert exp.itemid
            assert exp.delete()

        with self.subTest(msg=self.profile + " manually remapping data"):
            exp = WebExperience(path=path, gis=gis)
            remap_dict = {
                "dataSource_1": {
                    "itemId": "c50de463235e4161b206d000587af18b",
                    "portalUrl": gis.url,
                }
            }
            item = exp.upload(gis=gis, title="test exp", item_mapping=remap_dict)
            assert isinstance(item, Item)
            assert item["title"] == "test exp"
            assert exp._draft["attributes"]["portalUrl"] == gis.url
            assert (
                exp._draft["dataSources"]["dataSource_1"]["itemId"]
                == "c50de463235e4161b206d000587af18b"
            )
            assert exp._draft["dataSources"]["dataSource_1"]["portalUrl"] == gis.url
            assert exp.item == item
            assert exp.itemid
            assert exp.delete()

        with self.subTest(msg=self.profile + " auto remapping data"):
            exp = WebExperience(path=path, gis=gis)
            exp._draft["dataSources"]["dataSource_1"]["sourceLabel"] = "Giraffes"
            exp._draft["dataSources"]["dataSource_1"]["itemId"] = "123hehethiswontwork"
            item = exp.upload(gis=gis, title="test exp", auto_remap=True)
            assert isinstance(item, Item)
            assert item["title"] == "test exp"
            assert (
                exp._draft["dataSources"]["dataSource_1"]["itemId"]
                != "123hehethiswontwork"
            )
            assert exp.item == item
            assert exp.itemid
            assert exp.delete()

    # @unittest.skip("focusing elsewhere")
    def test_upload_resource_experience(self):
        test_file = os.path.join(QA_LABS_FOLDER, "ResourceUpload.zip")
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        shutil.copyfile(test_file, temp_zip.name)
        with zipfile.ZipFile(temp_zip.name, "r") as zip_ref:
            extract_dir = tempfile.mkdtemp()
            zip_ref.extractall(extract_dir)

        gis = self.gis
        res_folder = os.path.join(extract_dir, "ResourceUpload")
        exp = WebExperience(gis=gis, path=res_folder)
        assert exp._expdict["template"] == "blankfullscreengrid"
        exp.upload(gis=gis, title="Resource Upload Test")
        new_item = exp.item
        assert new_item != None
        res = new_item.resources()
        resources_copied = False
        for resource in res.list():
            if resource["resource"] == "images/image-resources-list.json":
                resources_copied = True
                break
        assert resources_copied
        exp.delete()


@integration_test
@from_to_profiles.all_except_k8s
class TestUploadCloneExperience(unittest.TestCase):
    """Test Uploading and Cloning Experiences"""

    # @unittest.skip("focusing elsewhere")
    def test_clone_resource_experience(self):
        test_file = os.path.join(QA_LABS_FOLDER, "ResourceUpload.zip")
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        shutil.copyfile(test_file, temp_zip.name)
        with zipfile.ZipFile(temp_zip.name, "r") as zip_ref:
            extract_dir = tempfile.mkdtemp()
            zip_ref.extractall(extract_dir)

        gis = self.from_gis
        gis2 = self.to_gis
        res_folder = os.path.join(extract_dir, "ResourceUpload")
        exp = WebExperience(gis=gis, path=res_folder)
        exp.upload(gis=gis, title="Resource Clone Test")
        new_item = exp.item
        uploaded_config = new_item.resources.get("config/config.json")
        assert uploaded_config["attributes"]["portalUrl"] == gis.url
        clone_list = gis2.content.clone_items([new_item], search_existing_items=False)
        assert len(clone_list) == 1
        cloned_item = clone_list[0]
        new_config = cloned_item.resources.get("config/config.json")
        assert new_config["attributes"]["portalUrl"] == gis2.url
        new_item.delete()
        cloned_item.delete()


if __name__ == "__main__":
    unittest.main()

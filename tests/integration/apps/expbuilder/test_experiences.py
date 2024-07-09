import unittest
from arcgis.gis import GIS, Item
from arcgis.apps.expbuilder import WebExperience
import pathlib
from utils.decorators import integration_test

profiles = ["your_online_admin_profile", "your_enterprise_admin_profile"]

@integration_test
class TestExperience(unittest.TestCase):
    """Test Basic WebExperience Methods"""

    # @unittest.skip("focusing elsewhere")
    def test_new_experience(self):
        """Make a new experience, reload, save, save, publish, delete"""
        for profile in profiles:
            # establish gis connection
            gis = GIS(profile=profile, verify_cert=False)
            exp = WebExperience()

            # assert some properties
            with self.subTest(msg=profile + " properties"):
                assert exp._gis
                assert exp.item
                assert exp.itemid
                assert exp._expdict["template"] == "blankfullscreen"
                assert exp._draft["template"] == "blankfullscreen"
                assert isinstance(exp._resources, list)

            # test reload save
            with self.subTest(msg=profile + " reload save"):
                exp._draft = {"this_is" : "bad!"}
                assert exp.reload()
                assert exp._draft == exp._expdict
                assert exp._draft["template"] == "blankfullscreen"

            # test save
            with self.subTest(msg=profile + " save"):
                exp._draft["test"] = "we love testing"
                assert exp.save(title="pikachu", tags="ash, misty, brock")
                assert exp._expdict["test"] == "we love testing"
                assert exp.item.title == "pikachu"
                assert exp.item.tags == ["ash", "misty", "brock"]

            # test publish
            with self.subTest(msg=profile + " publish"):
                assert exp.item.get_data() == {}
                assert exp.save(publish=True, access="org")
                assert 'status: Published' in exp.item.typeKeywords
                # assert exp.item.access == "org"

            # test delete
            with self.subTest(msg=profile + " delete"):
                exp_id = exp.itemid
                assert gis.content.get(exp_id)
                assert exp.delete()
                assert not gis.content.get(exp_id)

    # @unittest.skip("focusing elsewhere")
    def test_duplicate_clone(self):
        """Assert existing experiences are able to be duplicated and cloned"""
        # get our online and enterprise experiences and assert they're as expected
        online = GIS(profile=profiles[0], verify_cert=False)
        ent = GIS(profile=profiles[1], verify_cert=False)
        online_exp = WebExperience(item="43391102644f4067b05a7aaca5f7a89d", gis=online)
        ent_exp = WebExperience(item="d79f3e55c3e7484a871b42be5291268c", gis=ent)
        assert online_exp
        assert ent_exp

        # test duplicating
        for exp in [online_exp, ent_exp]:
            with self.subTest(msg="duplicate " + exp._gis.url):
                """exp2 = exp._duplicate(
                    title="rhyperior", tags=["jesse", "james", "meowth"]
                )"""
                exp2 = exp.save(
                    title="rhyperior", tags=["jesse", "james", "meowth"], duplicate=True
                )
                assert exp2
                assert exp2.item.title == "rhyperior"
                # assert exp2.item.tags == ["jesse", "james", "meowth"]
                assert exp2._expdict == exp._expdict
                assert exp2._draft == exp._draft
                assert exp2.item.get_data() == exp.item.get_data()
                assert exp2.delete()

    # @unittest.skip("focusing elsewhere")
    def test_views(self):
        """Assert an IFrame is returned for the previewing methods"""
        from IPython.display import IFrame

        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            exp = WebExperience()
            assert exp

            # test preview method
            with self.subTest(msg=profile + " preview"):
                preview = exp.preview()
                assert isinstance(preview, IFrame)

            # test view method
            with self.subTest(msg=profile + " view"):
                assert exp.save(publish=True)
                view = exp.view()
                assert isinstance(view, IFrame)

            assert exp.delete()

    # @unittest.skip("focusing elsewhere")
    def test_local_experience(self):
        """Make a new experience from local JSON and test properties/methods"""
        path_root = str(pathlib.Path(__file__).parent.resolve())
        path = path_root + "/testconfig.json"
        for profile in profiles:
            # path = "/Users/cowboy/GitHub/geosaurus/tests/integration/apps/expbuilder/testconfig.json"
            gis = GIS(profile=profile, verify_cert=False)

            with self.subTest(msg=profile + " creating"):
                exp = WebExperience(path=path, gis=gis)
                assert exp._draft
                assert exp._gis
                assert exp.item == None
                assert exp.itemid == None

            with self.subTest(msg=profile + " adding to portal"):
                exp = WebExperience(path=path, gis=gis)
                item = exp.upload(gis=gis, title="test exp")
                assert isinstance(item, Item)
                assert item["title"] == "test exp"
                assert exp._draft["attributes"]["portalUrl"] == gis.url
                assert exp.item == item
                assert exp.itemid
                assert exp.delete()

            with self.subTest(msg=profile + " manually remapping data"):
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

            with self.subTest(msg=profile + " auto remapping data"):
                exp = WebExperience(path=path, gis=gis)
                exp._draft["dataSources"]["dataSource_1"]["sourceLabel"] = "Giraffes"
                exp._draft["dataSources"]["dataSource_1"][
                    "itemId"
                ] = "123hehethiswontwork"
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


if __name__ == "__main__":
    unittest.main()

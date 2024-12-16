import unittest
from arcgis.gis import Item
from arcgis.apps.itemgraph import _get_dependencies as gd
from utils.decorators import integration_test, profiles

@integration_test
@profiles.admin_agol
class TestDependencyFunctions(unittest.TestCase):

    def test_gd_function(self):

        # test with item only with related items
        gis = self.gis
        surv = gis.content.get("d78a3338d1cc485bb61342d00dc65e07")
        no_rel = gd._get_item_dependencies(surv, gis, False, False)
        standard = gd._get_item_dependencies(surv, gis, True, False)
        fwd_rel, rev_rel = gd._get_item_dependencies(surv, gis, True, True)

        assert no_rel == []
        assert isinstance(standard, list)
        assert isinstance(standard[0], str)
        assert len(standard) == 2
        assert fwd_rel == standard
        assert isinstance(rev_rel, list)
        assert isinstance(rev_rel[0], str)
        assert len(rev_rel) == 1

        # test with complex item
        exp = gis.content.get("1d69afc7e86c4ab59c4781e67d51fa9c")
        out_list = gd._get_item_dependencies(exp, gis, False, False)
        assert isinstance(out_list, list)
        assert isinstance(out_list[0], str)
        assert len(out_list) == 4

    def test_related_items_function(self):
        surv = self.gis.content.get("d78a3338d1cc485bb61342d00dc65e07")

        # test both
        fwd_list, rev_list = gd._get_related_items(surv, True, True)
        assert isinstance(fwd_list, list)
        assert isinstance(fwd_list[0], Item)
        assert isinstance(rev_list, list)
        assert isinstance(rev_list[0], Item)
        assert len(fwd_list) == 2
        assert len(rev_list) == 1

        # only forward
        fwd_list, rev_list = gd._get_related_items(surv, True, False)
        assert len(fwd_list) == 2
        assert rev_list == []

        # only reverse
        fwd_list, rev_list = gd._get_related_items(surv, False, True)
        assert fwd_list == []
        assert len(rev_list) == 1
    
    def test_parsing_functions(self):

        gis = self.gis

        with self.subTest(msg="webmap"):
            wm = gis.content.get("faa67b0af7914a2f9f4d96c561816c6e")
            deps = gd._parse_webmap(wm)
            assert isinstance(deps, list)
            assert isinstance(deps[0], str)
            for itemid in ["2113d04eade0432784e8edd336193e68"]:
                assert itemid in deps

        with self.subTest(msg="dashboard"):
            db = gis.content.get("b2cd4978e44e41949a83529b0d77afc4")
            deps = gd._parse_dashboard(db)
            assert isinstance(deps, list)
            assert isinstance(deps[0], str)
            for itemid in ["70c2c5a1c9354682a19bbef156d91851"]:
                assert itemid in deps

        with self.subTest(msg="experience builder"):
            exp = gis.content.get("1d69afc7e86c4ab59c4781e67d51fa9c")
            deps = gd._parse_exb(exp)
            assert isinstance(deps, list)
            assert isinstance(deps[0], str)
            for itemid in [
                "8223fde866dd486f8ab9ddb541e5aefb",
                "70c2c5a1c9354682a19bbef156d91851",
                "8460b4e015fe4ffeae985031825870f9",
                "e8cbe9eb69fa4ab8b800597ce7e5cebc",
            ]:
                assert itemid in deps

        with self.subTest(msg="web mapping application"):
            wma = gis.content.get("564e9b35b1694482b7b9032f1696eb9e")
            deps = gd._parse_wma(wma)
            assert isinstance(deps, list)
            assert isinstance(deps[0], str)
            for itemid in ["ff3866656a5b48f6bd271ec5f8deda50"]:
                assert itemid in deps

        with self.subTest(msg="storymap"):
            sm = gis.content.get("ebd88b8426db4384bb3d328ebcbc93f5")
            deps = gd._parse_storymap(sm)
            assert isinstance(deps, list)
            assert isinstance(deps[0], str)
            for itemid in ["994302e6d3034727adcdc8d26bc0af55"]:
                assert itemid in deps

if __name__ == "__main__":
    unittest.main()
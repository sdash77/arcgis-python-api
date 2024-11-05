import unittest
from unittest.mock import MagicMock, Mock
from arcgis.gis import GIS, Item
from arcgis import env
from arcgis.auth.tools import LazyLoader

arcgismapping = LazyLoader("arcgis.map")
from utils.decorators import integration_test

PROFILES = ["your_enterprise_profile", "your_online_profile"]


###########################################################################
@integration_test
class TestItemContentStatus(unittest.TestCase):
    """Tests the Item Content Status Property"""

    _gis_objs = None

    @classmethod
    def setUpClass(cls):
        cls._gis_objs = [GIS(profile=p, verify_cert=False) for p in PROFILES]

    # ----------------------------------------------------------------------
    def test_get_set_content_status_private(self):
        """Tests setting the content for unshared items"""
        for gis in self._gis_objs:
            env.active_gis = gis
            wm = arcgismapping.Map()
            item = wm.save(
                {"title": "testwebmap", "tags": "a,c,d", "snippet": "snippet"}
            )
            if item:
                assert isinstance(item, Item)
                orig_status = item.content_status
                for cs in ("deprecated", None):
                    item.content_status = cs
                    if cs in ["authoritative", "deprecated"]:
                        assert item.content_status in [
                            None,
                            "deprecated",
                            "org_authoritative",
                            "public_authoritative",
                        ]
                    else:
                        assert item.content_status in [
                            "",
                            "deprecated",
                            "org_authoritative",
                            "public_authoritative",
                        ]
                item.delete(permanent=True)
            env.active_gis = None
            del gis

    # ----------------------------------------------------------------------
    def test_set_unverified_org(self):
        """Tests is the content_status Exception is raised."""
        gis = GIS(profile="your_enterprise_profile", verify_cert=False)

        wm = arcgismapping.Map()
        item = wm.save({"title": "testwebmap", "tags": "a,c,d", "snippet": "snippet"})
        item.sharing.sharing_level = "EVERYONE"
        with self.assertRaises(Exception) as context:
            item.content_status = "public_authoritative"
        item.protect(False)
        item.delete(permanent=True)

    # ----------------------------------------------------------------------
    def test_get_set_content_status_public(self):
        """tests setting properties on public Item"""
        for gis in self._gis_objs:
            env.active_gis = gis
            wm = arcgismapping.Map()
            item = wm.save(
                {"title": "testwebmap", "tags": "a,c,d", "snippet": "snippet"}
            )
            item.sharing.sharing_level = "EVERYONE"
            if item:
                assert isinstance(item, Item)
                orig_status = item.content_status
                for cs in ("deprecated", None):
                    item.content_status = cs
                    if cs in ["authoritative", "deprecated"]:
                        assert item.content_status in [
                            None,
                            "deprecated",
                            "org_authoritative",
                            "public_authoritative",
                        ]
                    else:
                        assert item.content_status in [
                            None,
                            "deprecated",
                            "org_authoritative",
                            "public_authoritative",
                            "",
                        ]
                # reset item content status
                #
                if orig_status in ["org_authoritative", "public_authoritative"]:
                    orig_status = "authoritative"
                    item.content_status = orig_status
                elif orig_status == "":
                    item.content_status = None
                else:
                    item.content_status = orig_status

                item.protect(False)
                item.delete(permanent=True)
            env.active_gis = None
            del gis


if __name__ == "__main__":
    unittest.main()

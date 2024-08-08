import sys
import logging
import uuid
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, Item, User
from arcgis.gis._impl._content_manager import RecycleBin, RecycleItem
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = [
    'your_online_profile',
    'your_enterprise_profile',
    'your_dev_online_profile',
]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class TestRecycleBin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis_objs = [
            GIS(profile=profile, verify_cert=False, proxy=PROXIES)
            for profile in profiles
        ]

    def test_someone_elses_recyclebin(self):
        """tests as an admin, accessing a different user's recyclebin"""
        for gis in self.gis_objs:
            rbin = RecycleBin(gis=gis)
            gis: GIS = gis
            if rbin._supported():
                for user in gis.users.search("*"):
                    if user['disabled'] == False:
                        title: str = f"kml title {uuid.uuid4().hex[:6]}"
                        item = gis.content.add(
                            {
                                "typeKeywords": ["Data", "Map", "kml"],
                                "url": "https://developers.google.com/static/kml/documentation/KML_Samples.kml",
                                "type": "KML",
                                "addAsBasemap": "false",
                                "title": title,
                            },
                            owner=user,
                        )
                        item.delete()
                        rbin = user.recyclebin
                        assert isinstance(list(rbin.content), list)
                        for content in rbin.content:
                            if (
                                content.properties["type"] == "KML"
                                and content.properties["title"] == title
                            ):
                                r = content.restore()
                                assert isinstance(r, Item)
                                assert r.delete()
                        for content in rbin.content:
                            if (
                                content.properties["type"] == "KML"
                                and content.properties["title"] == title
                            ):
                                assert content.delete()
                        break

    def test_recyclebin_class(self):
        """tests getting the recycle bin and operations on current logged in user"""
        for gis in self.gis_objs:
            rbin = RecycleBin(gis=gis)
            if rbin._supported():
                title: str = f"kml title {uuid.uuid4().hex[:6]}"
                item = gis.content.add(
                    {
                        "typeKeywords": ["Data", "Map", "kml"],
                        "url": "https://developers.google.com/static/kml/documentation/KML_Samples.kml",
                        "type": "KML",
                        "addAsBasemap": "false",
                        "title": title,
                    }
                )
                item.delete()
                rbin = RecycleBin(gis=gis)

                for content in rbin.content:
                    if (
                        content.properties["type"] == "KML"
                        and content.properties["title"] == title
                    ):
                        r = content.restore()
                        assert isinstance(r, Item)
                        assert r.delete()
                for content in rbin.content:
                    if (
                        content.properties["type"] == "KML"
                        and content.properties["title"] == title
                    ):
                        print(content)
                        assert content.delete()


if __name__ == "__main__":
    unittest.main()

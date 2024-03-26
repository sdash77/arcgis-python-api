import sys
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
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


profiles = ["your_online_profile", "your_enterprise_profile"]
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)


@integration_test
class Test_SearchEnrich(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile="your_online_profile",
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_search_enrich_true(self):
        """tests the search with enrich=true"""
        gis = self.gis
        items = gis.content.search("*", "Feature Layer", enrich=True)
        assert isinstance(items, list)

    def test_search_enrich_false(self):
        """tests the search with enrich=false"""
        from arcgis.gis import ContentManager

        gis: GIS = self.gis
        cm: ContentManager = gis.content

        items = cm.search("*", "Feature Layer", enrich=False)
        assert isinstance(items, list)

    def test_advanced_search_enrich_true(self):
        """tests the advanced search with enrich=true"""
        gis = self.gis
        cm = gis.content
        query = f"owner: {gis.users.me.username}"
        items = cm.advanced_search(query, enrich=True)
        assert isinstance(items, dict)

    def test_advanced_search_enrich_false(self):
        """tests the advanced search with enrich=false"""
        gis = self.gis
        cm = gis.content
        query = f"owner: {gis.users.me.username}"
        items = cm.advanced_search(query, enrich=False)
        assert isinstance(items, dict)

class Test_SearchFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gis = GIS(
            profile="your_online_profile",
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_advanced_search_filter(self):
        gis = self.gis
        cm = gis.content
        items = cm.advanced_search("*", filter="tags:data")
        assert isinstance(items, dict)


if __name__ == "__main__":
    unittest.main()

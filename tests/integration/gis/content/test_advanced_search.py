import unittest
from arcgis.gis import ContentManager
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()


@profiles.all
@integration_test
class TestAdvancedSearchEnrich(unittest.TestCase):

    def test_search_enrich_true(self):
        """tests the search with enrich=true"""
        items = self.gis.content.search("*", "Feature Layer", enrich=True)
        assert isinstance(items, list)

    def test_search_enrich_false(self):
        """tests the search with enrich=false"""
        cm: ContentManager = self.gis.content
        items = cm.search("*", "Feature Layer", enrich=False)
        assert isinstance(items, list)

    def test_advanced_search_enrich_true(self):
        """tests the advanced search with enrich=true"""
        cm: ContentManager = self.gis.content
        query = f"owner: {self.gis.users.me.username}"
        items = cm.advanced_search(query, enrich=True)
        assert isinstance(items, dict)

    def test_advanced_search_enrich_false(self):
        """tests the advanced search with enrich=false"""
        cm: ContentManager = self.gis.content
        query = f"owner: {self.gis.users.me.username}"
        items = cm.advanced_search(query, enrich=False)
        assert isinstance(items, dict)


@integration_test
@profiles.enterprise_and_agol
class TestAdvancedSearchFilter(unittest.TestCase):

    def test_advanced_search_filter(self):
        cm: ContentManager = self.gis.content
        items = cm.advanced_search("*", filter="tags:data")
        assert isinstance(items, dict)


if __name__ == "__main__":
    unittest.main()

import unittest
from utils.decorators import integration_test, profiles
from config import QALAB_ROOT_PATH


@integration_test
@profiles.enterprise_and_agol
class TestItemRelationships(unittest.TestCase):
    def setUp(self):
        self.items = []
        self.pitems = []
        fp: str = QALAB_ROOT_PATH + r"\esri_requests\issue_10433\issue_10433.zip"
        self.folder = self.gis.content.folders._get_or_create("integration_testing_gis_item_relationship")
        item = self.folder.add(
            item_properties={
                "type": "Shapefile",
                "title": "test_related_items",
                "tags": "integration_testing",
            },
            file=fp,
        ).result()
        self.items.append(item)
        self.pitems.append(
            item.publish(
                {
                    'name': "test_related_items_data",
                }
            )
        )

    def test_relationships(self):
        """tests the relationships"""
        for pitem in self.pitems:
            related = pitem.related_items(
                rel_type="Service2Data", direction="forward"
            )
            assert len(related) > 0

    def tearDown(self):
        for i in self.pitems:
            i.delete(permanent=True)
        for i in self.items:
            i.delete(permanent=True)
        if self.folder:
            self.folder.delete(permanent=True)


if __name__ == "__main__":
    unittest.main()

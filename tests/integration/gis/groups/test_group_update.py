import unittest
import uuid
from arcgis.gis import Group
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging
from integration.config import INTEGRATION_TEST_ITEM_TAG

enable_verbose_logging()


@profiles.all
@integration_test
class TestGroupUpdate(unittest.TestCase):

    def setUp(self):
        self.group = self.gis.groups.create(
            title=f"group_update_{uuid.uuid4().hex}", tags=INTEGRATION_TEST_ITEM_TAG, snippet="snippet"
        )
        assert isinstance(self.group, Group)

    def tearDown(self):
        self.group.delete()

    def test_update_group_snippet(self):
        res = self.group.update(snippet="test_group_update_snippet", clear_empty_fields=True)
        assert res
        assert self.group.snippet == "test_group_update_snippet"

    def test_update_group_title(self):
        """this method tests the update method on Group"""
        new_title = f"updated_group_{uuid.uuid4().hex[:4]}"
        res = self.group.update(title=new_title)
        assert res
        assert self.group.title == new_title


if __name__ == "__main__":
    unittest.main()

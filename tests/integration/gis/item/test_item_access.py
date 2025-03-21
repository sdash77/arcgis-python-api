from arcgis.gis import SharingLevel
import unittest
import uuid
from utils.decorators import integration_test, profiles
from integration.config import INTEGRATION_TEST_ITEM_TAG


@integration_test
@profiles.all
class TestItemAccess(unittest.TestCase):
    """
    Tests item access can be updated properly through item.update(). This
    method uses the same logic for managing access. First, create an item
    and verify it's private, then update and verify for org level sharing,
    then update and verify for public level.
    Note: The item is flagged as private by default, and will not be shared
    with any group.
    https://developers.arcgis.com/rest/users-groups-and-items/add-item/
    """

    def setUp(self):
        self.folder = self.gis.content.folders._get_or_create(
            "integration_testing_gis_item_access"
        )
        self.test_item = self.folder.add(
            item_properties={
                "title": "test item access",
                "access": "public",
                "type": "Feature Service",
                "tags": INTEGRATION_TEST_ITEM_TAG,
            },
            url="https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/CapitolhillEnrichedByPop372895/FeatureServer",
        ).result()

    def tearDown(self):
        if self.test_item:
            self.test_item.delete(permanent=True)
        if self.folder:
            self.folder.delete(permanent=True)

    # ----------------------------------------------------------------------
    def test_item_access(self):
        assert isinstance(self.test_item.sharing.shared_with["level"], SharingLevel)
        assert self.test_item.sharing.shared_with["level"] == SharingLevel.PRIVATE
        assert self.test_item.sharing.shared_with["level"].value == "PRIVATE"
        assert self.test_item.sharing.shared_with["groups"] == []

        orig_val = self.test_item.access
        self.test_item.update(item_properties={"access": "org"})
        self.assertNotEqual(
            orig_val, self.test_item.access, "Item access value not updated."
        )
        assert self.test_item.sharing.shared_with["level"].value == "ORGANIZATION"
        assert self.test_item.sharing.shared_with["level"] == SharingLevel.ORG
        assert self.test_item.shared_with["groups"] == []

        next_val = self.test_item.access
        self.test_item.update(item_properties={"access": "public"})
        self.assertNotEqual(
            next_val, self.test_item.access, "Access property not updated on Item."
        )
        assert self.test_item.sharing.shared_with["level"].value == "EVERYONE"
        assert self.test_item.sharing.shared_with["level"] == SharingLevel.EVERYONE
        assert self.test_item.shared_with["groups"] == []

    # ----------------------------------------------------------------------
    def test_item_access_with_share(self):
        result = self.test_item.sharing.sharing_level = SharingLevel.ORG
        assert result.value == "ORGANIZATION"
        shr_group = self.gis.groups.create(
            f"test_group_{uuid.uuid4().hex[:4]}",
            tags=INTEGRATION_TEST_ITEM_TAG,
        )
        grp_share_res = self.test_item.sharing.groups.add(shr_group)
        assert grp_share_res
        assert self.test_item.sharing.shared_with["level"] == SharingLevel.ORG
        assert self.test_item.sharing.shared_with["level"] != SharingLevel.EVERYONE
        assert self.test_item.shared_with["groups"][0].id == shr_group.id

        org_share = self.test_item.sharing.shared_with["level"]
        public_share = self.test_item.sharing.sharing_level = SharingLevel.EVERYONE
        self.assertNotEqual(
            org_share.value,
            public_share.value,
            "Sharing level value not set to EVERYONE as expected.",
        )
        self.assertEqual(
            self.test_item.sharing.shared_with["level"].value,
            "EVERYONE",
            "Sharing level is not EVERYONE",
        )

        self.test_item.sharing.sharing_level = "PRIVATE"
        self.assertNotEqual(
            self.test_item.sharing.sharing_level,
            public_share,
            "Sharing level should not PRIVATE not EVERYONE",
        )
        self.assertNotEqual(
            self.test_item.sharing.sharing_level,
            org_share,
            "Sharing level should not PRIVATE not ORG",
        )
        self.assertEqual(
            self.test_item.sharing.shared_with["level"].value,
            "PRIVATE",
            "Sharing level not PRIVATE as expected.",
        )

        shr_group.delete()


if __name__ == "__main__":
    unittest.main()

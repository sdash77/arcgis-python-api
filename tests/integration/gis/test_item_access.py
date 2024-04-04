from arcgis.gis import GIS, SharingLevel
import unittest
import uuid
from utils.decorators import integration_test

profiles = ["your_online_profile", "your_enterprise_profile"]


###########################################################################
@integration_test
class TestItemAccess(unittest.TestCase):
    """
    Ensures item access is updated properly through content.add() and
    item.update(). These methods use the same logic for managing access.
    First, create an item and verify it's shared publicly, then update and
    verify for org level sharing, then update and verify for private level.
    """

    # ----------------------------------------------------------------------
    def test_item_access(self):
        for profile in profiles:
            with self.subTest(msg=profile):
                gis = GIS(profile=profile, verify_cert=False)
                test_item = gis.content.add(
                    item_properties={
                        "access": "public",
                        "type": "Feature Service",
                        "url": "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/CapitolhillEnrichedByPop585927/FeatureServer",
                    },
                    data="https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/CapitolhillEnrichedByPop585927/FeatureServer",
                )
                assert isinstance(test_item.sharing.shared_with["level"], SharingLevel)
                assert test_item.sharing.shared_with["level"] == SharingLevel.EVERYONE
                assert test_item.sharing.shared_with["level"].value != "ORGANIZATION"
                assert test_item.sharing.shared_with["groups"] == []

                test_item.update(item_properties={"access": "org"})
                assert test_item.sharing.shared_with["level"].value != "EVERYONE"
                assert test_item.sharing.shared_with["level"] == SharingLevel.ORG
                assert test_item.shared_with["groups"] == []

                test_item.update(item_properties={"access": "private"})
                assert test_item.sharing.shared_with["level"].value != "EVERYONE"
                assert test_item.sharing.shared_with["level"] != "ORGANIZATION"
                assert test_item.sharing.shared_with["level"] == SharingLevel.PRIVATE
                assert test_item.shared_with["groups"] == []

                test_item.delete()

    # ----------------------------------------------------------------------
    def test_item_access_with_share(self):
        for profile in profiles:
            with self.subTest(msg=profile):
                gis = GIS(profile=profile, verify_cert=False)
                test_item = gis.content.add(
                    item_properties={
                        "access": "public",
                        "type": "Feature Service",
                        "url": "https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/CapitolhillEnrichedByPop585927/FeatureServer",
                    },
                    data="https://services7.arcgis.com/JEwYeAy2cc8qOe3o/arcgis/rest/services/CapitolhillEnrichedByPop585927/FeatureServer",
                )

                result = test_item.sharing.sharing_level = SharingLevel.ORG
                assert result.value == "ORGANIZATION"
                shr_group = gis.groups.create(
                    f"test group {uuid.uuid4().hex[:4]}", tags="tags"
                )
                grp_share_res = test_item.sharing.groups.add(shr_group)
                assert grp_share_res
                assert test_item.sharing.shared_with["level"] == SharingLevel.ORG
                assert test_item.sharing.shared_with["level"] != SharingLevel.EVERYONE
                assert test_item.shared_with["groups"][0].id == shr_group.id

                test_item.sharing.sharing_level = "EVERYONE"
                assert test_item.sharing.shared_with["level"].value == "EVERYONE"

                test_item.sharing.sharing_level = "PRIVATE"
                assert test_item.sharing.shared_with["level"].value == "PRIVATE"

                test_item.delete()
                shr_group.delete()


if __name__ == "__main__":
    unittest.main()

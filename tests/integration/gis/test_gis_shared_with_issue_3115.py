import unittest
import datetime
from arcgis.gis import GIS
from arcgis.gis import Item, UserManager, User
from utils.decorators import integration_test


@integration_test
class TestIssue3115(unittest.TestCase):
    """ """

    def test_shared_with(self):
        """
        tests the shared with logic
        """

        profiles = {"your_online_profile"}
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=False)
            items = gis.content.search("*, owner:{username}".format(username=gis.users.me.username), item_type="Feature Layer")
            if len(items) > 0:
                item_id = items[0].itemid
                item = gis.content.get(item_id)
                assert isinstance(item, Item)
                assert item.shared_with
                if gis.users.me.role == "org_admin":
                    if len(gis.groups.search("sample_share123")) > 0:
                        for grp in gis.groups.search("sample_share123"):
                            if grp.title == "sample_share123":
                                grp.delete()
                                break
                    grp = gis.groups.create("sample_share123", "tags")
                    item.sharing.groups.add(grp)
                    assert len(item.shared_with["groups"]) > 0
                    um = gis.users
                    isinstance(um, UserManager)
                    dt = datetime.datetime.now()
                    try:

                        temp_account = um.create(
                            username=f"test{dt.microsecond}",
                            password="Funk!0P8p",
                            firstname="fake",
                            lastname="account",
                            email="notreal@esri.com",
                            role="viewer",
                        )
                        temp_account.update_role("org_admin")
                        isinstance(temp_account, User)
                        temp_account.reset(
                            password="Funk!0P8p",
                            new_password="Funk!0P9p",
                            new_security_question=0,
                            new_security_answer="Redlands",
                        )
                        gis2 = GIS(
                            username=temp_account.username,
                            password="Funk!0P9p",
                            verify_cert=False,
                            set_active=False,
                        )
                        assert len(gis2.content.get(item_id).shared_with["groups"]) == 0
                        del gis2
                    except Exception as e:
                        raise (e)
                    finally:
                        temp_account.delete()
                        grp.delete()


if __name__ == "__main__":
    unittest.main()

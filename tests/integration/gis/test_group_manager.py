"""
Tests Updatest to GroupManager and Group Classes for 8.4+ REST API
"""
import unittest
import uuid
from arcgis.gis import GIS, Group, GroupManager
from utils.decorators import integration_test


@integration_test
class TestGM_AGOL_190(unittest.TestCase):
    def test_user_list(self):
        """tests the userList endpoint"""
        for profile in [
            "your_online_profile",
            "your_enterprise_profile",
        ]:
            try:
                group = None
                gis = GIS(profile=profile, verify_cert=False, trust_env=True)
                if gis.version >= [8, 4]:
                    isinstance(gis, GIS)
                    gm = gis.groups
                    isinstance(gm, GroupManager)
                    grp_name = f"grp_{uuid.uuid4().hex[:6]}"
                    group = gm.create(title=grp_name, tags="tag1,tag2")
                    isinstance(group, Group)
                    assert "owner" in group.user_list()
                    assert "users" in group.user_list()
                    users = gis.users.search("*")
                    res = group.add_users(usernames=[u.username for u in users])
                    assert isinstance(res, dict)
                    assert len(group.user_list()["users"]) >= 0
                    assert group.delete()
                    group = None
                else:
                    isinstance(gis, GIS)
                    gm = gis.groups
                    isinstance(gm, GroupManager)
                    grp_name = f"grp_{uuid.uuid4().hex[:6]}"
                    group = gm.create(title=grp_name, tags="tag1,tag2")
                    isinstance(group, Group)
                    assert group.user_list() is None
                    assert group.delete()
                    group = None
            except Exception as e:
                raise e
            finally:
                if group:
                    group.delete()

    # -----------------------------------------------------------------
    def test_add_users_groups(self):
        for profile in [
            "your_online_profile",
            "your_enterprise_profile",
        ]:
            try:
                group = None
                gis = GIS(profile=profile, verify_cert=False, trust_env=True)
                isinstance(gis, GIS)
                gm = gis.groups
                isinstance(gm, GroupManager)
                grp_name = f"grp_{uuid.uuid4().hex[:6]}"
                group = gm.create(title=grp_name, tags="tag1,tag2")
                users = gis.users.search("*")
                if len(users) > 25:
                    users = users[:5]
                assert group.add_users(usernames=[u.username for u in users])
                group.delete()
                group = None
            except Exception as e:
                raise e
            finally:
                if group:
                    group.delete()

    # -----------------------------------------------------------------
    def test_add_users_groups_large(self):
        for profile in [
            "your_online_profile",
            "your_enterprise_profile",
        ]:
            try:
                group = None
                gis = GIS(profile=profile, verify_cert=False, trust_env=True)
                isinstance(gis, GIS)
                gm = gis.groups
                isinstance(gm, GroupManager)
                grp_name = f"grp_{uuid.uuid4().hex[:6]}"
                group = gm.create(title=grp_name, tags="tag1,tag2")
                users = gis.users.search("*")
                if len(users) > 25:
                    assert group.add_users(usernames=[u.username for u in users])
                group.delete()
                group = None
            except Exception as e:
                raise e
            finally:
                if group:
                    group.delete()

    # -----------------------------------------------------------------
    def test_add_admins_groups_large(self):
        for profile in [
            "your_online_profile",
            "your_enterprise_profile",
        ]:
            try:
                group = None
                gis = GIS(profile=profile, verify_cert=False, trust_env=True)
                isinstance(gis, GIS)
                gm = gis.groups
                isinstance(gm, GroupManager)
                grp_name = f"grp_{uuid.uuid4().hex[:6]}"
                group = gm.create(title=grp_name, tags="tag1,tag2")
                users = gis.users.search("*")
                if len(users) > 25:
                    assert group.add_users(admins=[u.username for u in users])
                group.delete()
                group = None
            except Exception as e:
                raise e
            finally:
                if group:
                    group.delete()


if __name__ == "__main__":
    unittest.main()

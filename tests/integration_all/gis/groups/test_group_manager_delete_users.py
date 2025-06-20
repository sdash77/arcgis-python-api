import sys, uuid
import unittest
from arcgis.gis import GIS, GroupManager, Group, User
from utils.decorators import integration_test, profiles

@profiles.admin_enterprise_and_agol
@integration_test
class TestUserDeleteWithGroups(unittest.TestCase):
    def test_delete_with_groups_reassign(self):
        """tests the logic for deleting a user that owns groups and is reassigned to another user"""

        group1_name = "owner_%s" % uuid.uuid4().hex[:5]
        group2_name = "member_%s" % uuid.uuid4().hex[:5]
        username = "tuser_%s" % uuid.uuid4().hex[:5]
        gis = self.gis
        um = gis.users
        user = um.create(
            username=username,
            password="!Am4zingp0iNt",
            firstname="testaccount",
            lastname="testaccount",
            email="test@esri.com",
            role="org_user",
            user_type="GISProfessionalAdvUT"
        )
        gm = gis.groups

        assert isinstance(gm, GroupManager)
        group = gm.create(title=group1_name, tags="tags,integration_test")
        group2 = gm.create(title=group2_name, tags="tags,integration_test")

        group.add_users(usernames=[user])
        group2.add_users(usernames=[user])
        group.update_users_roles(managers=[user])
        group.reassign_to(user)
        group.remove_users(usernames=[gis.users.me])
        assert isinstance(user, User)

        assert user.delete(reassign_to=gis.users.me)

        group.delete()
        group2.delete()

    def test_delete_with_groups(self):
        """tests the logic for deleting a user that owns groups and is not reassigned to another user"""

        group1_name = "owner_%s" % uuid.uuid4().hex[:5]
        group2_name = "member_%s" % uuid.uuid4().hex[:5]
        username = "tuser_%s" % uuid.uuid4().hex[:5]
        gis = self.gis
        um = gis.users
        user = um.create(
            username=username,
            password="!Am4zingp0iNt",
            firstname="testaccount",
            lastname="testaccount",
            email="test@esri.com",
            role="org_user",
            user_type="GISProfessionalAdvUT"
        )
        gm = gis.groups

        assert isinstance(gm, GroupManager)
        group = gm.create(title=group1_name, tags="tags,integration_test")
        group2 = gm.create(title=group2_name, tags="tags,integration_test")

        group.add_users(usernames=[user])
        group2.add_users(usernames=[user])
        group.update_users_roles(managers=[user])
        group.reassign_to(user)
        group.remove_users(usernames=[gis.users.me])
        assert isinstance(user, User)
        
        assert user.delete(reassign_to=gis.users.me)
        
        assert group.delete()
        assert group2.delete()

if __name__ == "__main__":
    unittest.main()

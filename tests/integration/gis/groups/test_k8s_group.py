import os
import unittest
import unittest.mock
import uuid
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import (
    GIS,
    GroupApplication,
    Group,
    GroupManager,
    CategorySchemaManager,
    GroupMigrationManager,
    UserManager,
)
from arcgis.gis import (
    GIS,
    Item,
    User,
    UserManager,
    Group,
    GroupMigrationManager,
)
from arcgis.gis._impl._jb import StatusJob
from integration.config import QALAB_ROOT_PATH
from utils.decorators import integration_test, profiles


fp = os.path.join(QALAB_ROOT_PATH, "group_manager_data", "parkinglots.zip")


@profiles.admin_all
@integration_test
class TestGroup(unittest.TestCase):
    """
    Tests the `Group` class operations
    """

    def test_group_properties(self):
        """tests the group properties"""
        gm = self.gis.groups
        group = self.gis.groups.create(
            title=f"test_{uuid.uuid4().hex[:5]}", tags="integration_testing"
        )
        assert isinstance(group, Group)
        assert isinstance(group.applications, list)
        assert group.get_thumbnail() is None
        assert group.get_thumbnail_link()
        assert isinstance(group.categories, CategorySchemaManager)
        assert group.download_thumbnail() is None
        group.delete_group_thumbnail()
        assert isinstance(group.migration, GroupMigrationManager)
        assert group.delete()

    def test_list_content(self):
        """tests the group content and member listings"""
        gm = self.gis.groups
        group = self.gis.groups.create(
            title=f"test_{uuid.uuid4().hex[:5]}", tags="integration_testing"
        )
        um = self.gis.users
        assert isinstance(um, UserManager)
        user = um.create(
            username=f"user{uuid.uuid4().hex[:5]}a",
            password="esri.AGP1!",
            firstname="firstname",
            lastname="last_name",
            email="pythonapi@esri.com",
            role="admin",
            user_type="creatorUT",
        )
        group.add_users(usernames=[user.username])
        assert isinstance(group.get_members(), dict)
        assert isinstance(group, Group)
        assert isinstance(group.content(), list)
        group.delete()
        user.delete()

    # ----------------------------------------------------------------------
    def test_update_group(self):
        """this method tests the update method on Group"""
        gm = self.gis.groups
        group = self.gis.groups.create(
            title=f"test_{uuid.uuid4().hex[:5]}", tags="integration_testing"
        )
        assert isinstance(group, Group)
        new_title = f"nt_{uuid.uuid4().hex[:5]}"
        group.update(title=new_title)
        assert isinstance(group, Group)

        um = self.gis.users
        assert isinstance(um, UserManager)
        user = um.create(
            username=f"user{uuid.uuid4().hex[:5]}a",
            password="esri.AGP1!",
            firstname="firstname",
            lastname="last_name",
            email="pythonapi@esri.com",
            role="admin",
            user_type="creatorUT",
        )
        group.add_users(usernames=[user.username])
        group.reassign_to(target_owner=user.username)
        assert new_title == group.title
        # print(group.delete())
        assert group.delete()
        assert user.delete()

    def test_add_user_make_owner_group(self):
        """this method tests the add and make owner methods"""
        gm = self.gis.groups
        group = self.gis.groups.create(
            title=f"test_{uuid.uuid4().hex[:5]}", tags="integration_testing"
        )
        assert isinstance(group, Group)
        um = self.gis.users
        assert isinstance(um, UserManager)
        user = um.create(
            username=f"user{uuid.uuid4().hex[:5]}a",
            password="esri.AGP1!",
            firstname="firstname",
            lastname="last_name",
            email="pythonapi@esri.com",
            role="admin",
            user_type="creatorUT",
        )
        group.add_users(usernames=[user.username])  # adds a new user.
        assert group.reassign_to(
            target_owner=user.username
        )  # changes the owner
        assert group.delete()
        assert user.delete()


@profiles.admin_all
@integration_test
class TestGroupApplication(unittest.TestCase):
    """
    Tests the `GroupApplication` class operations
    """

    def test_accept_decline_ops(self):
        """tests the application accept/decline operation for `Group`"""
        gis = self.gis
        um = gis.users
        isinstance(um, UserManager)
        user = um.create(
            username=f"user{uuid.uuid4().hex[:5]}a",
            password="esri.AGP1!",
            firstname="firstname",
            lastname="last_name",
            email="pythonapi@esri.com",
            role="admin",
            user_type="creatorUT",
        )

        user.reset(
            new_security_question=1,
            new_security_answer="Redlands",
            password="esri.AGP1!",
            new_password="esri.AGP2!",
        )
        url = gis._url
        username = user.username
        group = gis.groups.create(
            title=f"test_{uuid.uuid4().hex[:5]}", tags="integration_testing"
        )
        group_id = group.groupid
        del gis

        gis = GIS(
            url=url,
            username=username,
            password="esri.AGP2!",
            verify_cert=False,
            trust_env=True,
        )
        resp = gis.groups.get(group_id).join()
        print(resp)
        assert resp
        del gis

        gis = self.gis
        group = gis.groups.get(group_id)
        assert isinstance(group, Group)
        assert isinstance(group.applications, list)
        # run the accept workflow
        for app in group.applications:
            assert isinstance(app, GroupApplication)
            assert app.accept()
        group.delete()
        group = gis.groups.create(
            title=f"test_{uuid.uuid4().hex[:5]}", tags="integration_testing"
        )
        group_id = group.groupid
        del gis

        gis = GIS(
            url=url,
            username=username,
            password="esri.AGP2!",
            verify_cert=False,
            trust_env=True,
        )
        resp = gis.groups.get(group_id).join()
        del gis

        gis = self.gis
        group = gis.groups.get(group_id)
        assert isinstance(group, Group)
        assert isinstance(group.applications, list)
        # run the accept workflow
        for app in group.applications:
            assert isinstance(app, GroupApplication)
            print(app.properties)
            assert app.decline()

        del gis

        gis = self.gis
        group = gis.groups.get(group_id)
        user = gis.users.get(username)

        assert group.delete()
        assert user.delete()


@profiles.all
@integration_test
class TestGroupManager(unittest.TestCase):
    """
    Tests the `GroupManager` class operations
    """

    # ----------------------------------------------------------------------
    def test_create_group_manager(self):
        """tests the creation of the group manager object"""
        self.assertTrue(isinstance(self.gis.groups, GroupManager))

    def test_create(self):
        """tests the creation of a group"""
        gm = self.gis.groups
        isinstance(gm, GroupManager)
        grp = gm.create(
            title=f"test_grp1_{uuid.uuid4().hex[:3]}", tags="integration_testing"
        )
        self.assertTrue(isinstance(grp, Group))
        assert grp.delete()

    # ----------------------------------------------------------------------
    def test_create_dict(self):
        """tests the creation of a group"""
        gm = self.gis.groups
        isinstance(gm, GroupManager)
        d = {
            "title": f"test_grp1_{uuid.uuid4().hex[:3]}",
            "tags": "tag1",
            "access": "private",
        }
        grp = gm.create_from_dict(d)
        self.assertTrue(isinstance(grp, Group))
        assert grp.delete()

    # ----------------------------------------------------------------------
    def test_search(self):
        """tests the searching of a group"""
        gm = self.gis.groups
        isinstance(gm, GroupManager)
        res = gm.search(max_groups=10)
        assert len(res) > 0

    # ----------------------------------------------------------------------
    def test_get_group(self):
        """tests the `GET` of a group"""
        gm = self.gis.groups
        isinstance(gm, GroupManager)
        grp = gm.create(
            title=f"test_grp1_{uuid.uuid4().hex[:3]}", tags="integration_testing"
        )
        assert gm.get(grp.id).id == grp.id  # checks the
        assert grp.delete()


if __name__ == "__main__":
    unittest.main()

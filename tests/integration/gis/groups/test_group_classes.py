import unittest
import uuid
from arcgis.gis import GIS, ItemTypeEnum, Group, GroupManager, GroupApplication, GroupMigrationManager, CategorySchemaManager
from utils.decorators import integration_test, profiles
from integration.config import get_resource_path, INTEGRATION_TEST_ITEM_TAG
from utils.data_utils import publish_test_item, cleanup_published_items


fp = get_resource_path("staging_data/parkinglots.zip", unique_copy=True)


@profiles.admin_all
@integration_test
class TestGroup(unittest.TestCase):
    """Tests the `Group` class operations"""
    @classmethod
    def setUpClass(cls):
        cls.group = cls.gis.groups.create(
            title=f"group_{uuid.uuid4().hex[:4]}", tags=INTEGRATION_TEST_ITEM_TAG
        )
        assert isinstance(cls.group, Group)

        cls.user = cls.gis.users.create(
            username=f"user_{uuid.uuid4().hex[:4]}",
            password="esri.AGP1!",
            firstname="firstname",
            lastname="lastname",
            email="pythonapi@esri.com",
            role="org_publisher",
            user_type="creatorUT",
        )
        cls.user.update_role(role="org_admin")
        cls.group.add_users(usernames=[cls.user.username])

        cls.item = publish_test_item(
            gis=cls.gis, source_data_path=fp, item_type=ItemTypeEnum.SHAPEFILE, layer_name=f"list_group_{uuid.uuid4().hex[:4]}"
        )
        cls.item.sharing.groups.add(cls.group)

        cls.owner = cls.group.get_members()['owner']

    @classmethod
    def tearDownClass(cls):
        cleanup_published_items([cls.item])
        cls.group.delete()
        cls.user.delete()

    def test_group_properties(self):
        """tests the group properties"""
        assert isinstance(self.group.applications, list)
        assert self.group.get_thumbnail() is None
        assert self.group.get_thumbnail_link()
        assert isinstance(self.group.categories, CategorySchemaManager)
        assert self.group.download_thumbnail() is None
        self.group.delete_group_thumbnail()
        if not self.gis._is_agol:
            assert isinstance(self.group.migration, GroupMigrationManager)

    def test_list_group_user_and_content(self):
        """tests the group content and member listings"""
        assert isinstance(self.group.get_members(), dict)
        assert self.user.username == self.group.get_members()['users'][0]

        assert isinstance(self.group.content(), list)
        assert self.item.itemid == self.group.content()[0].itemid

    def test_group_reassign_owner(self):
        """tests the add and make owner methods"""
        assert self.group.reassign_to(target_owner=self.user.username)
        assert self.group.get_members()['owner'] == self.user.username
        self.group.reassign_to(target_owner=self.owner)


@profiles.admin_all
@integration_test
class TestGroupApplication(unittest.TestCase):
    """Tests the GroupApplication class operations"""

    def setUp(self):
        # new user send application
        self.user = self.gis.users.create(
            username=f"application_user_{uuid.uuid4().hex[:4]}",
            password="esri.AGP1!",
            firstname="firstname",
            lastname="last_name",
            email="pythonapi@esri.com",
            role="org_publisher",
            user_type="creatorUT",
        )
        self.user.update_role(role="org_admin")

        self.user.reset(
            new_security_question=1,
            new_security_answer="Redlands",
            password="esri.AGP1!",
            new_password="esri.AGP2!"
        )
        self.user_gis = GIS(
            url=self.gis.url,
            username=self.user.username,
            password="esri.AGP2!",
            verify_cert=False,
            trust_env=True,
        )
        self.group = self.gis.groups.create(
            title=f"group_application_{uuid.uuid4().hex[:4]}", tags=INTEGRATION_TEST_ITEM_TAG
        )
        self.user_gis.groups.get(self.group.groupid).join()

    def tearDown(self):
        self.user.delete()
        self.group.delete()

    def test_accept_ops(self):
        """tests the application accept/decline operation for `Group`"""
        # accept application
        assert isinstance(self.group.applications, list)
        for app in self.group.applications:
            assert isinstance(app, GroupApplication)
            assert app.accept()
        assert len(self.group.applications) == 0

    def test_decline_ops(self):
        # decline application
        assert isinstance(self.group.applications, list)
        for app in self.group.applications:
            assert isinstance(app, GroupApplication)
            assert app.decline()
        assert len(self.group.applications) == 0


@profiles.all
@integration_test
class TestGroupManager(unittest.TestCase):
    """Tests the GroupManager class operations"""

    def test_create_group_manager(self):
        """tests the creation of the group manager object"""
        assert isinstance(self.gis.groups, GroupManager)

    def test_create(self):
        """tests the creation of a group"""
        grp = self.gis.groups.create(
            title=f"test_grp_{uuid.uuid4().hex[:4]}", tags=INTEGRATION_TEST_ITEM_TAG
        )
        assert isinstance(grp, Group)
        assert grp.delete()

    def test_create_dict(self):
        """tests the creation of a group from dict"""
        d = {
            "title": f"test_grp_{uuid.uuid4().hex[:4]}",
            "tags": INTEGRATION_TEST_ITEM_TAG,
            "access": "private",
        }
        grp = self.gis.groups.create_from_dict(d)
        assert isinstance(grp, Group)
        assert grp.delete()

    def test_get_group(self):
        """tests the `GET` of a group"""
        grp = self.gis.groups.create(
            title=f"test_grp_{uuid.uuid4().hex[:4]}", tags=INTEGRATION_TEST_ITEM_TAG
        )
        assert self.gis.groups.get(grp.id).id == grp.id
        assert grp.delete()


if __name__ == "__main__":
    unittest.main()

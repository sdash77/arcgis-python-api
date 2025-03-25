import unittest
import uuid
from arcgis.gis import GIS, User, UserManager, Group, GroupManager
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis.sharing import UserInvitationManager
from utils.decorators import integration_test

PROFILES = ["your_online_admin_profile", "your_ent_admin_profile"]

proxies = detect_proxy(True)


@integration_test
class TestUserInvitationManager(unittest.TestCase):
    """Tests the user invitation manager"""

    def test_manager(self):
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=proxies)
            me = gis.users.me
            imgr = me.invitations
            assert imgr
            assert isinstance(imgr, UserInvitationManager)

    def test_list_invites(self):
        """tests the list function for a user"""
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=proxies)
            me = gis.users.me
            imgr = me.invitations
            assert isinstance(imgr.list, list)

    def test_accept(self):
        """tests the accept function"""
        group = None
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=proxies)
            me = gis.users.me
            imgr = me.invitations
            assert isinstance(imgr.list, list)
            um = gis.users
            test_user = None
            try:
                test_user = um.create(
                    username=f"user_{uuid.uuid4().hex[:5]}bc",
                    password="VeryS3cur3!",
                    firstname="delete",
                    lastname="thisaccount",
                    email="support@esri.com",
                    role='publisher',
                )
                assert isinstance(test_user, User)
                gm = gis.groups
                isinstance(gm, GroupManager)
                group = gm.create(title="test_group_123a", tags="a,b,c")
                group.reassign_to(target_owner=test_user)
                group.leave()
                group.invite_users(usernames=[me])
                assert isinstance(me.invitations.list, list)
                assert len(me.invitations.list) > 0
                res = me.invitations.list[0].accept()
                assert isinstance(res, dict)

            except Exception as e:
                print(e)
                raise e
            finally:
                if group:
                    group.delete()
                if test_user:
                    test_user.delete()

    def test_properties(self):
        """tests the properties on the invitation"""
        group = None
        user = None
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=proxies)
            me = gis.users.me
            imgr = me.invitations
            assert isinstance(imgr.list, list)
            um = gis.users
            test_user = None
            try:
                test_user = um.create(
                    username=f"user_{uuid.uuid4().hex[:5]}bc",
                    password="VeryS3cur3!",
                    firstname="delete",
                    lastname="thisaccount",
                    email="support@esri.com",
                    role='publisher',
                )
                assert isinstance(test_user, User)
                gm = gis.groups
                isinstance(gm, GroupManager)
                group = gm.create(title="test_group_123a", tags="a,b,c")
                group.reassign_to(target_owner=test_user)
                group.leave()
                group.invite_users(usernames=[me])
                assert isinstance(me.invitations.list, list)
                assert len(me.invitations.list) > 0
                res = me.invitations.list[0].properties
                assert isinstance(res, dict)

            except Exception as e:
                print(e)
                raise e
            finally:
                if group:
                    group.delete()
                if test_user:
                    test_user.delete()

    def test_decline(self):
        """tests the decline operation"""
        group = None
        for profile in PROFILES:
            gis = GIS(profile=profile, verify_cert=False, proxy=proxies)
            me = gis.users.me
            imgr = me.invitations
            assert isinstance(imgr.list, list)
            um = gis.users
            test_user = None
            try:
                test_user = um.create(
                    username=f"user_{uuid.uuid4().hex[:5]}bc",
                    password="VeryS3cur3!",
                    firstname="delete",
                    lastname="thisaccount",
                    email="support@esri.com",
                    role='publisher',
                )
                assert isinstance(test_user, User)
                gm = gis.groups
                isinstance(gm, GroupManager)
                group = gm.create(title="test_group_123a", tags="a,b,c")
                group.reassign_to(target_owner=test_user)
                group.leave()
                group.invite_users(usernames=[me])
                assert isinstance(me.invitations.list, list)
                assert len(me.invitations.list) > 0
                res = me.invitations.list[0].decline()
                assert isinstance(res, dict)

            except Exception as e:
                print(e)
                raise e
            finally:
                if group:
                    group.delete()
                if test_user:
                    test_user.delete()


if __name__ == "__main__":
    unittest.main()

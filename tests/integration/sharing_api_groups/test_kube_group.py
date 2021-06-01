import sys, os
import unittest
import unittest.mock
from unittest.mock import MagicMock
import uuid

from arcgis.gis import (GIS, GroupApplication,
                        Group, GroupManager,
                        CategorySchemaManager,
                        GroupMigrationManager, UserManager)
from arcgis.gis import ProfileManager
from arcgis.gis import GIS, Item, User, UserManager, Group, GroupMigrationManager
from arcgis.gis._impl._jb import StatusJob

profiles = ['your_kubernetes_profile']
#['your_online_profile', 'your_enterprise_profile', 'your_kubernetes_profile']  # profile names go here
dest_profile = 'your_dest_ent_profile'
VERIFY_CERT = False # Boolean T/F

if 'your_dest_ent_profile' not in ProfileManager().list():
    gis = GIS(
        url = "https://datascienceqa.esri.com/portal",
        username = "portaladmin",
        password = "esri.agp",
        profile='your_dest_ent_profile',
        verify_cert=False, trust_env=True)
    del gis

try:
    from utils import NOTEBOOK_TESTS_DIR
    fp = os.path.join(NOTEBOOK_TESTS_DIR, "parkinglots.zip")

except:
    fp = r"./parkinglots.zip"

###########################################################################
class TestGroupImportExport(unittest.TestCase):
    """Tests the Group Import/Export Methods on a Group Object"""
    #----------------------------------------------------------------------
    def test_group_export_async(self):
        """tests exporting the group items to an epk"""
        for profile in profiles:

            gis = GIS(profile=profile, verify_cert=False, trust_env=True)
            for i in gis.content.search("erasemedata123"):
                assert i.delete()
            pitem = gis.content.add({'title' : "erasemedata123", "tags" : ['a', 'b', 'c']}, data=fp)
            #pitem = item.publish()
            for grp in gis.groups.search("export_test_group"):
                assert grp.delete()
            new_group = gis.groups.create(title='export_test_group', tags='a,b,c')
            isinstance(pitem, Item)
            pitem.share(groups=[new_group])
            epk_file = new_group.migration.create(items=[pitem],
                                                  future=True) # SHould Return an StatusJob
            assert isinstance(epk_file, StatusJob)
            assert epk_file.result()
            assert isinstance(epk_file.result(), Item)
            assert epk_file.result().delete()
            assert pitem.delete()
    #----------------------------------------------------------------------
    def test_group_export_sync(self):
        """tests exporting the group items to an epk"""
        for profile in profiles:

            gis = GIS(profile=profile, verify_cert=False, trust_env=True)
            for i in gis.content.search("erasemedata123"):
                assert i.delete()
            pitem = gis.content.add({'title' : "erasemedata123", "tags" : ['a', 'b', 'c']}, data=fp)
            #pitem = item.publish()
            for grp in gis.groups.search("export_test_group"):
                assert grp.delete()
            new_group = gis.groups.create(title='export_test_group', tags='a,b,c')
            isinstance(pitem, Item)
            pitem.share(groups=[new_group])

            epk_file = new_group.migration.create(items=[pitem],
                                                  future=False) # SHould Return an Item
            assert isinstance(epk_file, Item)
            assert epk_file.delete()
            assert pitem.delete()
###########################################################################
class TestImport2Group(unittest.TestCase):
    """tests the import methods"""
    @unittest.skip('failing')
    def test_group_import_two_gis_objects(self):
        """tests importing the group items from an epk"""
        for profile in profiles:

            gis = GIS(profile=profile, verify_cert=False, trust_env=True)

            for i in gis.content.search("erasemedata123"):
                assert i.delete()
            pitem = gis.content.add({'title' : "erasemedata123", "tags" : ['a', 'b', 'c']}, data=fp)
            for grp in gis.groups.search("export_test_group"):
                assert grp.delete()
            new_group = gis.groups.create(title='export_test_group', tags='a,b,c')
            isinstance(pitem, Item)
            pitem.share(groups=[new_group])
            epk_file = new_group.migration.create(items=[pitem],
                                                  future=False) # SHould Return an Item
            export_package_file = epk_file.download()
            assert isinstance(epk_file, Item)
            assert pitem.delete()
            gis_dest = GIS(profile='your_dest_ent_profile', verify_cert=False, trust_env=True, set_active=False)
            grps = gis_dest.groups.search("new_group1_dest")
            if len(grps) > 0:
                [grp.delete() for grp in grps]
            group_dest = gis_dest.groups.create("new_group1_dest", tags='migration')

            import uuid
            new_item = gis_dest.content.add({"title": f"test_import_{uuid.uuid4().hex[:6]}", "type": "Export Package",
                                 "typeKeywords": ["a", "b", "c"], "tags": ["atag", "btag", "ctag"]}, data=export_package_file)

            new_item.share(groups=[group_dest])
            m = group_dest.migration
            print('inspecting')
            inspection = m.inspect(new_item)
            print('inspecting done')
            assert isinstance(m, GroupMigrationManager)
            print('loading')
            res = m.load(epk_file)

            assert res
            assert isinstance(res, StatusJob)
            assert isinstance(res.result(), dict)
            assert all([i.delete() for i in res.result()['itemsImported']])
            print('loading done')
            print('clean up')
            [i.delete() for i in group_dest.content()]
            new_group.delete()
    #----------------------------------------------------------------------
    def test_group_import(self):
        """tests importing the group items from an epk"""
        for profile in profiles:
            gis = GIS(profile=profile,
                      trust_env=True,
                      verify_cert=False)
            for i in gis.content.search("erasemedata123"):
                assert i.delete()
            pitem = gis.content.add({'title' : "erasemedata123", "tags" : ['a', 'b', 'c']}, data=fp)
            for grp in gis.groups.search("export_test_group"):
                assert grp.delete()
            new_group = gis.groups.create(title='export_test_group', tags='a,b,c')
            isinstance(pitem, Item)
            pitem.share(groups=[new_group])
            epk_file = new_group.migration.create(items=[pitem],

                                                  future=False) # SHould Return an Item
            assert isinstance(epk_file, Item)
            assert pitem.delete()
            m = new_group.migration
            assert isinstance(m, GroupMigrationManager)
            res = m.load(epk_file)
            assert res
            assert isinstance(res, StatusJob)
            assert isinstance(res.result(), dict)
            assert all([i.delete() for i in res.result()['itemsImported']])
            new_group.delete()
    #----------------------------------------------------------------------
    def test_inspect_package(self):
        """
        tests the `inspect` package call on Portal
        """
        for profile in profiles:

            ##
            ## SETUP EXPORT
            ##
            gis = GIS(profile=profile, trust_env=True, verify_cert=False)
            for i in gis.content.search("erasemedata123"):
                assert i.delete()

            pitem = gis.content.add({'title' : "erasemedata123", "tags" : ['a', 'b', 'c']}, data=fp)
            for grp in gis.groups.search("export_test_group"):
                assert grp.delete()
            new_group = gis.groups.create(title='export_test_group', tags='a,b,c')
            pitem.share(groups=[new_group])
            epk_file = new_group.migration.create(items=[pitem],
                                                  future=False) # SHould Return an Item
            assert isinstance(epk_file, Item)
            assert pitem.delete()
            new_group.delete()

            ##
            ## BEGIN PREVIEW TEST
            ##

            for grp in gis.groups.search("export_test_group2342"):
                assert grp.delete()
            new_group = gis.groups.create(title='export_test_group2342', tags='a,b,c')

            epk_file.share(groups=[new_group])
            m = new_group.migration
            assert isinstance(m, GroupMigrationManager)
            res = m.inspect(epk_file)
            assert res
            assert isinstance(res, dict)
            ##
            ## CLEAN UP
            ##
            assert new_group.delete()
            ##
            ## NEED TRY/EXCEPT HERE BECAUSE PRERELEASE (10.8.1)
            ## HAS BUG ON DELETING PREVIEWED ITEMS
            ##
            try:
                epk_file.delete()
            except:
                pass
###########################################################################
class TestGroup(unittest.TestCase):
    """
    Tests the `Group` class operations
    """
    def test_group_properties(self):
        """tests the group properties"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            gm = gis.groups
            group = gis.groups.create(title=f'test_{uuid.uuid4().hex[:5]}', tags='tag1,tag2')
            self.assertIsInstance(group, Group)
            isinstance(group, Group)
            assert isinstance(group.applications, list)
            assert group.get_thumbnail() is None
            assert group.get_thumbnail_link()
            assert isinstance(group.categories, CategorySchemaManager)
            assert group.download_thumbnail() is None
            group.delete_group_thumbnail()
            assert isinstance(group.migration, GroupMigrationManager)
            assert group.delete()

    #----------------------------------------------------------------------
    def test_list_content(self):
        """tests the group content and member listings"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            gm = gis.groups
            group = gis.groups.create(title=f'test_{uuid.uuid4().hex[:5]}', tags='tag1,tag2')
            um = gis.users
            isinstance(um, UserManager)
            user = um.create(username=f"user{uuid.uuid4().hex[:5]}a", password="esri.AGP1!", firstname='firstname', lastname='last_name', email='pythonapi@esri.com')
            group.add_users(usernames=[user.username])
            assert isinstance(group.get_members(), dict)

            self.assertIsInstance(group, Group)
            isinstance(group, Group)
            assert isinstance(group.content(), list)
            assert isinstance(group, Group)
            group.delete()
            user.delete()
    #----------------------------------------------------------------------
    def test_update_group(self):
        """this method tests the update method on Group"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            gm = gis.groups
            group = gis.groups.create(title=f'test_{uuid.uuid4().hex[:5]}', tags='tag1,tag2')
            self.assertIsInstance(group, Group)
            new_title = f'nt_{uuid.uuid4().hex[:5]}'
            group.update(title=new_title)
            isinstance(group, Group)

            um = gis.users
            isinstance(um, UserManager)
            user = um.create(username=f"user{uuid.uuid4().hex[:5]}a", password="esri.AGP1!", firstname='firstname', lastname='last_name', email='pythonapi@esri.com')
            group.add_users(usernames=[user.username])
            group.reassign_to(target_owner=user.username)
            assert new_title == group.title
            #print(group.delete())
            assert group.delete()
            assert user.delete()
    #----------------------------------------------------------------------
    def test_add_user_make_owner_group(self):
        """this method tests the add and make owner methods"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            gm = gis.groups
            group = gis.groups.create(title=f'test_{uuid.uuid4().hex[:5]}', tags='tag1,tag2')
            self.assertIsInstance(group, Group)
            isinstance(group, Group)
            um = gis.users
            isinstance(um, UserManager)
            user = um.create(username=f"user{uuid.uuid4().hex[:5]}a", password="esri.AGP1!", firstname='firstname', lastname='last_name', email='pythonapi@esri.com')
            group.add_users(usernames=[user.username]) # adds a new user.
            assert group.reassign_to(target_owner=user.username) # changes the owner
            assert group.delete()

            assert user.delete()


###########################################################################
class TestGroupApplication(unittest.TestCase):
    """
    Tests the `GroupApplication` class operations
    """
    #----------------------------------------------------------------------
    def test_accept_decline_ops(self):
        """tests the application accept/decline operation for `Group`"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            um = gis.users
            isinstance(um, UserManager)
            user = um.create(username=f"user{uuid.uuid4().hex[:5]}a", password="esri.AGP1!", firstname='firstname', lastname='last_name', email='pythonapi@esri.com')

            user.reset(new_security_question=1,
                       new_security_answer="Redlands",
                       password='esri.AGP1!',
                       new_password="esri.AGP2!")
            url = gis._url
            username = user.username
            group = gis.groups.create(title=f'test_{uuid.uuid4().hex[:5]}', tags='tag1,tag2')
            group_id = group.groupid
            del gis

            gis = GIS(url=url, username=username, password='esri.AGP2!', verify_cert=VERIFY_CERT, trust_env=True)
            resp = gis.groups.get(group_id).join()
            print(resp)
            assert resp
            del gis
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            group = gis.groups.get(group_id)
            assert isinstance(group, Group)
            assert isinstance(group.applications, list)
            # run the accept workflow
            for app in group.applications:
                assert isinstance(app, GroupApplication)
                assert app.accept()
            group.delete()
            group = gis.groups.create(title=f'test_{uuid.uuid4().hex[:5]}', tags='tag1,tag2')
            group_id = group.groupid
            del gis

            gis = GIS(url=url, username=username, password='esri.AGP2!', verify_cert=VERIFY_CERT, trust_env=True)
            resp = gis.groups.get(group_id).join()
            del gis

            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            group = gis.groups.get(group_id)
            assert isinstance(group, Group)
            assert isinstance(group.applications, list)
            # run the accept workflow
            for app in group.applications:
                assert isinstance(app, GroupApplication)
                print(app.properties)
                assert app.decline()

            del gis

            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            group = gis.groups.get(group_id)
            user = gis.users.get(username)

            assert group.delete()
            assert user.delete()

###########################################################################
class TestGroupManager(unittest.TestCase):
    """
    Tests the `GroupManager` class operations
    """
    #----------------------------------------------------------------------
    def test_create_group_manager(self):
        """tests the creation of the group manager object"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            self.assertTrue(isinstance(gis.groups, GroupManager))
    #----------------------------------------------------------------------
    def test_create(self):
        """tests the creation of a group"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            gm = gis.groups
            isinstance(gm, GroupManager)
            grp = gm.create(title=f'test_grp1_{uuid.uuid4().hex[:3]}', tags='tag1')
            self.assertTrue(isinstance(grp, Group))
            assert grp.delete()
    #----------------------------------------------------------------------
    def test_create_dict(self):
        """tests the creation of a group"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            gm = gis.groups
            isinstance(gm, GroupManager)
            d = {"title":f'test_grp1_{uuid.uuid4().hex[:3]}', "tags":'tag1', 'access' : 'private'}
            grp = gm.create_from_dict(d)
            self.assertTrue(isinstance(grp, Group))
            assert grp.delete()
    #----------------------------------------------------------------------
    def test_search(self):
        """tests the searching of a group"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            gm = gis.groups
            isinstance(gm, GroupManager)
            res = gm.search(max_groups=10)
            assert len(res) > 0
    #----------------------------------------------------------------------
    def test_get_group(self):
        """tests the `GET` of a group"""
        for profile in profiles:
            gis = GIS(profile=profile, verify_cert=VERIFY_CERT, trust_env=True)
            gm = gis.groups
            isinstance(gm, GroupManager)
            grp = gm.create(title=f'test_grp1_{uuid.uuid4().hex[:3]}', tags='tag1')
            assert gm.get(grp.id).id == grp.id # checks the
            assert grp.delete()

###########################################################################
if __name__ == "__main__":
    unittest.main()

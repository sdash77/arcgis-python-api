import sys
#sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_issue_3989\src")
import os
import unittest
import pytest

import arcgis

from arcgis.gis import GIS, Item, User, UserManager, Group, GroupMigrationManager
from arcgis.gis._impl._jb import StatusJob


try:
    from utils import NOTEBOOK_TESTS_DIR
    fp = os.path.join(NOTEBOOK_TESTS_DIR, "parkinglots.zip")
    
except:
    fp = r"./parkinglots.zip"
    

try:
    url = "https://rags19003.ags.esri.com/portal"
    username = "CWadmin"
    password = "esri.agp2"
    SKIPIT = False
except:
    SKIPIT = True
###########################################################################
#@unittest.skipIf(SKIPIT, "cannot connect to the GIS")

class TestGroupImportExport(unittest.TestCase):
    """Tests the Group Import/Export Methods on a Group Object"""
    #----------------------------------------------------------------------
    def test_group_export_async(self):
        """tests exporting the group items to an epk"""
        gis = GIS(url=url, username=username, password=password, verify_cert=False)
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
        gis = GIS(url=url, username=username, password=password, verify_cert=False)
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
@unittest.skipIf(SKIPIT, "cannot connect to the GIS")
class TestImport2Group(unittest.TestCase):
    """tests the import methods"""
    #----------------------------------------------------------------------
    
    def test_group_import(self):
        """tests importing the group items from an epk"""
        gis = GIS(url=url, username=username, password=password, verify_cert=False)
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
        ##
        ## SETUP EXPORT
        ##
        gis = GIS(url=url, username=username, password=password, verify_cert=False)
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
        
        
if __name__ == "__main__":
    unittest.main()
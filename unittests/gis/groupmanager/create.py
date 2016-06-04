import unittest
import os
import sys
from arcgis.gis import *

# add needed root paths to sys.path
cwd = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(cwd))
sys.path.append(root_dir)
import shared_utils.shared_utils as utils

title = "newgroup1"
tags = "tag1,tag2"
tagCompare = ['tag1', 'tag2']
description = "group description"
snippet = "new group snippet"
access = "public"
thumb = None
inviteOnly = True
sortField = "avgRating"
sortOrder = "desc"
isViewOnly = False
batManThumb = os.path.join(sys.path[0], "batman.png")

### This tests the creation of a group usine _Create_ and _CreateFromDict_
### It also tests _Delete_ and Update thumbnail, download thumbnail
### No user adding, or more 'workflow' type tests are done. These to be done else where
## TO-DO :  find a better directory than c:\temp for intermediate data

class TestGISGroupManager_Create(unittest.TestCase):
    __owner__ = "Kevin"

    @classmethod
    def setUpClass(self):
        srvProps = utils.get_server_info(os.path.join(root_dir, 'unittest.ini'))
        self.host = srvProps['url']
        self.username = srvProps['admin_user']
        self.password = srvProps['admin_pass']
        self.arcgiscom = True if "arcgis.com" in self.host else False
        self.local = False if self.arcgiscom else True
        self.gis = GIS(self.host, self.username, self.password)

        self.g = self.gis.groups

        # Quick search, clean up of existing groups so tests dont fall down if a previous cleanup failed.
        searchG = self.g.search(title)
        for foundG in searchG:
            foundG.delete()

        self.newGroup = self.g.create(title, tags, description, snippet, access, thumb, inviteOnly, sortField, sortOrder, isViewOnly)

    @classmethod
    def tearDownClass(self):
        '''anything needed for clean up in here'''

        self.newGroup.delete()
        try:
            os.remove(os.path.join(r'c:\temp', "batman.png"))
        except:
            pass

    def test_groupProperties(self):

        # check properties of group we previously created
        self.assertEqual(self.newGroup.title, title)
        self.assertEqual(self.newGroup.tags, tagCompare)
        self.assertEqual(self.newGroup.description, description)
        self.assertEqual(self.newGroup.snippet, snippet)
        self.assertEqual(self.newGroup.access, access)
        self.assertEqual(self.newGroup.thumbnail, thumb)
        self.assertEqual(self.newGroup.isInvitationOnly, inviteOnly)
        self.assertEqual(self.newGroup.sortField, sortField)
        self.assertEqual(self.newGroup.sortOrder, sortOrder)
        self.assertEqual(self.newGroup.isViewOnly, isViewOnly)
        self.assertEqual(self.newGroup.owner, self.username)


    def test_createAlreadyExistingGroup(self):

        self.assertIsNone(self.g.create(title, tags, description, snippet, access))
        # This is the returned message, dont see a way to get that:
        # "Unable to create group. \ You already have a group named 'newgroup1'. Try a different name."

    def test_setThumbnail(self):
        # upload the thumbnail
        thumbUp = self.newGroup.update(thumbnail=batManThumb)
        self.assertTrue(thumbUp)

        # download the thumbnail
        self.newGroup.download_thumbnail(r'c:\temp')
        self.assertTrue(os.path.exists(os.path.join(r'c:\temp', "batman.png")))

    def test_createFromDict(self):

        createDict = {'title': "secondGroup",
                      'tags': tags,
                      'description' : description,
                      'snippet': snippet,
                      'access' : access,
                      'isInvitationOnly' : False,
                      'sortField' : 'avgRating',
                      'sortOrder' : 'desc',
                      'thumbnail' : batManThumb,
                      'isViewOnly' : False}


        group2 = self.g.create_from_dict(createDict)

        self.assertEqual(group2.title, "secondGroup")
        self.assertEqual(group2.tags, tagCompare)
        self.assertEqual(group2.description, description)
        self.assertEqual(group2.snippet, snippet)
        self.assertEqual(group2.owner, self.username)

        group2.delete()


if __name__ == '__main__':
    unittest.main()
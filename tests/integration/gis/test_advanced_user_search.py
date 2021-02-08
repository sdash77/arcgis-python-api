import sys
import copy
import json
import unittest
import pytest
from arcgis.gis import GIS, Item, User, Group, ProfileManager
from arcgis._impl.common._utils import local_time_to_online
import datetime
#--------------------------------------------------------------------------
if not 'your_kubernetes_profile' in ProfileManager().list():
    from arcgis.gis import GIS
    gis = GIS(url="https://devent.esri.com/gis",
              username='admin',
              password='esri.agp',
              profile='your_kubernetes_profile')
#--------------------------------------------------------------------------
class TestAdvancedUserSearch(unittest.TestCase):
    """
    Tests the advanced User Search
    """
    def setUp(self):
        self._gis = []
        self._now = local_time_to_online(datetime.datetime.now())
        self._then = local_time_to_online(datetime.datetime.now() - datetime.timedelta(days=130))
        profiles = ['your_online_profile', 'your_enterprise_profile', 'your_kubernetes_profile']
        for profile in profiles:
            self._gis.append(GIS(profile=profile, verify_cert=False))
    #----------------------------------------------------------------------
    def testCounts(self):
        """tests the total counts"""
        now = self._now
        then = self._then
        for gis in self._gis:
            orgid = gis.users.me.orgId
            q = f"orgid: {orgid}"
            count = gis.users.advanced_search(query=q, return_count=True)
            assert count >= 0
    #----------------------------------------------------------------------
    def testStartMaxUsers(self):
        """tests the total counts"""
        now = self._now
        then = self._then
        for gis in self._gis:
            orgid = gis.users.me.orgId
            q = f"orgid: {orgid}"
            res = gis.users.advanced_search(query=q, start=5, max_users=10)
            assert len(res['results']) >= 1
            assert res['start'] == 5
    #----------------------------------------------------------------------
    def testAllUsers(self):
        """tests the total counts"""
        now = self._now
        then = self._then
        for gis in self._gis:
            orgid = gis.users.me.orgId
            q = f"orgid: {orgid}"
            res = gis.users.advanced_search(query=q, max_users=-1)
            assert res
            assert len(res['results']) >= 1
            assert res['num'] <= 10
            assert res['start'] == 1
    #----------------------------------------------------------------------
    def testWildCardSearch(self):
        """tests the * syntax"""
        for gis in self._gis:
            res = gis.users.advanced_search(query="esri_*")
            assert len(res['results']) >= 0


if __name__ == "__main__":
    unittest.main()

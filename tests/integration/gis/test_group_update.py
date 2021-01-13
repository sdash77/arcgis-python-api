import os
import sys
import json
import time
import datetime
import unittest
import uuid
import pytest
from arcgis.gis import GIS, Item, Group, GroupManager

PROFILES = ['your_online_profile', 'your_enterprise_profile']


class TestGroupMethods(unittest.TestCase):

    def test_update(self):
        for p in PROFILES:
            gis = GIS(profile=p, verify_cert=False, trust_env=True)
            gm = gis.groups
            assert isinstance(gm, GroupManager)
            grp = gm.create(title=f"grp{uuid.uuid4().hex}", tags="tags1,tags2", snippet="snippet")
            assert grp.snippet == "snippet"
            assert grp.update(snippet="", clear_empty_fields=True)
            assert grp.snippet == ""
            grp.delete()

if __name__ == "__main__":
    unittest.main()
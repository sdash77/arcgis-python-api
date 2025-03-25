import os
import sys
import json
import time
import datetime
import logging
import unittest
import uuid
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, Item, Group, GroupManager
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging()


@profiles.enterprise_and_agol
@integration_test
class TestGroupMethods(unittest.TestCase):
    def test_update(self):
        gm = self.gis.groups
        assert isinstance(gm, GroupManager)
        grp = gm.create(
            title=f"grp{uuid.uuid4().hex}", tags="tags1,tags2", snippet="snippet"
        )
        assert grp.snippet == "snippet"
        assert grp.update(snippet="", clear_empty_fields=True)
        assert grp.snippet == ""
        grp.delete()


if __name__ == "__main__":
    unittest.main()

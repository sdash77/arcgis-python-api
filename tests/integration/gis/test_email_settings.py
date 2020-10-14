import sys
import os
import unittest
import pytest

import arcgis
print(arcgis.__file__)
from arcgis.gis import GIS, Item, User, UserManager

try:

    url = "https://rpubs16029.ags.esri.com/portal"
    username = "PAPIadmin"
    password = "PAPIletmein01"
    gis = GIS(url, username, password, verify_cert=False)
    ALL_GOOD = True
except:
    ALL_GOOD = False

@unittest.skipIf(ALL_GOOD == False, "Could not connect to Portal")
class TestEmailSettings(unittest.TestCase):
    """Tests the Email Settings for 10.8.1 Portal"""
    _gis = None
    #----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        url = "https://rpubs16029.ags.esri.com/portal"
        username = "PAPIadmin"
        password = "PAPIletmein01"
        try:
            cls._gis = GIS(url, username, password, verify_cert=False)
        except:
            cls._gis = None
    #----------------------------------------------------------------------
    def test_get_email_setting(self):
        """Tests getting the EmailManager from the System"""
        if self._gis:
            from arcgis.gis.admin._system import EmailManager
            assert isinstance(self._gis.admin.system.email, EmailManager)
    #----------------------------------------------------------------------
    def test_get_email_properties(self):
        """Tests getting the EmailManager Properties"""
        if self._gis:
            from arcgis.gis.admin._system import EmailManager
            from arcgis._impl.common._mixins import PropertyMap
            em = self._gis.admin.system.email
            assert isinstance(em, EmailManager)
            if em.properties:
                em.delete()
            assert em.properties is None
            assert em.update(server="mail.smtpbucket.com",
                      from_email="jasmine@puppydawg.com",
                      require_auth=False, email_label="Woof I'm a Dog",
                      port=8025,
                      encryption="NONE")
            isinstance(em.properties, PropertyMap)
    #----------------------------------------------------------------------
    def test_delete_update_test_email_settings(self):
        """Tests the delete, update and test parts of the EmailManager"""
        if self._gis:
            from arcgis.gis.admin._system import EmailManager
            from arcgis._impl.common._mixins import PropertyMap
            em = self._gis.admin.system.email
            assert isinstance(em, EmailManager)
            if em.properties:
                em.delete()
            assert em.properties is None
            assert em.update(server="mail.smtpbucket.com",
                      from_email="jasmine@puppydawg.com",
                      require_auth=False,
                      email_label="Woof I'm a Dog",
                      port=8025,
                      encryption="SSL")
            assert em.test(email='will.smith@fakeemailaccount.com')
            assert em.delete()

###########################################################################
if __name__ == "__main__":
    unittest.main()
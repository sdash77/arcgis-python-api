import sys
import os
import unittest

import arcgis

print(arcgis.__file__)
from arcgis.gis import GIS, Item, User, UserManager
from utils.decorators import integration_test

try:

    url = "https://dev0019757.esri.com/portal"
    username = "portaladmin"
    password = "esri.agp"
    (
        GIS(
            url, username, password, verify_cert=False, use_gen_token=True
        ).users.me.update(security_question=1, security_answer="Dark and stormy night")
    )
    gis = GIS(url, username, password, verify_cert=False)
    ALL_GOOD = True
except:
    ALL_GOOD = False


@unittest.skipIf(ALL_GOOD == False, "Could not connect to Portal")
@integration_test
class TestEmailSettings(unittest.TestCase):
    """Tests the Email Settings for 10.9.1 Portal"""

    _gis = None
    # ----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        url = "https://dev0019757.esri.com/portal"
        username = "portaladmin"
        password = "esri.agp"
        try:
            cls._gis = GIS(url, username, password, verify_cert=False)
        except:
            cls._gis = None

    # ----------------------------------------------------------------------
    def test_get_email_setting(self):
        """Tests getting the EmailManager from the System"""
        if self._gis:
            from arcgis.gis.admin._system import EmailManager

            assert isinstance(self._gis.admin.system.email, EmailManager)

    # ----------------------------------------------------------------------
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
            assert em.update(
                server="SMTP2.esri.com",
                from_email="arcgispyapibot@esri.com",
                require_auth=False,
                email_label="Test Email",
                port=25,
                encryption="SSL",
            )
            isinstance(em.properties, PropertyMap)

    # ----------------------------------------------------------------------
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
            assert em.update(
                server="SMTP2.esri.com",
                from_email="arcgispyapibot@esri.com",
                require_auth=False,
                email_label="Test Email",
                port=25,
                encryption="SSL",
            )
            assert em.test(email="arcgispyapibot@esri.com")
            assert em.delete()


###########################################################################
if __name__ == "__main__":
    unittest.main()

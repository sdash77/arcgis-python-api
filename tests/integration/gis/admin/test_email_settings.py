import unittest
from utils.decorators import integration_test, profiles
from arcgis.gis.admin._system import EmailManager
from arcgis._impl.common._mixins import PropertyMap


@profiles.admin_enterprise
@integration_test
class TestEmailSettings(unittest.TestCase):
    """Tests the EmailManager"""

    # ----------------------------------------------------------------------
    def test_get_email_setting(self):
        """Tests getting the EmailManager from the System"""
        

        assert isinstance(self.gis.admin.system.email, EmailManager)

    # ----------------------------------------------------------------------
    def test_get_email_properties(self):
        """Tests getting the EmailManager Properties"""
        em = self.gis.admin.system.email
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
        em = self.gis.admin.system.email
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

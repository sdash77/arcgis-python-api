import platform
import unittest
from utils.decorators import integration_test

if platform.platform().lower().find("windows") > -1:

    @integration_test
    class TestBuiltInAuth(unittest.TestCase):

        def test_built_in_auth(self):
            from arcgis.gis import GIS

            """
            # Login with built-in for a federated server
            built_in_auth = GIS(
                url="https://rqawinbi01pt.ags.esri.com/gis",
                username="gisproadv1",
                password="portalaccount1",
                verify_cert=False,
            )
    
            print("Logged in as: " + built_in_auth.properties.user.username)
            """

if __name__ == "__main__":

    unittest.main()

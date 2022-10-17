import platform
import unittest

if platform.platform().lower().find("windows") > -1:

    class TestIWAAuth(unittest.TestCase):

        def test_IWA_auth(self):
            from arcgis.gis import GIS

            # Login with IWA for a federated server
            # IWA_auth = GIS(url="https://rqawiniwa02pt.ags.esri.com/gis", verify_cert=False)

            # print("Logged in as: " + IWA_auth.properties.user.username)


if __name__ == "__main__":

    unittest.main()

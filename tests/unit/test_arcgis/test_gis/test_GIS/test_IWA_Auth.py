import platform

if platform.platform().lower().find("windows") > -1:

    def test_IWA_auth():
        from arcgis.gis import GIS

        # Login with IWA for a federated server
        IWA_auth = GIS(url="https://rqawiniwa02pt.ags.esri.com/gis", verify_cert=False)

        print("Logged in as: " + IWA_auth.properties.user.username)

    test_IWA_auth()

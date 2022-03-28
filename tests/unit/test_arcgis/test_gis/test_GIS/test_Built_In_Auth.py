import platform

if platform.platform().lower().find("windows") > -1:

    def test_built_in_auth():
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

    test_built_in_auth()

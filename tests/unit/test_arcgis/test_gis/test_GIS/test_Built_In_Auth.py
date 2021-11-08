import unittest
import pytest


def test_built_in_auth():
    from arcgis.gis import GIS

    # Login with built-in for a federated server
    built_in_auth = GIS(
        url="https://rqawiniwa02pt.ags.esri.com/gis",
        username="gisproadv1",
        password="portalaccount1",
    )

    print("Logged in as: " + built_in_auth.properties.user.username)

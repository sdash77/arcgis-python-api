import unittest
import pytest


def test_IWA_auth():
    from arcgis.gis import GIS

    # Login with IWA for a federated server
    IWA_auth = GIS(url="https://rqawiniwa02pt.ags.esri.com/gis/home/")

    print("Logged in as: " + IWA_auth.properties.user.username)

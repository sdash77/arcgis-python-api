import unittest
import pytest


def test_built_in_auth():
    from arcgis.gis import GIS

    # Login with built-in for a federated server
    built_in_auth = GIS(
        url="https://rqalnxbi01pt.esri.com/gis/home/",
        username="apps0001",
        password="testapps0001",
    )

    print("Logged in as: " + built_in_auth.properties.user.username)

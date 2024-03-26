import sys
import json
import os, uuid
import tempfile
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ['your_online_profile']  # , 'your_enterprise_profile'
PROXIES = detect_proxy(True)  # Handles Fiddler when True
enable_verbose_logging(__logger__)

notebook_json = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": "## Welcome to your notebook.\n",
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": "#### Run this cell to connect to your GIS and get " "started:",
        },
        {
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {"trusted": True},
            "outputs": [
                {
                    "name": "stderr",
                    "output_type": "stream",
                    "text": "Clowns are everywhere! RUN!!!!!\n: "
                    "UserWarning: You are logged on as "
                    "portaladmin with an administrator role, "
                    "proceed with caution.\n"
                    "  self.users.me.username)\n",
                }
            ],
            "source": 'from arcgis.gis import GIS\ngis = GIS("home")',
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": "#### Now you are ready to start!",
        },
        {
            "cell_type": "code",
            "execution_count": 2,
            "metadata": {"trusted": True},
            "outputs": [
                {"name": "stdout", "output_type": "stream", "text": "portaladmin\n"}
            ],
            "source": "print(gis.users.me.username)",
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {"trusted": True},
            "outputs": [],
            "source": "",
        },
    ],
    "metadata": {
        "esriNotebookRuntime": {
            "notebookRuntimeName": "ArcGIS Notebook " "Python 3 " "Advanced",
            "notebookRuntimeVersion": "5.0",
        },
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.7.9",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 2,
}


@integration_test
class Test_RuntimeInstancesMethodAGOL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._gis = GIS(profile='your_online_profile', verify_cert=False, proxy=PROXIES)

    def test_runtime(self):
        gis = self._gis
        from arcgis.notebook import list_runtimes

        res = list_runtimes(gis)
        assert isinstance(res, list)


@integration_test
class Test_RuntimeInstancesMethodEnterprise(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = "https://rqawinbi01pt.ags.esri.com/gis"
        username = "NBAdvanced"
        password = "NBAdvanced.1"
        cls._gis = GIS(
            url=url,
            username=username,
            password=password,
            verify_cert=False,
            proxy=PROXIES,
        )

    def test_runtime(self):
        gis = self._gis
        from arcgis.notebook import list_runtimes

        res = list_runtimes(gis)
        assert isinstance(res, list)


if __name__ == "__main__":
    unittest.main()

import sys

#
#  Update the Path to set the test area
sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_8882\src")
import json
import os, uuid
import tempfile
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS

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


class TestAGOLNotebookManager(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        assert cls._item.delete()

    @classmethod
    def setUpClass(cls):
        cls._gis = GIS(profile='your_online_profile', verify_cert=False, proxy=PROXIES)

        d = tempfile.gettempdir()
        fp = os.path.join(d, f"test_nbs{uuid.uuid4().hex[:4]}.ipynb")
        writer = open(fp, "w")
        writer.write(json.dumps(notebook_json))
        writer.close()
        cls._item = cls._gis.content.add(
            {
                "type": "Notebook",
                "tags": "delete me",
                "title": f"item_{uuid.uuid4().hex[:6]}",
                "properties": {
                    "notebookRuntimeName": "ArcGIS Notebook Python 3 Advanced",
                    "notebookRuntimeVersion": "5.0",
                },
            },
            data=fp,
        )

    def test_snapeshots(self):
        assert isinstance(self._item.snapshots, list)


if __name__ == "__main__":
    unittest.main()

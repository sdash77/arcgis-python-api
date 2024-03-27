import sys
import json
import os, uuid
import tempfile
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from arcgis.gis.agonb import snapshot as _agosnapshot
from arcgis.gis.nb import _snapshot as _entsnapshot
from arcgis.notebook import list_snapshots, create_snapshot
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

    def test_snapshots_agol(self):
        """tests the AGO snapshot function"""
        res = create_snapshot(self._item, name='abcd2')
        assert res
        assert isinstance(res, _agosnapshot.SnapShot)

    def test_list_snapshots(self):
        """tests the list_snapshots method"""
        res = create_snapshot(self._item, name='abcd2')
        assert len(self._item.snapshots) == len(list_snapshots(self._item))


@integration_test
class TestEntNotebookManager(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        assert cls._item.delete()

    @classmethod
    def setUpClass(cls):
        cls._gis = GIS(
            url="https://rqawinbi01pt.ags.esri.com/gis",
            username="NBAdvanced",
            password="NBAdvanced.1",
            verify_cert=False,
            proxy=PROXIES,
        )

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

    def test_snapshots_ent(self):
        """tests the Enterprise snapshot function"""
        res = create_snapshot(self._item, name='abcd2')
        assert res
        assert isinstance(res, _entsnapshot.SnapShot)

    def test_list_snapshots(self):
        """tests the list_snapshots method"""
        res = create_snapshot(self._item, name='abcd2')
        assert len(self._item.snapshots) == len(list_snapshots(self._item))


"""
if __name__ == "__main__":
    url = "https://rqawinbi01pt.ags.esri.com/gis"
    username = "PAPIadmin"
    password = "PAPIletmein01"
    gis = GIS(url=url, username=username, password=password, verify_cert=False)
    item = gis.content.get("7a289cd368af41a89edeca783dc0072f")
    res1 = create_snapshot(item, name='abcd2')
    [s.delete() for s in item.snapshots]
    print(res1)
    gis = GIS(profile='your_online_profile', verify_cert=False)
    item = gis.content.get("11662e6097c34ec2be7043cdc17cfce2")
    res2 = create_snapshot(item, name='abcd2')
    print(res2)
    [s.delete() for s in item.snapshots]
"""


if __name__ == "__main__":
    unittest.main()

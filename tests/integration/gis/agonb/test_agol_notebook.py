import sys
import os
import json
import time
import uuid
import logging
import unittest
import tempfile
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS, ItemProperties, ItemTypeEnum
from arcgis.gis.agonb import AGOLNotebookManager
from arcgis.gis.agonb.instpref import InstancePreference
from arcgis.gis.agonb.runtime import RuntimeManager
from arcgis.gis.agonb.nb import NotebookManager
from arcgis.gis.agonb.containers import Container, ContainerManager
from arcgis.gis.agonb.snapshot import SnapShot, SnapshotManager
from utils.decorators import integration_test, profiles

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    root.addHandler(handler)


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
                {
                    "name": "stdout",
                    "output_type": "stream",
                    "text": "portaladmin\n",
                }
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
            "notebookRuntimeVersion": "11.0",
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


@profiles.admin_agol
@integration_test
class TestAGOLNotebookManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = tempfile.gettempdir()
        fp = os.path.join(d, f"test_nbs{uuid.uuid4().hex[:4]}.ipynb")
        writer = open(fp, "w")
        writer.write(json.dumps(notebook_json))
        writer.close()

        cls.root_folder = cls.gis.content.folders.get()

        cls._item = cls.root_folder.add(
            item_properties= ItemProperties(
                title=f"test_item_{uuid.uuid4().hex[:6]}",
                item_type=ItemTypeEnum.NOTEBOOK,
                snippet="Test item for AGOL Notebook Manager.",
                description="This is a test item for AGOL Notebook Manager.",
                properties={
                    "notebookRuntimeName": "ArcGIS Notebook Python 3 Advanced",
                    "notebookRuntimeVersion": "11.0",
                }
            ),
            file=fp
        ).result()

    def test_access_agonb(self):
        assert self.gis.notebook_server
        assert isinstance(self.gis.notebook_server[0], AGOLNotebookManager)

    def test_access_properties(self):
        nb = self.gis.notebook_server[0]
        assert isinstance(nb, AGOLNotebookManager)
        assert nb.containers
        assert nb.instance_preferences
        assert nb.notebooksmanager
        assert nb.runtimes
        assert nb.snapshots

    def test_access_instance_pref(self):
        nb = self.gis.notebook_server[0]
        assert isinstance(nb, AGOLNotebookManager)
        ip = nb.instance_preferences
        isinstance(ip, InstancePreference)
        assert ip.available
        assert ip.instances

    def test_notebooksmanager(self):
        nb = self.gis.notebook_server[0]
        assert isinstance(nb, AGOLNotebookManager)
        nbm = nb.notebooksmanager
        assert isinstance(nbm, NotebookManager)

    def test_runtimes(self):
        nb = self.gis.notebook_server[0]
        assert isinstance(nb, AGOLNotebookManager)
        runtimes = nb.runtimes
        assert runtimes
        isinstance(runtimes, RuntimeManager)
        r = runtimes.list()
        assert isinstance(r, list)
        assert runtimes.manifest(r[1]["id"])

    def test_start_single_container(self):
        nb = self.gis.notebook_server[0]
        assert isinstance(nb, AGOLNotebookManager)
        cm = nb.containers
        assert isinstance(cm, ContainerManager)
        r = cm.list()

        start = cm.start(runtime=nb.runtimes.list()[0]["id"]).result()
        assert start
        r = cm.list()
        self.assertIsNotNone(r["containers"], "No containers found")

    def test_containers(self):
        nb = self.gis.notebook_server[0]
        assert isinstance(nb, AGOLNotebookManager)
        cm = nb.containers
        assert isinstance(cm, ContainerManager)
        r = cm.list()
        self.assertIsNotNone(r["containers"], "Could not list of ContainerManagers")
        start = cm.start(runtime=nb.runtimes.list()[0]["id"]).result()
        self.assertTrue(start, "Could not start Container Manager")
        r = cm.list()
        self.assertIsNotNone(r["containers"], "Could not list of ContainerManagers")
        if "containers" in r and len(r["containers"]) > 0:
            container_id = r["containers"][0]["id"]
            container = cm.get(container_id)
            container.shutdown()
            runtimes = nb.runtimes.list()[0]["id"]
            start = cm.start(
                runtime=runtimes,
            ).result()
            self.assertTrue(start, "Could not start Container Manager")
            r = cm.list()
            self.assertIsNotNone(r["containers"], "Could not list of ContainerManagers")
            container_id = r["containers"][0]["id"]
            container = cm.get(container_id)
            assert container.properties
            cn = container.notebooks
            container.shutdown()
        else:
            self.fail("Could not start or access initial notebook objects")

    def test_snapshots(self):
        nb = self.gis.notebook_server[0]
        item = self._item
        assert isinstance(nb, AGOLNotebookManager)
        snapmgr = nb.snapshots
        assert isinstance(snapmgr, SnapshotManager)
        res = snapmgr.create(item=item, name="testsnapshot")
        assert res
        listed = snapmgr.list(item)

        snapshot = snapmgr.list(item)[0]
        assert isinstance(snapshot, SnapShot)

        saved_item = listed[0].save_as_item(title="snapshotcopy")
        assert saved_item
        assert saved_item.delete()
        assert snapshot.delete()
        assert self._item.delete()


if __name__ == "__main__":
    unittest.main()

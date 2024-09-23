import unittest
import os, json, uuid
from arcgis.gis.nb import NotebookServer
from utils.decorators import integration_test, profiles


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
            "notebookRuntimeVersion": "9.0",
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
@profiles.admin_enterprise
class TestNBS109SnapShotManger(unittest.TestCase):
    """Tests the SnapshotManager and SnapShot classes for Notebook Server"""

    def test_get_snapshot_manager(self):
        """tests that the snapshot manager is returned."""
        assert len(self.gis.notebook_server) >= 0
        nbs = self.gis.notebook_server[0]
        assert isinstance(nbs, NotebookServer)
        snapmgr = nbs.notebooks.snapshots
        assert snapmgr

    def test_mgr_methods(self):
        """tests that the snapshot manager creates and deletes snapshot."""
        item = None
        try:
            import tempfile

            d = tempfile.gettempdir()
            fp = os.path.join(d, f"test_nbs{uuid.uuid4().hex[:4]}.ipynb")
            with open(fp, "w") as writer:
                writer.write(json.dumps(notebook_json))

            nbs = self.gis.notebook_server[0]

            item = self.gis.content.add(
                {
                    "type": "Notebook",
                    "tags": "delete me",
                    "title": f"item_{uuid.uuid4().hex[:6]}",
                    "properties": {
                        "notebookRuntimeName": "ArcGIS Notebook Python 3 Advanced",
                        "notebookRuntimeVersion": "9.0",
                    },
                },
                data=fp,
            )

            assert item
            snapmgr = nbs.notebooks.snapshots
            resp = snapmgr.create(item=item, name="testsnapshot")
            assert resp
            snaps = snapmgr.list(item)
            old_len = len(snaps)
            print()
            snaps[-1].delete()
            snaps = snapmgr.list(item)
            new_len = len(snaps)
            assert old_len != new_len
            resp = snapmgr.create(item=item, name=f"test_{uuid.uuid4().hex[:5]}")
            snaps = snapmgr.list(item)
            assert os.path.isfile(snaps[0].download())
            assert snaps[0].properties
            assert snaps[0].save_as_item(title="amazing").delete()
            assert snaps[0].restore()
        except Exception as e:
            raise e
        finally:
            if item:
                item.delete()


if __name__ == "__main__":
    unittest.main()

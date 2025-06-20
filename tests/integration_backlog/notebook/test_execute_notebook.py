import json
import os, uuid
import tempfile
import unittest
from utils.decorators import integration_test, profiles
from utils._logging import enable_verbose_logging


enable_verbose_logging()
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
            "notebookRuntimeVersion": "8.0",
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
@profiles.admin_enterprise_and_agol
class TestAGOLNotebookManager(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        assert cls._item.delete()

    @classmethod
    def setUpClass(cls):
        cls._gis = cls.gis
        d = tempfile.gettempdir()
        fp = os.path.join(d, f"test_nbs{uuid.uuid4().hex[:4]}.ipynb")
        writer = open(fp, "w")
        writer.write(json.dumps(notebook_json))
        writer.close()
        if cls.gis._is_agol:
            notebookRuntimeVersion = "8.0"
        else:
            notebookRuntimeVersion = "9.0"

        cls._item = cls._gis.content.add(
            {
                "type": "Notebook",
                "tags": "delete me",
                "title": f"item_{uuid.uuid4().hex[:6]}",
                "properties": {
                    "notebookRuntimeName": "ArcGIS Notebook Python 3 Advanced",
                    "notebookRuntimeVersion": notebookRuntimeVersion,
                },
            },
            data=fp,
        )

    def test_execute_notebook(self):
        """tests the AGOL execute notebook method"""
        gis = self._gis
        from arcgis.notebook import execute_notebook

        res = execute_notebook(
            item=self._item,
            timeout=50,
            update_portal_item=True,
            parameters=None,
            save_parameters=False,
            server_index=0,
            gis=gis,
            future=False,
        )
        assert isinstance(res, dict)
        assert "jobUrl" in res

    def test_open_notebook_future(self):
        from arcgis._impl._async.jobs import Job

        gis = self._gis
        mgr = gis.notebook_server[0]
        if gis._is_agol:
            nbm = mgr.notebooksmanager
            open_result = nbm.open_notebook(
                itemid=self._item,
                templateid=None,
                nb_runtimeid=None,
                template_nb=None,
                instance_type=None,
                future=True,
            )
        else:
            nbm = mgr.notebooks
            open_result = nbm.open_notebook(
                itemid=self._item.id,
                future=True,
            )
        assert isinstance(open_result, Job)
        assert open_result.result()

    def test_open_notebook(self):

        gis = self._gis
        mgr = gis.notebook_server[0]
        if gis._is_agol:
            nbm = mgr.notebooksmanager
            open_result = nbm.open_notebook(
                itemid=self._item,
                templateid=None,
                nb_runtimeid=None,
                template_nb=None,
                instance_type=None,
                future=False,
            )
        else:
            nbm = mgr.notebooks
            open_result = nbm.open_notebook(
                itemid=self._item.id,
                future=False,
            )

        assert open_result

    def test_execute_notebook_future(self):
        """tests the AGOL execute notebook method"""
        from arcgis._impl._async.jobs import Job

        gis = self._gis
        from arcgis.notebook import execute_notebook

        res = execute_notebook(
            item=self._item,
            timeout=50,
            update_portal_item=True,
            parameters=None,
            save_parameters=False,
            server_index=0,
            gis=gis,
            future=True,
        )
        assert isinstance(res, Job)
        assert res.result()


if __name__ == "__main__":
    unittest.main()

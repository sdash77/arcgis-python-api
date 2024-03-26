import sys
import json
import os, uuid
import tempfile
import logging
import unittest
from arcgis.auth.tools._util import detect_proxy
from arcgis.gis import GIS
from utils.decorators import integration_test
from arcgis.notebook import list_runtimes

__logger__ = logging.getLogger()


def enable_verbose_logging(root):
    """Enables all messages to be shown to stdout"""
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(' -  -  - ')
    # handler.setFormatter(formatter)
    root.addHandler(handler)


profiles = ["your_online_admin_profile"]  # , 'your_enterprise_profile'
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
        cls._gis = GIS(
            profile="your_online_admin_profile",
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

    # @unittest.skip("I work")
    def test_execute_notebook_agol(self):
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

    # @unittest.skip("said so")
    def test_open_notebook_agol_future(self):
        from arcgis._impl._async.jobs import Job

        gis = self._gis
        mgr = gis.notebook_server[0]
        print(mgr)
        nbm = mgr.notebooksmanager
        open_result = nbm.open_notebook(
            itemid=self._item,
            templateid=None,
            nb_runtimeid=None,
            template_nb=None,
            instance_type=None,
            future=True,
        )
        assert isinstance(open_result, Job)
        assert open_result.result()

    # @unittest.skip("said so")
    def test_open_notebook_agol(self):
        from arcgis._impl._async.jobs import Job

        gis = self._gis
        mgr = gis.notebook_server[0]
        print(mgr)
        nbm = mgr.notebooksmanager
        open_result = nbm.open_notebook(
            itemid=self._item,
            templateid=None,
            nb_runtimeid=None,
            template_nb=None,
            instance_type=None,
            future=False,
        )

        assert open_result

    # @unittest.skip("said so")
    def test_execute_notebook_agol_future(self):
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
        # res = res.result()
        assert res.result()


@integration_test
class Test_ExecuteNotebookMethod(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        assert cls._item.delete()

    @classmethod
    def setUpClass(cls):
        url = "https://rextapilnx02eb.esri.com/portal"
        username = "NBAdvanced"
        password = "NBAdvanced.1"
        ent_json_data = '{"nbformat_minor":2,"metadata":{"language_info":{"pygments_lexer":"ipython3","nbconvert_exporter":"python","codemirror_mode":{"name":"ipython","version":3},"name":"python","mimetype":"text/x-python","file_extension":".py","version":"3.7.11"},"esriNotebookRuntime":{"notebookRuntimeName":"ArcGIS Notebook Python 3 Standard","notebookRuntimeVersion":"9.0"},"kernelspec":{"name":"python3","language":"python","display_name":"Python 3 (ipykernel)"}},"cells":[{"metadata":{},"source":"## Welcome to your notebook.\\n","cell_type":"markdown"},{"metadata":{},"source":"#### Run this cell to connect to your GIS and get started:","cell_type":"markdown"},{"outputs":[{"output_type":"stream","name":"stderr","text":"/opt/conda/lib/python3.7/site-packages/arcgis/gis/__init__.py:575: UserWarning:\\n\\nYou are logged on as andrew with an administrator role, proceed with caution.\\n\\n"}],"metadata":{"trusted":false},"execution_count":1,"source":"from arcgis.gis import GIS\\ngis = GIS(\\"home\\")","cell_type":"code"},{"metadata":{},"source":"#### Now you are ready to start!","cell_type":"markdown"},{"outputs":[{"output_type":"stream","name":"stdout","text":"<User username:andrew>\\n"}],"metadata":{"trusted":false},"execution_count":2,"source":"print(gis.users.me)","cell_type":"code"},{"outputs":[{"output_type":"stream","name":"stdout","text":"I\'m finished\\n"}],"metadata":{"trusted":true},"execution_count":1,"source":"output = \\"I\'m finished\\"\\nprint(output)","cell_type":"code"},{"outputs":[],"metadata":{"trusted":true},"execution_count":null,"source":"","cell_type":"code"}],"nbformat":4}'

        cls._gis = GIS(
            url=url,
            username=username,
            password=password,
            verify_cert=False,
            proxy=PROXIES,
        )
        runtimes = list_runtimes(gis=cls._gis)
        runtimes[-1]
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
                    "notebookRuntimeVersion": "8.0",
                },
            },
            data=fp,
        )
        cls._item.update(
            {
                "notebookRuntimeName": runtimes[-1]["name"],
                "notebookRuntimeVersion": runtimes[-1]["version"],
            }
        )
        print("stop")

    def test_open_notebook_ent_future(self):
        from arcgis._impl._async.jobs import Job

        gis = self._gis
        mgr = gis.notebook_server[0]
        print(mgr)
        nbm = mgr.notebooks
        open_result = nbm.open_notebook(
            itemid=self._item.id,
            future=True,
        )
        assert isinstance(open_result, Job)
        assert open_result.result()

    def test_open_notebook_ent(self):
        from arcgis._impl._async.jobs import Job

        gis = self._gis
        mgr = gis.notebook_server[0]
        nbm = mgr.notebooks
        open_result = nbm.open_notebook(
            itemid=self._item.id,
            future=True,
        )

        assert open_result
        assert open_result.result()
        print("stop")

    # @unittest.skip("i work")
    def test_execute_notebook_ent(self):
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

    def test_execute_notebook_ent_future(self):
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

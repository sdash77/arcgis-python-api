"""
This is 10.8.1+ Functionality Tests for Notebook Server
"""
import sys

sys.path.insert(0, r"C:\SVN\geosaurus_master_issue_7655\src")
import json
import unittest
import os, json
import arcgis
from arcgis.gis import GIS
from arcgis.gis.nb import NotebookServer, NotebookManager
from arcgis.gis.tasks._schedule import TaskManager, Task
from arcgis.gis.tasks._schedule import Run

try:
    url = "https://datasciencedev.esri.com/portal"
    username = "portaladmin"
    password = "esri.agp"
    gis = GIS(
        url=url, username=username, password=password, verify_cert=False, trust_env=True
    )
    SKIP_TESTS = False
except:
    SKIP_TESTS = True


json_data = '{"nbformat_minor":2,"metadata":{"language_info":{"pygments_lexer":"ipython3","nbconvert_exporter":"python","codemirror_mode":{"name":"ipython","version":3},"name":"python","mimetype":"text/x-python","file_extension":".py","version":"3.7.11"},"esriNotebookRuntime":{"notebookRuntimeName":"ArcGIS Notebook Python 3 Standard","notebookRuntimeVersion":"6.0"},"kernelspec":{"name":"python3","language":"python","display_name":"Python 3 (ipykernel)"}},"cells":[{"metadata":{},"source":"## Welcome to your notebook.\\n","cell_type":"markdown"},{"metadata":{},"source":"#### Run this cell to connect to your GIS and get started:","cell_type":"markdown"},{"outputs":[{"output_type":"stream","name":"stderr","text":"/opt/conda/lib/python3.7/site-packages/arcgis/gis/__init__.py:575: UserWarning:\\n\\nYou are logged on as andrew with an administrator role, proceed with caution.\\n\\n"}],"metadata":{"trusted":false},"execution_count":1,"source":"from arcgis.gis import GIS\\ngis = GIS(\\"home\\")","cell_type":"code"},{"metadata":{},"source":"#### Now you are ready to start!","cell_type":"markdown"},{"outputs":[{"output_type":"stream","name":"stdout","text":"<User username:andrew>\\n"}],"metadata":{"trusted":false},"execution_count":2,"source":"print(gis.users.me)","cell_type":"code"},{"outputs":[{"output_type":"stream","name":"stdout","text":"I\'m finished\\n"}],"metadata":{"trusted":true},"execution_count":1,"source":"output = \\"I\'m finished\\"\\nprint(output)","cell_type":"code"},{"outputs":[],"metadata":{"trusted":true},"execution_count":null,"source":"","cell_type":"code"}],"nbformat":4}'


class TestNotebookService(unittest.TestCase):
    """
    Tests the Services Manager and Service class for notebook server
    """

    def test_get_services_manager(self):
        """tests that the snapshot manager is returned."""
        servers = gis.admin.servers.list()
        for s in servers:
            if type(s).__name__ == "NotebookServer":
                nbs = s
                mgr = nbs.notebooks.services
                assert mgr
                assert mgr.properties
                assert isinstance(mgr.services, (tuple, list))
                assert isinstance(mgr.types, dict)
                break

    def test_services_add_ops(self):
        """tests the create notebook service tool"""
        nb_item = gis.content.add(
            item_properties={'type': "Notebook", "title": "nb_title", "text": json_data}
        )
        servers = gis.admin.servers.list()
        for s in servers:
            if type(s).__name__ == "NotebookServer":
                nbs = s
                mgr = nbs.notebooks.services
                item_tool = mgr.create(nb_item, "title", "description")
                assert item_tool
                assert mgr.services
                if len(mgr.services) > 0:
                    for s in mgr.services:
                        assert s.properties
                assert nb_item.delete()
                assert item_tool.delete()
                break


if __name__ == "__main__":
    unittest.main()

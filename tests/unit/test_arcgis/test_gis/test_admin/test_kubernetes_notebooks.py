
import types
import sys

from arcgis.gis.kubernetes._admin.notebooks._snapshot import KubeSnapShot, KubeSnapshotManager
from arcgis.gis.kubernetes._admin.notebooks._dataaccess import KubeNotebookFile



from unittest.mock import MagicMock, patch


class MockGIS:
    def __init__(self):
        self._con = types.SimpleNamespace()
        self._con.get = lambda url, params=None: {"notebooks": [], "runtimes": []}
        self._con.post = lambda url, params, try_json=True: {"status": "success", "snapshots": []}
        self._is_arcgisonline = False
        self._is_kubernetes = True
        self.session = types.SimpleNamespace()
        self.session.post = lambda url, params: types.SimpleNamespace(json=lambda: {"status": "success"})
        self._con.token = "dummy"

class TestKubernetesNotebooks(unittest.TestCase):

            
    def test_kubesnapshot_methods(self):
        # Patch the class to look like arcgis.gis.Item
        with patch("arcgis.gis.Item", create=True):
            item = MagicMock()
            item.id = "item123"
            item.type = "Notebook"
            item.itemid = "item123"
            item.__class__ = sys.modules["arcgis.gis"].Item  # Fakes the type check
            sm = KubeSnapshotManager(url="http://dummy/snapshots", gis=MockGIS())
            props = {"properties": {"name": "snap1"}, "resourceKey": "rk1"}
            snap = KubeSnapShot(item, sm, props)
            self.assertEqual(str(snap), "<SnapShot snap1>")
            self.assertEqual(repr(snap), "<SnapShot snap1>")

    def test_kubenotebookfile_methods(self):
        class MockDA:
            def __init__(self):
                self._gis = MockGIS()
                self._url = "http://dummy"
                self._username = "user"
            def _download(self, filename):
                return f"/tmp/{filename}"
            def _delete(self, filename):
                return True
        da = MockDA()
        definition = {"name": "file1", "Name": "file1"}
        file = KubeNotebookFile(definition, da)
        self.assertEqual(str(file), "<NotebookFile file=file1>")
        self.assertEqual(file.properties["name"], "file1")
        self.assertTrue(file.rename("file2"))
        self.assertEqual(file.download(), "/tmp/file1")
        self.assertTrue(file.erase())
        self.assertTrue(file.delete())

if __name__ == "__main__":
    unittest.main()
import types

from arcgis.gis.kubernetes._admin.notebooks._snapshot import KubeSnapShot, KubeSnapshotManager
from arcgis.gis.kubernetes._admin.notebooks._dataaccess import KubeNotebookFile
# Mocks for arcgis.gis.Item and GIS
class MockItem:
    def __init__(self, id="item123", type="Notebook"):
        self.id = id
        self.type = type
        self.itemid = id

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

# Test for _snapshot.py
def test_kubesnapshot_methods():
    item = MockItem()
    sm = KubeSnapshotManager(url="http://dummy/snapshots", gis=MockGIS())
    props = {"properties": {"name": "snap1"}, "resourceKey": "rk1"}
    snap = KubeSnapShot(item, sm, props)
    assert str(snap) == "<SnapShot snap1>"
    assert repr(snap) == "<SnapShot snap1>"
    assert snap.download() == "success"
    assert snap.save_as_item("newtitle") == "success"
    assert snap.restore() == "success"
    assert snap.delete() is True

def test_kubesnapshotmanager_methods():
    item = MockItem()
    sm = KubeSnapshotManager(url="http://dummy/snapshots", gis=MockGIS())
    assert isinstance(sm.properties, dict)
    assert sm._convert(item, "rk1", "title") == "success"
    assert sm._download(item, "rk1") == "success"
    assert sm.create(item, "snap", "desc") == "success"
    assert sm.list(item) == []
    assert sm._restore(item, "rk1") == "success"
    assert sm._delete(item, "rk1") == "success"

# Test for _dataaccess.py


def test_kubenotebookfile_methods():
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
    assert str(file) == "<NotebookFile file=file1>"
    assert file.properties["name"] == "file1"
    assert file.rename("file2") is True
    assert file.download() == "/tmp/file1"
    assert file.erase() is True
    assert file.delete() is True

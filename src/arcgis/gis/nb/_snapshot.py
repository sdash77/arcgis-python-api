import os
import json
from collections import namedtuple
from arcgis.gis import GIS, Item
from arcgis._impl.common._mixins import PropertyMap

###########################################################################
class SnapShotManager(object):
    """
    Allows for management and creation of save points for Notebooks.
    """
    _gis = None
    _url = None
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis):
        self._url = url
        self._gis = gis
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """returns the properties of the endpoint"""
        if self._properties is None:
            res = self._gis._con.get(self._url, {'f' : 'json'})
            self._properties = PropertyMap(res)
        return self._properties
    #----------------------------------------------------------------------
    def convert(self, item, snapshot, title):
        """
        Converts a Snapshot to a new notebook.

        :returns: Item

        """
        if isinstance(item, Item) and item.type.lower() == 'notebook':
            url = f"{self._url}/convert"
            params = {
                "f" : "json",
                "itemId" : item.id,
                "resourceKey" : snapshot,
                "notebookTitle" : title
            }
            return self._gis._con.post(url, params)
        else:
            raise ValueError("`item` must be a Notebook")
    #----------------------------------------------------------------------
    def download(self, item, snapshot):
        """
        retrieves a snap shot locally on disk.
        """

        if isinstance(item, Item) and item.type.lower() == 'notebook':
            url = f"{self._url}/download"
            params = {
                "f" : "json",
                "itemId" : item,
                "resourceKey" : snapshot,
            }
            return self._gis._con.get(url, params)
        else:
            raise ValueError("`item` must be a Notebook")
    #----------------------------------------------------------------------
    def create(self, item, name, description=None, notebook_json=None, access=False):
        """
        Creates a Snapshot of a Given Item.

        {
        "snapshotResourceKey": "snapshot-51364a5a64424aa6bfd991401ac6f94c.json",
        "status": "success"
        }
        """
        if isinstance(item, Item) and item.type.lower() == 'notebook':
            params = {
                'f' : 'json',
                'itemId' : item.id,
                'name' : name,
                'description' : description or "",
                'notebookJSON' : notebook_json or "",
                'privateAccess' : access,
            }
            url = f"{self._url}/create"
            return self._gis._con.post(url, params)
        else:
            raise ValueError("`item` must be a Notebook")
    #----------------------------------------------------------------------
    def list(self, item):
        """
        Returns a list of SnapShots for a notebook item.

        :return: namedtuple of snapshot properties

        """
        if isinstance(item, Item) and item.type.lower() == 'notebook':
            params = {
                'f' : 'json',
                'itemId' : item.id,
            }
            url = f"{self._url}/list"
            res = self._gis._con.post(url, params)
            if 'status' in res and res['status'] == 'success' and len(res['snapshots']) > 0:
                snaptuple = namedtuple("SnapshotInfo", res['snapshots'][0])
                return [snaptuple(**snap) for snap in res['snapshots']]
            else:
                return []
        else:
            raise ValueError("`item` must be a Notebook")
    #----------------------------------------------------------------------
    def restore(self, item, snapshot, preserve=True, description=None):
        """restors the notebook to a previous state"""
        if isinstance(item, Item) and item.type.lower() == 'notebook':
            params = {
            "itemId" : item.id,
            "resourceKeys" : snapshot,
            "preserveAsSnapshot" : preserve,
            "description" : description or "",
            "f": "json"
            }
            url = f"{self._url}/restore"
            return self._gis._con.post(url, params)
        else:
            raise ValueError("`item` must be a Notebook")
    #----------------------------------------------------------------------
    def delete(self, item, snapshot):
        """deletes a snapshot associated with the notebook item"""
        if isinstance(item, Item) and item.type.lower() == 'notebook':
            params = {
            "itemId" : item.id,
            "resourceKeys" : snapshot,
            "f": "json"
            }
            url = f"{self._url}/delete"
            return self._gis._con.post(url, params)
        else:
            raise ValueError("`item` must be a Notebook")


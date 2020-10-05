import os
import json
from arcgis.gis import GIS, Item
from arcgis._impl.common._mixins import PropertyMap

class NotebookSnapShot(object):
    """

    """
    _item = None
    _url = None
    _properties = None
    _gis = None
    def __init__(self, url, item, gis):
        self._url = url
        self._item = item
        self._gis = gis

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
    def properties(self):
        """returns the properties of the endpoint"""
        if self._properties is None:
            res = self._gis._con.get(self._url, {'f' : 'json'})
            self._properties = PropertyMap(res)
        return self._properties
    #----------------------------------------------------------------------
    def _convert(self, item, key, title):
        """
        Converts a Snapshot to a new notebook.

        :returns: Item

        """
        if hasattr(item, 'id'):
            item = item.id
        url = f"{self._url}/convert"
        params = {
            "f" : "json",
            "itemId" : item,
            "resourceKey" : key,
            "notebookTitle" : title
        }
        return self._gis._con.post(url, params)
    #----------------------------------------------------------------------
    def _download(self, item, key):
        """
        retrieves a snap shot locally on disk.

        :return: string
        """
        url = f"{self._url}/download"
        params = {
            "f" : "json",
            "itemId" : item,
            "resourceKey" : key,
        }
        return self._gis._con.get(url, params)
    #----------------------------------------------------------------------
    def create(self, **kwargs):
        pass
    #----------------------------------------------------------------------
    def list(self, item):
        """returns a list of SnapShots for a notebook item"""
        if isinstance(item, Item) and item.type.lower() == 'notebook':

        else:
            raise ValueError("`item` must be a Notebook")
    #----------------------------------------------------------------------
    def _restore(self, **kwargs):
        """restors the notebook to a previous state"""
        pass
    def _delete(self, item, snapshot):
        """deletes a snapshot associated with the notebook item"""
        pass

#cf5d69ce23c84fa89c0b8f252ce6adfa
"""
Contains the base class that all server object inherit from.
"""
from __future__ import absolute_import
import json
from collections import OrderedDict
from urllib.request import HTTPError
from arcgis.gis._impl._con import Connection
from arcgis.gis import GIS
from arcgis._impl.common._isd import InsensitiveDict
###########################################################################
class KubeSecurity(object):
    """class most server object inherit from"""
    _con = None
    _url = None
    _json_dict = None
    _json = None
    _properties = None
    def __init__(self, url:str, gis:"GIS") -> "KubeSecurity":
        """class initializer"""
        self._url = url
        self._gis = gis
        self._con = gis._con
    #----------------------------------------------------------------------
    def _init(self, connection=None):
        """loads the properties into the class"""
        if connection is None:
            connection = self._con
        params = {"f":"json"}
        try:
            result = connection.get(path=self._url,
                                    params=params)
            if isinstance(result, dict):
                self._json_dict = result
                self._properties = InsensitiveDict(result)
            else:
                self._json_dict = {}
                self._properties = InsensitiveDict({})
        except HTTPError as err:
            raise RuntimeError(err)
        except:
            self._json_dict = {}
            self._properties = InsensitiveDict({})
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the object properties
        """
        if self._properties is None:
            self._init()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def url(self):
        """gets/sets the service url"""
        return self._url
    #----------------------------------------------------------------------
    @url.setter
    def url(self, value):
        """gets/sets the service url"""
        self._url = value
        self._refresh()
    #----------------------------------------------------------------------
    def _refresh(self):
        """reloads all the properties of a given service"""
        self._init()

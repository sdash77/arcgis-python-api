"""
Contains the base class that all portaladmin object inherit from.
"""
from __future__ import absolute_import
import json
from collections import OrderedDict
from ..connection import _ArcGISConnection
from ...gis import GIS
###########################################################################
class BasePortalAdmin(OrderedDict):
    _con = None
    _url = None
    _json_dict = None
    _json = None
    def __init__(self, url, gis=None, initialize=True, **kwargs):
        """class initializer"""
        super(BasePortalAdmin, self).__init__()
        self._url = url
        if isinstance(gis, _ArcGISConnection):
            self._con = gis
        elif isinstance(gis, GIS):
            self._gis = gis
            self._con = gis._con
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
        if initialize:
            self.init(connection=self._con)
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """loads the properties into the class"""
        if connection is None:
            connection = self._con
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                      not attr.startswith('_')]
        params = {"f":"json"}
        result = connection.get(path=self._url,
                                params=params)
        self._json_dict = result
        for k,v in result.items():
            if k in attributes:
                setattr(self, "_"+ k, v)
                self[k] = v
            else:
                self[k] = v
        self.__dict__.update(result)
    #----------------------------------------------------------------------
    @property
    def connection(self):
        """gets/sets the connection object"""
        return self._con
    #----------------------------------------------------------------------
    @connection.setter
    def connection(self, value):
        """gets/sets the connection object"""
        if isinstance(value, _ArcGISConnection):
            self._con = value
            self._gis = None
            self.refresh()
        elif isinstance(value, GIS):
            self._con = value._con
            self._gis = value
            self.refresh()
        else:
            raise ValueError(
                "connection must be of type GIS or _ArcGISConnection")
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
        self.refresh()
    #----------------------------------------------------------------------
    def __str__(self):
        if self._json_dict is None:
            self.init()
        val = self._json_dict
        if val is None:
            return "{}"
        return json.dumps(self._json_dict)
    #----------------------------------------------------------------------
    def __repr__(self):
        return "{classname}({data})".format(
            classname=self.__class__.__name__,
            data=self.__str__())
    #----------------------------------------------------------------------
    def __iter__(self):
        """creates iterable for classes properties"""
        for k,v in self._json_dict.items():
            yield k,v
    #----------------------------------------------------------------------
    def refresh(self):
        """reloads all the properties of a given service"""
        self.init()

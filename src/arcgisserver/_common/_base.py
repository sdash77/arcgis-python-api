"""
Contains the base class that all server object inherit from.
"""
from __future__ import absolute_import
import json
from collections import OrderedDict
from ._connection import ServerConnection
###########################################################################
class BaseServer(OrderedDict):
    _con = None
    _url = None
    _json_dict = None
    _json = None
    def __init__(self, url, connection=None, initialize=True, **kwargs):
        """class initializer"""
        super(BaseServer, self).__init__()
        self._url = url
        if isinstance(connection, ServerConnection):
            self._con = connection
        else:
            raise ValueError("connection must be of type SiteConnection")
        if initialize:
            self.init(connection)
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
        if isinstance(value, SiteConnection):
            self._con = value
            self.refresh()
        else:
            raise ValueError("connection must be of type SiteConnection")
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
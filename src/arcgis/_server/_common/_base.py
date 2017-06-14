"""
Contains the base class that all server object inherit from.
"""
from __future__ import absolute_import
import json
from collections import OrderedDict
from ._connection import ServerConnection
from ..._impl.common._mixins import PropertyMap
###########################################################################
class BaseServer(object):
    _con = None
    _url = None
    _json_dict = None
    _json = None
    _properties = None
    def __init__(self, url, connection=None, initialize=True, **kwargs):
        """class initializer"""
        super(BaseServer, self).__init__()
        self._url = url
        if isinstance(connection, ServerConnection):
            self._con = connection
        else:
            raise ValueError("connection must be of type SiteConnection")
        if initialize:
            self._init(connection)
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
                self._properties = PropertyMap(result)
            else:
                self._json_dict = {}
                self._properties = PropertyMap({})
        except:
            self._json_dict = {}
            self._properties = PropertyMap({})
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
    def __getattr__(self, name):
        """adds dot notation to any class"""
        if self._properties is None:
            self._init()
        try:
            return self._properties.__getitem__(name)
        except:
            for k,v in self._json_dict.items():
                if k.lower() == name.lower():
                    return v
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__,
                                                                        name))
    #----------------------------------------------------------------------
    def __getitem__(self, key):
        """helps make object function like a dictionary object"""
        try:
            return self._properties.__getitem__(key)
        except KeyError:
            for k,v in self._json_dict.items():
                if k.lower() == key.lower():
                    return v
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__,
                                                                        key))
        except:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__,
                                                                        key))
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
            self._init()
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
    def _refresh(self):
        """reloads all the properties of a given service"""
        self._init()

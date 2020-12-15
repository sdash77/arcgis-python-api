import json
from collections import OrderedDict
from urllib.request import HTTPError
from arcgis.gis._impl._con import Connection
from arcgis.gis import GIS
from arcgis._impl.common._mixins import PropertyMap

class KubeOrgSecurity(object):
    """"""
    def users(self):
        pass
    def groups(self):
        pass
class KubeOrgLicense():
    """"""
    ...
class KubeOrgFederation():
    """"""
    ...
class KubeOrganization():
    """A Single Kubernetes Organization"""
    _security = None
    _federation = None
    _license = None

    def __init__(self, url, gis=None, initialize=True, **kwargs):
        """class initializer"""
        if gis is None and 'connection' in kwargs:
            connection = kwargs['connection']
            gis = kwargs.pop('connection', None)
        self._url = url

        #gis = kwargs.pop('gis', None)
        if not gis is None and \
           isinstance(gis, GIS):
            gis = gis._portal.con

        if isinstance(gis, Connection):
            self._con = gis
        elif hasattr(gis, '_con'):
            self._gis = gis._con
        else:
            raise ValueError("gis must be of type Connection or GIS")
        if initialize:
            self._init(gis)
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
        except HTTPError as err:
            raise RuntimeError(err)
        except:
            self._json_dict = {}
            self._properties = PropertyMap({})
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
        self.refresh()
    #----------------------------------------------------------------------
    def _refresh(self):
        """reloads all the properties of a given service"""
        self._init()


    @property
    def security(self):
        if self._security is None:
            self._security = KubeOrgSecurity(url=f"{self._url}/security",
                                             gis=self._gis, initialize=False)
        pass

    @property
    def license(self):
        pass

    @property
    def federation(self):
        pass

class KubeOrganizations():
    """
    """
    _url = None
    _gis = None
    _properties = None

    _con = None
    _url = None
    _json_dict = None
    _json = None
    _properties = None
    def __init__(self, url, gis=None, initialize=True, **kwargs):
        """class initializer"""
        if gis is None and 'connection' in kwargs:
            connection = kwargs['connection']
            gis = kwargs.pop('connection', None)
        self._url = url

        #gis = kwargs.pop('gis', None)
        if not gis is None and \
           isinstance(gis, GIS):
            gis = gis._portal.con

        if isinstance(gis, Connection):
            self._con = gis
        elif hasattr(gis, '_con'):
            self._gis = gis._con
        else:
            raise ValueError("gis must be of type Connection or GIS")
        if initialize:
            self._init(gis)
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
        except HTTPError as err:
            raise RuntimeError(err)
        except:
            self._json_dict = {}
            self._properties = PropertyMap({})
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
        self.refresh()
    #----------------------------------------------------------------------
    def __iter__(self):
        """creates iterable for classes properties"""
        for k,v in self._json_dict.items():
            yield k,v
    #----------------------------------------------------------------------
    def _refresh(self):
        """reloads all the properties of a given service"""
        self._init()


    @property
    def orgs(self) -> tuple:
        """
        Returns a list of registerd organizations with the Kubernetes deployment

        :returns: tuple
        """
        return tuple([KubeOrganization(url=f"{self._url}/{org}",
                                 gis=self._gis)\
                for org in self.properties['organizations']])

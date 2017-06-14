"""
This provides access to a server and it's services for non administrative
functions.  This allows developers to access a REST service just like a
user/developer would.
"""
from __future__ import absolute_import
from six.moves.urllib_parse import urlparse
import json
from .._common import BaseServer
from .._service._layerfactory import Service
from .._common import ServerConnection
from ..._impl.common._mixins import PropertyMap
########################################################################
class Catalog(BaseServer):
    """This object represents an ArcGIS Server instance"""
    _url = None
    _con = None
    _json = None
    _json_dict = None
    _adminUrl = None
    _folders = None
    _services = None
    _currentVersion = None
    _location = None
    _currentFolder = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url=None, tokenurl=None,
                 username=None, password=None,
                 key_file=None, cert_file=None,
                 expiration=60, all_ssl=True,
                 referer=None, proxy_host=None,
                 proxy_port=None, portal_connection=None,
                 initialize=True, **kwargs):
        """Constructor"""
        self._pc = portal_connection
        self._is_agol = kwargs.pop('is_agol', False)
        if url.lower().find('arcgis.com') > -1:
            self._is_agol = True
        self._url = self._validateurl(url=url)
        if (username and password) or \
           (key_file and cert_file) or \
           portal_connection:
            self._adminUrl = self._validateAdminUrl(url=url)
        con = ServerConnection(baseurl=self._url,
                                tokenurl=tokenurl,
                                username=username,
                                password=password,
                                key_file=key_file,
                                cert_file=cert_file,
                                expiration=expiration,
                                all_ssl=all_ssl,
                                referer=referer,
                                proxy_host=proxy_host,
                                proxy_port=proxy_port,
                                portal_connection=portal_connection)

        super(Catalog, self).__init__(url=self._url,
                                     connection=con,
                                     initialize=initialize)
        self._con = con
        self._location = self._url
        self._currentFolder = "root"
        if initialize:
            self._init(self._con)
    #----------------------------------------------------------------------
    def _validateAdminUrl(self, url):
        """assembles the admin url"""
        parsed = urlparse(url)
        if self._is_agol == False:
            parts = parsed.path[1:].split('/')
            if len(parts) == 0:
                return "%s://%s/arcgis/admin" % (parsed.scheme, parsed.netloc)
            elif len(parts) > 0:
                return "%s://%s/%s/admin" % (parsed.scheme, parsed.netloc, parts[0])
        else:
            parts = parsed.path[1:].split('/')
            return "%s://%s/%s/ArcGIS/rest/services" % (parsed.scheme, parsed.netloc, parts[0])
    #----------------------------------------------------------------------
    def _validateurl(self, url):
        """assembles the server url"""
        parsed = urlparse(url)
        if self._is_agol == False:
            parts = parsed.path[1:].split('/')
            if len(parts) == 0:
                return "%s://%s/arcgis/rest/services" % (parsed.scheme, parsed.netloc)
            elif len(parts) > 0:
                return "%s://%s/%s/rest/services" % (parsed.scheme, parsed.netloc, parts[0])
        else:
            parts = parsed.path[1:].split('/')
            if len(parts) == 0:
                res = self._con.get("portals/self", {"f": "json"})
                return "%s://%s/%s/ArcGIS/rest/services" % ( parsed.scheme,
                                                             parsed.netloc,
                                                             res['id'])
            return "%s://%s/%s/ArcGIS/rest/services" % (parsed.scheme, parsed.netloc, parts[0])
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
    def _init(self, connection=None, folder='root'):
        """loads the property data into the class"""
        params = {
            "f" : "json"
        }
        if folder == "root":
            url = self.root
        else:
            url = self.location
        if connection is None:
            connection = self._con
        missing = {}
        json_dict = connection.get(path=url, params=params)
        self._json_dict = json_dict
        self._json = json.dumps(json_dict)
        try:
            if isinstance(json_dict, dict):
                self._json_dict = result
                self._properties = PropertyMap(json_dict)
            else:
                self._json_dict = {}
                self._properties = PropertyMap({})
        except:
            self._json_dict = {}
            self._properties = PropertyMap({})
        for k,v in json_dict.items():
            if k == 'folders':
                v.insert(0, 'root')
                setattr(self, "_"+ k, v)
        self.__dict__.update(missing)
    #----------------------------------------------------------------------
    def find(self, service_name, folder=None):
        """
        finds a service based on it's name in a given folder
        """
        from six.moves.urllib_parse import quote
        c_folder = self.folder

        params = {
            "f" : "json"
        }
        self.folder = folder
        url = self.location
        connection = self._con
        missing = {}
        json_dict = connection.get(path=url,
                                   params=params)
        if 'services' in json_dict:
            for v in json_dict['services']:
                print(v)
                if v['name'].lower().replace(self.folder.lower() + "/", '') == service_name.lower():
                    url = "{base}/{name}/{stype}".format(base=self._url,
                                                         name=quote(v['name']),
                                                         stype=v['type'])
                    self.folder = c_folder
                    return Service(url=url, server=self)
                del v
        self.folder = c_folder
        return None
    #----------------------------------------------------------------------
    @property
    def root(self):
        """gets the url of the class"""
        return self._url
    #----------------------------------------------------------------------
    @property
    def site_manager(self):
        """points to the adminstrative side of ArcGIS Server"""
        if self._is_agol == False:
            from ..admin.administration import SiteManager
            if self._adminUrl:
                return SiteManager(connection=self._con,
                               url=self._adminUrl,
                               initialize=False)
            return None
    #----------------------------------------------------------------------
    @property
    def location(self):
        """returns the current url position in the server folder structure"""
        return self._location
    #----------------------------------------------------------------------
    @property
    def current_version(self):
        """gets the current version of arcgis server"""
        if self._currentVersion is None:
            self._init()
        return self._currentVersion or getattr(self, 'currentVersion', None)
    #----------------------------------------------------------------------
    @property
    def user(self):
        """gets the logged in user"""
        if self._is_agol == False:
            params = {"f" : "json"}
            url = "%s/self" % self.root.replace("/services", "")
            return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    @property
    def info(self):
        """gets the site's information"""
        params = {"f" : "json"}
        url = "%s/info" % self.root.replace("/services", "")
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    @property
    def services(self):
        """gets the services in the current folder"""
        from six.moves.urllib_parse import quote
        services = []
        if self._services is None:
            self._init()
        for s in self._services:
            url = "{base}/{name}/{stype}".format(base=self._url,
                                                 name=quote(s['name']),
                                                 stype=s['type'])

            services.append(Service(url=url, server=self))
        return services
    #----------------------------------------------------------------------
    @property
    def folders(self):
        """returns the folders on server"""
        if self._folders is None:
            self._init(folder="root")
        return self._folders
    #----------------------------------------------------------------------
    @property
    def folder(self):
        """gets/sets the current folder name"""
        return self._currentFolder
    #----------------------------------------------------------------------
    @folder.setter
    def folder(self, value):
        """gets/sets the current folder name"""
        lfolders = [f.lower() for f in self.folders]
        if value in self.folders:
            if value.lower() not in ['root', '/', ''] and \
               value.lower() in [f.lower() for f in self._folders]:
                value = self._folders[lfolders.index(value.lower())]
                self._currentFolder = value
                self._location = "%s/%s" % (self.root, value)
            else:
                self._currentFolder = 'root'
                self._location = self.root
            self._init(folder=value)
        elif value is None:
            self._currentFolder = 'root'
            self._location = self.root
            self._init(folder='root')
        elif value in ['/', '', 'root']:
            self._currentFolder = value
            self._location = "%s/%s" % (self.root, value)
            self._init(folder='root')


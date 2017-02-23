"""
This provides access to a server and it's services for non administrative
functions.  This allows developers to access a REST service just like a
user/developer would.
"""
from __future__ import absolute_import
from six.moves.urllib_parse import urlparse
import json
from .._common import BaseServer
from .._service._layerfactory import Layer
from .._common import ServerConnection
########################################################################
class ServerManager(BaseServer):
    """This object represents an ArcGIS Server instance"""
    _url = None
    _con = None
    _json = None
    _json_dict = None
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
                 initialize=True):
        """Constructor"""

        self._url = self._validateurl(url=url)

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

        super(ServerManager, self).__init__(url=self._url,
                                     connection=con,
                                     initialize=initialize)
        self._con = con
        self._location = self._url
        self._currentFolder = "root"
        if initialize:
            self.init(self._con)
    #----------------------------------------------------------------------
    def _validateurl(self, url):
        """assembles the server url"""
        parsed = urlparse(url)
        parts = parsed.path[1:].split('/')
        if len(parts) == 0:
            self._adminUrl = "%s://%s/arcgis/admin" % (parsed.scheme, parsed.netloc)
            return "%s://%s/arcgis/rest/services" % (parsed.scheme, parsed.netloc)
        elif len(parts) > 0:
            self._adminUrl = "%s://%s/%s/admin" % (parsed.scheme, parsed.netloc, parts[0])
            return "%s://%s/%s/rest/services" % (parsed.scheme, parsed.netloc, parts[0])
    #----------------------------------------------------------------------
    def init(self, connection=None, folder='root'):
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
        attributes = [attr for attr in dir(self)
                      if not attr.startswith('__') and \
                      not attr.startswith('_')]
        for k,v in json_dict.items():
            if k == "folders":
                pass
            elif k in attributes:
                setattr(self, "_"+ k, json_dict[k])
            else:
                missing[k] = v
                setattr(self, k,v)
        json_dict = connection.get(path=self.root,
                                 params=params)
        for k,v in json_dict.items():
            if k == 'folders':
                v.insert(0, 'root')
                setattr(self, "_"+ k, v)
        self.__dict__.update(missing)
    #----------------------------------------------------------------------
    @property
    def root(self):
        """gets the url of the class"""
        return self._url
    #----------------------------------------------------------------------
    @property
    def site_manager(self):
        """points to the adminstrative side of ArcGIS Server"""
        from ..admin.administration import SiteManager
        return SiteManager(connection=self._con,
                           url=self._adminUrl,
                           initialize=False)
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
            self.init()
        return self._currentVersion
    #----------------------------------------------------------------------
    @property
    def user(self):
        """gets the logged in user"""
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
        services = []
        if self._services is None:
            self.init()
        for s in self._services:
            url = "{base}/{name}/{stype}".format(base=self._url,
                                                 name=s['name'],
                                                 stype=s['type'])
            services.append(Layer(url=url, server=self))
        return services
    #----------------------------------------------------------------------
    @property
    def folders(self):
        """returns the folders on server"""
        if self._folders is None:
            self.init(folder="root")
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
            self.init(folder=value)
        elif value is None:
            self._currentFolder = 'root'
            self._location = self.root
            self.init(folder='root')
        elif value in ['/', '', 'root']:
            self._currentFolder = value
            self._location = "%s/%s" % (self.root, value)
            self.init(folder='root')


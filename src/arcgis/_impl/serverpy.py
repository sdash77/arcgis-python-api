from __future__ import absolute_import
import json
import tempfile
from six.moves.urllib_parse import urlparse
from .connection import _ArcGISConnection
from .server.ags.catalog import Catalog
from .server.manage.administration import AGSAdministration
class Server(object):
    """
    Controls and managers ArcGIS Server
    """
    _portal_connection = None
    _username = None
    _password = None
    _url = None
    _key_file = None
    _cert_file = None
    _expiration = 60
    _referer = None
    _proxy_host = None
    _proxy_port = None
    _connection = None
    _workdir = None
    _version = None
    _admin_url = None
    _catalog_url = None
    _catalog = None
    _administration = None
    #----------------------------------------------------------------------
    def __init__(self, url, tokenurl=None,
                 username=None,
                 password=None, key_file=None,
                 cert_file=None, expiration=60,
                 referer=None, proxy_host=None,
                 proxy_port=None, connection=None,
                 portal_connection=None,
                 workdir=tempfile.gettempdir()):
        """initializer"""
        self._url = url
        self._validate_url(url)
        self._tokenurl = tokenurl
        self._username = username
        self._password = password
        self._key_file = key_file
        self._cert_file = cert_file
        self._expiration = expiration
        self._referer = referer
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        self._connection = connection
        self._workdir = workdir
        self._portal_connection = portal_connection
        if connection is None:
            self._connection = _ArcGISConnection(baseurl=self._url,
                                                 tokenurl=tokenurl,
                                                 username=username,
                                                 password=password,
                                                 key_file=key_file,
                                                 cert_file=cert_file,
                                                 expiration=expiration,
                                                 all_ssl=True,
                                                 referer=referer,
                                                 proxy_host=proxy_host,
                                                 proxy_port=proxy_port,
                                                 connection=portal_connection)
        else:
            self._connection = connection
        self.site_info
    #----------------------------------------------------------------------
    @property
    def is_federated(self):
        return self._connection.product == "FEDERATED_SERVER"
    #----------------------------------------------------------------------
    def _validate_url(self, url):
        """"""
        parsed = urlparse(url)
        scheme = parsed.scheme
        netloc = parsed.netloc
        if len(parsed.path) > 0:
            path = parsed.path[1:].split("/")[0]
        else:
            path = ""
        if len(path) > 0:
            self._catalog_url = "{scheme}://{netloc}/{path}/rest".format(scheme=scheme,
                                                                            netloc=netloc,
                                                                            path=path)
            self._admin_url = "{scheme}://{netloc}/{path}/admin".format(scheme=scheme,
                                                                            netloc=netloc,
                                                                            path=path)
        else:
            self._catalog_url = "{scheme}://{netloc}/{path}/rest".format(scheme=scheme,
                                                                       netloc=netloc,
                                                                       path="arcgis")
            self._admin_url = "{scheme}://{netloc}/{path}/admin".format(scheme=scheme,
                                                                          netloc=netloc,
                                                                          path="arcgis")
    #----------------------------------------------------------------------
    @property
    def site_info(self):
        """gets the site's information"""
        if self._catalog_url is None:
            self._validate_url(url=self._url)
        url = self._catalog_url + "/info"
        return self._connection.get(path=url, try_json=True)
    #----------------------------------------------------------------------
    def login(self):
        """creates a connection class if none is provided."""
        if self._connection is None:
            self._connection = _ArcGISConnection(baseurl=self._url,
                                                 username=self._username,
                                                 password=self._password,
                                                 key_file=self._key_file,
                                                 cert_file=self._cert_file,
                                                 expiration=self._expiration,
                                                 all_ssl=True,
                                                 referer=self._referer,
                                                 proxy_host=self._proxy_host,
                                                 proxy_port=self._proxy_port,
                                                 connection=self._portal_connection)
        return self._connection
    #----------------------------------------------------------------------
    def logout(self):
        """deletes the connection class"""
        self._connection = None
    #----------------------------------------------------------------------
    @property
    def catalog(self):
        """Represents the User View of the Server"""
        return Catalog(url=self._catalog_url,
                       connection=self._connection,
                       initialize=False)
    #---------- ------------------------------------------------------------
    @property
    def administration(self):
        """Allows an administrator to manage and control services on a given site."""
        return AGSAdministration(url=self._admin_url,
                                 connection=self._connection)
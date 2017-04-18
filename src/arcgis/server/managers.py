"""
   Front end controls to the server.
"""
import ssl
from ._view import Catalog
from .admin.administration import SiteManager

########################################################################
class Server(object):
    """
    Gains Access to the ArcGIS REST API
    """
    _url = None
    _con =  None
    _adminUrl = None
    _server = None
    _sm = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url=None,
                 tokenurl=None,
                 username=None,
                 password=None,
                 verify_cert=False,
                 gis=None,
                 **kwargs):
        """Constructor"""
        if verify_cert == False:
            ssl._create_default_https_context = ssl._create_unverified_context
        key_file = kwargs.pop('key_file', None)
        cert_file = kwargs.pop('cert_file', None)
        expiration = kwargs.pop('expiration', 60)
        all_ssl = kwargs.pop('all_ssl', None)
        is_agol = kwargs.pop('is_agol', False)
        if url.lower().find("arcgis.com") > -1:
            is_agol = True
        if all_ssl is None:
            from six.moves.urllib_parse import urlparse
            all_ssl = urlparse(url).scheme == "https"
        referer = kwargs.pop('referer', None)
        proxy_host = kwargs.pop('proxy_host', None)
        proxy_port= kwargs.pop('proxy_port', None)
        initialize = kwargs.pop('initialize', None)
        self._server = Catalog(url,
                               tokenurl,
                               username,
                               password,
                               key_file,
                               cert_file,
                               expiration,
                               all_ssl,
                               referer,
                               proxy_host,
                               proxy_port,
                               gis,
                               initialize,
                               is_agol=is_agol)
        self._con = self._server.connection
        if is_agol == False:
            self._sm = self._server.site_manager
            self._info = self._server.info
    #----------------------------------------------------------------------
    @property
    def connection(self):
        """gets server the connection object"""
        return self._server.connection
    #----------------------------------------------------------------------
    @property
    def users(self):
        """returns operations to work with users"""
        if self._sm:
            from ._server import UserManager
            return UserManager(self._sm)
    #----------------------------------------------------------------------
    @property
    def datastore(self):
        """
        This resource provides information about the data holdings of the
        server. Data items are used by ArcGIS for Desktop and other clients
        to validate data paths referenced by GIS services.
        You can register new data items with the server by using the
        Register Data Item operation. Use the Find Data Items operation to
        search through the hierarchy of data items.
        A relational data store type represents a database platform that
        has been registered for use on a portal's hosting server by the
        ArcGIS Server administrator. Each relational data store type
        describes the properties ArcGIS Server requires in order to connect
        to an instance of a database for a particular platform. At least
        one registered relational data store type is required before client
        applications such as Insights for ArcGIS can create Relational
        Database Connection portal items.
        The Compute Ref Count operation counts and lists all references to
        a specific data item. This operation helps you determine if a
        particular data item can be safely deleted or refreshed."""
        if self._sm:
            return self._sm.data
    #----------------------------------------------------------------------
    @property
    def usage(self):
        """
        This resource is a collection of all the usage reports created
        within your site. The Create Usage Report operation lets you define
        a new usage report.
        """
        if self._sm:
            return self._sm.usagereports
    #----------------------------------------------------------------------
    @property
    def catalog(self):
        """
        The content resource is the root node and initial entry point into
        an ArcGIS Server host. This resource represents a catalog of
        folders and services published on the host.
        """
        return self._server
    #----------------------------------------------------------------------
    @property
    def machines(self):
        """
        This resource represents a collection of all the server machines that
        have been registered with the site. It other words, it represents
        the total computing power of your site. A site will continue to run
        as long as there is one server machine online.
        For a server machine to start hosting GIS services, it must be
        grouped (or clustered). When you create a new site, a cluster called
        'default' is created for you.
        The list of server machines in your site can be dynamic. You can
        register additional server machines when you need to increase the
        computing power of your site or unregister them if you no longer
        need them.
        """
        if self._sm:
            return self._sm.machines
        return

    #----------------------------------------------------------------------
    @property
    def data(self):
        """
        This resource provides information about the data holdings of the
        server. Data items are used by ArcGIS for Desktop and other clients
        to validate data paths referenced by GIS services.
        You can register new data items with the server by using the
        Register Data Item operation. Use the Find Data Items operation to
        search through the hierarchy of data items.
        A relational data store type represents a database platform that
        has been registered for use on a portal's hosting server by the
        ArcGIS Server administrator. Each relational data store type
        describes the properties ArcGIS Server requires in order to connect
        to an instance of a database for a particular platform. At least
        one registered relational data store type is required before client
        applications such as Insights for ArcGIS can create Relational
        Database Connection portal items.
        The Compute Ref Count operation counts and lists all references to
        a specific data item. This operation helps you determine if a
        particular data item can be safely deleted or refreshed.
        """
        if self._sm:
            return self._sm.data
    #----------------------------------------------------------------------
    @property
    def logs(self):
        """
        This allows users to access the  ArcGIS Server's logs and lets
        administrators query and find errors and/or problems related to
        the server or a service.

        Logs are the records written by the various components of ArcGIS
        Server. You can query the logs and change various log settings.
        **Note**
        ArcGIS Server Only
        """
        if self._sm:
            return self._sm.logs
    #----------------------------------------------------------------------
    @property
    def kml(self):
        """
        This resource is a container for all the KMZ files created on the
        server.
        """
        if self._sm:
            return self._sm.kml
    #----------------------------------------------------------------------
    @property
    def me(self):
        """
        returns the current logged in username
        """
        if self._sm:
            from ._server import User
            res = self.users.search(self._sm.info._loggedInUser)
            if len(res) > 0:
                return res[0]
            else:
                return self._sm.info._loggedInUser
        else:
            return self._con._username
    #----------------------------------------------------------------------
    @property
    def info(self):
        """

        A read-only resource that returns meta information about the server
        """
        if self._sm:
            return self._sm.info
    #----------------------------------------------------------------------
    @property
    def system(self):
        """
        provides access to common system configuration settings
        """
        if self._sm:
            from ._server import SystemManager
            return SystemManager(self._sm)

    #----------------------------------------------------------------------
    @property
    def services(self):
        """
        Provides administrator access to the services on ArcGIS Server as a
        ServerManager Object.
        """
        if self._sm:
            return self._sm.services

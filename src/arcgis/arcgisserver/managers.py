"""
   Front end controls to the server.
"""
from ._view import Server
from .admin.administration import SiteManager
########################################################################
class ServerManager(object):
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
                 url=None, tokenurl=None,
                 username=None, password=None,
                 key_file=None, cert_file=None,
                 expiration=60, all_ssl=True,
                 referer=None, proxy_host=None,
                 proxy_port=None, portal_connection=None,
                 initialize=True):
        """Constructor"""
        self._server = Server(url,
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
                              portal_connection,
                              initialize)
        self._sm = self._server.site_manager
        self._info = self._server.info
    #----------------------------------------------------------------------
    @property
    def users(self):
        """returns operations to work with users"""
        return self._sm.security
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
        return self._sm.data
    #----------------------------------------------------------------------
    @property
    def usage(self):
        """
        This resource is a collection of all the usage reports created
        within your site. The Create Usage Report operation lets you define
        a new usage report.
        """
        return self._sm.usagereports
    #----------------------------------------------------------------------
    @property
    def content(self):
        """
        The content resource is the root node and initial entry point into
        an ArcGIS Server host. This resource represents a catalog of
        folders and services published on the host.
        """
        return self._server
    #----------------------------------------------------------------------
    @property
    def config(self):
        """
        TODO: This property will provide the ability to control and manipulate
        a Site's datastores.
        """
        return
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
        return self._sm.logs
    #----------------------------------------------------------------------
    @property
    def kml(self):
        """
        This resource is a container for all the KMZ files created on the
        server.
        """
        return self._sm.kml
    #----------------------------------------------------------------------
    @property
    def info(self):
        """

        A read-only resource that returns meta information about the server
        """
        return self._sm.info

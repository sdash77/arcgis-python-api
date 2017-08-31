import arcgis
from arcgis import gis
from .admin.administration import Server
import logging
_log = logging.getLogger(__name__)
###########################################################################
class ServerManager(object):
    """
    ServerManager is a set of tools to work with your WebGIS that allows
    administrators to federate, unfederate and manage ArcGIS Servers.

    Parameters:
     :param gis: on-premise GIS object
    """
    _gis = None
    _catalog_list = None
    _server_list = None
    _portal = None
    _gis = None
    _pa = None
    _federation = None

    #----------------------------------------------------------------------
    def __init__(self, gis):
        self._gis = gis
        self._portal = gis._portal
        self._pa = gis.admin
        self._federation = self._pa.federation
        self._server_list = None
        self._catalog_list = None
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._pa._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._pa._url)
    #----------------------------------------------------------------------
    def list(self):
        """gets all servers in a GIS"""
        from . import Catalog
        if self._server_list is not None:
            return self._server_list

        self._server_list = []
        self._catalog_list = []
        res = self._portal.con.post("portals/self/servers", {"f": "json"})
        servers = res['servers']
        admin_url = None
        for server in servers:
            try:
                admin_url = server['adminUrl']
                c = Catalog(url=admin_url, portal_connection=self._gis._portal.con)
                self._server_list.append(c.admin)
                self._catalog_list.append(c)
            except:
                _log.warn("Could not access the server at " + admin_url)

        return self._server_list
    #----------------------------------------------------------------------
    def get(self, role=None, function=None):
        """
        returns a server(s) by role or function.

        Parameters:
        :param role: Whether the server is a hosting server for the portal,
        a federated server, or a server with restricted access to
        publishing. The allowed values are FEDERATED_SERVER,
        FEDERATED_SERVER_WITH_RESTRICTED_PUBLISHING, or HOSTING_SERVER.
        :param function: Server function associates a specific function
        with the server. It takes in a comma separated list of values. The
        allowed values are GeoAnalytics,RasterAnalytics, and ImageHosting.
        """
        servers = []
        if role is None and function is None:
            raise ValueError("A role or function must be provided")
        for server in self._federation.servers['servers']:
            if str(role).lower() == server['serverRole'].lower():
                servers.append(Server(url=server['adminUrl'], gis=self._gis))
            elif str(function).lower() in server['serverFunction'].lower():
                servers.append(Server(url=server['adminUrl'], gis=self._gis))
        return servers
    #----------------------------------------------------------------------
    @property
    def _server_info(self):
        """
        returns federation information for all servers associated the
        WebGIS
        """
        return self._federation.servers['servers']
    #----------------------------------------------------------------------
    def _federate(self,
                 url,
                 admin_url,
                 username,
                 password):
        """
        This operation enables ArcGIS Servers to be federated with Portal
        for ArcGIS.
        Parameters:
         :url: The URL of the GIS server used by external users when
          accessing the ArcGIS Server site. If the site includes the Web
          Adaptor, the URL includes the Web Adaptor address, for example,
          https://webadaptor.domain.com/arcgis. If you've added ArcGIS
          Server to your organization's reverse proxy server, the URL is
          the reverse proxy server address (for example,
          https://reverseproxy.domain.com/myorg). Note that the federation
          operation will perform a validation check to determine if the
          provided URL is accessible from the server site. If the resulting
          validation check fails, a warning will be generated in the Portal
          for ArcGIS logs. However, federation will not fail if the URL is
          not validated, as the URL may not be accessible from the server
          site, such as is the case when the server site is behind a
          firewall.
         :admin_url: The URL used for accessing ArcGIS Server when
          performing administrative operations on the internal network, for
          example, https://gisserver.domain.com:6443/arcgis.
         :username: The username of the primary site administrator account
         :password: password of the username above.
        Output:
         server response with server ID
        """
        res = self._federation.federate(url,
                                        admin_url,
                                        username,
                                        password)
        self._server_list = None
        return res
    #----------------------------------------------------------------------
    def _unfederate(self, server_id):
        """
        This operation unfederates an ArcGIS Server from Portal for ArcGIS.

        Parameters:
         :server_id: unique ID of the server
        """
        res = self._federation(server_id)
        self._server_list = None
        return res
    #----------------------------------------------------------------------
    def update(self, server, role, function=None):
        """
        This operation allows you to set an ArcGIS Server federated with
        Portal for ArcGIS as the hosting server or to enforce fine-grained
        access control to a federated server. You can also remove hosting
        server status from an ArcGIS Server. You can also remove hosting
        server status from an ArcGIS Server. To set a hosting server, an
        enterprise geodatabase must be registered as a managed database
        with the ArcGIS Server.

        Parameters:
         :param server: arcgis.gis.Server object
         :param role: Whether the server is a hosting server for the portal, a
          federated server, or a server with restricted access to
          publishing. The allowed values are:
           FEDERATED_SERVER, FEDERATED_SERVER_WITH_RESTRICTED_PUBLISHING,
           or HOSTING_SERVER.
         :param function: Function associates a specific function with the
         server. It takes in a comma separated list of values. The allowed
         values are GeoAnalytics,RasterAnalytics, and ImageHosting. Values
         can be comma separated but it is not recommend that a single
         server have all the server functions
        """
        if isinstance(server, Server) == False:
            raise ValueError("server must be of type arcgis.gis.Server")
        roles = ["FEDERATED_SERVER",
                 "FEDERATED_SERVER_WITH_RESTRICTED_PUBLISHING",
                 "HOSTING_SERVER"]
        functions = {
            "geoanalytics" : "GeoAnalytics",
            "rasteranalytics" : "RasterAnalytics",
            "imagehosting" : "ImageHosting",
            "none" : None
        }
        if not role.upper() in roles:
            raise ValueError("Invalid role, allowed values: %s" % ",".join(roles))
        if not str(function).lower() in functions.keys():
            raise ValueError("Invalid function, allowed values: %s" % ",".join(functions.keys()))
        else:
            function = functions[str(function).lower()]
        server_id = None
        from six.moves.urllib.parse import urlparse
        b = urlparse(url=server._admin_url).netloc.lower()
        for s in self._server_info:
            if b == urlparse(s['adminUrl'].lower()).netloc:
                server_id = s['id']
                break
            del s
        return self._federation.update(server_id, role, function)
    #----------------------------------------------------------------------
    def validate(self):
        """
        This operation returns information on the status of ArcGIS Servers
        registered with Portal for ArcGIS.

        Output: Boolean.  If false, there is an issue with 1 or more of the
        Federated Servers.  True means all servers are functioning as
        expected.
        """
        return self._federation.validate_all()['status'] == 'success'
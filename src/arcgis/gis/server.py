"""
A collection of classes for administering an ArcGIS Enterprise's server.
"""
import ssl
import logging
import arcgis
from .._impl.common._mixins import PropertyMap
from .._impl.connection import _ArcGISConnection
from .._impl._server._common import ServerConnection
from ..gis import GIS
from .._impl._server._view import Catalog
from .._impl._server.admin._logs import Log
from .._impl._server.admin._data import Datastore as AdminDataStore

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
    #----------------------------------------------------------------------
    def __init__(self, gis):
        self._gis = gis
        self._portal = gis._portal
        self._pa = gis.admin
        self._federation = self._pa.federation
        self._server_list = None
    #----------------------------------------------------------------------
    def list(self):
        """gets all servers in a GIS"""
        if self._server_list is not None:
            return self._server_list

        self._server_list = []

        res = self._portal.con.post("portals/self/servers", {"f": "json"})
        servers = res['servers']
        admin_url = None
        for server in servers:
            try:
                admin_url = server['adminUrl']
                self._server_list.append(Server(url=admin_url, gis=self._gis, info=server))
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
###########################################################################
class Server(object):
    """
    An ArcGIS Enterprise server used for hosting services

    Parameters:
    :param url: site url of the server
    :param tokenurl: optional URL for pointing to the server's token url
    :param username: name of login user
    :param password: password of login user
    :param verify_cert: boolean value, False means any invalid certificates
    will be ignored.  True means only valid certificates will be accepted.
    :param gis: if a server is federated, a GIS object should be given
    inorder to ensure that the Portal Security is used over server token.
    """
    _url = None
    _con =  None
    _admin_url = None
    _server = None
    _sm = None
    _servicemanager = None
    _systemmanager = None
    _logmanager = None
    _sitemanager = None
    _usermanager = None
    _datastoremanager = None
    _reportmanager = None
    _machinemanager = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url=None,
                 tokenurl=None,
                 username=None,
                 password=None,
                 verify_cert=False,
                 gis=None,
                 **kwargs):
        """An ArcGIS Enterprise server"""
        ### TODO: don't set unverified context
        if not verify_cert:
            ssl._create_default_https_context = ssl._create_unverified_context
        key_file = kwargs.pop('key_file', None)
        cert_file = kwargs.pop('cert_file', None)
        expiration = kwargs.pop('expiration', 60)
        all_ssl = kwargs.pop('all_ssl', None)
        is_agol = kwargs.pop('is_agol', False)
        info = kwargs.pop('info', None)
        if url.lower().find("arcgis.com") > -1:
            is_agol = True
        if all_ssl is None:
            from six.moves.urllib_parse import urlparse
            all_ssl = urlparse(url).scheme == "https"
        referer = kwargs.pop('referer', None)
        proxy_host = kwargs.pop('proxy_host', None)
        proxy_port= kwargs.pop('proxy_port', None)
        initialize = kwargs.pop('initialize', True)
        self._admin_url = url
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

        self._con = self._server._con
        if not is_agol:
            self._sm = self._server.site_manager
        if info:
            self.info = PropertyMap(info)
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._admin_url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._admin_url)
    #----------------------------------------------------------------------
    def _publish_sd(self,
                   sd_file,
                   folder=None):
        """
        publishes a service definition file to arcgis server
        """
        if sd_file.lower().endswith('.sd') == False:
            return False
        if self._sm:
            catalog = self._server
            if 'System' in catalog.folders:
                catalog.folder = 'System'
            else:
                return False
            service = catalog.find(service_name="PublishingTools",
                                   folder="System")
            if service is None:
                service = catalog.find(service_name="PublishingToolsEx",
                                       folder="System")
            if service is None:
                return False
            uploads = self._sm.uploads
            status, res = uploads.upload(path=sd_file, description="sd file")
            if status:
                uid = res['item']['itemID']
                res = service.publish_service_definition(in_sdp_id=uid)
                return True
            return False
        else:
            return False
    #----------------------------------------------------------------------
    @property
    def site(self):
        """
        A site is a collection of server resources. This collection
        includes server machines that are installed with ArcGIS Server,
        including GIS services, data and so on. The site resource also
        lists the current version of the software.
        When you install ArcGIS Server on a server machine for the first
        time, you must create a new site. Subsequently, newer server
        machines can join your site and increase its computing power. Once
        a site is no longer required, you can delete the site, which will
        cause all of the resources to be cleaned up.
        """
        if self._sm:
            if self._sitemanager is None:
                self._sitemanager = SiteManager(self._sm)
            return self._sitemanager
    #----------------------------------------------------------------------
    @property
    def users(self):
        """returns operations to work with users"""
        if self._sm:
            if self._usermanager is None:
                self._usermanager = UserManager(server=self._sm)
            return self._usermanager
    #----------------------------------------------------------------------
    @property
    def datastores(self):
        """
        This resource provides information about the data holdings of the
        _server. Data items are used by ArcGIS for Desktop and other clients
        to validate data paths referenced by GIS services.
        You can register new data items with the _server by using the
        Register Data Item operation. Use the Find Data Items operation to
        search through the hierarchy of data items.
        A relational data store type represents a database platform that
        has been registered for use on a portal's hosting _server by the
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
            if self._datastoremanager is None:
                self._datastoremanager = DataStoreManager(self._sm)
            return self._datastoremanager
    #----------------------------------------------------------------------
    @property
    def usage(self):
        """
        This resource is a collection of all the usage reports created
        within your site. The Create Usage Report operation lets you define
        a new usage report.
        """
        if self._sm:
            if self._reportmanager is None:
                self._reportmanager = ReportManager(self._sm)
            return self._reportmanager
    #----------------------------------------------------------------------
    @property
    def _catalog(self):
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
        This resource represents a collection of all the _server machines that
        have been registered with the site. It other words, it represents
        the total computing power of your site. A site will continue to run
        as long as there is one _server machine online.
        For a _server machine to start hosting GIS services, it must be
        grouped (or clustered). When you create a new site, a cluster called
        'default' is created for you.
        The list of _server machines in your site can be dynamic. You can
        register additional _server machines when you need to increase the
        computing power of your site or unregister them if you no longer
        need them.
        """
        if self._sm:
            if self._machinemanager is None:
                self._machinemanager = MachineManager(self._sm)
            return self._machinemanager
        return None

    #----------------------------------------------------------------------
    @property
    def _site(self):
        """
        The site maintains all its configuration and meta information on
        disk in a set of files that make up the Configuration Store.
        """
        if self._sm:
            return self._sm
    #----------------------------------------------------------------------
    @property
    def logs(self):
        """
        This allows users to access the  ArcGIS Server's logs and lets
        administrators query and find errors and/or problems related to
        the _server or a service.

        Logs are the records written by the various components of ArcGIS
        Server. You can query the logs and change various log settings.
        **Note**
        ArcGIS Server Only
        """
        if self._sm:
            if self._logmanager is None:
                self._logmanager = LogManager(self._sm)
            return self._logmanager
    #----------------------------------------------------------------------
    @property
    def _kml(self):
        """
        This resource is a container for all the KMZ files created on the
        _server.
        """
        if self._sm:
            return self._sm.kml
    #----------------------------------------------------------------------
    @property
    def _me(self):
        """
        returns the current logged in username
        """
        if self._sm:
            res = self.users.search(self._sm.info._loggedInUser)
            if len(res) > 0:
                return res[0]
            else:
                return self._sm.info._loggedInUser
        else:
            return self._con._username
    #----------------------------------------------------------------------
    @property
    def _info(self):
        """

        A read-only resource that returns meta information about the _server
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
            if self._systemmanager is None:
                self._systemmanager = SystemManager(self._sm)
            return self._systemmanager
    #----------------------------------------------------------------------
    @property
    def services(self):
        """
        Provides administrator access to the services on ArcGIS Server as a
        ServerManager Object.
        """
        if self._sm:
            if self._servicemanager is None:
                self._servicemanager = ServiceManager(self)
            return self._servicemanager
###########################################################################
class ServiceManager(object):
    """
    Helper class for managing services. This class is not created by users directly. An instance of this class,
    called 'services', is available as a property of the Server object. Users call methods on this 'services' object to
    managing services.
    """
    _currentFolder = None
    _services = None
    def __init__(self, server):
        self._svcmgr = server._sm.services
        self._server = server
        self._currentFolder = None

    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._svcmgr._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._svcmgr._url)

    @property
    def folders(self):
        """ returns a list of all folders """
        return self._svcmgr.folders

    def list(self, folder='/', refresh=False):
        """
        returns a list of services in the specified folder

        Parameters:
        :param folder: name of the folder to list services from
        :param refresh: Bool, default is False. If True, the list of services will be
        requested to the server, else the list will be returned from cache.
        """
        if folder != self._currentFolder or \
           self._services is None or refresh:
            self._currentFolder = folder
            self._svcmgr.folder = folder
            services =  self._svcmgr.services
            self._services = [Service(None, None, service=svc, svcmgr=self._svcmgr) for svc in services]
        return self._services

    def create_folder(self, folder, description=""):
        """
           Creates a unique folder
           Parameters:
            :param folder_name - name of folder
            :param description - describes the folder
           Output:
            result as dictionary
        """
        res = self._svcmgr.create_folder(folder, description)
        self._svcmgr._folders = None
        return res

    def delete_folder(self, folder):
        """
           Deletes a folder
           Parameters:
            :param folder - name of folder to remove
           Output:
            boolean
        """
        res = self._svcmgr.delete_folder(folder)
        self._svcmgr._folders = None
        return res

    def publish_sd(self, sd_file_path, folder=None):
        """
        Publishes a service definition file to the server
        :param sd_file_path: service defition file
        :param folder: optional folder name
        :return: True if published, False otherwise
        """
        self._services = None
        return self._server._publish_sd(sd_file_path, folder)

    def create_service(self, service):
        """
        Creates a new GIS service in the folder. A service is created by
        submitting a JSON representation of the service to this operation.

        The JSON representation of a service contains the following four
        sections:
         - Service Description Properties-Common properties that are shared
          by all service types. Typically, they identify a specific service.
         - Service Framework Properties-Properties targeted towards the
          framework that hosts the GIS service. They define the life cycle
          and load balancing of the service.
         - Service Type Properties -Properties targeted towards the core
          service type as seen by the server administrator. Since these
          properties are associated with a server object, they vary across
          the service types. The Service Types section in the Help
          describes the supported properties for each service.
         - Extension Properties-Represent the extensions that are enabled
          on the service. The Extension Types section in the Help describes
          the supported out-of-the-box extensions for each service type.
        Output:
        dictionary status message
        """
        self._services = None
        return self._svcmgr.create_service(service)

    def exists(self, folder_name, name=None, service_type=None):
        """
        This operation allows you to check whether a folder or a service
        exists. To test if a folder exists, supply only a folder_name. To
        test if a service exists in a root folder, supply both serviceName
        and service_type with folder_name=None. To test if a service exists
        in a folder, supply all three parameters.

        Parameters:
        :param folder_name - a folder name
        :param name - a service name
        :param service_type - a service type. Allowed values:
        GeometryServer | ImageServer | MapServer | GeocodeServer |
        GeoDataServer | GPServer | GlobeServer | SearchServer
        """
        return self._svcmgr.exists(folder_name, name, service_type)
########################################################################
class Service(object):
    """
    Represents a GIS administrative service

    Parameter:
    :param url: admin url of the service
    :param server: server object
    :param service: service object
    :param svcmgr: service manager object
    """
    _service = None
    _svcmgr = None

    def __init__(self, url, server, **kwargs):
        """initializer"""
        from .._impl.connection import _ArcGISConnection
        from .._impl._server._common import ServerConnection
        service = kwargs.pop('service', None)
        svcmgr = kwargs.pop('svcmgr', None)
        if service is not None:
            self._service = service
            self._svcmgr = svcmgr
        elif isinstance(server, (_ArcGISConnection, ServerConnection)):
            self._service = arcgis._impl._server.admin._services.Service(url, server)
        else:
            self._service = arcgis._impl._server.admin._services.Service(url, server._con)

        self._properties = PropertyMap(self._service._json_dict)

    @classmethod
    def _from_service(cls, service):
        return cls(None, None, service=service)

    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._service.url)

    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._service.url)

    @property
    def properties(self):
        """
        The properties of the Service
        """
        return self._properties

    def start(self):
        """Starts the service"""
        return self._service.start()

    def stop(self):
        """Stops the service"""
        return self._service.stop()

    def delete(self):
        """Deletes the service and return True if successful, False otherwise"""
        return self._service.delete()

    def edit(self, service):
        """
        To edit a service, you need to submit the complete JSON
        representation of the service, which includes the updates to the
        service properties. Editing a service causes the service to be
        restarted with updated properties.
        """
        return self._service.edit(service)

    @property
    def status(self):
        """Returns the status of the service """
        return self._service.status

    @property
    def statistics(self):
        """Returns the stats for the service """
        return self._service.statistics

    def rename(self, new_name):
        """Renames this service to the new name"""
        params = {
            "f": "json",
            "serviceName": self.properties.serviceName,
            "serviceType": self.properties.type,
            "serviceNewName": new_name
        }

        u_url = self._service._url[:self._service._url.rfind('/')] + "/renameService"

        res = self._service._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
########################################################################
class MachineManager(object):
    """
    This resource represents a collection of all the server machines that
    have been registered with the site. It other words, it represents the
    total computing power of your site. A site will continue to run as long
    as there is one server machine online.
    For a server machine to start hosting GIS services, it must be grouped
    (or clustered). When you create a new site, a cluster called 'default'
    is created for you.
    The list of server machines in your site can be dynamic. You can
    register additional server machines when you need to increase the
    computing power of your site or unregister them if you no longer need
    them.

    Parameters:
    :param server: server administration object
    """
    _machines = None
    _pm = None
    #----------------------------------------------------------------------
    def __init__(self, server, **kwargs):
        """Constructor"""
        hydrate = kwargs.pop('hydrate', False)
        self._sm = server
        self._machines = server.machines
        if hydrate:
            self._machines.properties
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._machines._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._machines._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the machine's properties
        """
        return self._machines.properties
    #----------------------------------------------------------------------
    def list(self):
        """
        returns the list of machines in the GIS
        """
        ms = []
        for m in self._machines.list:
            ms.append(Machine(machine=m))
        return ms
    #----------------------------------------------------------------------
    def get(self, name):
        """
        gets a single instance of a machine

        Parameters:
        :param name: name of the machine
        """
        return Machine(self._machines.get(machine_name=name))
    #----------------------------------------------------------------------
    def register(self, name, admin_url):
        """
           For a server machine to participate in a site, it needs to be
           registered with the site. The server machine must have ArcGIS
           Server software installed and authorized.
           Registering machines this way is a "pull" approach to growing
           the site and is a convenient way when a large number of machines
           need to be added to a site. In contrast, a server machine can
           choose to join a site.
           Parameters:
            :param name: - name of the server machine
            :param admin_url: - URL wher ethe Administrator API is running on the
                               server machine.
                               Example: http://<machineName>:6080/arcgis/admin
           Output:
              JSON message as dictionary
        """
        res = self._machines.register(name, admin_url)
        self._machines.init()
        return res
    #----------------------------------------------------------------------
    def rename(self, name, new_name):
        """
           You must use this operation if one of the registered machines
           has undergone a name change. This operation updates any
           references to the former machine configuration.
           By default, when the server is restarted, it is capable of
           identifying a name change and repairing itself and all its
           references. This operation is a manual call to handle the
           machine name change.
           Parameters:
            :param name: - The former name of the server machine that is
                          registered with the site.
            :param new_name: - The new name of the server machine.
           Output:
              JSON messages as dictionary
        """
        res = self._machines.rename(name, new_name)
        self._machines.init()
        return res
########################################################################
class Machine(object):
    """
       A server machine represents a machine on which ArcGIS Server
       software has been installed and licensed. A site is made up one or
       more of such machines that work together to host GIS services and
       data and provide administrative capabilities for the site. Each
       server machine is capable of performing all these tasks and hence a
       site can be thought of as a distributed peer-to-peer network of such
       machines.
       A server machine communicates with its peers over a range of TCP and
       UDP ports that can be configured using the edit operation. For a
       server machine to host GIS services, it needs to be added to a
       cluster. Starting and stopping the server machine enables and
       disables, respectively, its ability to host GIS services.
       The administrative capabilities of the server machine are available
       through the ArcGIS Server Administrator API that can be accessed
       over HTTP(S). For a server machine to participate in a site, it must
       be registered with the site. A machine can participate in only one
       site at a time. To remove a machine permanently from the site, you
       can use the unregister operation.

       Parameter:
       :param machine: Machine object
    """
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self, machine):
        """Constructor"""
        self._machine = machine
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._machine._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._machine._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        lists the machine's properties
        """
        return self._machine.properties
    #----------------------------------------------------------------------
    @property
    def status(self):
        """ returns the state """
        return self._machine.status
    #----------------------------------------------------------------------
    def start(self):
        """ Starts the server machine """
        return self._machine.start()
    #----------------------------------------------------------------------
    def stop(self):
        """ Stops the server machine """
        return self._machine.stop()
    #----------------------------------------------------------------------
    def unregister(self):
        """
           This operation causes the server machine to be deleted from the
           Site.
           The server machine will no longer participate in the site or run
           any of the GIS services. All resources that were acquired by the
           server machine (memory, files, and so forth) will be released.
           Typically, you should only invoke this operation if the machine
           is going to be shut down for extended periods of time or if it
           is being upgraded.
           Once a machine has been unregistered, you can create a new site
           or join an existing site.
        """
        return self._machine.unregister()
    #----------------------------------------------------------------------
    @property
    def ssl_certificates(self):
        """
        This resource lists all the certificates (self-signed and CA-signed)
        created for the server machine. The server securely stores these
        certificates inside a key store within the configuration store.
        Before you enable SSL on your server, you need to generate
        certificates and get them signed by a trusted certificate authority
        (CA). For your convenience, the server is capable of generating
        self-signed certificates that can be used during development or
        staging. However, it is critical that you get CA-signed
        certificates when standing up a production server.
        In order to get a certificate signed by a CA, you need to generate
        a CSR (certificate signing request) and then submit it to your CA.
        The CA will sign your certificate request which can then be
        imported into the server by using the import CA signed certificate
        operation.
        """
        return self._machine.ssl_certificates
    #----------------------------------------------------------------------
    def ssl_certificate(self, certificate):
        """
        A certificate represents a key pair that has been digitally signed
        and acknowledged by a Certifying Authority (CA). It is the most
        fundamental component in enabling SSL on your server.
        The Generate Certificate operation creates a new self-signed
        certificate and adds it to the keystore. In order for browsers and
        other HTTP client applications to trust the SSL connection on the
        server, this certificate must be digitally signed by a CA and then
        imported into the keystore. Even though a self-signed certificate
        can be used to enable SSL, it is recommended that you use a
        self-signed certificates only on staging or development servers.

        Parameters:
         :certificate: name of the certificate to grab information for
        """
        self._machine.ssl_certificate(certificate)
    #----------------------------------------------------------------------
    def export_certificate(self, certificate):
        """
        A certificate represents a key pair that has been digitally signed
        and acknowledged by a Certifying Authority (CA). It is the most
        fundamental component in enabling SSL on your server.
        The Generate Certificate operation creates a new self-signed
        certificate and adds it to the keystore. In order for browsers and
        other HTTP client applications to trust the SSL connection on the
        server, this certificate must be digitally signed by a CA and then
        imported into the keystore. Even though a self-signed certificate
        can be used to enable SSL, it is recommended that you use a
        self-signed certificates only on staging or development servers.

        Parameters:
         :certificate: name of the certificate to grab information for
        """
        return self._machine.export_certificate(certificate)
    #----------------------------------------------------------------------
    def generate_CSR(self, certificate):
        """
        This operation generates a certificate signing request (CSR) for a
        self-signed certificate. A CSR is required by a CA to create a
        digitally signed version of your certificate.
        Parameters:
         :certificate: name of the certificate to grab information for
        """
        return self._machine.generate_CSR(certificate)
    #----------------------------------------------------------------------
    def import_CA_signed_certificate(self,
                                     certificate,
                                     ca_signed_certificate):
        """
        Parameters:
         :certificate: name of the certificate to grab information for
         :ca_signed_certificate: The multi-part POST parameter containing the
          signed certificate file.
        """
        return self._machine.import_CA_signed_certificate(certificate,
                                                          ca_signed_certificate)
    #----------------------------------------------------------------------
    def import_existing_server_certificate(self,
                                           alias,
                                           cert_password,
                                           cert_file):
        """
        This operation imports an existing server certificate, stored in
        the PKCS #12 format, into the keystore.
        If the certificate is a CA signed certificate, you must first
        import the CA Root or Intermediate certificate using the
        importRootCertificate operation.

        Parameters:
         :alias: A unique name for the certificate that easily identifies
          it.
         :cert_password: password to unlock the file containing the
          certificate
         :cert_file: multi-part POST parameter containing the certificate
          file
        """
        return self._machine.import_existing_server_certificate(alias,
                                                                cert_password,
                                                                cert_file)
    #----------------------------------------------------------------------
    def import_root_certificate(self,
                                alias,
                                root_CA_certificate):
        """
        This operation imports a certificate authority (CA)'s root and
        intermediate certificates into the keystore.
        To create a production quality CA-signed certificate, you need to
        add the CA's certificates into the keystore that enables the SSL
        mechanism to trust the CA (and the certificates it has signed).
        While most of the popular CA's certificates are already available
        in the keystore, you can use this operation if you have a custom
        CA or specific intermediate certificates.

        Parameters:
         :alias: name of teh certificate
         :root_CA_certificate:multi-part POST parameter containing the
          certificate file.
        """
        return self._machine.import_root_certificate(
            alias,
            root_CA_certificate)
########################################################################
class LogManager(object):
    """
    Log Mangement of a server

    This resource is accessed through by administrators to check on error
    messages.

    Parameters:
     :param server: server object
    """
    _url = None
    _con = None
    _json_dict = None
    _operations = None
    _resources = None
    _json = None
    #----------------------------------------------------------------------
    def __init__(self, server):
        """Constructor"""
        self._sm = server
        self._logs = server.logs
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._logs._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._logs._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """ returns the properties for the Logs """
        return self._logs.properties
    #----------------------------------------------------------------------
    def count_error_reports(self, machine="*"):
        """ This operation counts the number of error reports (crash
            reports) that have been generated on each machine.
            Parameters:
               :param machine: - name of the machine in the cluster.  * means all
                                 machines.  This is default
            Output:
               dictionary with report count and machine name
        """
        return self._logs.count_error_reports(machine=machine)
    #----------------------------------------------------------------------
    def clean(self):
        """ Deletes all the log files on all server machines in the site.  """
        return self._logs.clean()
    #----------------------------------------------------------------------
    @property
    def settings(self):
        """ returns the current log settings """
        return self._logs.settings
    #----------------------------------------------------------------------
    def edit(self,
             level="WARNING",
             log_dir=None,
             max_age=90,
             max_report_count=10):
        """
           The log settings are for the entire site.
           Parameters:
             :param level: - Can be one of [OFF, SEVERE, WARNING, INFO, FINE,
                             VERBOSE, DEBUG].
             :param log_dir: - File path to the root of the log directory
             :param max_age: - number of days that a server should save a log
                             file.
             :param ax_report_count: - maximum number of error report files
                                       per machine
        """
        return self._logs.edit_settings(level=level,
                                        log_dir=log_dir,
                                        max_age=max_age,
                                        max_report_count=max_report_count)
    #----------------------------------------------------------------------
    def query(self,
              start_time=None,
              end_time=None,
              since_server_start=False,
              level="WARNING",
              services="*",
              machines="*",
              server="*",
              codes=None,
              process_IDs=None,
              export=False,
              export_type="CSV", #CSV or TAB
              out_path=None):
        """
           The query operation on the logs resource provides a way to
           aggregate, filter, and page through logs across the entire site.
           Parameters:

        """
        return self._logs.query(
            start_time=start_time,
            end_time=end_time,
            since_server_start=since_server_start,
            level=level,
            services=services,
            machines=machines,
            server=server,
            codes=codes,
            process_IDs=process_IDs,
            export=export,
            export_type=export_type,
            out_path=out_path
        )
########################################################################
class ReportManager(object):
    """
    Manages and modifies the usage reports for ArcGIS Server

    Parameter:
    :param server: Server object
    """
    _machines = None
    _pm = None
    _reports = None
    #----------------------------------------------------------------------
    def __init__(self, server):
        """Constructor"""
        self._sm = server
        self._reports = self._sm.usagereports
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._reports._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._reports._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the report manager's properties
        """
        return self._reports.properties
    #----------------------------------------------------------------------
    def list(self):
        """returns a list of reports on the server"""
        reports = []
        for report in self._reports.reports:
            reports.append(Report(report))
        return reports
    #----------------------------------------------------------------------
    @property
    def settings(self):
        """
        The usage reports settings are applied to the entire site. A GET
        request returns the current usage reports settings. When usage
        reports are enabled, service usage statistics are collected and
        persisted to a statistics database. When usage reports are
        disabled, the statistics are not collected. The interval
        parameter defines the duration (in minutes) during which the usage
        statistics are sampled or aggregated (in-memory) before being
        written out to the statistics database. Database entries are
        deleted after the interval specified in the max_history parameter (
        in days), unless the max_history parameter is 0, for which the
        statistics are persisted forever.
        """
        return self._reports.usage_settings
    #----------------------------------------------------------------------
    def edit(self,
             interval,
             enabled=True,
             max_history=0):
        """
        The usage reports settings are applied to the entire site. A POST
        request updates the usage reports settings.

        Parameters:
           interval - Defines the duration (in minutes) for which
             the usage statistics are aggregated or sampled, in-memory,
             before being written out to the statistics database.
           enabled - default True - Can be true or false. When usage
             reports are enabled, service usage statistics are collected
             and persisted to a statistics database. When usage reports are
             disabled, the statistics are not collected.
           max_history - default 0 - Represents the number of days after
             which usage statistics are deleted after the statistics
             database. If the max_history parameter is set to 0, the
             statistics are persisted forever.
        """
        return self._reports.edit_settings(interval,
                                           enabled,
                                           max_history)
    #----------------------------------------------------------------------
    def create(self,
               reportname,
               queries,
               metadata=None,
               since="LAST_DAY",
               from_value=None,
               to_value=None,
               aggregation_interval=None):
        """
        Creates a new usage report. A usage report is created by submitting
        a JSON representation of the usage report to this operation.

        Parameters:
           reportname - the unique name of the report
           since - the time duration of the report. The supported values
              are: LAST_DAY, LAST_WEEK, LAST_MONTH, LAST_YEAR, CUSTOM
              LAST_DAY represents a time range spanning the previous 24
                 hours.
              LAST_WEEK represents a time range spanning the previous 7
                 days.
              LAST_MONTH represents a time range spanning the previous 30
                 days.
              LAST_YEAR represents a time range spanning the previous 365
                 days.
              CUSTOM represents a time range that is specified using the
                 from and to parameters.
           from_value - optional value - The timestamp (milliseconds since
              UNIX epoch, namely January 1, 1970, 00:00:00 GMT) for the
              beginning period of the report. Only valid when since is
              CUSTOM
           to_value - optional value - The timestamp (milliseconds since
              UNIX epoch, namely January 1, 1970, 00:00:00 GMT) for the
              ending period of the report.Only valid when since is
              CUSTOM.
           aggregation_interval - Optional. Aggregation interval in minutes.
              Server metrics are aggregated and returned for time slices
              aggregated using the specified aggregation interval. The time
              range for the report, specified using the since parameter
              (and from and to when since is CUSTOM) is split into multiple
              slices, each covering an aggregation interval. Server metrics
              are then aggregated for each time slice and returned as data
              points in the report data.
              When the aggregation_interval is not specified, the following
              defaults are used:
                 LAST_DAY: 30 minutes
                 LAST_WEEK: 4 hours
                 LAST_MONTH: 24 hours
                 LAST_YEAR: 1 week
                 CUSTOM: 30 minutes up to 1 day, 4 hours up to 1 week, 1
                 day up to 30 days, and 1 week for longer periods.
             If the interval specified in Usage Reports Settings is
             more than the aggregationInterval, the interval is
             used instead.
           queries - A list of queries for which to generate the report.
              You need to specify the list as an array of JSON objects
              representing the queries. Each query specifies the list of
              metrics to be queries for a given set of resourceURIs.
              The queries parameter has the following sub-parameters:
                 resourceURIs - Comma separated list of resource URIs for
                 which to report metrics. Specifies services or folders
                 for which to gather metrics.
                    The resourceURI is formatted as below:
                       services/ - Entire Site
                       services/Folder/  - Folder within a Site. Reports
                         metrics aggregated across all services within that
                         Folder and Sub-Folders.
                       services/Folder/ServiceName.ServiceType - Service in
                         a specified folder, for example:
                         services/Map_bv_999.MapServer.
                       services/ServiceName.ServiceType - Service in the
                         root folder, for example: Map_bv_999.MapServer.
                 metrics - Comma separated list of metrics to be reported.
                   Supported metrics are:
                    RequestCount - the number of requests received
                    RequestsFailed - the number of requests that failed
                    RequestsTimedOut - the number of requests that timed out
                    RequestMaxResponseTime - the maximum response time
                    RequestAvgResponseTime - the average response time
                    ServiceActiveInstances - the maximum number of active
                      (running) service instances sampled at 1 minute
                      intervals, for a specified service
           metadata - Can be any JSON Object. Typically used for storing
              presentation tier data for the usage report, such as report
              title, colors, line-styles, etc. Also used to denote
              visibility in ArcGIS Server Manager for reports created with
              the Administrator Directory. To make any report created in
              the Administrator Directory visible to Manager, include
              "managerReport":true in the metadata JSON object. When this
              value is not set (default), reports are not visible in
              Manager. This behavior can be extended to any client that
              wants to interact with the Administrator Directory. Any
              user-created value will need to be processed by the client.

        Example:
        >>> queryObj = [{
           "resourceURIs": ["services/Map_bv_999.MapServer"],
           "metrics": ["RequestCount"]
        }]
        >>> obj.createReport(
           reportname="SampleReport",
           queries=queryObj,
           metadata="This could be any String or JSON Object.",
           since="LAST_DAY"
        )
        """
        res = self._reports.create_usage_report(reportname,
                                                queries,
                                                metadata,
                                                since,
                                                from_value,
                                                to_value,
                                                aggregation_interval)
        try:
            self._reports.init()
            return Report(res)
        except:
            return res
    #----------------------------------------------------------------------
    def quick_report(self,
                     since="LAST_WEEK",
                     queries="services/",
                     metrics="RequestsFailed"):
        """
        The operation quick_report generates an on the fly usage report for
        a service, services, or folder.

        :Parameters:
           since - the time duration of the report. The supported values
              are: LAST_DAY, LAST_WEEK, LAST_MONTH, LAST_YEAR, CUSTOM
              LAST_DAY represents a time range spanning the previous 24
                 hours.
              LAST_WEEK represents a time range spanning the previous 7
                 days.
              LAST_MONTH represents a time range spanning the previous 30
                 days.
              LAST_YEAR represents a time range spanning the previous 365
                 days.
              CUSTOM represents a time range that is specified using the
                 from and to parameters.
           queries - A list of queries for which to generate the report.
              You need to specify the list as an array of JSON objects
              representing the queries. Each query specifies the list of
              metrics to be queries for a given set of resourceURIs.
              The queries parameter has the following sub-parameters:
                 resourceURIs - Comma separated list of resource URIs for
                 which to report metrics. Specifies services or folders
                 for which to gather metrics.
                    The resourceURI is formatted as below:
                       services/ - Entire Site
                       services/Folder/  - Folder within a Site. Reports
                         metrics aggregated across all services within that
                         Folder and Sub-Folders.
                       services/Folder/ServiceName.ServiceType - Service in
                         a specified folder, for example:
                         services/Map_bv_999.MapServer.
                       services/ServiceName.ServiceType - Service in the
                         root folder, for example: Map_bv_999.MapServer.
           metrics - Comma separated list of metrics to be reported.
                   Supported metrics are:
                    RequestCount - the number of requests received
                    RequestsFailed - the number of requests that failed
                    RequestsTimedOut - the number of requests that timed out
                    RequestMaxResponseTime - the maximum response time
                    RequestAvgResponseTime - the average response time
                    ServiceActiveInstances - the maximum number of active
                    (running) service instances sampled at 1 minute
                    intervals, for a specified service
         :Output:
          Python dictionary of data on a successful query.
        """
        return self._reports.quick_report(since=since,
                                          queries=queries,
                                          metrics=metrics
                                        )
########################################################################
class Report(object):
    """
    A Single Usage Report returned by ArcGIS Server
    (This class should not be created by a user)
    Parameter:
    :param report: internal Report object
    """
    _properties = None
    _con = None
    #----------------------------------------------------------------------
    def __init__(self, report):
        """Constructor"""
        from .._impl._server.admin._usagereports import UsageReport
        if isinstance(report, UsageReport):
            self._report = report
            self._con = self._report._con
            self._properties = report._json_dict
        else:
            raise ValueError("Invalid Input, a UsageReport must be given.")
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the Report Properties
        """
        if self._properties is None:
            self._report.init()
            self._properties = PropertyMap(self._report._json_dict)
        return self._properties
    #----------------------------------------------------------------------
    def edit(self, report):
        """
        Edits the usage report. To edit a usage report, you need to submit
        the complete JSON representation of the usage report which
        includes updates to the usage report properties. The name of the
        report cannot be changed when editing the usage report.

        Values are changed in the class, to edit a property like
        metrics, pass in a new value.  Changed values to not take until the
        edit() is called.
        """
        import json
        params = {
            "f" : "json",
            "usagereport" : json.dumps(report)
        }
        url = self._report.url + "/edit"
        self._report.init()
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def delete(self):
        """deletes the current report"""
        return self._report.delete()
    #----------------------------------------------------------------------
    def query(self, query_filter=None):
        """
        Retrieves server usage data for the report. This operation
        aggregates and filters server usage statistics for the entire
        ArcGIS Server site. The report data is aggregated in a time slice,
        which is obtained by dividing up the time duration by the default
        (or specified) aggregationInterval parameter in the report. Each
        time slice is represented by a timestamp, which represents the
        ending period of that time slice.
        In the JSON response, the queried data is returned for each metric-
        resource URI combination in a query. In the report-data section,
        the queried data is represented as an array of numerical values. A
        response of null indicates that data is not available or requests
        were not logged for that metric in the corresponding time-slice.

        Parameters:
           query_filter - The report data can be filtered by the machine
             where the data is generated. The filter accepts a comma
             separated list of machine names; * represents all machines.

             Examples:
               # filters for the specified machines
               {"machines": ["WIN-85VQ4T2LR5N", "WIN-239486728937"]}
               # no filtering; all machines are accepted
               {"machines": "*"}
        """
        return self._report.query(query_filter=query_filter)
########################################################################
class DataStoreManager(object):
    """
    This resource provides information about the data holdings of the
    server. Data items are used by ArcGIS for Desktop and other clients to
    validate data paths referenced by GIS services.

    You can register new data items with the server by using the Register
    Data Item operation. Use the Find Data Items operation to search
    through the hierarchy of data items.

    A relational data store type represents a database platform that has
    been registered for use on a portal's hosting server by the ArcGIS
    Server administrator. Each relational data store type describes the
    properties ArcGIS Server requires in order to connect to an instance of
    a database for a particular platform. At least one registered
    relational data store type is required before client applications such
    as Insights for ArcGIS can create Relational Database Connection portal
    items.

    The Compute Ref Count operation counts and lists all references to a
    specific data item. This operation helps you determine if a particular
    data item can be safely deleted or refreshed.

    Parameters:
    :param server: Server object
    """
    _properties = None
    _ds = None
    _server = None
    #----------------------------------------------------------------------
    def __init__(self, server):
        """Constructor"""
        self._sm = server
        self._ds = self._sm.data
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._ds._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._ds._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the machine's properties
        """
        return self._ds.properties
    #----------------------------------------------------------------------
    def list(self):
        """returns a list of datastore objects"""
        stores = []
        self._ds._datastores = None
        for d in self._ds.datastores:
            stores.append(Datastore(d))
            del d
        return stores
    #----------------------------------------------------------------------
    @property
    def config(self):
        """
           The data store configuration properties affect the behavior of
           the data holdings of the server. The properties include:
           blockDataCopy - When this property is false, or not set at all,
           copying data to the site when publishing services from a client
           application is allowed. This is the default behavior. When this
           property is true, the client application is not allowed to copy
           data to the site when publishing. Rather, the publisher is
           required to register data items through which the service being
           published can reference data. Values: true | false
        """
        return self._ds.config
    #----------------------------------------------------------------------
    @config.setter
    def config(self, config):
        """
        This operation allows you to update the data store configuration
        You can use this to allow or block the automatic copying of data
        to the server at publish time
        Parameters:
        :param config: - the JSON object containing the data configuration
        Output:
        JSON message as dictionary
        """
        return self._ds.config(config)
    #----------------------------------------------------------------------
    def get(self, path):
        """ Returns the data item object at the given path

        Parameters:
        :param path: required string, the data item path
        Output:
        None if the data item is not found at that path and the data item
        object if its found
        """
        return self._ds.get(path)
    #----------------------------------------------------------------------
    def add_folder(self,
                   name,
                   server_path,
                   client_path=None):
        """
        Registers a folder with the data store.
        Input
            name - unique fileshare name on the server
            server_path - the path to the folder from the server (and client, if shared path)
            client_path - if folder is replicated, the path to the folder from the client
            if folder is shared, don't set this parameter
        Output:
              the data item is registered successfully, None otherwise
        """
        self._ds._datastores = None
        return self._ds.add_folder(name=name,
                                   server_path=server_path,
                                   client_path=client_path)
    #----------------------------------------------------------------------
    def add(self,
            name,
            item):
        """
        Registers a new data item with the data store.
        Input
            item - The disct representing the data item.
            See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000001s9000000
        Output:
              True if the data item is registered successfully, False otherwise
        """
        self._ds._datastores = None
        return self._ds.add(name=name, item=item)
    #----------------------------------------------------------------------
    def add_bigdata(self,
                    name,
                    server_path=None):
        """
        Registers a bigdata fileshare with the data store.
        Input
            name - unique bigdata fileshare name on the server
            server_path - the path to the folder from the server
        Output:
              the data item if registered successfully, None otherwise
        """
        self._ds._datastores = None
        return self._ds.add_bigdata(name=name,
                                    server_path=server_path)
    #----------------------------------------------------------------------
    def add_database(self,
                     name,
                     conn_str,
                     client_conn_str=None,
                     conn_type="shared"):
        """
        Registers a database with the data store.
        Input
            name - unique database name on the server
            conn_str - the path to the folder from the server (and client, if shared or serverOnly database)
            client_conn_str: connection string for client to connect to replicated enterprise database>
            conn_type - "<shared|replicated|serverOnly>"
        Output:
            the data item is registered successfully, None otherwise
        """
        self._ds._datastores = None
        return self._ds.add_database(name,
                                     conn_str,
                                     client_conn_str,
                                     conn_type)
    #----------------------------------------------------------------------
    def get_total_refcount(self, path):
        """
           Computes the total number of references to a given data item
           that exist on the server. You can use this operation to
           determine if a data resource can be safely deleted (or taken
           down for maintenance).
           Parameters:
              path - The complete hierarchical path to the item
           Output:
              JSON message as dictionary
        """
        return self._ds.get_total_refcount(path=path)
    #----------------------------------------------------------------------
    def make_datastore_machine_primary(self,
                                       item_name,
                                       machine_name):
        """
        Promotes a standby machine to the primary Data Store machine. The
        existing primary machine is downgraded to a standby machine.

        Parameters:
         :item_name: name of the data store item
         :machine_name: name of the machine to promote to primary
        """
        return self._ds.make_datastore_machine_primary(
            item_name, machine_name)
    #----------------------------------------------------------------------
    def get_relational_datastore_type(self, type_id):
        """
        This resource lists the properties of a registered relational data
        store type. The properties returned are those that client
        applications must provide when creating a Relational Database
        Connection portal item.

        Parameters:
         :type_id: datastore type id
        """
        return self._ds.get_relational_datastore_type(type_id=type_id)
    #----------------------------------------------------------------------
    @property
    def relational_datastore_types(self):
        """
        This resource lists the relational data store types that have been
        registered with the server. Each registered relational data store
        type has both an id and a name property, as well as an array of
        userDefinedProperties, which indicates the properties client
        applications must provide when creating a Relational Database
        Connection portal item. Only administrators can register and
        unregister a relational data store type. The following database
        platforms are supported: SAP HANA, Microsoft SQL Server and
        Teradata.
        """
        return self._ds.relational_datastore_types
    #----------------------------------------------------------------------
    def search(self,
               parent_path=None,
               ancestor_path=None,
               types=None,
               id=None):
        """
           You can use this operation to search through the various data
           items registered in the server's data store.
           Parameters:
              parent_path - The path of the parent under which to find items
              ancestor_path - The path of the ancestor under which to find
                             items.
              types - A filter for the type of the items
              id - A filter to search by the ID of the item
           Output:
              dictionary
        """
        return self._ds.search(parent_path, ancestor_path, types, id)
    #----------------------------------------------------------------------
    def _register_data_item(self, item):
        """
           Registers a new data item with the server's data store.
           Input
              item - The JSON representing the data item.
              See http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000001s9000000
           Output:
              dictionary
        """

        return self._ds._register_data_item(item)
    #----------------------------------------------------------------------
    @property
    def data_items(self):
        """ This resource lists data items that are the root of all other
            data items in the data store.
        """
        return self._ds.items
    #----------------------------------------------------------------------
    def validate(self):
        """ validates all the items in the datastore """
        res = self._ds.validate()
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def make_primary(self, datastore_name, machine_name):
        """
        Promotes a standby machine to the primary Data Store machine. The
        existing primary machine is downgraded to a standby machine.

        """
        return self._ds.make_primary(datastore_name, machine_name)
    #----------------------------------------------------------------------
    def remove_datastore_machine(self, item_name, machine_name):
        """
        Removes a standby machine from the Data Store. This operation is
        not supported on the primary Data Store machine.

        Parameters:
           item_name - name of the data store item
           machine_name - name of the machine to remove
        """
        return self._ds.remove_datastore(item_name, machine_name)
    #----------------------------------------------------------------------
    def start(self, item_name, machine_name):
        """
        Starts the database instance running on the Data Store machine.

        Parameters:
           item_name - name of the item to start
           machine_name - name of the machine to start on
        """
        return self._ds.start_datastore(item_name, machine_name)
    #----------------------------------------------------------------------
    def stop(self, item_name, machine_name):
        """
        Stop the database instance running on the Data Store machine.

        Parameters:
           item_name - name of the item to stop
           machine_name - name of the machine to stop on
        """
        return self._ds.stop_datastore(item_name, machine_name)
    #----------------------------------------------------------------------
    def _unregister_data_item(self, path):
        """
        Unregisters a data item that has been previously registered with
        the server's data store.

        Parameters:
           path - path to share folder

        Example:
           path = r"/fileShares/folder_share"
           print data.unregisterDataItem(path)
        """
        return self._ds._unregister_data_item(path)
    #----------------------------------------------------------------------
    def validate_egdb(self, data_store_name, name):
        """
        Checks the status of ArcGIS Data Store and provides a health check
        response.

        Parameters:
           data_store_namee - name of the datastore
           name - name of the machine
        """
        return self._ds.validate_egdb(data_store_name, name)
########################################################################
class Datastore(object):
    """
    Represents a Single Datastore in DataStoreManager

    Parameter:
    :param datastore: reprsents a single instance of datastore
    """
    _store = None
    #----------------------------------------------------------------------
    def __init__(self, datastore):
        """Constructor"""
        self._store = datastore
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """
        returns the machine's properties
        """
        return self._store.properties
    #----------------------------------------------------------------------
    def __str__(self):
        return str(self._store)
    #----------------------------------------------------------------------
    def __repr__(self):
        return str(self._store)
    #----------------------------------------------------------------------
    @property
    def manifest(self):
        """
        The manifest resource for bigdata fileshares,
        """
        return self._store.manifest
    #----------------------------------------------------------------------
    @manifest.setter
    def manifest(self, value):
        """
        Updates the manifest resource for bigdata fileshares
        """
        return self._store.manifest(value)
    #---------------------------------------------------------------------
    @property
    def hints(self):
        """
        This returns the hints resource for a big data file share. Hints
        are advanced parameters to control the generation of Manifest.
        """
        return self._store.hints
    #---------------------------------------------------------------------
    @hints.setter
    def hints(self,
              hints):
        """
        Upload a hints file for a big data file share item. This will
        replace the existing hints file. To apply the control parameters in
        the hints file and regenerate the manifest, use the editDataItem to
        edit the big data file share (using the same data store item as
        input) which will regenerate the manifest. When a manifest is
        regenerated, it will be updated only for datasets that have hints
        and for new datasets that are added to the existing big data file
        share location.

        Parameters:
         :name: name of the big data item to update
         :hints: The hints file to be uploaded.
        """
        return self._store.hints(hints)
    #----------------------------------------------------------------------
    @property
    def ref_count(self):
        """
        The total number of references to this data item that exist on the
        server. You can use this property to determine if this data item
        can be safely deleted (or taken down for maintenance).
        """
        return self._store.ref_count
    #----------------------------------------------------------------------
    def delete(self):
        """
        Unregisters this data item from the data store
        """
        return self._store.delete()
    #----------------------------------------------------------------------
    def update(self, item):
        """
        Edits this data item to update its connection information.

        Input
            item - the dict representation of the updated item
        Output:
              True if successful
        """
        return self._store.update(item)
    #----------------------------------------------------------------------
    def validate(self):
        """
        Validates that this data item's path (for file shares) or connection string (for databases)
        is accessible to every server node in the site

        Output:
              True if successful
        """
        return self._store.validate()
    #----------------------------------------------------------------------
    @property
    def datasets(self):
        """
        Returns the datasets in the data store (currently implemented for big data file shares.)
        """
        return self._store.datasets
########################################################################
class UserManager(object):
    """
    This resource represents all users available in the user store that can
    administer ArcGIS Server and access the GIS services hosted on the
    server. In short, it represents the complete user space.
    As the user space could be potentially large, there isn't any listing
    of users, but you can use Get Users or Search operations to access
    their account information.
    ArcGIS Server is capable of connecting to your enterprise identity
    stores such as Active Directory or other directory services exposed
    through the LDAP protocol. Such identity stores are treated as read
    only, and ArcGIS Server does not attempt to update them. As a result,
    operations that need to update the identity store (such as adding
    users, removing users, updating users, assigning roles and removing
    assigned roles) are not supported when identity stores are read only.
    On the other hand, you could configure your ArcGIS Server to use the
    default identity store (shipped with the server) which is treated as a
    read-write store.
    The total numbers of users are returned in the response.

    Note:
       Typically, this resource must be accessed over an HTTPS connection.
    """
    _sm = None
    _security = None
    #----------------------------------------------------------------------
    def __init__(self, server):
        """Constructor"""
        self._sm = server
        self._security = server.security
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._security._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._security._url)
    #----------------------------------------------------------------------
    def create(self, username, password, firstname,
               lastname, email=None, description=None):
        """
        Add a user account to the user store
           Parameters:
              username - The name of the user. The name must be unique in
                         the user store.
              password - The password for this user
              fullname - an optional full name for the user
              description - an option field to add comments or description
                            for the user account
              email - an optional email for the user account
           Output:
              User Object
        """
        res = self._security.add_user(username=username,
                                      password=password,
                                      fullname="%s %s" % (firstname, lastname),
                                      description=description,
                                      email=email)
        if isinstance(res, dict) and \
           'status' in res and \
           res['status'] == 'success':
            return self.search(username=username)[0]
        elif isinstance(res, bool) and \
             res:
            return self.search(username=username)[0]
        return None
    #----------------------------------------------------------------------
    def get(self, username):
        """
        finds a users
           Parameters:
             :username: name of the user to find
           Ouput:
             User object
        """
        res = self.search(username=username, max_results=1)
        if len(res) == 0:
            return None
        return res[0]
    #----------------------------------------------------------------------
    @property
    def me(self):
        """
        Gets the user object as the current logged in user. If the username
        cannot be found, for example, the site administrator account, then
        just the username is returned.
        """
        res = self.search(username=self._security._con._username,
                          max_results=1)
        if len(res) == 0:
            return self._security._con._username
        return res[0]
    #----------------------------------------------------------------------
    def search(self, username, max_results=25):
        """
        You can use this operation to search a specific user or a group of
        users from the user store. The size of the search result can be
        controlled with the max_results parameter.

        Parameters:
         :username: user or users to find
         :max_results: integer value of the maximum number of users to
         return
        Output:
         list of User objects
        """
        users = []
        res = self._security.find_users(criteria=username, max_count=max_results)
        if "users" in res:
            for user in res["users"]:
                users.append(User(self._security, user))
                del user
        return users
    @property
    def roles(self):
        """Helper object to manage custom roles for users"""
        return RoleManager(self._security)
########################################################################
class User(dict):
    """
    Individual User Account
    """
    _security = None
    _user_dict = None
    #----------------------------------------------------------------------
    def __init__(self, security, user_dict):
        """Constructor"""
        dict.__init__(self)
        if security is None or \
           user_dict is None:
            raise ValueError("Values of security and user_dict" + \
                             " must be provided")
        self._security = security
        self._user_dict = user_dict
        self.__dict__.update(self._user_dict)
    #----------------------------------------------------------------------
    def __getattr__(self, name):
        try:
            return dict.__getitem__(self, name)
        except:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, name))
    #----------------------------------------------------------------------
    def __getitem__(self, k): # support user attributes as dictionary keys on this object, eg. user['role']
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            return self.__dict__[k]
    #----------------------------------------------------------------------
    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s username:%s>' % (type(self).__name__, self.username)
    #----------------------------------------------------------------------
    def _repr_html_(self):
        fullName = 'Not Provided'
        email = 'Not Provided'
        description = 'Not Provided'
        role = 'Not Provided'
        try:
            fullName = self.fullname
        except:
            fullName = 'Not Provided'
        try:
            description = self.description
        except:
            description = 'Not Provided'
        try:
            email = self.email
        except:
            email = 'Not Provided'
        import datetime
        return """<div class="9item_container" style="height: auto; overflow: hidden; border: 1px solid #cfcfcf; border-radius: 2px; background: #f6fafa; line-height: 1.21429em; padding: 10px;">
                    <div class="item_right" style="float: none; width: auto; overflow: hidden;">
                    <br/><b>Username</b>: """ + str(self.username) + """
                        <br/><b>Full Name</b>: """ + str(fullName) + """
                        <br/><b>Description</b>: """ + str(description)  + """
                        <br/><b>Email</b>: """ + str(email)  + """
                        <br/><b>Disabled</b>: """ + str(self.disabled)  + """
                        <br/><b>Current As:</b>: """ + str(datetime.datetime.now().strftime("%B %d, %Y")) + """

                    </div>
                </div>
                """
    #----------------------------------------------------------------------
    def update(self, password=None, full_name=None,
               description=None, email=None):
        """
        Updates a user account in the user store

           Parameters:
              username - the name of the user. The name must be unique in
                         the user store.
              password - the password for this user.
              fullname - an optional full name for the user.
              description - an optional field to add comments or description
                            for the user account.
              email - an optional email for the user account.
        """

        res = self._security.update_user(self.username, password,
                                          full_name, description,
                                          email)
        if res['status'] == 'success':
            user = self._security.find_users(criteria=self.username, max_count=1)['users'][0]
            self._user_dict = user
            self.__dict__.update(user)
        return res
    #----------------------------------------------------------------------
    def add_role(self, role_name):
        """
        You must use this operation to assign roles to a user account when
        working with an user and role store that supports reads and writes.
        By assigning a role to a user, the user account automatically
        inherits all the permissions that have been assigned to the role.

        Parameter:
         :role: role name to assign to current user
        """

        return self._security.assign_roles(username=self.username,
                                           roles=role_name)
    #----------------------------------------------------------------------
    def delete(self):
        """deletes the current user account"""
        username = self.username
        return self._security.delete_user(username=username)
########################################################################
class RoleManager(object):
    """
    This resource represents all roles available in the role store. The
    ArcGIS Server security model supports a role-based access control in
    which each role can be assigned certain permissions (privileges) to
    access one or more resources. Users are assigned to these roles. The
    server then authorizes each requesting user based on all the roles
    assigned to the user.
    As the role space could be potentially large, you can use the paged Get
    Roles operation to iterate through the list of roles, or you can use
    the Search Roles operation to search for a specific role.
    ArcGIS Server is capable of connecting to your enterprise identity
    stores such as Active Directory or other directory services exposed via
    the LDAP protocol. Such identity stores are treated as read-only stores
    and ArcGIS Server does not attempt to update them. As a result,
    operations that need to update the role store (such as adding roles,
    removing roles, updating roles) are not supported when the role store
    is read-only. On the other hand, you can configure your ArcGIS Server
    to use the default role store shipped with the server, which is
    treated as a read-write store.
    """
    _security = None
    #----------------------------------------------------------------------
    def __init__(self, security):
        """Constructor"""
        self._security = security

    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._security._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._security._url)
    #----------------------------------------------------------------------
    def create(self, name, description):
        """Creates and returns a custom role with the specified parameters

        Parameters:
         :name: name of the role (must be unique)
         :description: optional descriptive field as string
        Output:
         JSON dictionary
        """
        return self._security.add_role(name=name, description=description)
    #----------------------------------------------------------------------
    def all(self, start_index=0, max_roles=255):
        """
        Returns list of all roles in the Server
        :param max_roles: the maximum number of roles to be returned
        :return: list of all roles in the server
        """
        roles = self._security.list_roles(start_index=start_index,
                                          page_size=max_roles)
        return [Role(self._security, role) for role in roles['roles']]
    #----------------------------------------------------------------------
    def get_role(self, role_id, max_roles=10):
        """
        Returns the role with the specified role id. Returns list of all roles in the
        Server if a role_id is not specified
        :role_id: the role id of the role to get. Leave None to get all roles
        :max_roles: the total number of roles to limit search to
        :return: list of roles
        """
        roles = self._security.search_roles(role_filter=role_id,
                                            max_count=max_roles)
        return [Role(self._security, role) for role in roles['roles']]
########################################################################
class Role(dict):
    """
    represents a single role on server
    """
    _roledict = None
    _security = None
    #----------------------------------------------------------------------
    def __init__(self, security, roledict):
        """Constructor"""
        dict.__init__(self)
        if security is None or \
           roledict is None:
            raise ValueError("Values of security and roledict" + \
                             " must be provided")
        self._security = security
        self._roledict = roledict
        self.__dict__.update(self._roledict)
    #----------------------------------------------------------------------
    def __getattr__(self, name):
        try:
            return dict.__getitem__(self, name)
        except:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, name))
    #----------------------------------------------------------------------
    def __getitem__(self, k): # support user attributes as dictionary keys on this object, eg. user['role']
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            return self.__dict__[k]
    #----------------------------------------------------------------------
    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s rolename:%s>' % (type(self).__name__, self.rolename)
    #----------------------------------------------------------------------
    def update(self, description=None):
        """
        Updates a role in the role store with new information. This
        operation is available only when the role store is a read-write
        store such as the default ArcGIS Server store.

        Parameters:
         :description: An optional field to add comments or a description
          for the role
        Output:
         status dictionary
        """
        res =  self._security.update_role(rolename=self.rolename,
                                          description=description)
        if res:
            self.__dict__.update(self._security.search_roles(
                role_filter=self.rolename,
                max_count=1)['roles'][0])
        return res
    #----------------------------------------------------------------------
    def delete(self):
        """
        deletes the current role
        """
        res = self._security.delete_role(rolename=self.rolename)
        self = None
    #----------------------------------------------------------------------
    def set_privileges(self, privilage):
        """
        Administrative access to ArcGIS Server is modeled as three broad
        tiers of privileges:
          ADMINISTER-A role that possesses this privilege has unrestricted
           administrative access to ArcGIS Server.
          PUBLISH-A role with PUBLISH privilege can only publish GIS
           services to ArcGIS Server.
          ACCESS-No administrative access. A role with this privilege can
           only be granted permission to access one or more GIS services.
        By assigning these privileges to one or more roles in the role
        store, ArcGIS Server's security model supports role-based access
        control to its administrative functionality.
        These privilege assignments are stored independent of ArcGIS
        Server's role store. As a result, you don't need to update your
        enterprise identity stores (like Active Directory).
        """
        allowed = ['administer', 'publish', 'access']
        if privilage.lower() in allowed:
            privilage = privilage.upper()
        else:
            raise ValueError("Invalid privilage.")
        return self._security.assign_privilege(rolename=self.rolename,
                                               privilege=privilage)
########################################################################
class SystemManager(object):
    """
    The System resource is a collection of miscellaneous server-wide
    resources such as server properties, server directories, the
    configuration store, Web Adaptors, and licenses.
    """
    _sm = None
    _system = None
    #----------------------------------------------------------------------
    def __init__(self, server):
        """Constructor"""
        self._sm = server
        self._system = server.system
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._sm._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._sm._url)
    #----------------------------------------------------------------------
    @property
    def jobs(self):
        """
        This resource is a collection of all the administrative jobs
        (asynchronous operations) created within your site. When operations
        that support asynchronous execution are run, the server creates a
        new job entry that can be queried for its current status and
        messages.

        Note: These administrative jobs are not the same as geoprocessing
         jobs.
        """
        return self._system.jobs
    #----------------------------------------------------------------------
    @property
    def licenses(self):
        """
        The licenses resource lists the current license level of ArcGIS
        Server and all authorized extensions. Contact Esri Customer Service
        if you have questions about license levels or expiration properties.
        """
        return self._system.licenses
    #----------------------------------------------------------------------
    @property
    def directories(self):
        """
        Provides access to the server's directories
        """
        return DirectoryManager(system=self._system)

    #----------------------------------------------------------------------
    def clear_cache(self):
        """
        This resource currently supports a single operation to clear the
        REST cache.
        """
        return self._system.clear_rest_cache()
    #----------------------------------------------------------------------
    @property
    def server_properties(self):
        """
        The Server has configuration parameters that can be govern some of its
        intricate behavior. The Server Properties resource is a container for
        such properties. These properties are available to all server objects
        and extensions through the server environment interface.
        The properties include:
         CacheSizeForSecureTileRequests - An integer that specifies the
          number of users whose token information will be cached. This
          increases the speed of tile retrieval for cached services. If not
          specified, the default cache size is 200,000. Both REST and SOAP
          services honor this property. You'll need to manually restart
          ArcGIS Server in order for this change to take effect.
         DisableAdminDirectoryCache - Disables browser caching of the
          Administrator Directory pages. The default is false. To disable
          browser caching, set this property to true.
         disableIPLogging - When a possible cross-site request forgery
          (CSRF) attack is detected, the server logs a message containing
          the possible IP address of the attacker. If you do not want IP
          addresses listed in the logs, set this property to true. Also,
          HTTP request referrers are logged at FINE level by the REST and
          SOAP handlers unless this property is set to true.
         javaExtsBeginPort - Specifies a start port of the port range used
          for debugging Java server object extensions.
          Example: 8000
         javaExtsEndPort - Specifies an end port of the port range used for
          debugging Java server object extensions.
          Example: 8010
         localTempFolder - Defines the local folder on a machine that can
          be used by GIS services and objects. If this property is not
          explicitly set, the services and objects will revert to using the
          system's default temporary directory.

          Note:
          If this property is used, you must create the temporary directory
          on every server machine in the site. Example: /tmp/arcgis.

          messageFormat - Defines the transmission protocol supported by
           the services catalog in the server.
           Values: esriServiceCatalogMessageFormatBin,
                   esriServiceCatalogMessageFormatSoap,
                   esriServiceCatalogMessageFormatSoapOrBin
          messageVersion - Defines the version supported by the services
           catalog in the server. Example: esriArcGISVersion101
          PushIdentityToDatabase - Propogates the credentials of the logged
           -in user to make connections to an Oracle database. This
           property is only supported for use with Oracle databases.
           Values: true | false
          suspendDuration - Specifies the duration for which the ArcGIS
           service hosting processes should suspend at startup. This
           duration is specified in milliseconds. This is an optional
           property that takes effect when suspendServiceAtStartup is set
           to true. If unspecified and suspension of service at startup is
           requested, then the default suspend duration is 30 seconds.
           Example: 10000 (meaning 10 seconds)
          suspendServiceAtStartup - Suspends the ArcGIS service hosting
           processes at startup. This will enable attaching to those
           processes and debugging code that runs early in the lifecycle of
           server extensions soon after they are instantiated.
           Values: true | false
          uploadFileExtensionWhitelist - This specifies what files are
           allowed to be uploaded through the file upload API by
           identifying the allowable extensions. It is a list of comma
           separated extensions without dots. If this property is not
           specified a default list is used. This is the default list: soe,
           sd, sde, odc, csv, txt, zshp, kmz, and geodatabase.

         Note:
         Updating this list overrides the default list completely. This
         means if you set this property to a subset of the default list
         then only those items in the subset will be accepted for upload.
         Example: sd, so, sde, odc.

         uploadItemInfoFileExtensionWhitelist - This specifies what files
          are allowed to be uploaded through the service iteminfo upload
          API by identifying the allowable extensions. It should be a list
          of comma separated extensions without dots. If this property is
          not specified a default list is used. This is the default list:
          xml, img, png, gif, jpg, jpeg, bmp.

        Note:
        This list overrides the default list completely. This means if you
        set this property to a subset of the default list then only those
        items in the subset will be accepted for upload. Example: png, svg,
        gif, jpg, tiff, bmp.

        WebContextURL - Defines the web front end as seen by your users.
         Example: http://mycompany.com/gis
        """
        return self._system.server_properties
    #----------------------------------------------------------------------
    @property
    def configuration_store(self):
        """
        provides access to the configuration store settings
        """
        return self._system.configuration_store
########################################################################
class DirectoryManager(object):
    """
    A collection of all the server directories is listed under this
    resource.
    You can add a new directory using the Register Directory operation. You
    can then configure GIS services to use one or more of these
    directories. If you no longer need the server directory, you must
    remove the directory by using the Unregister Directory operation.
    """
    _system = None
    def __init__(self, system):
        self._system = system
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._system._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._system._url)
    #----------------------------------------------------------------------
    @property
    def all(self):
        """
        Server directories are used by GIS services as a location to output
        items such as map images, tile caches, and geoprocessing results.
        In addition, some directories contain configurations that power the
        GIS services.
        """
        return self._system.server_directories
    #----------------------------------------------------------------------
    def edit_services_directory(self,
            allowedOrigins,
            arcgis_com_map,
            arcgis_com_map_text,
            jsapi_arcgis,
            jsapi_arcgis_css,
            jsapi_arcgis_css2,
            jsapi_arcgis_sdk,
            serviceDirEnabled):
        """
        With this operation you can enable or disable the HTML view of
        ArcGIS REST API (also known as the Services Directory). You can
        also adjust the JavaScript and map viewer previews of services in
        the Services Directory so that they work with your own locally
        hosted JavaScript API and map viewer.

        Parameters:
         :allowedOrigins: Comma-separated list of URLs of domains allowed to make
          requests. * can be used to denote all domains.
         :arcgis_com_map: URL of the map viewer application used for service
          previews. Defaults to the ArcGIS.com map viewer but could be used
          to point at your own Portal for ArcGIS map viewer.
         :arcgis_com_map_text:
         :jsapi_arcgis: The URL of the JavaScript API to use for service
          previews. Defaults to the online ArcGIS API for JavaScript, but
          could be pointed at your own locally-installed instance of the
          JavaScript API.
         :jsapi_arcgis_css: CSS file associated with the ArcGIS API for
          JavaScript. Defaults to the online Dojo tundra.css.
         :jsapi_arcgis_css2:Additional CSS file associated with the ArcGIS
          API for JavaScript. Defaults to the online esri.css.
         :jsapi_arcgis_sdk: URL of the ArcGIS API for JavaScript help.
         :serviceDirEnabled: Flag to enable/disable the HTML view of the
          services directory.
        """
        return self._system.edit_services_directory(allowedOrigins, arcgis_com_map,
                                            arcgis_com_map_text,
                                            jsapi_arcgis,
                                            jsapi_arcgis_css,
                                            jsapi_arcgis_css2,
                                            jsapi_arcgis_sdk,
                                            serviceDirEnabled)
    #----------------------------------------------------------------------
    def get(self, name):
        """
        Gets a single directory registered with ArcGIS Server

        Parameters:
         :name: name of the registered directory
        """
        return self._system.get_directory(name=name)
    #----------------------------------------------------------------------
    def add(self,
            name,
            physicalPath,
            directoryType,
            maxFileAge,
            cleanupMode="NONE",
            description=None):
        """
        Registers a new server directory. While registering the server
        directory, you can also specify the directory's cleanup parameters

        Parameters:
         :name: The name of the server directory.
         :physicalPath: The absolute physical path of the server directory.
         :directoryType: The type of server directory.
         :cleanupMode: Defines if files in the server directory needs to be
          cleaned up.
         :maxFileAge: Defines how long a file in the directory needs to be
          kept before it is deleted.
         :description:  An optional description for the server directory.
        """
        return self._system.register(name, physicalPath, directoryType,
                                    maxFileAge, cleanupMode, description)
########################################################################
class SiteManager(object):
    """
    A site is a collection of server resources. This collection includes
    server machines that are installed with ArcGIS Server, including GIS
    services, data and so on. The site resource also lists the current
    version of the software.
    When you install ArcGIS Server on a server machine for the first time,
    you must create a new site. Subsequently, newer server machines can
    join your site and increase its computing power. Once a site is no
    longer required, you can delete the site, which will cause all of
    the resources to be cleaned up.

    Parameters:
     :server: arcgis.gis.server object
    """
    _sm = None
    #----------------------------------------------------------------------
    def __init__(self, server, initialize=False):
        """Constructor"""
        self._sm = server
        if initialize:
            self._sm._init()
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._sm._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._sm._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """returns the site """
        return self._sm.properties
    #----------------------------------------------------------------------
    def create(self,
               username,
               password,
               config_store_connection,
               directories,
               cluster=None,
               logs_settings=None,
               run_async=False):
        """
        This is the first operation that you must invoke when you install
        ArcGIS Server for the first time. Creating a new site involves:

          -Allocating a store to save the site configuration
          -Configuring the server machine and registering it with the site
          -Creating a new cluster configuration that includes the server
           machine
          -Configuring server directories
          -Deploying the services that are marked to auto-deploy

        Because of the sheer number of tasks, it usually takes a little
        while for this operation to complete. Once a site has been created,
        you can publish GIS services and deploy them to your server
        machines.

        Parameters:
           username - The name of the administrative account to be used by
             the site. This can be changed at a later stage.
           password - The credentials of the administrative account.
           configStoreConnection - A JSON object representing the
             connection to the configuration store. By default, the
             configuration store will be maintained in the ArcGIS Server
             installation directory.
           directories - A JSON object representing a collection of server
             directories to create. By default, the server directories will
             be created locally.
           cluster - An optional cluster configuration. By default, the
             site will create a cluster called 'default' with the first
             available port numbers starting from 4004.
           logsSettings - Optional log settings.
           runAsync - A flag to indicate if the operation needs to be run
             asynchronously. Values: true | false
        """
        return self._sm.create(username,
                               password,
                               config_store_connection,
                               directories,
                               cluster,
                               logs_settings,
                               run_async)
    #----------------------------------------------------------------------
    def join(self, admin_url, username, password):
        """
        The Join Site operation is used to connect a server machine to an
        existing site. This is considered a 'push' mechanism, in which a
        server machine pushes its configuration to the site. For the
        operation to be successful, you need to provide an account with
        administrative privileges to the site.
        When an attempt is made to join a site, the site validates the
        administrative credentials, then returns connection information
        about its configuration store back to the server machine. The
        server machine then uses the connection information to work with
        the configuration store.
        If this is the first server machine in your site, use the Create
        Site operation instead.

        Parameters:
           admin_url - The site URL of the currently live site. This is
            typically the Administrator Directory URL of one of the server
            machines of a site.
           username - The name of an administrative account for the site.
           password - The password of the administrative account.
        """
        return self._sm.join(admin_url, username, password)
    #----------------------------------------------------------------------
    def delete(self):
        """
        Deletes the site configuration and releases all server resources.
        This is an unrecoverable operation. This operation is well suited
        for development or test servers that need to be cleaned up
        regularly. It can also be performed prior to uninstall. Use caution
        with this option because it deletes all services, settings, and
        other configurations.
        This operation performs the following tasks:
          - Stops all server machines participating in the site. This in
            turn stops all GIS services hosted on the server machines.
          - All services and cluster configurations are deleted.
          - All server machines are unregistered from the site.
          - All server machines are unregistered from the site.
          - The configuration store is deleted.
        """
        return self._sm.delete()
    #----------------------------------------------------------------------
    def export(self, location=None):
        """
        Exports the site configuration to a location you specify as input
        to this operation.

        Parameters:
           location - A path to a folder accessible to the server where the
            exported site configuration will be written. If a location is
            not specified, the server writes the exported site
            configuration file to directory owned by the server and returns
            a virtual path (an HTTP URL) to that location from where it can
            be downloaded.

        """
        return self._sm.export(location)
    #----------------------------------------------------------------------
    def import_site(self, location):
        """
        This operation imports a site configuration into the currently
        running site. Importing a site means replacing all site
        configurations (including GIS services, security configurations,
        and so on) of the currently running site with those contained in
        the site configuration file you supply as input. The input site
        configuration file can be obtained through the exportSite
        operation.
        This operation will restore all information included in the backup,
        as noted in exportSite. When it is complete, this operation returns
        a report as the response. You should review this report and fix any
        problems it lists to ensure your site is fully functioning again.
        The importSite operation lets you restore your site from a backup
        that you created using the exportSite operation.

        Parameters:
           location - A file path to an exported configuration or an ID
            referencing the stored configuration on the server.
        """
        return self._sm.import_site(location=location)
    #----------------------------------------------------------------------
    def upgrade(self, run_async=False):
        """
        This is the first operation that must be invoked during an ArcGIS
        Server upgrade. Once the new software version has been installed
        and the setup has completed, this operation will be available. A
        successful run of this operation will complete the upgrade of
        ArcGIS Server.

        **caution**
        If errors are returned with the upgrade operation, you must address
        the errors before you may continue. For example, if you encounter
        an error about an invalid license, you will need to re-authorize
        the software using a valid license and you may then retry this
        operation.

        **note**
        This operation is available only when a server machine is currently
        being upgraded. It will not be available after a successful upgrade
        of a server machine.

        Paramters:
         :run_async: A flag to indicate if the operation needs to be run
          asynchronously. The default value is false.
        """
        return self._sm.upgrade(run_async)
    #----------------------------------------------------------------------
    @property
    def public_key(self):
        """gets the public key"""
        return self._sm.public_key




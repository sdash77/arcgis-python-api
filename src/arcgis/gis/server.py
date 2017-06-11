import ssl
import logging
import arcgis


from arcgis._impl.common._mixins import PropertyMap

from arcgis._server._view import Catalog

_log = logging.getLogger(__name__)

class ServerManager(object):
    _gis = None

    def __init__(self, gis):
        self._gis = gis
        self._portal = gis._portal
        self._server_list = None

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
                self._server_list.append(Server(url=admin_url, gis=self))
            except:
                _log.warn("Could not access the server at " + admin_url)

        return self._server_list
    #----------------------------------------------------------------------


    def federate(self):
        pass
    #----------------------------------------------------------------------

class Server(object):
    """
    An ArcGIS Enterprise server used for hosting services
    """
    _url = None
    _con =  None
    _admin_url = None
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
        """An ArcGIS Enterprise server"""
        ### TODO: write doc

        ### TODO: don't set unverified context
        if not verify_cert:
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
        self._con = self._server.connection
        if not is_agol:
            self._sm = self._server.site_manager
            # self._info = self._server.info

    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._admin_url)

    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._admin_url)
    # ----------------------------------------------------------------------

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
            catalog = self.catalog
            isinstance(catalog, Catalog)
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

    # #----------------------------------------------------------------------
    # @property
    # def connection(self):
    #     """gets _server the connection object"""
    #     return self._server.connection
    #----------------------------------------------------------------------
    @property
    def users(self):
        """returns operations to work with users"""
        if self._sm:
            from arcgis._server._server import UserManager
            return UserManager(self._sm)
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
            return self._sm.machines
        return

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
            return self._sm.logs
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
            from arcgis._server import User
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
            from arcgis._server import SystemManager
            return SystemManager(self._sm)

    #----------------------------------------------------------------------
    @property
    def services(self):
        """
        Provides administrator access to the services on ArcGIS Server as a
        ServerManager Object.
        """
        if self._sm:
            return ServiceManager(self)

class ServiceManager(object):
    """
    Helper class for managing services. This class is not created by users directly. An instance of this class,
    called ‘services’, is available as a property of the Server object. Users call methods on this ‘services’ object to
    managing services.
    """
    def __init__(self, server):
        self._svcmgr = server._sm.services
        self._server = server

    @property
    def folders(self):
        """ returns a list of all folders """
        return self._svcmgr.folders

    def list(self, folder='/'):
        """ returns a list of services in the specified folder """
        self._svcmgr.folder = folder
        services =  self._svcmgr.services
        return [Service(None, None, service=svc, svcmgr=self._svcmgr) for svc in services]

    def create_folder(self, folder, description=""):
        """
           Creates a unique folder
           Inputs:
              folder_name - name of folder
              description - describes the folder
           Output:
              result as dictionary
        """
        return self._svcmgr.create_folder(self, folder, description)

    def delete_folder(self, folder):
        """
           Deletes a folder
           Inputs:
              folder - name of folder to remove
           Output:
              bool
        """
        return self._svcmgr.delete_folder(folder)

    def publish_sd(self, sd_file_path, folder=None):
        """
        Publishes a service definition file to the server
        :param sd_file_path: service defition file
        :param folder: optional folder name
        :return: True if published, False otherwise
        """
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
        return self._svcmgr.create_service(service)

    def exists(self, folder_name, name=None, service_type=None):
        """
        This operation allows you to check whether a folder or a service
        exists. To test if a folder exists, supply only a folder_name. To
        test if a service exists in a root folder, supply both serviceName
        and service_type with folder_name=None. To test if a service exists
        in a folder, supply all three parameters.

        Inputs:
           folder_name - a folder name
           name - a service name
           service_type - a service type. Allowed values:
                GeometryServer | ImageServer | MapServer | GeocodeServer |
                GeoDataServer | GPServer | GlobeServer | SearchServer
        """
        return self._svcmgr.exists(folder_name, name, service_type)

class Service(object):
    """A GIS service"""
    _service = None
    _svcmgr = None

    def __init__(self, url, server, **kwargs):
        service = kwargs.pop('service', None)
        svcmgr = kwargs.pop('svcmgr', None)
        if service is not None:
            self._service = service
            self._svcmgr = svcmgr
        else:
            self._service = arcgis._server.admin._services.Service(url, server._con)

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

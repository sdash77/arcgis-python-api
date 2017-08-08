"""
The System resource is a collection of miscellaneous server-wide
resources such as server properties, server directories, the
configuration store, Web Adaptors, and licenses.
"""
from __future__ import absolute_import
from __future__ import print_function
from .._common import BaseServer

########################################################################
class System(BaseServer):
    """
    The System resource is a collection of miscellaneous server-wide
    resources such as server properties, server directories, the
    configuration store, Web Adaptors, and licenses.
    """
    _json = None
    _json_dict = None
    _con = None
    _url = None
    _resources = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor"""
        super(System, self).__init__(connection=connection,
                                     url=url)
        self._con = connection
        if url.lower().endswith("/system"):
            self._url = url
        else:
            self._url = url + "/system"
        if initialize:
            self._init(connection)
    #----------------------------------------------------------------------
    @property
    def server_properties(self):
        """gets the server properties for the site as an object"""
        return ServerProperties(url=self._url + "/properties",
                                connection=self._con,
                                initialize=True)
    #----------------------------------------------------------------------
    @property
    def server_directories(self):
        """returns the server directory object in a list"""
        directs = []
        url = self._url + "/directories"
        params = {
            "f" : "json"
        }
        res = self._con.get(path=url,
                            params=params)
        for direct in res['directories']:
            directs.append(
                ServerDirectory(url=url + "/%s" % direct["name"],
                                connection=self._con,
                                initialize=True))
        return directs
    #----------------------------------------------------------------------
    def get_directory(self, name):
        """
        Gets a single directory registered with ArcGIS Server

        Parameters:
         :name: name of the registered directory
        """
        url = self._url + "/directories"
        params = {
            "f" : "json"
        }
        res = self._con.get(path=url,
                            params=params)
        for direct in res['directories']:
            if name.lower() == direct['name'].lower():
                return ServerDirectory(url=url + "/%s" % direct["name"],
                                       connection=self._con,
                                       initialize=True)
        return None
    #----------------------------------------------------------------------
    def register(self,
                 name,
                 physica_path,
                 directory_type,
                 max_age,
                 cleanup_mode="NONE",
                 description=None):
        """
        Registers a new server directory. While registering the server
        directory, you can also specify the directory's cleanup parameters

        Parameters:
         :name: The name of the server directory.
         :physica_path: The absolute physical path of the server directory.
         :directory_type: The type of server directory.
         :cleanup_mode: Defines if files in the server directory needs to be
          cleaned up.
         :max_age: Defines how long a file in the directory needs to be
          kept before it is deleted.
         :description:  An optional description for the server directory.
        """
        url = self._url + "/directories/register"
        params = {
            "name" : name,
            "physicalPath" : physica_path,
            "directoryType" : directory_type,
            "cleanupMode" : cleanup_mode,
            "maxFileAge" : max_age
        }
        if description:
            params['description'] = description
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res

    #----------------------------------------------------------------------
    @property
    def licenses(self):
        """
        The licenses resource lists the current license level of ArcGIS for
        Server and all authorized extensions. Contact Esri Customer Service
        if you have questions about license levels or expiration properties.
        """
        url = self._url + "/licenses"
        params = {
            "f" : "json"
        }
        return self._con.get(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    @property
    def jobs(self):
        """get the Jobs object"""
        url = self._url + "/jobs"
        return Jobs(url=url,
                    connection=self._con,
                    initialize=True)
    #----------------------------------------------------------------------
    @property
    def web_adaptors(self):
        """
        This property lists all the Web Adaptors that have been registered
        with the site. The server will trust all these Web Adaptors and
        will authorize calls from these servers.
        To configure a new Web Adaptor with the server, you'll need to use
        the configuration web page or the command line utility. For full
        instructions, see Configuring the Web Adaptor after installation.
        """
        url = self._url + "/webadaptors"
        params = {
            "f" : "json"
        }
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    @property
    def web_adaptors_configuration(self):
        """
        The Web Adaptors configuration is a resource for all the
        configuration parameters shared across all the Web Adaptors in the
        site. Most importantly, this resource lists the shared key that is
        used by all the Web Adaptors to encrypt key data bits in the
        incoming requests to the server.
        """
        url = self._url + "/webadaptors/config"
        params = {
            "f" : "json"
        }
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def update_web_adaptors_configuration(self, config):
        """
        You can use this operation to change the configuration parameters
        and shared key.

        Inputs:
           config - the sharedkey attribute must always be
            present in this JSON
        """
        url = self._url + "/webadaptors/config/update"
        params = {
            "f" : "json",
            "webAdaptorConfig" : config
        }
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def update_web_adaptor(self,
                           wa_id,
                           description,
                           http_port,
                           https_port):
        """
        This operation allows you to update the description, HTTP port, and
        HTTPS port of a Web Adaptor that is registered with the server.

        **Note**
        This operation is only meant to change the descriptive properties
        of the Web Adaptor and does not affect the configuration of the web
        server that deploys your Web Adaptor.

        Parameters:
         :wa_id: web adaptor id
         :description: descriptive text
         :http_port: The HTTP port of the web server
         :https_port: the HTTPS (SSL) port of the web server
        """
        url = self._url + "/webadaptors/{w}/update".format(w=wa_id)
        params = {
            'f' : 'json',
            'description' : description,
            'httpPort' : http_port,
            'httpsPort' : https_port
        }
        res = self._con.post(path=url,
                              postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def unregister_webadaptor(self, wa_id):
        """
        Unregistering a Web Adaptor removes the Web Adaptor from the
        server's trusted list. The Web Adaptor can no longer submit requests
        to the server.
        """
        url = self._url + "/webadaptors/{waid}/update".format(
            waid=wa_id)
        params = {
            "f" : "json",
        }
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    @property
    def configuration_store(self):
        """returns the ConfigurationStore object for this site"""
        url = self._url + "/configstore"

        return ConfigurationStore(url=url,
                                  connection=self._con)
    #----------------------------------------------------------------------
    def clear_rest_cache(self):
        """
        This operation clears the cache on all REST handlers in the system.
        While the server typically manages the REST cache for you, use this
        operation to get explicit control over the cache.
        """
        params = {'f': 'json'}
        url = self._url + "/handlers/rest/cache/clear"
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    @property
    def deployment(self):
        """
        ArcGIS Server has a deployment configuration resource that can
        control the load balancing functionality between GIS server
        machines:
           singleClusterMode-At 10.4, in large sites with a single cluster,
           the site is configured to prevent load balancing between GIS
           server machines. This reduces network traffic between machines
           in the site and helps reduce load on your network. The default
           is true for new installations of ArcGIS Server, meaning that
           load balancing is disabled. Upgrades from earlier versions will
           set this property to true if the site uses a single cluster.
           Sites with multiple clusters cannot use singleClusterMode.
           To prevent load balancing, the following criteria must be met:
            - All machines in the site must participate in a single
              cluster. Multiple clusters cannot exist.
            - An external load balancer or ArcGIS Web Adaptor must be
             configured to forward requests to the site. If no external
             gateway exists, requests will only be handled by the
             machine designated in the request.
           To enable load balancing, set this property to false. Updating
           this property will restart all machines in the site.
        """
        url = self._url + "/deployment"
        params = {
            "f" : "json"
        }
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def edit_services_directory(self,
                                allowed_origins,
                                arcgis_com_map,
                                arcgis_com_map_text,
                                jsapi_arcgis,
                                jsapi_arcgis_css,
                                jsapi_arcgis_css2,
                                jsapi_arcgis_sdk,
                                service_dir_enabled):
        """
        With this operation you can enable or disable the HTML view of
        ArcGIS REST API (also known as the Services Directory). You can
        also adjust the JavaScript and map viewer previews of services in
        the Services Directory so that they work with your own locally
        hosted JavaScript API and map viewer.

        Parameters:
         :allowed_origins: Comma-separated list of URLs of domains allowed to make
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
         :service_dir_enabled: Flag to enable/disable the HTML view of the
          services directory.
        """
        params = {
            "f" : "json",
            "allowedOrigins": allowed_origins,
            "arcgis.com.map" : arcgis_com_map,
            "arcgis.com.map.text" : arcgis_com_map_text,
            "jsapi.arcgis" : jsapi_arcgis,
            "jsapi.arcgis.css" : jsapi_arcgis_css,
            "jsapi.arcgis.css2" : jsapi_arcgis_css2,
            "jsapi.arcgis.sdk" : jsapi_arcgis_sdk,
            "servicesDirEnabled" : service_dir_enabled
        }
        url = self._url + "/handlers/rest/servicesdirectory/edit"
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    @property
    def handlers(self):
        """
        A handler exposes the GIS capabilities of ArcGIS Server through a
        specific interface/API. There are two types of handlers currently
        available in the server:
          Rest-Exposes the REST-ful API
          Soap-Exposes the SOAP API
        The Rest Handler resource exposes some of the administrative
        operations on the REST handler such as clearing the cache.
        """
        url = self._url + "/handlers"
        params = {"f" : "json"}
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    @property
    def rest_handler(self):
        """
        Provides a list of resources accessible throught the REST API
        """
        url = self._url + "/handlers/rest"
        params = {'f': 'json'}
        return self._con.get(path=url,
                             params=params)

########################################################################
class ConfigurationStore(BaseServer):
    """
    Configuration store helper
    """
    _con = None
    _url = None
    _json = None
    _json_dict = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 connection,
                 initialize=False):
        """Constructor"""
        super(ConfigurationStore, self).__init__(connection=connection,
                                                 url=url)
        self._url = url
        self._con = connection
        if initialize:
            self._init(connection)
    #----------------------------------------------------------------------
    def recover(self):
        """
        If the shared configuration store for a site is unavailable, a site
        in read-only mode will operate in a degraded capacity that allows
        access to the ArcGIS Server Administrator Directory. You can recover
        a site if the shared configuration store is permanently lost. The
        site must be in read-only mode, and the site configuration files
        must have been copied to the local repository when switching site
        modes. The recover operation will copy the configuration store from
        the local repository into the shared configuration store location.
        The copied local repository will be from the machine in the site
        where the recover operation is performed.
        """
        url = self._url + "/recover"
        params = {"f" : "json"}
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def edit(self,
             type_value,
             connection,
             move=True,
             run_async=False):
        """
        You can use this operation to update the configuration store.
        Typically, this operation is used to change the location of the
        store.
        When ArcGIS Server is installed, the default configuration store
        uses local paths. As the site grows (more server machines are
        added), the location of the store must be updated to use a shared
        file system path. On the other hand, if you know at the onset that
        your site will have two or more server machines, you can start from
        a shared path while creating a site and skip this step altogether.

        Inputs:
           type_value - Type of the configuration store. Values: FILESYSTEM
           connection - A file path or connection URL to the physical
            location of the store.
           move - default True - A boolean to indicate if you want to move
            the content of the current store to the new store.
           run_async - default False - Decides if this operation must run
            asynchronously.
        """
        url = self._url + "/edit"
        params = {
            "f" : "json",
            "type" : type_value,
            "connectionString" : connection,
            "move" : move,
            "runAsync" : run_async
        }
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
########################################################################
class Jobs(BaseServer):
    """
    This resource is a collection of all the administrative jobs
    (asynchronous operations) created within your site. When operations
    that support asynchronous execution are run, the server creates a new
    job entry that can be queried for its current status and messages.
    """
    _con = None
    _json = None
    _jobs = None
    _json_dict = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self, url,
                 connection,
                 initialize=False):
        """Constructor"""
        super(Jobs, self).__init__(connection=connection,
                                   url=url)
        self._url = url
        self._con = connection
        if initialize:
            self._init(connection)
    #----------------------------------------------------------------------
    @property
    def jobs(self):
        """gets the job ids"""
        if self._jobs is None:
            self._init()
        return self._jobs
    #----------------------------------------------------------------------
    def get(self, job_id):
        """
        A job represents the asynchronous execution of an operation. You
        can acquire progress information by periodically querying the job.

        Inputs:
           job_id - id of the job
        """
        url = self._url + "/%s" % job_id
        params = {
            "f" : "json"
        }
        return self._con.get(path=url,
                             params=params)
########################################################################
class ServerProperties(BaseServer):
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
    _con = None
    _url = None
    _json = None
    _json_dict = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 connection,
                 initialize=False):
        """Constructor"""
        super(ServerProperties, self).__init__(connection=connection,
                                               url=url)
        if url.lower().endswith('/properties'):
            self._url = url
        else:
            self._url = url + "/properties"
        if initialize:
            self._init(connection)
    #----------------------------------------------------------------------
    def update(self, properties):
        """
        This operation allows you to update the server property
        """
        url = self._url + "/update"
        params = {
            "f" : "json",
            "properties" : properties
        }
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
########################################################################
class ServerDirectory(BaseServer):
    """
    Server directories are used by GIS services as a location to output
    items such as map images, tile caches, and geoprocessing results. In
    addition, some directories contain configurations that power the GIS
    services.
    In a Site with more than one server machine these directories must be
    available on network shares, accessible to every machine in the site.

    The following directory types can be registered with the server:
     Output - Stores various information generated by services, such as map
      images. Instances: One or more
     Cache - Stores tile caches used by map, globe, and image services for
      rapid performance. Instances: One or more
     Jobs - Stores results and other information from geoprocessing
      services. Instances: One or more
     System - Stores files that are used internally by the GIS server.
      Instances: One Server directories that contain output of various GIS
      services can be periodically cleaned to remove old unused files. By
      using the cleanup mode and maximum file age parameters, you control
      when when you would like the files in these directories to be
      cleaned.

    All the output server directories are automatically virtualized (they
    can be accessed over a URL) for you through the ArcGIS Server REST API.
    """
    _con = None
    _url = None
    _json = None
    _json_dict = None
    _url = None
    _name = None
    _physicalPath = None
    _directoryType = None
    _cleanupMode = None
    _maxFileAge = None
    _description = None
    _virtualPath = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 connection,
                 initialize=False):
        """Constructor"""
        super(ServerDirectory, self).__init__(connection=connection,
                                              url=url)
        self._url = url
        self._con = connection
        if initialize:
            self._init(connection)
    #----------------------------------------------------------------------
    def edit(self,
             physica_path,
             cleanup_mode,
             max_age,
             description):
        """
        The server directory's edit operation allows you to change the path
        and clean up properties of the directory. This operation updates
        the GIS service configurations (and points them to the new path)
        that are using this directory, causing them to restart. It is
        therefore recommended that any edit to the server directories be
        performed when the server is not under load.
        This operation is mostly used when growing a single machine site to
        a multiple machine site configuration, which requires that the
        server directories and configuration store be put on a
        network-accessible file share.

        Inputs:
           physica_path - The absolute physical path of the server
            directory.
           cleanup_mode - Defines if files in the server directory needs to
            be cleaned up. The default is NONE.
           max_age - Defines how long a file in the directory needs to
            be kept before it is deleted.
           description - An optional description for the server directory
        """
        url = self._url + "/edit"
        params = {
            "f" : "json",
            "physicalPath" : physica_path,
            "cleanupMode" : cleanup_mode,
            "maxFileAge" : max_age,
            "description" : description
        }
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def clean(self):
        """
        Cleans the content (files and folders) within the directory that
        have passed their expiration date. Every server directory has the
        max file age and cleanup mode parameter that govern when a file
        created inside is supposed to be cleaned up. The server directory
        cleaner automatically cleans up the content within server
        directories at regular intervals. However, you can explicitly clean
        the directory by invoking this operation.
        """
        url = self._url + "/clean"
        params = {
            "f" : "json"
        }
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def recover_directory(self):
        """
        If the shared server directories for a site are unavailable, a site
        in read-only mode will operate in a degraded capacity that allows
        access to the ArcGIS Server Administrator Directory. You can recover
        a site if the shared server directories are permanently lost. The
        site must be in read-only mode, and the site configuration files
        must have been copied to the local repository when switching site
        modes. The recover operation will copy the server directories from
        the local repository into the shared server directories location.
        The copied local repository will be from the machine in the site
        where the recover operation is performed.
        """
        url = self._url + "/recover"
        params = {'f': 'json'}
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def unregister(self):
        """
        Unregisters a server directory. Once a directory has been
        unregistered, it can no longer be referenced (used) from within a
        GIS service.
        """
        url = self._url + "/unregister"
        params = {
            "f" : "json"
        }
        res = self._con.post(path=url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res

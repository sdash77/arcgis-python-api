from __future__ import absolute_import
from __future__ import print_function
from .._common import BaseServer
from .parameters import Extension
import os
import json
import tempfile
########################################################################
class Services(BaseServer):
    """ returns information about the services on AGS """
    _currentURL = None
    _url = None
    _con = None
    _json_dict = None
    _folderName = None
    _folders = None
    _foldersDetail = None
    _folderDetail = None
    _webEncrypted = None
    _description = None
    _isDefault = None
    _services = None
    _json = None
    #----------------------------------------------------------------------
    def __init__(self, url, connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection object
        """
        super(Services, self).__init__(connection=connection,
                                       url=url)
        self._con = connection
        self._url = url
        self._currentURL = url
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    @property
    def webEncrypted(self):
        """ returns if the server is web encrypted """
        if self._webEncrypted is None:
            self.init()
        return self._webEncrypted
    #----------------------------------------------------------------------
    @property
    def folderName(self):
        """ returns current folder """
        return self._folderName
    #----------------------------------------------------------------------
    @folderName.setter
    def folderName(self, folder):
        """gets/set the current folder"""

        if folder == "" or\
             folder == "/":
            self._currentURL = self._url
            self._services = None
            self._description = None
            self._folderName = None
            self._webEncrypted = None
            self.init()
            self._folderName = folder
        elif folder in self.folders:
            self._currentURL = self._url + "/%s" % folder
            self._services = None
            self._description = None
            self._folderName = None
            self._webEncrypted = None
            self.init()
            self._folderName = folder
    #----------------------------------------------------------------------
    @property
    def folders(self):
        """ returns a list of all folders """
        if self._folders is None:
            self.init()
        if "/" not in self._folders:
            self._folders.append("/")
        return self._folders
    #----------------------------------------------------------------------
    @property
    def foldersDetail(self):
        """returns the folder's details"""
        if self._foldersDetail is None:
            self.init()
        return self._foldersDetail
    #----------------------------------------------------------------------
    @property
    def description(self):
        """ returns the decscription """
        if self._description is None:
            self.init()
        return self._description
    #----------------------------------------------------------------------
    @property
    def isDefault(self):
        """ returns the is default property """
        if self._isDefault is None:
            self.init()
        return self._isDefault
    #----------------------------------------------------------------------
    @property
    def services(self):
        """ returns the services in the current folder """
        self._services = []
        params = {
                    "f" : "json"
                }
        json_dict = self._con.get(path=self._currentURL,
                                 params=params)
        if "services" in json_dict.keys():
            for s in json_dict['services']:
                uURL = self._currentURL + "/%s.%s" % (s['serviceName'], s['type'])
                self._services.append(
                    Service(url=uURL,
                               connection=self._con)
                )
        return self._services
    #----------------------------------------------------------------------
    @property
    def extensions(self):
        """
        This resource is a collection of all the custom server object
        extensions that have been uploaded and registered with the server.
        You can register new server object extensions using the register
        extension operation. When updating an existing extension, you need
        to use the update extension operation. If an extension is no longer
        required, you can use the unregister operation to remove the
        extension from the site.
        """
        url = self._url + "/types/extensions"
        params = {'f' : 'json'}
        return self._con.get(path=url,
                             params=params)
    #----------------------------------------------------------------------
    def find_services(self, service_type="*"):
        """
            returns a list of a particular service type on AGS
            Input:
              service_type - Type of service to find.  The allowed types
                             are: ("GPSERVER", "GLOBESERVER", "MAPSERVER",
                             "GEOMETRYSERVER", "IMAGESERVER",
                             "SEARCHSERVER", "GEODATASERVER",
                             "GEOCODESERVER", "*").  The default is *
                             meaning find all service names.
            Output:
              returns a list of service names as <folder>/<name>.<type>
        """
        allowed_service_types = ("GPSERVER", "GLOBESERVER", "MAPSERVER",
                                 "GEOMETRYSERVER", "IMAGESERVER",
                                 "SEARCHSERVER", "GEODATASERVER",
                                 "GEOCODESERVER", "*")
        lower_types = [l.lower() for l in service_type.split(',')]
        for v in lower_types:
            if v.upper() not in allowed_service_types:
                return {"message" : "%s is not an allowed service type." % v}
        params = {
            "f" : "json"
        }
        type_services = []
        folders = self.folders
        folders.append("")
        baseURL = self._url
        for folder in folders:
            if folder == "":
                url = baseURL
            else:
                url = baseURL + "/%s" % folder
            res = self._con.get(path=url, params=params)
            if res.has_key("services"):
                for service in res['services']:
                    if service['type'].lower() in lower_types:
                        service['URL'] = url + "/%s.%s" % (service['serviceName'],
                                                           service_type)
                        type_services.append(service)
                    del service
            del res
            del folder
        return type_services
    #----------------------------------------------------------------------
    def examineFolder(self, folder=None):
        """
        A folder is a container for GIS services. ArcGIS Server supports a
        single level hierarchy of folders.
        By grouping services within a folder, you can conveniently set
        permissions on them as a single unit. A folder inherits the
        permissions of the root folder when it is created, but you can
        change those permissions at a later time.

        Parameters:
         :folder: name of folder to exmine
        """
        params = {'f': 'json'}
        if folder:
            url = self._url + "/" + folder
        else:
            url = self._url
        return self._con.get(path=url, params=params)
    #----------------------------------------------------------------------
    def canCreateService(self,
                         service,
                         options=None,
                         folderName=None,
                         serviceType=None
                         ):
        """
        Use canCreateService to determine whether a specific service can be
        created on the ArcGIS Server site.

        Parameters:
         :folderName: This is an optional parameter to indicate the folder
          where canCreateService will check for the service.
         :serviceType: The type of service that can be created. This is an
          optional parameter, though either theserviceType or service
          parameter must be used.
         :service: The service configuration in JSON format. For more
          information about the service configuration options, see
          createService. This is an optional parameter, though either the
          serviceType or service parameter must be used.
         :options: This is an optional parameter that provides additional
          information about the service, such as whether it is a hosted
          service.
        """
        url = self._url + "/canCreateService"
        params = {"f" : "json",
                  'service' : service}
        if options:
            params['options'] = options
        if folderName:
            params['folderName'] = folderName
        if serviceType:
            params['serviceType'] = serviceType
        return self._con.post(path=url,
                              postdata=params)

    #----------------------------------------------------------------------
    def addFolderPermission(self, principal, isAllowed=True, folder=None):
        """
           Assigns a new permission to a role (principal). The permission
           on a parent resource is automatically inherited by all child
           resources
           Input:
              principal - name of role to assign/disassign accesss
              isAllowed -  boolean which allows access
           Output:
              JSON message as dictionary
        """
        if folder is not None:
            uURL = self._url + "/%s/%s" % (folder, "/permissions/add")
        else:
            uURL = self._url + "/permissions/add"
        params = {
            "f" : "json",
            "principal" : principal,
            "isAllowed" : isAllowed
        }
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def listFolderPermissions(self,folderName):
        """
           Lists principals which have permissions for the folder.
           Input:
              folderName - name of the folder to list permissions for
           Output:
              JSON Message as Dictionary
        """
        uURL = self._url + "/%s/permissions" % folderName
        params = {
            "f" : "json",
        }
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def cleanPermissions(self, principal):
        """
           Cleans all permissions that have been assigned to a role
           (principal). This is typically used when a role is deleted.
           Input:
              principal - name of the role to clean
           Output:
              JSON Message as Dictionary
        """
        uURL = self._url + "/permissions/clean"
        params = {
            "f" : "json",
            "principal" : principal
        }
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def createFolder(self, folderName, description=""):
        """
           Creates a unique folder name on AGS
           Inputs:
              folderName - name of folder on AGS
              description - describes the folder
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "folderName" : folderName,
            "description" : description
        }
        uURL = self._url + "/createFolder"
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def deleteFolder(self, folderName):
        """
           deletes a folder on AGS
           Inputs:
              folderName - name of folder to remove
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json"
        }
        if folderName in self.folders:
            uURL = self._url + "/%s/deleteFolder" % folderName
            return self._con.post(path=uURL, postdata=params)
        else:
            return {"error" : "folder does not exist"}
    #----------------------------------------------------------------------
    def deleteService(self, serviceName, serviceType, folder=None):
        """
           deletes a service from AGS
           Inputs:
              serviceName - name of the service
              serviceType - type of the service
              folder - name of the folder the service resides, leave None
                       for root.
           Output:
              JSON message as dictionary
        """
        if folder is None:
            uURL = self._url + "/%s.%s/delete" % (serviceName,
                                                  serviceType)
        else:
            uURL = self._url + "/%s/%s.%s/delete" % (folder,
                                                     serviceName,
                                                     serviceType)
        params = {
            "f" : "json"
        }
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def service_report(self, folder=None):
        """
           provides a report on all items in a given folder
           Inputs:
              folder - folder to report on given services. None means root
        """
        items = ["description", "status",
                 "instances", "iteminfo",
                 "properties"]
        if folder is None:
            uURL = self._url + "/report"
        else:
            uURL = self._url + "/%s/report" % folder
        params = {
            "f" : "json",
            "parameters" : items
        }
        return self._con.get(path=uURL, params=params)
    #----------------------------------------------------------------------
    @property
    def types(self):
        """ returns the allowed services types """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/types"
        return self._con.get(path=uURL,
                            params=params)
    #----------------------------------------------------------------------
    def federate(self):
        """
        This operation is used when federating ArcGIS Server with Portal
        for ArcGIS. It imports any services that you have previously
        published to your ArcGIS Server site and makes them available as
        items with Portal for ArcGIS. Beginning at 10.3, services are
        imported automatically as part of the federate process.
        If the automatic import of services fails as part of the federation
        process, the following severe-level message will appear in the
        server logs:
           Failed to import GIS services as items within portal.
        If this occurs, you can manually re-run the operation to import
        your services as items in the portal. Before you do this, obtain a
        portal token and then validate ArcGIS Server is federated with
        your portal using the portal website. This is done in
        My Organization > Edit Settings > Servers.
        After you run the Federate operation, specify sharing properties to
        determine which users and groups will be able to access each service.
        """
        params = {'f' : 'json'}
        url = self._url + "/federate"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def unfederate(self):
        """
        This operation is used when unfederating ArcGIS Server with Portal
        for ArcGIS. It removes any items from the portal that represent
        services running on your federated ArcGIS Server. You typically run
        this operation in preparation for a full unfederate action. For
        example, this can be performed using
               My Organization > Edit Settings > Servers
        in the portal website or the Unregister Server operation in the
        ArcGIS REST API.
        Beginning at 10.3, services are removed automatically as part of
        the unfederate process. If the automatic removal of service items
        fails as part of the unfederate process, you can manually re-run
        the operation to remove the items from the portal.
        """
        params = {'f' : 'json'}
        url = self._url + "/unfederate"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def unregisterExtension(self, extensionFilename):
        """
        Unregisters all the extensions from a previously registered server
        object extension (.SOE) file.

        Parameters:
         :extensionFilename: name of the previously registered .SOE file
        """
        params = {
            "f" : "json",
            "extensionFilename" : extensionFilename
        }
        url = self._url + "/types/extensions/unregister"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def updateExtension(self, itemID):
        """
        Updates extensions that have been previously registered with the
        server. All extensions in the new .SOE file must match with
        extensions from a previously registered .SOE file.
        Use this operation to update your implementations or extension
        configuration properties.

        Parameters:
         :itemID: itemID of the uploaded .SOE file
        """
        params = {'f':'json',
                  'id': itemID}
        url = self._url + "/types/extensions/update"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    def rename_service(self, serviceName, serviceType,
                       serviceNewName, folder=None):
        """
           Renames a published AGS Service
           Inputs:
              serviceName - old service name
              serviceType - type of service
              serviceNewName - new service name
              folder - location of where the service lives, none means
                       root folder.
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "serviceName" : serviceName,
            "serviceType" : serviceType,
            "serviceNewName" : serviceNewName
        }
        if folder is None:
            uURL = self._url + "/renameService"
        else:
            uURL = self._url + "/%s/renameService" % folder
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def createService(self, service):
        """
        Creates a new GIS service in the folder. A service is created by
        submitting a JSON representation of the service to this operation.
        """
        url = self._url + "/createService"
        params = {
            "f" : "json"
        }
        if isinstance(service, str):
            params['service'] = service
        elif isinstance(service, dict):
            params['service'] = json.dumps(service)
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def stopServices(self, services ):
        """
        Stops serveral services on a single server
        Inputs:
           services - is a list of dictionary objects. Each dictionary
                      object is defined as:
                        folderName - The name of the folder containing the
                        service, for example, "Planning". If the service
                        resides in the root folder, leave the folder
                        property blank ("folderName": "").
                        serviceName - The name of the service, for example,
                        "FireHydrants".
                        type - The service type, for example, "MapServer".
                     Example:
                        [{
                          "folderName" : "",
                          "serviceName" : "SampleWorldCities",
                          "type" : "MapServer"
                        }]
        """
        url = self._url + "/stopServices"
        if isinstance(services, dict):
            services = [services]
        elif isinstance(services, (list, tuple)):
            services = list(services)
        else:
            Exception("Invalid input for parameter services")
        params = {
            "f" : "json",
            "services" : {
                "services":services
            }
        }
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def startServices(self, services ):
        """
        starts serveral services on a single server
        Inputs:
           services - is a list of dictionary objects. Each dictionary
                      object is defined as:
                        folderName - The name of the folder containing the
                        service, for example, "Planning". If the service
                        resides in the root folder, leave the folder
                        property blank ("folderName": "").
                        serviceName - The name of the service, for example,
                        "FireHydrants".
                        type - The service type, for example, "MapServer".
                     Example:
                        [{
                          "folderName" : "",
                          "serviceName" : "SampleWorldCities",
                          "type" : "MapServer"
                        }]
        """
        url = self._url + "/startServices"
        if isinstance(services, dict):
            services = [services]
        elif isinstance(services, (list, tuple)):
            services = list(services)
        else:
            Exception("Invalid input for parameter services")
        params = {
            "f" : "json",
            "services" : {
                "services":services
            }
        }
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def editFolder(self, description, webEncrypted=False):
        """
        This operation allows you to change the description of an existing
        folder or change the web encrypted property.
        The web encrypted property indicates if all the services contained
        in the folder are only accessible over a secure channel (SSL). When
        setting this property to true, you also need to enable the virtual
        directory security in the security configuration.

        Inputs:
           description - a description of the folder
           webEncrypted - boolean to indicate if the services are
            accessible over SSL only.
        """
        url = self._url + "/editFolder"
        params = {
            "f" : "json",
            "webEncrypted" : webEncrypted,
            "description" : "%s" % description
        }
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def exists(self, folderName, serviceName=None, serviceType=None):
        """
        This operation allows you to check whether a folder or a service
        exists. To test if a folder exists, supply only a folderName. To
        test if a service exists in a root folder, supply both serviceName
        and serviceType with folderName=None. To test if a service exists
        in a folder, supply all three parameters.

        Inputs:
           folderName - a folder name
           serviceName - a service name
           serviceType - a service type. Allowed values:
                "GPSERVER", "GLOBESERVER", "MAPSERVER",
                "GEOMETRYSERVER", "IMAGESERVER", "SEARCHSERVER",
                "GEODATASERVER", "GEOCODESERVER"
        """

        url = self._url + "/exists"
        params = {
            "f" : "json",
            "folderName" : folderName,
            "serviceName" : serviceName,
            "type" : serviceType
        }
        return self._con.post(path=url,
                              postdata=params)
########################################################################
class Service(BaseServer):
    """ Defines a AGS Admin Service """
    _con = None
    _frameworkProperties = None
    _recycleInterval = None
    _instancesPerContainer = None
    _maxWaitTime = None
    _extensions = None
    _minInstancesPerNode = None
    _maxIdleTime = None
    _maxUsageTime = None
    _allowedUploadFileTypes = None
    _datasets = None
    _properties = None
    _recycleStartTime = None
    _clusterName = None
    _description = None
    _isDefault = None
    _type = None
    _serviceName = None
    _isolationLevel = None
    _capabilities = None
    _loadBalancing = None
    _configuredState = None
    _maxStartupTime = None
    _private = None
    _maxUploadFileSize = None
    _keepAliveInterval = None
    _maxInstancesPerNode = None
    _json = None
    _json_dict = None
    _interceptor = None
    _provider = None
    _portalProperties = None
    _jsonProperties = None
    _url = None
    #----------------------------------------------------------------------
    def __init__(self,
                 url,
                 connection,
                 initialize=False):
        """Constructor
            Inputs:
               url - admin url
               connection - SiteConnection object
               initialize - fills all the properties at object creation is
                            true
        """
        super(Service, self).__init__(connection=connection,
                                      url=url)
        self._url = url
        self._currentURL = url
        self._con = connection
        if initialize:
            self.init(connection)
    #----------------------------------------------------------------------
    def init(self, connection=None):
        """ populates server admin information """
        params = {
            "f" : "json"
        }
        if connection:
            json_dict = connection.get(path=self._url,
                                       params=params)
        else:
            json_dict = self._con.get(path=self._currentURL,
                                 params=params)
        self._json = json.dumps(json_dict)
        self._json_dict = json_dict
        attributes = [attr for attr in dir(self)
                    if not attr.startswith('__') and \
                    not attr.startswith('_')]
        for k,v in json_dict.items():
            if k.lower() == "extensions":
                self._extensions = []
                for ext in v:
                    self._extensions.append(Extension.fromJSON(ext))
                    del ext
            elif k in attributes:
                setattr(self, "_"+ k, json_dict[k])
            else:
                setattr(self, k, v)
            del k
            del v
    #----------------------------------------------------------------------
    def refreshProperties(self):
        """refreshes the object's values by re-querying the service"""
        self.init()
    #----------------------------------------------------------------------
    def jsonProperties(self):
        """returns the jsonProperties"""
        if self._jsonProperties is None:
            self.init()
        return self._jsonProperties
    #----------------------------------------------------------------------
    @property
    def frameworkProperties(self):
        """returns the framework properties for an AGS instance"""
        if self._frameworkProperties is None:
            self.init()
        return self._frameworkProperties
    #----------------------------------------------------------------------
    @property
    def portalProperties(self):
        """returns the service's portal properties"""
        if self._portalProperties is None:
            self.init()
        return self._portalProperties
    #----------------------------------------------------------------------
    @property
    def interceptor(self):
        """returns the interceptor property"""
        if self._interceptor is None:
            self.init()
        return self._interceptor
    #----------------------------------------------------------------------
    @property
    def provider(self):
        """returns the provider for the service"""
        if self._provider is None:
            self.init()
        return self._provider
    #----------------------------------------------------------------------
    @property
    def recycleInterval(self):
        if self._recycleInterval is None:
            self.init()
        return self._recycleInterval
    #----------------------------------------------------------------------
    @property
    def instancesPerContainer(self):
        if self._instancesPerContainer is None:
            self.init()
        return self._instancesPerContainer
    #----------------------------------------------------------------------
    @property
    def maxWaitTime(self):
        if self._maxWaitTime is None:
            self.init()
        return self._maxWaitTime
    #----------------------------------------------------------------------
    @property
    def extensions(self):
        if self._extensions is None:
            self.init()
        return self._extensions
    #----------------------------------------------------------------------
    def modifyExtensions(self,
                         extensionObjects=None):
        """
        enables/disables a service extension type based on the name
        """
        if extensionObjects is None:
            extensionObjects = []
        if len(extensionObjects) > 0 and \
           isinstance(extensionObjects[0], Extension):
            self._extensions = extensionObjects
            res = self.edit(str(self))
            self._json = None
            self.init()
            return res
    #----------------------------------------------------------------------
    def hasChildPermissionsConflict(self, principal, permission):
        """
        You can invoke this operation on the resource (folder or service)
        to determine if this resource has a child resource with opposing
        permissions. This operation is typically invoked before adding a
        new permission to determine if the new addition will overwrite
        existing permissions on the child resources.
        For more information, see the section on the Continuous Inheritance
        Model.
        Since this operation basically checks if the permission to be added
        will cause a conflict with permissions on a child resource, this
        operation takes the same parameters as the Add Permission operation.

        Parameters:
         :principal: name of the role for whom the permission is being
          assigned
         :permission: The permission JSON object. The format is described
          below.
          Format:
           {
           "isAllowed": <true|false>,
           "constraint": ""
           }
        """
        params = {
            "f" : "json",
            "principal" : principal,
            "permission" : permission
        }
        url = self._url + "/permissions/hasChildPermissionsConflict"
        return self._con.post(path=url,
                              postdata=params)
    #----------------------------------------------------------------------
    @property
    def minInstancesPerNode(self):
        if self._minInstancesPerNode is None:
            self.init()
        return self._minInstancesPerNode
    #----------------------------------------------------------------------
    @property
    def maxIdleTime(self):
        if self._maxIdleTime is None:
            self.init()
        return self._maxIdleTime
    #----------------------------------------------------------------------
    @property
    def maxUsageTime(self):
        if self._maxUsageTime is None:
            self.init()
        return self._maxUsageTime
    #----------------------------------------------------------------------
    @property
    def allowedUploadFileTypes(self):
        if self._allowedUploadFileTypes is None:
            self.init()
        return self._allowedUploadFileTypes
    #----------------------------------------------------------------------
    @property
    def datasets(self):
        if self._datasets is None:
            self.init()
        return self._datasets
    #----------------------------------------------------------------------
    @property
    def properties(self):
        if self._properties is None:
            self.init()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def recycleStartTime(self):
        if self._recycleStartTime is None:
            self.init()
        return self._recycleStartTime
    #----------------------------------------------------------------------
    @property
    def clusterName(self):
        if self._clusterName is None:
            self.init()
        return self._clusterName
    #----------------------------------------------------------------------
    @property
    def description(self):
        if self._description is None:
            self.init()
        return self._description
    #----------------------------------------------------------------------
    @property
    def isDefault(self):
        if self._isDefault is None:
            self.init()
        return self._isDefault
    #----------------------------------------------------------------------
    @property
    def type(self):
        if self._type is None:
            self.init()
        return self._type
    #----------------------------------------------------------------------
    @property
    def maxUploadFileSize(self):
        if self._maxUploadFileSize is None:
            self.init()
        return self._maxUploadFileSize
    #----------------------------------------------------------------------
    @property
    def keepAliveInterval(self):
        if self._keepAliveInterval is None:
            self.init()
        return self._keepAliveInterval
    #----------------------------------------------------------------------
    @property
    def maxInstancesPerNode(self):
        if self._maxInstancesPerNode is None:
            self.init()
        return self._maxInstancesPerNode
    #----------------------------------------------------------------------
    @property
    def private(self):
        if self._private is None:
            self.init()
        return self._private
    #----------------------------------------------------------------------
    @property
    def maxStartupTime(self):
        if self._maxStartupTime is None:
            self.init()
        return self._maxStartupTime
    #----------------------------------------------------------------------
    @property
    def loadBalancing(self):
        if self._loadBalancing is None:
            self.init()
        return self._loadBalancing
    #----------------------------------------------------------------------
    @property
    def configuredState(self):
        if self._configuredState is None:
            self.init()
        return self._configuredState
    #----------------------------------------------------------------------
    @property
    def capabilities(self):
        if self._capabilities is None:
            self.init()
        return self._capabilities
    #----------------------------------------------------------------------
    @property
    def isolationLevel(self):
        if self._isolationLevel is None:
            self.init()
        return self._isolationLevel
    #----------------------------------------------------------------------
    @property
    def serviceName(self):
        if self._serviceName is None:
            self.init()
        return self._serviceName
    #----------------------------------------------------------------------
    def start_service(self):
        """ starts the specific service """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/start"
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def stop_service(self):
        """ stops the current service """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/stop"
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def restart_services(self):
        """ restarts the current service """
        self.stop_service()
        self.start_service()
        return {'status': 'success'}
    #----------------------------------------------------------------------
    def delete_service(self):
        """deletes a service from arcgis server"""
        params = {
            "f" : "json",
        }
        uURL = self._url + "/delete"
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    @property
    def status(self):
        """ returns the status of the service """
        params = {
            "f" : "json",
        }
        uURL = self._url + "/status"
        return self._con.get(path=uURL, params=params)
    #----------------------------------------------------------------------
    @property
    def statistics(self):
        """ returns the stats for the service """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/statistics"
        return self._con.get(path=uURL, params=params)
    #----------------------------------------------------------------------
    @property
    def permissions(self):
        """ returns the permissions for the service """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/permissions"
        return self._con.get(path=uURL, param_dict=params)
    #----------------------------------------------------------------------
    @property
    def iteminfo(self):
        """ returns the item information """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/iteminfo"
        return self._con.get(path=uURL, params=params)
    #----------------------------------------------------------------------
    def registerExtension(self, itemID):
        """
        Registers a new server object extension file with the server.
        Before you register the file, you need to upload the .SOE file to
        the server using the Upload Data Item operation. The itemID
        returned by the upload operation must be passed to the register
        operation.
        This operation registers all the server object extensions defined
        in the .SOE file.

        Parameters:
         :itemID: The itemID of the uploaded .SOE file.
        """
        params = {
            "id" : itemID,
            "f" : "json"
        }
        url = self._url + "/types/extensions/register"
        return self._con.post(path=url,
                              postdata=params)

    #----------------------------------------------------------------------
    def deleteItemInfo(self):
        """
        Deletes the item information.
        """
        params = {
            "f" : "json"
        }
        uURL = self._url + "/iteminfo/delete"
        return self._con.get(path=uURL, params=params)
    #----------------------------------------------------------------------
    def itemInfoUpload(self, folder, filePath):
        """
        Allows for the upload of new itemInfo files such as metadata.xml
        Inputs:
           folder - folder on ArcGIS Server
           filePath - full path of the file to upload
        Output:
           json as dictionary
        """
        files = {}
        url = self._url + "/iteminfo/upload"
        params = {
            "f" : "json",
            "folder" : folder
        }
        files['file'] = filePath
        return self._con.post(path=url,
                          postdata=params,
                          files=files)
    #----------------------------------------------------------------------
    def editItemInfo(self, json_dict):
        """
        Allows for the direct edit of the service's item's information.
        To get the current item information, pull the data by calling
        iteminfo property.  This will return the default template then pass
        this object back into the editItemInfo() as a dictionary.

        Inputs:
           json_dict - iteminfo dictionary.
        Output:
           json as dictionary
        """
        url = self._url + "/iteminfo/edit"
        params = {
            "f" : "json",
            "serviceItemInfo" : json.dumps(json_dict)
        }
        return self._con.post(path=url,
                             postdata=params)
    #----------------------------------------------------------------------
    def serviceManifest(self, fileType="json"):
        """
        The service manifest resource documents the data and other
        resources that define the service origins and power the service.
        This resource will tell you underlying databases and their location
        along with other supplementary files that make up the service.

        Inputs:
           fileType - this can be json or xml.  json return the
            manifest.json file.  xml returns the manifest.xml file.


        """

        url = self._url + "/iteminfo/manifest/manifest.%s" % fileType
        params = {
        }
        f = self._con.get(path=url,
                      params=params,
                     out_folder=tempfile.gettempdir(),
                     file_name=os.path.basename(url))
        return open(f, 'r').read()
    #----------------------------------------------------------------------
    def addPermission(self, principal, isAllowed=True):
        """
           Assigns a new permission to a role (principal). The permission
           on a parent resource is automatically inherited by all child
           resources.
           Inputs:
              principal - role to be assigned
              isAllowed - access of resource by boolean
           Output:
              JSON message as dictionary
        """
        uURL = self._url + "/permissions/add"
        params = {
            "f" : "json",
            "principal" : principal,
            "isAllowed" : isAllowed
        }
        return self._con.post(path=uURL, postdata=params)
    #----------------------------------------------------------------------
    def edit(self, service):
        """
        To edit a service, you need to submit the complete JSON
        representation of the service, which includes the updates to the
        service properties. Editing a service causes the service to be
        restarted with updated properties.
        """
        url = self._url + "/edit"
        params = {
            "f" : "json"
        }
        if isinstance(service, str):
            params['service'] = service
        elif isinstance(service, dict):
            params['service'] = json.dumps(service)
        return self._con.post(path=url, postdata=params)

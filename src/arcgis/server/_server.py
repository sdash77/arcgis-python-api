"""
Help Classes for the Server API
"""
from __future__ import division
from __future__ import absolute_import
from .admin._security import Security
from .admin._system import System
import datetime
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
        from .admin.administration import SiteManager
        if isinstance(server, SiteManager):
            self._sm = server
            self._security = server.security
            isinstance(self._security, Security)
            self._security.connection._username
        else:
            raise ValueError("UserManager must take a SiteManager object")
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
        if 'status' in res and res['status'] == 'success':
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
        Gets the user object as the current logged in user.
        """
        res = self.search(username=self._security.connection._username,
                          max_results=1)[0]
        return res
    #----------------------------------------------------------------------
    def search(self, username, max_results=25):
        """
        You can use this operation to search a specific user or a group of
        users from the user store. The size of the search result can be
        controlled with the max_results parameter.

        Inputs:
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
            fullName = self.fullName
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
        try:
            role = self.role
        except:
            role = "Not Provided"
        return """<div class="9item_container" style="height: auto; overflow: hidden; border: 1px solid #cfcfcf; border-radius: 2px; background: #f6fafa; line-height: 1.21429em; padding: 10px;">
                    <div class="item_right" style="float: none; width: auto; overflow: hidden;">
                        <br/><b>Full Name</b>: """ + str(fullName) + """
                        <br/><b>Description</b>: """ + str(description)  + """
                        <br/><b>Email</b>: """ + str(email)  + """
                        <br/><b>Role</b>: """ + str(role)  + """
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
        isinstance(self._security, Security)
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
        if isinstance(security, Security):
            self._security = security
        else:
            raise ValueError("Invalid input, must be type _security.Security")

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
        if res['status'] == 'success':
            self.__dict__.update(self._security.search_roles(
                role_filter=self.rolename,
                max_count=1)['roles'][0])
        return res
    #----------------------------------------------------------------------
    def delete(self):
        """
        deletes the current role
        """
        isinstance(self._security, Security)
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
        isinstance(self._security, Security)
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
        from .admin.administration import SiteManager
        from .admin._system import System
        if isinstance(server, SiteManager):
            self._sm = server

            self._system = server.system
        else:
            raise ValueError("SystemManager must take a SiteManager object")

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
        return self._system.serverProperties
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
    @property
    def directories(self):
        """
        Server directories are used by GIS services as a location to output
        items such as map images, tile caches, and geoprocessing results.
        In addition, some directories contain configurations that power the
        GIS services.
        """
        from .admin._system import System
        isinstance(self._system, System)
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
        from .admin._system import System
        isinstance(self._system, System)
        return self._system.register(name, physicalPath, directoryType,
                                    maxFileAge, cleanupMode, description)




########################################################################

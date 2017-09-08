"""
The security resource is a container for all resources and
operations that deal with security for your site. Under this
resource, you will find resources that represent the users and
roles in your current security configuration.
Since the content sent to and from this resource (and operations
within it) could contain confidential data like passwords, it is
recommended that this resource be accessed over HTTPS protocol.
"""
from __future__ import absolute_import
from __future__ import print_function
from .._common import BaseServer
########################################################################
class Security(BaseServer):
    """ The security resource is a container for all resources and
        operations that deal with security for your site. Under this
        resource, you will find resources that represent the users and
        roles in your current security configuration.
        Since the content sent to and from this resource (and operations
        within it) could contain confidential data like passwords, it is
        recommended that this resource be accessed over HTTPS protocol.
    """
    _url = None
    _con = None
    _resources = None
    _json_dict = None
    _json = None
    _um = None
    _rm = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis,
                 initialize=False):
        """Constructor
            Parameters:
               url - admin url

        """
        self._url = url
        self._con = gis
        if initialize:
            self._init(gis)
    #----------------------------------------------------------------------
    @property
    def users(self):
        """
        returns an object to control/manage users
        """
        if self._um is None:
            self._um = UserManager(url=self._url,
                                   gis=self._con,
                                   initialize=False)
        return self._um
    #----------------------------------------------------------------------
    @property
    def roles(self):
        """
        returns an object to manage a site's roles
        """
        if self._rm is None:
            self._rm = RoleManager(url=self._url, gis=self._con)
        return self._rm
    #----------------------------------------------------------------------
    def disable_primary_site_administrator(self):
        """
           You can use this operation to disable log in privileges for the
           primary site administrator account. This operation can only be
           invoked by an administrator in the system. To re-enable this
           account, use the Enable Primary Site Administrator operation.
        """
        dURL = self._url + "/psa/disable"
        params = {
            "f" : "json"
        }
        res = self._con.post(path=dURL, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    @property
    def primary_site_administrator_status(self):
        """ returns if the primary site admin has been disabled """
        params = {
            "f" : "json"
        }
        u_url = self._url + "/psa"
        return self._con.get(path=u_url, params=params)
    #----------------------------------------------------------------------
    def update_primary_site_administrator(self, username, password):
        """
           Updates account properties of the primary site administrator
           Parameters:
              username - You can optionally provide a new name for the
              primary site administrator account.
              password - The password for the new primary site
              administrator account.
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
        }
        if username is not None:
            params['username'] = username
        if password is not None:
            params['password'] = password
        u_url = self._url + "/psa/update"
        res = self._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res

########################################################################
class UserManager(BaseServer):
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
    _url = None
    _con = None
    _resources = None
    _json_dict = None
    _json = None
    _rm = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis,
                 initialize=False):
        """Constructor
            Parameters:
               url - admin url

        """
        self._url = url
        self._con = gis
        if initialize:
            self._init(gis)
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    @property
    def me(self):
        """
        Gets the user object as the current logged in user. If the username
        cannot be found, for example, the site administrator account, then
        just the username is returned.
        """
        res = self.search(username=self._con._username,
                          max_results=1)
        if len(res) == 0:
            return self._con._username
        return res[0]
    #----------------------------------------------------------------------
    def create(self,
                 username,
                 password,
                 fullname=None,
                 description=None,
                 email=None):
        """ Add a user account to the user store
           Parameters:
              username - The name of the user. The name must be unique in
                         the user store.
              password - The password for this user
              fullname - an optional full name for the user
              description - an option field to add comments or description
                            for the user account
              email - an optional email for the user account
        """
        params = {
            "f" : "json",
            "username" : username,
            "password" : password,
        }
        if fullname is not None:
            params['fullname'] = fullname
        if description is not None:
            params['description'] = description
        if email is not None:
            params['email'] = email
        a_url = self._url + "/users/add"
        res = self._con.post(path=a_url, postdata=params)
        if 'status' in res:
            if res['status'] == 'success':
                return self.get(username=username)
            else:
                return res['status']
        return res
    #----------------------------------------------------------------------
    def _get_user_privileges(self, username):
        """
           Returns the privilege associated with a user
           Parameters:
              username - name of the user
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "username" : username
        }
        url = self._url + "/users/getPrivilege"
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def _get_user_roles(self, username, user_filter=None, max_count=None):
        """
           This operation returns a list of role names that have been
           assigned to a particular user account.
           Parameters:
              username - name of the user for whom the returned roles
              user_filter - filter to be applied to the resultant role set.
              max_count - maximum number of results to return for this query
        """
        u_url = self._url + "/roles/getRolesForUser"
        params = {
            "f" : "json",
            "username" : username
        }
        if user_filter:
            params['filter'] = user_filter

        if max_count:
            params['maxCount'] = max_count
        return self._con.post(path=u_url, postdata=params)
    #----------------------------------------------------------------------
    def _list_users(self, start_index=0, page_size=10):
        """
           This operation gives you a pageable view of users in the user
           store. It is intended for iterating over all available user
           accounts. To search for specific user accounts instead, use the
           Search Users operation.
           Parameters:
              start_index - The starting index (zero-based) from the users
                           list that must be returned in the result page.
                           The default is 0.
              page_size - The maximum number of user accounts to return in
                         the result page.
           Output:
              JSON response message as dictionary
        """
        u_url = self._url + "/users/getUsers"
        params = {
            "f" : "json",
            "startIndex" : start_index,
            "pageSize" : page_size
        }
        return self._con.post(path=u_url,
                              postdata=params)
    #----------------------------------------------------------------------
    def _remove_roles_from_user(self, username, roles):
        """
           This operation removes roles that have been previously assigned
           to a user account. This operation is supported only when the
           user and role store supports reads and writes.
           Parameters:
              username - name of the user
              roles - comma seperated list of the role names
           Ouput:
              JSON Messages as dictionary
        """
        u_url = self._url + "/users/removeRoles"
        params = {
            "f" : "json",
            "username" : username,
            "roles" : roles
        }
        res = self._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _delete_user(self, username):
        """
           returns a username from the user store
           Parameters:
              username - name of the user to remove
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : 'json',
            "username" : username
        }
        u_url = self._url + "/users/remove"
        res = self._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _remove_users_from_role(self, rolename, users):
        """
           Removes a role assignment from multiple users.
           Parameters:
              rolename - name of the rolename
              users - comma seperated list of usernames.  They must exist
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : 'json',
            "rolename" : rolename,
            "users" : users
        }
        u_url = self._url + "/roles/removeUsersFromRole"
        res = self._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
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
        res = self._find_users(criteria=username, max_count=max_results)
        if "users" in res:
            for user in res["users"]:
                users.append(User(self, user))
                del user
        return users
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
    @property
    def roles(self):
        """Helper object to manage custom roles for users"""
        if self._rm is None:
            self._rm = RoleManager(self._url,
                                   gis=self._con)
        return self._rm
    #----------------------------------------------------------------------
    def _find_users(self, criteria=None, max_count=10):
        """
           You can use this operation to search a specific user or a group
           of users from the user store. The size of the search result can
           be controlled with the max_count parameter.
           Parameters:
              filter - a filter string to search for the users
              max_count - maximum size of the result
           Ouput:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "filter" : criteria,
            "maxCount" : max_count
        }
        u_url = self._url + "/users/search"
        return self._con.post(path=u_url, postdata=params)
    #----------------------------------------------------------------------
    def _update_user(self, username, password=None,
                    fullname=None, description=None,
                    email=None):
        """ Updates a user account in the user store
           Parameters:
              username - the name of the user. The name must be unique in
                         the user store.
              password - the password for this user.
              fullname - an optional full name for the user.
              description - an optional field to add comments or description
                            for the user account.
              email - an optional email for the user account.
        """
        user = {"username" : username}
        params = {
            "f" : "json",
            "user" : {}
        }
        if password is not None:
            user['password'] = password
        if fullname is not None:
            user['fullname'] = fullname
        if description is not None:
            user['description'] = description
        if email is not None:
            user['email'] = email
        params['user'] = user
        u_url = self._url + "/users/update"
        return self._con.post(path=u_url, postdata=params)
########################################################################
class User(dict):
    """
    Individual User Account
    """
    _security = None
    _user_dict = None
    #----------------------------------------------------------------------
    def __init__(self, usermanager, user_dict):
        """Constructor"""
        dict.__init__(self)
        if usermanager is None or \
           user_dict is None:
            raise ValueError("Values of UserManager and user_dict" + \
                             " must be provided")
        self._security = usermanager
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

        res = self._security._update_user(self.username, password,
                                          full_name, description,
                                          email)
        if res['status'] == 'success':
            user = self._security._find_users(criteria=self.username, max_count=1)['users'][0]
            self._user_dict = user
            self.__dict__.update(user)
            return True
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

        return self._security.roles._assign_roles(username=self.username,
                                                  roles=role_name)
    #----------------------------------------------------------------------
    def delete(self):
        """deletes the current user account"""
        username = self.username
        return self._security._delete_user(username=username)
########################################################################
class RoleManager(BaseServer):
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
    _url = None
    _con = None
    _resources = None
    _json_dict = None
    _json = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis,
                 initialize=False):
        """Constructor
            Parameters:
               url - security admin url
               gis - Server Connection Object with Admin Credentials
        """
        self._url = url
        self._con = gis
        if initialize:
            self._init(gis)
    #----------------------------------------------------------------------
    def __str__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return '<%s at %s>' % (type(self).__name__, self._url)
    #----------------------------------------------------------------------
    def create(self, name, description=""):
        """ Adds a role to the role store. This operation is available only
            when the role store is a read-write store such as the default
            ArcGIS Server store.
            If the name of the role exists in the role store, an error will
            be returned.
            Parameters:
               rolename - The name of the role. The name must be unique in the
                      role store.
               description - An optional field to add comments or a
                             description for the role.
            Output:
               JSON message as dictionary
        """
        params = {
            "f" : "json",
            "rolename" : name,
            "description" : description
        }
        a_url = self._url + "/roles/add"
        res = self._con.post(path=a_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _add_users_to_role(self, rolename, users):
        """ Assigns a role to multiple users """
        params = {
            "f" : "json",
            "rolename" : rolename,
            "users" : users
        }
        rURL = self._url + "/roles/addUsersToRole"
        res = self._con.post(path=rURL, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _assign_privilege(self, rolename, privilege="ACCESS"):
        """
           Administrative access to ArcGIS Server is modeled as three broad
           tiers of privileges:
               ADMINISTER - A role that possesses this privilege has
                           unrestricted administrative access to ArcGIS
                          Server.
               PUBLISH - A role with PUBLISH privilege can only publish GIS
                       services to ArcGIS Server.
               ACCESS-No administrative access. A role with this privilege
                      can only be granted permission to access one or more
                      GIS services.
           By assigning these privileges to one or more roles in the role
           store, ArcGIS Server's security model supports role-based access
           control to its administrative functionality.
           These privilege assignments are stored independent of ArcGIS
           Server's role store. As a result, you don't need to update your
           enterprise identity stores (like Active Directory).
           Parameters:
              rolename - The name of the role.
              privilege - The capability to assign to the role. The default
                          capability is ACCESS.
                          Values: ADMINISTER | PUBLISH | ACCESS
           Output:
              JSON Message
        """
        a_url = self._url + "/roles/assignPrivilege"
        params = {
            "f" : "json",
            "rolename" : rolename,
            "privilege" : privilege
        }
        res = self._con.post(path=a_url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _assign_roles(self, username, roles):
        """
           You must use this operation to assign roles to a user account
           when working with an user and role store that supports reads and
           writes.
           By assigning a role to a user, the user account automatically
           inherits all the permissions that have been assigned to the role
           Parameters:
              username - The name of the user.
              roles - A comma-separated list of role names. Each of role
                      names must exist in the role store.
           Output:
              returns JSON messages
        """
        params = {
            "f" : "json",
            "username" : username,
            "roles" : roles
        }
        u_url = self._url + "/users/assignRoles"
        res = self._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _get_privilege_for_role(self, rolename):
        """
           Returns the privilege associated with a role.
           Parameters:
              rolename - name of the role
           Output:
              JSON Messages
        """
        params = {
            "f" : "json",
            "rolename" : rolename
        }
        pURL = self._url + "/roles/getPrivilege"
        return self._con.post(path=pURL,
                              postdata=params)
    #----------------------------------------------------------------------
    def _get_user_privileges(self, username):
        """
           Returns the privilege associated with a user
           Parameters:
              username - name of the user
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "username" : username
        }
        url = self._url + "/users/getPrivilege"
        return self._con.post(path=url, postdata=params)
    #----------------------------------------------------------------------
    def all(self, start_index=0, page_size=10):
        """ This operation gives you a pageable view of roles in the role
            store. It is intended for iterating through all available role
            accounts. To search for specific role accounts instead, use the
            Search Roles operation.
            Parameters:
               start_index - The starting index (zero-based) from the roles
                            list that must be returned in the result page.
                            The default is 0.
               page_size - The maximum number of roles to return in the
                          result page. The default size is 10.
            Output:
               returns JSON messages as dictionary
        """
        u_url = self._url + "/roles/getRoles"
        params = {
            "f" : "json",
            "startIndex" : start_index,
            "pageSize" : page_size
        }
        roles = []
        res = self._con.post(path=u_url, postdata=params)
        if 'roles' in res:
            for role in res['roles']:
                roles.append(Role(rolemanager=self, roledict=role))
        return roles
    #----------------------------------------------------------------------
    def _get_roles_by_privilege(self, privilege):
        """
           Returns the roles associated with a pribilege.
           Parameters:
              privilege - name of the privilege
           Output:
              JSON response as dictionary
        """
        u_url = self._url + "/roles/getRolesByPrivilege"
        params = {
            "f" : "json",
            "privilege" : privilege
        }
        return self._con.post(path=u_url, postdata=params)
    #----------------------------------------------------------------------
    def _get_user_roles(self, username, user_filter=None, max_count=None):
        """
           This operation returns a list of role names that have been
           assigned to a particular user account.
           Parameters:
              username - name of the user for whom the returned roles
              user_filter - filter to be applied to the resultant role set.
              max_count - maximum number of results to return for this query
        """
        u_url = self._url + "/roles/getRolesForUser"
        params = {
            "f" : "json",
            "username" : username
        }
        if user_filter:
            params['filter'] = user_filter

        if max_count:
            params['maxCount'] = max_count
        return self._con.post(path=u_url, postdata=params)
    #----------------------------------------------------------------------
    def _get_users_within_role(self, rolename, user_filter=None, max_count=20):
        """
           You can use this operation to conveniently see all the user
           accounts to whom this role has been assigned.
           Parameters:
              rolename - name of the role
              user_filter - filter to be applied to the resultant user set
              max_count - maximum number of results to return
           Output:
              JSON Message as dictionary
        """
        u_url = self._url + "/roles/getUsersWithinRole"
        params = {
            "f" : "json",
            "rolename" : rolename,
            "maxCount" : max_count
        }
        if user_filter and \
           isinstance(user_filter, str):
            params['filter'] = user_filter
        return self._con.post(path=u_url, postdata=params)
    #----------------------------------------------------------------------
    def _delete_role(self, rolename):
        """
           Removes an existing role from the role store. This operation is
           available only when the role store is a read-write store such as
           the default ArcGIS Server store.
           Parameters:
              rolename - name of role to remove
           Output:
              JSON message if any
        """
        params = {
            "f" : "json",
            "rolename" : rolename
        }
        u_url = self._url + "/roles/remove"
        res = self._con.post(path=u_url,
                             postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _remove_roles_from_user(self, username, roles):
        """
           This operation removes roles that have been previously assigned
           to a user account. This operation is supported only when the
           user and role store supports reads and writes.
           Parameters:
              username - name of the user
              roles - comma seperated list of the role names
           Ouput:
              JSON Messages as dictionary
        """
        u_url = self._url + "/users/removeRoles"
        params = {
            "f" : "json",
            "username" : username,
            "roles" : roles
        }
        res = self._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _remove_users_from_role(self, rolename, users):
        """
           Removes a role assignment from multiple users.
           Parameters:
              rolename - name of the rolename
              users - comma seperated list of usernames.  They must exist
           Output:
              JSON message as dictionary
        """
        params = {
            "f" : 'json',
            "rolename" : rolename,
            "users" : users
        }
        u_url = self._url + "/roles/removeUsersFromRole"
        res = self._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    @property
    def count(self):
        """
           returns the number of roles for AGS
        """
        params = {
            "f" : "json"
        }
        u_url = self._url + "/roles"
        return self._con.get(path=u_url, params=params)
    #----------------------------------------------------------------------
    def get_role(self, role_id=None, max_count=10):
        """
           You can use this operation to search a specific role or a group
           of roles from the role store. The size of the search results can
           be controlled with the max_count parameter.
           Parameters:
              role_filter - a filter string to search for the roles
              max_count - maximum size of the result
           Ouput:
              JSON message as dictionary
        """
        params = {
            "f" : "json",
            "filter" : role_id,
            "maxCount" : max_count
        }
        roles = []
        u_url = self._url + "/roles/search"
        res = self._con.post(path=u_url, postdata=params)
        if 'roles' in res:
            for r in res['roles']:
                roles.append(Role(rolemanager=self, roledict=r))
            return roles
        return roles
    #----------------------------------------------------------------------
    def _update_role(self, rolename, description):
        """ Updates a role description in the role store
           Parameters:
              rolename - the name of the role. The name must be unique in
                         the role store.
              description - an optional field to add comments or description
                            for the role.
        """
        params = {
            "f" : "json",
            "rolename" : rolename
        }
        if description is not None:
            params['description'] = description
        u_url = self._url + "/roles/update"
        res = self._con.post(path=u_url, postdata=params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
########################################################################
class Role(dict):
    """
    represents a single role on server

    **(This is should not be created by a user)**
    """
    _roledict = None
    _security = None
    #----------------------------------------------------------------------
    def __init__(self, rolemanager, roledict):
        """Constructor"""
        dict.__init__(self)
        if rolemanager is None or \
           roledict is None:
            raise ValueError("Values of RoleManager and roledict" + \
                             " must be provided")
        self._security = rolemanager
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
        res =  self._security._update_role(rolename=self.rolename,
                                          description=description)
        if res:
            b = self._security.get_role(self.rolename, max_count=1)[0]
            self.__dict__.update(b._roledict)
        return res
    #----------------------------------------------------------------------
    def delete(self):
        """
        deletes the current role
        """
        res = self._security._delete_role(rolename=self.rolename)
        self = None
        return True
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
        return self._security._assign_privilege(rolename=self.rolename,
                                               privilege=privilage)
    #----------------------------------------------------------------------
    def grant(self, username):
        """
        Adds a user to the current role

        =========  =================================================
        Parmeters  **Description**
        ---------  -------------------------------------------------
        username   required string, account name to add to the role
        =========  =================================================

        :returns:
           boolean, True means added, False means could not add to
           Role
        """
        return self._security._add_users_to_role(rolename=self.rolename,
                                                 users=username)


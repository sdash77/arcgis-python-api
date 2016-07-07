from __future__ import absolute_import
import os
import base64
import datetime
import tempfile
from ._contentmanager import Item
class UserManager(object):
    """
    Manager class for managing GIS users. This class is not created by users directly.
    An instance of this class, called 'users', is available as a property of the Gis object.
    Users call methods on this 'users' object to manipulate (create, get, search...) users.
    """
    def __init__(self, portal):
        self._portal = portal



    def create(self, username, password, firstname, lastname, email, description=None, role='org_user',
               provider='arcgis', idpUsername=None):
        """ This operation is used to pre-create built-in or enterprise accounts within the portal.
        The provider parameter is used to indicate the type of user account. Only an administrator
        can call this method.

        .. note:
            When Portal for ArcGIS is connected to an enterprise identity store, enterprise users sign
            into portal using their enterprise credentials. By default, new installations of Portal for
            ArcGIS do not allow accounts from an enterprise identity store to be registered to the portal
            automatically. Only users with accounts that have been pre-created can sign in to the portal.
            Alternatively, you can configure the portal to register enterprise accounts the first time
            the user connects to the website.

        ================  ===============================================================================
        **Argument**      **Description**
        ----------------  -------------------------------------------------------------------------------
        username          required string, must be unique in the Portal,
                          >=6 characters, =<24 characters
        ----------------  -------------------------------------------------------------------------------
        password          required string, must be >= 8 characters. This is a required parameter only if
                          the provider is arcgis; otherwise, the password parameter is ignored.
        ----------------  -------------------------------------------------------------------------------
        firstname         required string, the first name for the user
        ----------------  -------------------------------------------------------------------------------
        lastname          required string, the last name for the user
        ----------------  -------------------------------------------------------------------------------
        email             required string, must be an email address
        ----------------  -------------------------------------------------------------------------------
        description       An optional description string for the user account.
        ----------------  -------------------------------------------------------------------------------
        role              The role for the user account. The default value is org_user.
                          Values: org_user | org_publisher | org_admin
        ----------------  -------------------------------------------------------------------------------
        provider          The provider for the account. The default value is arcgis.
                          Values: arcgis | enterprise
        ----------------  -------------------------------------------------------------------------------
        idpUsername       The name of the user as stored by the enterprise user store. This parameter is
                          only required if the provider parameter is enterprise.
        ================  ===============================================================================

        :return:
            the user, if created, else None

        """
        createuser_url = self._portal.url + "/portaladmin/security/users/createUser"
        #print(createuser_url)
        params = {
            'f': 'json',
            'username' : username,
            'password' : password,
            'firstname' : firstname,
            'lastname' : lastname,
            'email' : email,
            'description' : description,
            'role' : role,
            'provider' : provider,
            'idpUsername' : idpUsername
        }

        self._portal.con.post(createuser_url, params)
        return self.get(username)


    def signup(self, username, password, fullname, email):
        """ Signs up users to an instance of Portal for ArcGIS.

        .. note:
            This method only applies to Portal and not ArcGIS
            Online.  This method can be called anonymously, but
            keep in mind that self-signup can also be disabled
            in a Portal.  It also only creates built-in
            accounts, it does not work with enterprise
            accounts coming from ActiveDirectory or your
            LDAP.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        username          required string, must be unique in the Portal,
                          >4 characters
        ----------------  --------------------------------------------------------
        password          required string, must be >= 8 characters.
        ----------------  --------------------------------------------------------
        fullname          required string, name of the user
        ----------------  --------------------------------------------------------
        email             required string, must be an email address
        ================  ========================================================

        :return:
            the user, if created, else None

        """
        success = self._portal.signup(username, password, fullname, email)
        if success:
            return User(self._portal, username)
        else:
            return None

    def get(self, username):
        """ Returns the user object for the specified username.

        Arguments
            username        required string, the username whose user object you want.
        :return:
            None if the user is not found and returns a user object if the user is found
        """
        user = self._portal.get_user(username)
        if user is not None:
            return User(self._portal, user['username'], user)
        return None

    def search(self, query=None, sort_field='username', sort_order='asc', max_users=100, add_org=True):
        """ Searches portal users.

        Returns a list of users matching the specified query

        .. note::
            A few things that will be helpful to know.

            1. The query syntax has quite a few features that can't
               be adequately described here.  The query syntax is
               available in ArcGIS help.  A short version of that URL
               is http://bitly.com/1fJ8q31.

            2. Searching without specifying a query parameter returns
               a list of all users in your organization.

            3. Most of the time when searching groups you want to
               search within your organization in ArcGIS Online
               or within your Portal.  As a convenience, the method
               automatically appends your organization id to the query by
               default.  If you don't want the API to append to your query
               set add_org to false.  If you use this feature with an
               OR clause such as field=x or field=y you should put this
               into parenthesis when using add_org.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        query             optional string, query string.  See notes. pass None
                          to get list of all users in the org
        ----------------  --------------------------------------------------------
        sort_field        optional string, valid values can be username or created
        ----------------  --------------------------------------------------------
        sort_order        optional string, valid values are asc or desc
        ----------------  --------------------------------------------------------
        max_users         optional int, maximum number of users returned
        ----------------  --------------------------------------------------------
        add_org           optional boolean, controls whether to search within your
                          org (default is True)
        ================  ========================================================

        :return:
            A list of users:
        """
        if query is None:
            users = self._portal.get_org_users(max_users)
            return [User(self._portal, u['username'], u) for u in users]
        else:
            userlist = []

            users = self._portal.search_users(query, sort_field, sort_order, max_users, add_org)
            for user in users:
                userlist.append(User(self._portal, user['username'], user))
            return userlist

        #TODO: remove org users, invite users

    @property
    def me(self):
        """ Returns the logged in user
        """
        me = self._portal.logged_in_user()
        if me is not None:
            return User(self._portal, me['username'], me)
        else:
            return None

class User(dict):
    """
    Represents a registered user of the GIS (ArcGIS Online, or Portal for ArcGIS).
    """
    def __init__(self, portal, username, userdict=None):
        dict.__init__(self)
        self._portal = portal
        self.username = username
        self.thumbnail = None
        self._workdir = tempfile.gettempdir()
        # userdict = self._portal.get_user(self.username)
        self._hydrated = False
        if userdict:
            self.__dict__.update(userdict)
            dict.update(userdict)

    # Using http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991

    def __getattr__(self, name): # support user attributes as user.access, user.email, user.role etc
        # return dict.__getitem__(self, name)
        if not self._hydrated:
            userdict = self._portal.get_user(self.username)
            self._hydrated = True
            super(User, self).update(userdict)
            self.__dict__.update(userdict)
        return dict.__getitem__(self, name)


    def __getitem__(self, k): # support user attributes as dictionary keys on this object, eg. user['role']
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            if not self._hydrated:
                userdict = self._portal.get_user(self.username)
                self._hydrated = True
                super(User, self).update(userdict)
                self.__dict__.update(userdict)
            return dict.__getitem__(self, k)

    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)


    def __repr__(self):
        return '<%s username:%s>' % (type(self).__name__, self.username)

    def get_thumbnail_link(self):
        """ URL to the thumbnail image """
        thumbnail_file = self.thumbnail
        if thumbnail_file is None:
            return 'http://www.arcgis.com/home/js/arcgisonline/css/images/no-user-thumb.jpg'
        else:
            thumbnail_url_path = self._portal.con.baseurl + 'community/users/' + self.username + '/info/' + thumbnail_file
            return thumbnail_url_path

    def _repr_html_(self):
        thumbnail = self.thumbnail
        if self.thumbnail is None or not self._portal.is_logged_in:
            thumbnail = self.get_thumbnail_link()
        else:
            b64 = base64.b64encode(self.get_thumbnail())
            thumbnail = "data:image/png;base64," + str(b64,"utf-8") + "' width='200' height='133"

        firstName = 'Not Provided'
        lastName = 'Not Provided'
        fullName = 'Not Provided'
        description = "This user has not provided any personal information."

        try:
            firstName = self.firstName
        except:
            firstName = 'Not Provided'

        try:
            lastName = self.lastName
        except:
            firstName = 'Not Provided'

        try:
            fullName = self.fullName
        except:
            fullName = 'Not Provided'

        try:
            description = self.description
        except:
            description = "This user has not provided any personal information."

        url = self._portal.url  + "/home/user.html?user=" + self.username

        return """<div class="9item_container" style="height: auto; overflow: hidden; border: 1px solid #cfcfcf; border-radius: 2px; background: #f6fafa; line-height: 1.21429em; padding: 10px;">
                    <div class="item_left" style="width: 210px; float: left;">
                       <a href='""" + str(url) + """' target='_blank'>
                        <img src='""" + str(thumbnail) + """' class="itemThumbnail">
                       </a>
                    </div>

                    <div class="item_right" style="float: none; width: auto; overflow: hidden;">
                        <a href='""" + str(url) + """' target='_blank'><b>""" + str(fullName) + """</b>
                        </a>
                        <br><br><b>Bio</b>: """ + str(description) + """
                        <br><b>First Name</b>: """ + str(firstName) + """
                        <br><b>Last Name</b>: """ + str(lastName)  + """
                        <br><b>Username</b>: """ + str(self.username)  + """
                        <br><b>Joined</b>: """ + str(datetime.datetime.fromtimestamp(self.created/1000).strftime("%B %d, %Y")) + """

                    </div>
                </div>
                """

    """
    def get_attributes(self):
       Returns information for this user.

        Arguments
            None.
            ---------------- --------------------------------------------------------
            created           time (int), when user created
            ----------------  --------------------------------------------------------
            culture           string, two-letter language code
            ----------------  --------------------------------------------------------
            description       string, user supplied description
            ----------------  --------------------------------------------------------
            fullName          string, name of the user
            ----------------  --------------------------------------------------------
            modified          time (int), when user last modified
            ----------------  --------------------------------------------------------
            region            string, may be None
            ----------------  --------------------------------------------------------
            tags              string list, of user tags
            ----------------  --------------------------------------------------------
            thumbnail         string, name of file
            ----------------  --------------------------------------------------------
            username          string, name of the user

       :return:
            A dictionary object with the following keys:

            ================  ========================================================
            **Key**           **Value**
            ----------------  --------------------------------------------------------
            access            string
            ----------------  --------------------------------------------------------
            created           time (int)
            ----------------  --------------------------------------------------------
            culture           string, two-letter language code ('en')
            ----------------  --------------------------------------------------------
            description       string
            ----------------  --------------------------------------------------------
            email             string
            ----------------  --------------------------------------------------------
            fullName          string
            ----------------  --------------------------------------------------------
            idpUsername       string, name of the user in the enterprise system
            ----------------  --------------------------------------------------------
            groups            list of dictionaries.  For dictionary keys,
                              see get_group doc.
            ----------------  --------------------------------------------------------
            modified          time (int)
            ----------------  --------------------------------------------------------
            orgId             string, the organization id
            ----------------  --------------------------------------------------------
            preferredView     string, value is either Web, GIS, or null
            ----------------  --------------------------------------------------------
            region            string, None or two letter country code
            ----------------  --------------------------------------------------------
            role              string, value is either org_user, org_publisher,
                              org_admin
            ----------------  --------------------------------------------------------
            storageUsage      int
            ----------------  --------------------------------------------------------
            storageQuota      int
            ----------------  --------------------------------------------------------
            tags              list of strings
            ----------------  --------------------------------------------------------
            thumbnail         string, name of file
            ----------------  --------------------------------------------------------
            username          string, name of user
            ================  ========================================================

        return self._portal.get_user(self.username)
    """

    def reset(self, password, new_password=None, new_security_question=None, new_security_answer=None):
        """ Resets a user's password, security question, and/or security answer.

        .. note::
            This function does not apply to those using enterprise accounts
            that come from an enterprise such as ActiveDirectory, LDAP, or SAML.
            It only has an effect on built-in users.

            If a new security question is specified, a new security answer should
            be provided.

        =====================  =========================================================
        **Argument**           **Description**
        ---------------------  ---------------------------------------------------------
        password               required string, current password
        ---------------------  ---------------------------------------------------------
        new_password           optional string, new password if resetting password
        ---------------------  ---------------------------------------------------------
        new_security_question  optional int, new security question if desired
        ---------------------  ---------------------------------------------------------
        new_security_answer    optional string, new security question answer if desired
        =====================  =========================================================

        :return:
            a boolean, indicating success

        """
        return self._portal.reset_user(self.username, password, new_password,
                                       new_security_question, new_security_answer)

    def update(self, access=None, preferred_view=None, description=None, tags=None,
               thumbnail=None, fullname=None, email=None, culture=None, region=None):
        """ Updates this user's properties.

        .. note::
            Only pass in arguments for properties you want to update.
            All other properties will be left as they are.  If you
            want to update description, then only provide
            the description argument.

        ================  ==========================================================
        **Argument**      **Description**
        ----------------  ----------------------------------------------------------
        access            optional string, values: private, org, public
        ----------------  ----------------------------------------------------------
        preferred_view    optional string, values: Web, GIS, null
        ----------------  ----------------------------------------------------------
        description       optional string, a description of the user.
        ----------------  ----------------------------------------------------------
        tags              optional string, comma-separated tags for searching
        ----------------  ----------------------------------------------------------
        thumbnail         optional string, path or url to a file.  can be PNG, GIF,
                          JPEG, max size 1 MB
        ----------------  ----------------------------------------------------------
        fullname          optional string, name of the user, only for built-in users
        ----------------  ----------------------------------------------------------
        email             optional string, email address, only for built-in users
        ----------------  ----------------------------------------------------------
        culture           optional string, two-letter language code, fr for example
        ----------------  ----------------------------------------------------------
        region            optional string, two-letter country code, FR for example
        ================  ==========================================================

        :return:
            a boolean indicating success

        """
        return self._portal.update_user(self.username, access, preferred_view, description, tags, thumbnail, fullname, email, culture, region)

    def update_role(self, role):
        """ Updates this user's role to org_user, org_publisher, org_admin

        .. note::
            There are three types of roles in Portal - user, publisher, and administrator.
            A user can share items, create maps, create groups, etc.  A publisher can
            do everything a user can do and create hosted services.  An administrator can
            do everything that is possible in Portal.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        role              required string, one of these values org_user,
                          org_publisher, org_admin
        ================  ========================================================

        :return:
            a boolean, that indicates success

        """
        passed = self._portal.update_user_role(self.username, role)
        if passed:
            self.role = role
        return passed

    def delete(self, reassign_to=None):
        """ Deletes this user from the portal, optionally deleting or reassigning groups and items.

        .. note::
            You can not delete a user in Portal if that user owns groups or items.  If you
            specify someone in the reassign_to argument then items and groups will be
            transferred to that user.  If that argument is not set then the method
            will fail if the user has items or groups that need to be reassigned.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        reassign_to       optional string, new owner of items and groups
        ================  ========================================================

        :return:
            a boolean indicating whether the operation succeeded or failed.

        """
        return self._portal.delete_user(self.username, reassign_to)

    def reassign_to(self, target_username):
        """ Reassigns all of this user's items and groups to another user.

        Items are transferred to the target user into a folder named
        <user>_<folder> where user corresponds to the user whose items were
        moved and folder corresponds to the folder that was moved.

        .. note::
            This method must be executed as an administrator.  This method also
            can not be undone.  The changes are immediately made and permanent.

        ================  ===========================================================
        **Argument**      **Description**
        ----------------  -----------------------------------------------------------
        target_username   required string, user who will own items/groups after this.
        ================  ===========================================================

        :return:
            a boolean indicating success

        """
        return self._portal.reassign_user(self.username, target_username)

    def get_thumbnail(self):
        """ Returns the bytes that make up the thumbnail for this user.

        Arguments
            None.

        Returns
            bytes that represent the image.

        Example

        .. code-block:: python

            response = user.get_thumbnail()
            f = open(filename, 'wb')
            f.write(response)

        """
        thumbnail_file = self.thumbnail
        if thumbnail_file:
            thumbnail_url_path = 'community/users/' + self.username + '/info/' + thumbnail_file
            if thumbnail_url_path:
                return self._portal.con.get(thumbnail_url_path, try_json=False)

    def download_thumbnail(self, dir=None):
        """ Downloads the item thumbnail for this user, returns file path. """
        thumbnail_file = self.thumbnail

        # Only proceed if a thumbnail exists
        if thumbnail_file:
            thumbnail_url_path = 'community/users/' + self.username + '/info/' + thumbnail_file
            if thumbnail_url_path:
                if not dir:
                    dir = self._workdir
                file_name = os.path.split(thumbnail_file)[1]
                if len(file_name) > 50: #If > 50 chars, truncate to last 30 chars
                    file_name = file_name[-30:]
                file_path = os.path.join(dir, file_name)
                self._portal.con.download(thumbnail_url_path, file_path)
                return file_path
        else:
            return None

    def content(self):
        """Returns a dict of user items. The keys of the dict being the users folders, '/' being the root folder,
        and the values being a list of items in that folder."""
        retval = {}
        postdata = {
            "f": "json"
        }
        resp = self._portal.con.post('content/users/' + self.username, postdata)
        root_items = []
        for item in resp['items']:
            root_items.append(Item(self._portal, item['id'], item))

        retval['/'] = root_items

        folders = []
        for folder in resp['folders']:
            resp = self._portal.con.post('content/users/' + self.username + '/'  + folder['id'], postdata)
            folder_items = []
            for item in resp['items']:
                folder_items.append(Item(self._portal, item['id'], item))

            retval[folder['title']] = folder_items

        return retval
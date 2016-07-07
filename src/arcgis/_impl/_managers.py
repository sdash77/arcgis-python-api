import os
import json
from ._util import _is_shapefile
from ..lyr import FeatureCollection
from ._object import *
class DatastoreManager(object):
    """
    Manager class for managing the GIS data stores in on-premises ArcGIS Portals.
    This class is not created by users directly.
    An instance of this class, called 'datastores', is available as a property of the GIS object.
    Users call methods on this 'datastores' object to manage the data stores.
    """
    def __init__(self, gis, admin_url=None):
        self._gis = gis
        self._portal = gis._portal
        if admin_url is None:
            fedservers_url = self._gis._url + "portaladmin/federation/servers?f=json"
            res = self._gis._portal.con.get(fedservers_url)
            servers = res['servers']

            self._admin_url = None

            for server in servers:
                if server['isHosted']:
                    self._admin_url = server['adminUrl'] + '/admin'
        else:
            self._admin_url = admin_url

    def __str__(self):
        return json.dumps(self)

    @property
    def config(self):
        """
        The data store configuration properties affect the behavior of the data holdings of the server. The properties include:
        blockDataCopy-When this property is False, or not set at all, copying data to the site when publishing services from a client application is allowed. This is the default behavior.
        When this property is True, the client application is not allowed to copy data to the site when publishing. Rather, the publisher is required to register data items through which the service being published can reference data. Values: True | False
        Note:
        If you specify the property as True, users will not be able to publish geoprocessing services and geocode services from composite locators. These service types require data to be copied to the server. As a workaround, you can temporarily set the property to False, publish the service, and then set the property back to True.
        """
        params = {"f" : "json"}
        path = self._admin_url + "/data/config"
        res = self._portal.con.post(path, params)
        return res

    @config.setter
    def config(self, value):
        """
        The data store configuration properties affect the behavior of the data holdings of the server. The properties include:
        blockDataCopy-When this property is False, or not set at all, copying data to the site when publishing services from a client application is allowed. This is the default behavior.
        When this property is True, the client application is not allowed to copy data to the site when publishing. Rather, the publisher is required to register data items through which the service being published can reference data. Values: True | False
        Note:
        If you specify the property as True, users will not be able to publish geoprocessing services and geocode services from composite locators. These service types require data to be copied to the server. As a workaround, you can temporarily set the property to False, publish the service, and then set the property back to True.
        """
        params = {"f" : "json"}
        params['datastoreConfig'] = value
        path = self._admin_url + "/data/config/update"
        res = self._portal.con.post(path, params)
        return res

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
        conn_type = "shared"
        if client_path is not None:
            conn_type = "replicated"

        item = {
            "type" : "folder",
            "path" : "/fileShares/" + name,
            "info" : {
                "path" : server_path,
                "dataStoreConnectionType" : conn_type
            }
        }

        if client_path is not None:
            item['clientPath'] = client_path

        params = {
            "f" : "json",
            "item" : item
        }
        path = self._admin_url + "/data/registerItem"
        res = self._portal.con.post(path, params)
        if res['status'] == 'success' or res['status'] == 'exists':
            return DatastoreItem(self, "/fileShares/" + name)
        else:
            print(str(res))
            return None

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
        output = None
        path = self._admin_url + "/data/registerItem"

        params = {
            'f': 'json',
            'item' : {
                "path": "/bigDataFileShares/" + name,
                "type": "bigDataFileShare",
                "id": "",
                "info": {
                    "path" : server_path
                }
            }
        }
        res = self._portal.con.post(path, params)

        if res['status'] == 'success' or res['status'] == 'exists':
            output = DatastoreItem(self, "/bigDataFileShares/" + name)

        if res['success']:
            print("Created Big Data file share for " + name)
        elif res['status'] == 'exists':
            print("Big Data file share exists for " + name)

        return output

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

        item = {
            "type" : "egdb",
            "path" : "/enterpriseDatabases/" + name,
            "info" : {
                "connectionString" : conn_str,
                "dataStoreConnectionType" : conn_type
            }
        }

        if client_conn_str is not None:
            item['info']['clientConnectionString'] = client_conn_str

        is_managed = False
        if conn_type == "serverOnly":
            is_managed = True

        item['info']['isManaged'] = is_managed

        params = {
            "f" : "json",
            "item" : item
        }
        path = self._admin_url + "/data/registerItem"
        res = self._portal.con.post(path, params)
        if res['status'] == 'success' or res['status'] == 'exists':
            return DatastoreItem(self, "/enterpriseDatabases/" + name)
        else:
            print(str(res))
            return None

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
        params = {
            "f" : "json"
        }

        params['item'] = item

        path = self._admin_url + "/data/registerItem"
        res = self._portal.con.post(path, params)
        if res['status'] == 'success' or res['status'] == 'exists':
            return DatastoreItem(self, "/enterpriseDatabases/" + name)
        else:
            print(str(res))
            return None

    def get(self, path):
        """ Returns the data item object at the given path

        Arguments
            path        required string, the data item path
        :return:
            None if the data item is not found at that path and the data item object if its found
        """
        params = { "f" : "json" }
        urlpath = self._admin_url + "/data/items" + path

        datadict = self._portal.con.post(urlpath, params)
        if 'status' not in datadict:
            return DatastoreItem(self, path)
        else:
            print(datadict['messages'])
            return None

    def search(self, parent_path=None, ancestor_path=None,
               types=None, id=None):
        """
           You can use this operation to search through the various data
           items registered in the server's data store. Searching without specifying the parent_path and other parameters returns a lists of all registered data items
           Inputs:
              parentPath - The path of the parent under which to find items. To get the root data items, pass '/'
              ancestorPath - The path of the ancestor under which to find
                             items.
              types - A comma separated filter for the type of the items. Types include folder, egdb, bigDataFileShare, datadir
              id - A filter to search by the ID of the item

            :return:
            Returns a list of data items matching the specified query
        """
        params = {
            "f" : "json",
        }
        if parent_path is None and ancestor_path is None and types is None and id is None:
            ancestor_path = '/'
        if parent_path is not None:
            params['parentPath'] = parent_path
        if ancestor_path is not None:
            params['ancestorPath'] = ancestor_path
        if types is not None:
            params['types'] = types
        if id is not None:
            params['id'] = id


        path = self._admin_url + "/data/findItems"


        dataitems = []

        res = self._portal.con.post(path, params)
        for item in res['items']:
            dataitems.append(DatastoreItem(self, item['path']))
        return dataitems

    def validate(self):
        """
        Validates all items in the datastore and returns True if validated.

        In order for a data item to be registered and used successfully within the GIS's data store,
        you need to make sure that the path (for file shares) or connection string (for databases)
        is accessible to every server node in the site. To validate all registered data items all
        at once, you can invoke this operation.
        """
        params = {"f" : "json"}
        path = self._admin_url + "/data/validateAllDataItems"
        res = self._portal.con.post(path, params)
        return res['status'] == 'success'
###########################################################################
class ContentManager(object):
    """
    Manager class for manipulating GIS content. This class is not created by users directly.
    An instance of this class, called 'content', is available as a property of the Gis object.
    Users call methods on this 'content' object to manipulate (create, get, search...) items.
    """
    def __init__(self, portal):
        self._portal = portal

    def add(self, item_properties, data=None, thumbnail=None,
            metadata=None, owner=None, folder=None):
        """ Adds content to a Portal by creating an item.


            .. note::
                That content can be a file (such as a service definition, shapefile, CSV, layer package, geoprocessing package,
                map package) or it can be a URL (to an ArcGIS Server service, WMS service,
                or an application).

                If you are uploading a package or other file, provide a path or URL
                to the file in the data argument.

                From a technical perspective, none of the item properties below are required.  However,
                it is strongly recommended that title, type, typeKeywords, tags, snippet, and description
                be provided.


            ===============     ====================================================
            **Argument**        **Description**
            ---------------     ----------------------------------------------------
            item_properties     required dictionary, see below for the keys and
                                values
            ---------------     ----------------------------------------------------
            data                optional string, either a path or URL to the data
            ---------------     ----------------------------------------------------
            thumbnail           optional string, either a path or URL to an image
            ---------------     ----------------------------------------------------
            metadata            optional string, either a path or URL to metadata.
            ---------------     ----------------------------------------------------
            owner               optional string, defaults to logged in user.
            ---------------     ----------------------------------------------------
            folder              optional string, content folder where placing item
            ===============     ====================================================


            =================  ============================================================================
             **Key**            **Value**
            -----------------  ----------------------------------------------------------------------------
            type               optional string, indicates type of item.  See URL 1 below for valid values.
            -----------------  ----------------------------------------------------------------------------
            typeKeywords       optinal string list.  Lists all sub-types.  See URL 1 for valid values.
            -----------------  ----------------------------------------------------------------------------
            description        optional string.  Description of the item.
            -----------------  ----------------------------------------------------------------------------
            title              optional string.  Name of the item.
            -----------------  ----------------------------------------------------------------------------
            url                optional string.  URL to item that are based on URLs.
            -----------------  ----------------------------------------------------------------------------
            tags               optional string of comma-separated values.  Used for searches on items.
            -----------------  ----------------------------------------------------------------------------
            snippet            optional string.  Provides a very short summary of the what the item is.
            -----------------  ----------------------------------------------------------------------------
            extent             optional string with comma separated values for min x, min y, max x, max y.
            -----------------  ----------------------------------------------------------------------------
            spatialReference   optional string.  Coordinate system that the item is in.
            -----------------  ----------------------------------------------------------------------------
            accessInformation  optional string.  Information on the source of the content.
            -----------------  ----------------------------------------------------------------------------
            licenseInfo        optinal string, any license information or restrictions regarding content.
            -----------------  ----------------------------------------------------------------------------
            culture            optional string.  Locale, country and language information.
            -----------------  ----------------------------------------------------------------------------
            access             optional string.  Valid values: private, shared, org, or public.
            -----------------  ----------------------------------------------------------------------------
            commentsEnabled    optional boolean.  Default is true.  Controls whether comments are allowed.
            -----------------  ----------------------------------------------------------------------------
            culture            optional string.  Language and country information.
            =================  ============================================================================


        URL 1: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000ms000000

            :return:
                 The item if successfully added, None if unsuccessful.
            """

        if data is not None:
            title = os.path.splitext(os.path.basename(data))[0]
            extn = os.path.splitext(os.path.basename(data))[1].upper()
            if (extn == '.CSV'):
                filetype = 'CSV'
            elif (extn == '.SD'):
                filetype = 'Service Definition'
            if _is_shapefile(data):
                filetype = 'Shapefile'

            if not 'type' in item_properties:
                item_properties['type'] = filetype
            if not 'title' in item_properties:
                item_properties['title'] = title

        owner_name = owner
        if isinstance(owner, User):
            owner_name = owner.username

        itemid = self._portal.add_item(item_properties, data, thumbnail, metadata, owner_name, folder)

        if itemid is not None:
            return Item(self._portal, itemid)
        else:
            return None

    def create_service(self, name,
                       service_description="",
                       has_static_data=False,
                       max_record_count = 1000,
                       supported_query_formats = "JSON",
                       capabilities = "Image,Catalog,Metadata,Download,Pixels,Edit,Mensuration,Uploads",
                       description = "",
                       copyright_text = "",
                       wkid=102100,
                       service_type="imageService",
                       owner=None, folder=None):
        """ Creates a service in the Portal


            :return:
                 The item for the service, if successfully added, None if unsuccessful.
            """

        itemid = self._portal.create_service(name,
                                             service_description,
                                             has_static_data,
                                             max_record_count,
                                             supported_query_formats,
                                             capabilities,
                                             description,
                                             copyright_text,
                                             wkid,
                                             service_type, owner, folder)
        if itemid is not None:
            return Item(self._portal, itemid)
        else:
            return None

    def get(self, itemid):
        """ Returns the item object for the specified itemid.

        Arguments
            itemid        required string, the item identifier
        :return:
            None if the item is not found and returns an item object if the item is found
        """
        item = self._portal.get_item(itemid)
        if item is not None:
            return Item(self._portal, itemid, item)
        return None

    def search(self, query, item_type=None, sort_field='numViews', sort_order='desc', max_items=10, add_org=False):
        """ Searches for portal items.

        .. note::
            A few things that will be helpful to know.

            1. The query syntax has quite a few features that can't
                be adequately described here.  The query syntax is
                available in ArcGIS help.  A short version of that URL
                is http://bitly.com/1fJ8q31.

            2. Most of the time when searching groups you want to
                search within your organization in ArcGIS Online
                or within your Portal.  As a convenience, the method
                automatically appends your organization id to the query by
                default.  If you only want content from your org
                set add_org to True.

        ================  ===================================================================================
        **Argument**      **Description**
        ----------------  -----------------------------------------------------------------------------------
        query             required string, query string.  See notes.
        ----------------  -----------------------------------------------------------------------------------
        item_type         optional string, set type of item to search
                          http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000ms000000
        ----------------  -----------------------------------------------------------------------------------
        sort_field        optional string, valid values can be title, uploaded, type, owner, modified,
                          avgRating, numRatings, numComments, and numViews.
        ----------------  -----------------------------------------------------------------------------------
        sort_order        optional string, valid values are asc or desc
        ----------------  -----------------------------------------------------------------------------------
        max_items         optional int, maximum number of items returned, default is 10
        ----------------  -----------------------------------------------------------------------------------
        add_org           optional boolean, controls whether to search within your org (default is False)
        ================  ===================================================================================

        :return:
        Returns a list of items matching the specified query
        """
        itemlist = []
        if query is not None and query != '' and item_type is not None:
            query += ' AND '

        if item_type is not None:
            item_type = item_type.lower()
            if item_type == "web map":
                query += ' (type:"web map" NOT type:"web mapping application")'
            elif item_type == "web scene":
                query += ' (type:"web scene" NOT type:"CityEngine Web Scene")'
            elif item_type == "feature layer":
                query += ' (type:"feature service")'
            elif item_type == "image layer":
                query += ' (type:"image service")'
            elif item_type == "layer":
                query += ' (type:"layer" NOT type:"layer package" NOT type:"Explorer Layer")'
            elif item_type == "feature collection":
                query += ' (type:"feature collection" NOT type:"feature collection template")'
            elif item_type == "desktop application":
                query += ' (type:"desktop application" NOT type:"desktop application template")'
            else:
                query += ' (type:"' + item_type +'")'

        items = self._portal.search(query, sort_field=sort_field, sort_order=sort_order, max_results=max_items, add_org=add_org)
        for item in items:
            itemlist.append(Item(self._portal, item['id'], item))
        return itemlist
    # q: (type:"web map" NOT type:"web mapping applications") AND accountid:0123456789ABCDEF

    def create_folder(self, owner, folder):
        """ Creates a folder for the given user with the given title. Does nothing if the
        folder already exists.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        owner             required string, the name of the user
        ----------------  --------------------------------------------------------
        folder            required string, the name of the folder to create for the owner
        ================  ========================================================

        :return:
            a json object like the following:
            {"username" : "portaladmin","id" : "bff13218991c4485a62c81db3512396f","title" : "testcreate"} if the folder was created, None otherwise.
        """
        if folder != '/': # we don't create root folder
            owner_name = owner
            if isinstance(owner, User):
                owner_name = owner.username
            if self._portal.get_folder_id(owner_name, folder) is None:
                return self._portal.create_folder(owner_name, folder)
        return None

    def delete_folder(self, owner, folder):
        """ Deletes a folder for the given user with the given folder name.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        owner             required string, the name of the user
        ----------------  --------------------------------------------------------
        folder            required string, the name of the folder to delete
        ================  ========================================================

        :return:
            True if succeeded, False otherwise
        """
        if folder != '/':
            return self._portal.delete_folder(owner, folder)

    #def get_folder_id(self, owner, folder_name):
    #    """ Finds the folder for a particular owner and returns its id.

    #    ================  ========================================================
    #    **Argument**      **Description**
    #    ----------------  --------------------------------------------------------
    #    owner             required string, the name of the user
    #    ----------------  --------------------------------------------------------
    #    folder_name       required string, the name of the folder to search for
    #    ================  ========================================================

    #    :return:
    #        a boolean if succeeded.
    #    """
    #    return self._portal.get_folder_id(owner, folder_name)

    def import_data(self, df, address_fields=None):
        """
        Imports a Pandas data frame, that has an address column,
        to a feature collection


        df : pandas dataframe
        address_fields : dict containing mapping of df columns to address fields, eg: { "CountryCode" : "Country"} or { "Address" : "Address" }

        Returns feature collection, that can be used for analysis, visualization or published to the GIS as an item
        """
        path = "content/features/analyze"

        postdata = {
            "f": "pjson",
            "text" : df.to_csv(),
            "filetype" : "csv",

            "analyzeParameters" : {
                "enableGlobalGeocoding": "true",
                "sourceLocale":"en-us",
                #"locationType":"address",
                "sourceCountry":"",
                "sourceCountryHint":""
            }
        }

        if address_fields is not None:
            postdata['analyzeParameters']['locationType'] = 'address'

        res = self._portal.con.post(path, postdata)
        #import json
        #json.dumps(res)
        if address_fields is not None:
            res['publishParameters'].update({"addressFields":address_fields})

        path = "content/features/generate"
        postdata = {
            "f": "pjson",
            "text" : df.to_csv(),
            "filetype" : "csv",
            "publishParameters" : json.dumps(res['publishParameters'])
        }

        res = self._portal.con.post(path, postdata, use_ordered_dict=True)
        #print(json.dumps(res))
        fc = FeatureCollection(res['featureCollection']['layers'][0])
        return fc

###########################################################################
class GroupManager(object):
    """
    Manager class for manipulating GIS groups. This class is not created by users directly.
    An instance of this class, called 'groups', is available as a property of the Gis object.
    Users call methods on this 'groups' object to manipulate (create, get, search...) users.
    """
    def __init__(self, portal):
        self._portal = portal

    def create(self, title, tags, description=None,
               snippet=None, access='public', thumbnail=None,
               is_invitation_only=False, sort_field='avgRating',
               sort_order='desc', is_view_only=False, ):
        """ Creates a group and returns it if successful.

        ================  =========================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------
        title             required string, name of the group
        ----------------  ---------------------------------------------------------
        tags              required string, comma-delimited list of tags
        ----------------  ---------------------------------------------------------
        description       optional string, describes group in detail
        ----------------  ---------------------------------------------------------
        snippet           optional string, <250 characters summarizes group
        ----------------  ---------------------------------------------------------
        access            optional string, can be private, public, or org
        ----------------  ---------------------------------------------------------
        thumbnail         optional string, URL to group image
        ----------------  ---------------------------------------------------------
        is_invitation_only  optional boolean, defines whether users can join by
                          request.
        ----------------  ---------------------------------------------------------
        sort_field        optional string, specifies how shared items with
                          the group are sorted.
        ----------------  ---------------------------------------------------------
        sort_order        optional string, asc or desc for ascending or descending.
        ----------------  ---------------------------------------------------------
        is_view_only      optional boolean, defines whether the group is searchable
        ================  =========================================================

        :return:
            the group, if created, or None
        """
        groupid = self._portal.create_group_from_dict({
            'title' : title, 'tags' : tags, 'description' : description,
            'snippet' : snippet, 'access' : access, 'sortField' : sort_field,
            'sortOrder' : sort_order, 'isViewOnly' : is_view_only,
            'isinvitationOnly' : is_invitation_only}, thumbnail)
        #print(groupid)
        if groupid is not None:
            return Group(self._portal, groupid)
        else:
            return None

    def create_from_dict(self, dict):
        """
        Create a group with parameters specified in the dict
        See help of create() method for parameters
        :return:
            the group, if created, or None
        """
        thumbnail = dict.pop("thumbnail", None)

        groupid = self._portal.create_group_from_dict(dict, thumbnail)
        if groupid is not None:
            return Group(self._portal, groupid)
        else:
            return None

    def get(self, groupid):
        """ Returns the group object for the specified groupid.

        Arguments
            groupid        required string, the group identifier
        :return:
            None if the group is not found and returns a group object if the group is found
        """
        group = self._portal.get_group(groupid)
        if group is not None:
            return Group(self._portal, groupid)
        return None

    def search(self, query='', sort_field='title', sort_order='asc',
               max_groups=1000, add_org=True):
        """ Searches for portal groups.

        .. note::
            A few things that will be helpful to know.

            1. The query syntax has quite a few features that can't
                be adequately described here.  The query syntax is
                available in ArcGIS help.  A short version of that URL
                is http://bitly.com/1fJ8q31.

            2. Searching without specifying a query parameter returns
               a list of all groups in your organization.

            2. Most of the time when searching groups you want to
                search within your organization in ArcGIS Online
                or within your Portal.  As a convenience, the method
                automatically appends your organization id to the query by
                default.  If you don't want the API to append to your query
                set add_org to false.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        query             optional query string on Portal, required for Online.
                          If not specified, all groups will be searched. See notes
        ----------------  --------------------------------------------------------
        sort_field        optional string, valid values can be title, owner,
                          created
        ----------------  --------------------------------------------------------
        sort_order        optional string, valid values are asc or desc
        ----------------  --------------------------------------------------------
        max_groups        optional int, maximum number of groups returned
        ----------------  --------------------------------------------------------
        add_org           optional boolean, controls whether to search within
                          your org
        ================  ========================================================

        :return:
        Returns a list of groups matching the specified query
        """
        grouplist = []
        groups = self._portal.search_groups(query, sort_field, sort_order, max_groups, add_org)
        for group in groups:
            grouplist.append(Group(self._portal, group['id']))
        return grouplist
###########################################################################
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
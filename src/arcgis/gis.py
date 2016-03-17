"""
The **gis** module provides an information model for GIS hosted 
within ArcGIS Online or an ArcGIS Portal. This module provides functionality to manage 
(create, read, update and delete) GIS users, groups, content and datastores. This module
is the most important and provides the entry point into the GIS.
"""

import arcgis._impl.portalpy as portalpy
from arcgis.tools import *
from arcgis.lyr import *

import base64

from pydoc import locate
import datetime
import locale

import zipfile
# pylint: disable=fixme, line-too-long


def _lazy_property(fn):
    '''Decorator that makes a property lazy-evaluated.
    '''
    # http://stevenloria.com/lazy-evaluated-properties-in-python/
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property

class GIS(object):
    """
    .. _gis:

    **************
    The GIS object
    **************
    A GIS is representative of ArcGIS Online or an ArcGIS Portal
    site. The GIS object provides helper objects to manage (search, create, retrieve) GIS resources:
    * users
    * groups
    * content
    * datastore
    * tools - including geometry, geocoder, analysis, rasters, geoanalytics 

    Additionally, the GIS object has properties and methods to query it's state:
    * properties
    * usage()
    """

    _version = '0.1'

    def __init__(self, url=None, username=None, password=None):
        """
        Constructs a GIS object given a url and user credentials to ArcGIS Online 
        or an ArcGIS Portal. If no url is provided, ArcGIS Online is used. If username
        and password are not provided, anonymous access is used.
        """
        if url is None:
            url = "http://www.arcgis.com"

        self._url = url
        self._username = username
        self._password = password
        self._portal = None
        self.datastore = BigDataManager(self)
        self.tools = Tools(self)
        self.__enter__()

    def __enter__(self):
        self._portal = portalpy.Portal(self._url, self._username, self._password)
        
    @_lazy_property
    def users(self):
        """
        The resource manager for GIS users
        """
        return UserManager(self._portal)

    @_lazy_property
    def groups(self):
        """
        The resource manager for GIS groups
        """
        return GroupManager(self._portal)

    @_lazy_property
    def content(self):
        """
        The resource manager for GIS content
        """
        return ContentManager(self._portal)
    
    @_lazy_property
    def properties(self):
        """
        The properties of the GIS
        """
        return self._get_properties()

    def __exit__(self, typ, value, traceback):
        self._portal.logout()
        
    def __str__(self):
        return 'GIS @ ' + self._url

    def _repr_html_(self):
        """
        HTML Representation for IPython Notebook
        """
        return 'GIS @ <a href="' + self._url + '">' + self._url + '</a>'

    def _get_properties(self, force=False):
        """ Returns the portal properties (using cache unless force=True). """
        return self._portal.get_properties(force)

    def usage(self, startTime, endTime, period, vars, etype, stype, groupby, appId=None):
        """Usage statistics for the GIS"""
        return self._portal.usage(startTime, endTime, period, vars, etype, stype, groupby, appId)

    def map(self, location=None, zoomlevel=None):
        """Creates a map widget centered at the location (Address or (lat, long) tuple) with the specified zoom-level(integer)"""
        from arcgis.viz import MapView
        mapwidget = MapView()
        if location is not None:
            if isinstance(location, str):
                mapwidget.center = self.tools.geocoder.find_best_match(location)
            elif isinstance(location, tuple):
                mapwidget.center = location
            else:
                print("location must be an address(string) or (lat, long) pair as a tuple")
        if zoomlevel is not None:
            mapwidget.zoom = zoomlevel

        return mapwidget


class BigDataManager(object):
    """
    Manager class for managing Big Data file shares. This class is not created by users directly.
    An instance of this class, called 'bigdata', is available as a property of the GIS object.
    Users call methods on this 'bigdata' object to manage big data fileshares
    """
    def __init__(self, gis):
        self.gis = gis
        self.gae = GeoAnalyticsTools('https://dev06999.esri.com/server/rest/services/GeoAnalyticsTools/GPServer', gis)

    def list(self, server_path):
        return self.gae.list_bigdata_datasets(server_path)
            
    def register(self, server_path, fileshare_path, local_path, admin_url=None):
        self.gae.register_bigdata_fileshare(server_path, fileshare_path, local_path, admin_url)
        self.gae.list_bigdata_datasets(server_path)
    

class Tools(object):
    """
    Collection of GIS tools. This class holds references to the helper services and tools available 
    in the GIS. This class is not created by users directly.
    An instance of this class, called 'tools', is available as a property of the GIS object.
    Users access the GIS tools, such as the geocoder, spatial analysis tools, geoanalytics, raster 
    geoanalysis tools, etc through the gis.tools object
    """
    def __init__(self, gis):
        self._gis = gis
        self._geocoder = None
        self._geometry = None
        self._analysis = None
        self._raster_analysis = None
        self._geoanalytics = None

    @property
    def geocoder(self):
        """the geocoder, if available and configured"""
        if self._geocoder is not None:
            return self._geocoder
        try:
            geocodesvcurl = self._gis.properties['helperServices']['geocode'][0]['url']
            self._geocoder = Geocoder(None, geocodesvcurl, self._gis)
            return self._geocoder
        except KeyError:
            return None

    @property
    def geometry(self):
        """the portal's geometry  tools, if available and configured"""
        if self._geometry is not None:
            return self._geometry
        try:
            svcurl = self._gis.properties['helperServices']['geometry']['url']
            self._geometry = Geometry(None, svcurl, self._gis)
            return self._geometry
        except KeyError:
            return None

    @property
    def rasteranalytics(self):
        """the portal's raster analysis tools, if available and configured"""
        if self._raster_analysis is not None:
            return self._raster_analysis
        try:
            try:
                svcurl = self._gis.properties['helperServices']['rasterAnalytics']['url']
            except:
                svcurl = 'https://rdvmags01.esri.com/arcgis/rest/services/System/RasterAnalysisTools/GPServer'

            self._raster_analysis = RasterAnalysisTools(svcurl, self._gis) 
            return self._raster_analysis
        except KeyError:
            return None
        
    @property
    def geoanalytics(self):
        """the portal's geoanalytics tools, if available and configured"""
        if self._geoanalytics is not None:
            return self._geoanalytics
        try:
            try:
                svcurl = self._gis.properties['helperServices']['geoAnalytics']['url']
            except:
                svcurl = 'https://dev06999.esri.com/server/rest/services/GeoAnalyticsTools/GPServer'
            self._geoanalytics = GeoAnalyticsTools(svcurl, self._gis) 
            return self._geoanalytics
        except KeyError:
            return None

    @property
    def analysis(self):
        """the portal's spatial analysis tools, if available and configured"""
        if self._analysis is not None:
            return self._analysis
        try:
            try: 
                svcurl = self._gis.properties['helperServices']['analysis']['url']
            except:
                svcurl = 'https://analysis6.arcgis.com/arcgis/rest/services/tasks/GPServer'
            self._analysis = SpatialAnalysisTools(svcurl, self._gis)
            return self._analysis
        except KeyError:
            return None

    
class UserManager(object):
    """
    Manager class for managing GIS users. This class is not created by users directly.
    An instance of this class, called 'users', is available as a property of the Gis object.
    Users call methods on this 'users' object to manipulate (create, get, search...) users.
    """
    def __init__(self, portal):
        self._portal = portal

    def create(self, username, password, fullname, email):
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
# TODO: implementation note:
#            There is another method called createUser that
#            requires administrator access that can always
#            be used against 10.2.1 portals or later that
#            can create users whether they are builtin or
#            enterprise accounts.
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

    def list(self, max_users=1000):
        """ Return the list of users in your organization. This method does not work with 
        ArcGIS Online, only with Portal for ArcGIS.
         Arguments
            max_users : optional int, the maximum number of users to return.

        :return: The list of users in your org
        """
        # userlist = []
        users = self._portal.get_org_users(max_users)
        # for user in users:
        #     userlist.append(User(self._portal, user['username'], user))
        # return userlist
        return [User(self._portal, u['username'], u) for u in users]
        #https://portalpy.esri.com/arcgis/sharing/rest/portals/self/users?start=2&num=2&sortField=fullname&sortOrder=asc&f=pjson

    def search(self, query, sort_field='username', sort_order='asc', max_users=100, add_org=True):
        """ Searches portal users.

        Returns a list of users matching the specified query

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
               default.  If you don't want the API to append to your query
               set add_org to false.  If you use this feature with an
               OR clause such as field=x or field=y you should put this
               into parenthesis when using add_org.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        query             required string, query string.  See notes.
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
        userlist = []
        users = self._portal.search_users(query, sort_field, sort_order, max_users, add_org)
        for user in users:
            userlist.append(User(self._portal, user['username'], user))
        return userlist

        #TODO: remove org users, invite users

    def logged_in_user(self):
        """ Returns the logged in user
        """
        imemyself = self._portal.logged_in_user()
        return User(self._portal, imemyself['username'], imemyself)


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
        print(groupid)
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
        print(groupid)
        if groupid is not None:
            return Group(self._portal, groupid)
        else:
            return None

    def get(self, groupid):
        """ Returns the group object for the specified groupid.

        Arguments
            groupid        required string, the group identifier
        :return:
            None if the user is not found and returns a user object if the user is found
        """
        group = self._portal.get_group(groupid)
        if group is not None:
            return Group(self._portal, groupid)
        return None

#    def list(self, max_groups=1000):
#        """ Return the list of groups in your organization
#         Arguments
#            max_groups : optional int, the maximum number of groups to return.
#
#        :return: The list of groups in your org
#        """
#        return self.search("", max_groups=max_groups, add_org=True)
#        #https://portalpy.esri.com/arcgis/sharing/rest/community/groups?q=orgid%3A0123456789ABCDEF&sortField=&sortOrder=

    def search(self, query='', sort_field='title', sort_order='asc',
               max_groups=1000, add_org=True):
        """ Searches for portal groups.

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

def _is_shapefile(data):
    if zipfile.is_zipfile(data):
        zf = zipfile.ZipFile(data, 'r')
        namelist = zf.namelist()
        for name in namelist:
            if name.endswith('.shp') or name.endswith('.SHP'):
                return True
    return False


class ContentManager(object):
    """
    Manager class for manipulating GIS content. This class is not created by users directly.
    An instance of this class, called 'content', is available as a property of the Gis object.
    Users call methods on this 'content' object to manipulate (create, get, search...) items.
    """
    def __init__(self, portal):
        self._portal = portal

    def add(self, item_properties, data=None, thumbnail=None, metadata=None, owner=None, folder=None):
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

        itemid = self._portal.add_item(item_properties, data, thumbnail, metadata, owner, folder)

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
        max_items         optional int, maximum number of items returned, default is 6
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

    def create_folder(self, owner, title):
        """ Creates a folder for the given user with the given title.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        owner             required string, the name of the user
        ----------------  --------------------------------------------------------
        title             required string, the name of the folder to create for the owner
        ================  ========================================================

        :return:
            a json object like the following:
            {"username" : "portaladmin","id" : "bff13218991c4485a62c81db3512396f","title" : "testcreate"}
        """
        return self._portal.create_folder(owner, title)

    def delete_folder(self, owner, folder_id):
        """ Deletes a folder for the given user with the given folder_id.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        owner             required string, the name of the user
        ----------------  --------------------------------------------------------
        folder_id         required string, the id of the folder
        ================  ========================================================

        :return:
            a boolean if succeeded.
        """
        return self._portal.delete_folder(owner, folder_id)

    def get_folder_id(self, owner, folder_name):
        """ Finds the folder for a particular owner and returns its id.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        owner             required string, the name of the user
        ----------------  --------------------------------------------------------
        folder_name       required string, the name of the folder to search for
        ================  ========================================================

        :return:
            a boolean if succeeded.
        """
        return self._portal.get_folder_id(owner, folder_name)

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


#class ProjectManager(object):
#    """
#    Manager class for manipulating ArcGIS Pro projects. This class is not created by users directly.
#    An instance of this class, called 'projects', is available as a property of the GIS object.
#    Users call methods on this 'projects' object to manipulate (create, get, search...) projects.
#    """
#    def __init__(self, portal):
#        self._portal = portal
#        self.ArcGISProject = locate('arcgis.prj.ArcGISProject')

#    def create(self, project_path):
#        """ Creates a new ArcGIS Pro project and saves it at the specified file system path

#        ================  ========================================================
#        **Argument**      **Description**
#        ----------------  --------------------------------------------------------
#        project_path      required string, filesystem path of the project
#        ================  ========================================================

#        :return:
#            the project, if created, else None

#        """
#        #TODO
#        pass

#    def open(self, project_path, project_item=None):
#        """ Loads the ArcGIS Pro Project at the specified filesystem path or
#            from a project package item

#        Arguments
#            project_path        required string, the filesystem path of the ArcGIS Pro project
#                                If a project_item is provided, this is a directory path
#            project_item        optional item (type = project package) from the GIS
#                                If a project package item is provided, it is downloaded, unpacked
#                                and saved at the specified project_path
#        :return:
#            the ArcGIS Pro project object
#        """
#        if self.ArcGISProject is None:
#            raise ImportError("arcgis.map module is not installed. Please install the arcgis pro package")
            
#        return self.ArcGISProject(self._portal, project_path, project_item)
 
#    def search(self, project_name, search_path=None):
#        """ Searches for project_name in the GIS or in filesystem search path, if specified
#        :return:
#            A list of projects with the specified project name:
#        """
#        #TODO
#        pass


class Group(dict):
    """
    Represents a group (for example, San Bernardino Fires) within the GIS (ArcGIS Online or Portal for ArcGIS)
    """
    def __init__(self, portal, groupid, groupdict=None):
        dict.__init__(self)
        self._portal = portal
        self.groupid = groupid
        groupdict = self._portal.get_group(self.groupid)
        if groupdict:
            self.__dict__.update(groupdict)
            dict.update(groupdict)

    def __getattr__(self, name): # support group attributes as group.access, group.owner, group.phone etc
        return dict.__getitem__(self, name)
        """
        groupdict = self._portal.get_group(self.groupid)
        super().update(groupdict)
        self.__dict__.update(groupdict)
        return groupdict[name]
        """

    def __getitem__(self, k): # support group attributes as dictionary keys on this object, eg. group['owner']
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            groupdict = self._portal.get_group(self.groupid)
            super().update(groupdict)
            self.__dict__.update(groupdict)
            return dict.__getitem__(self, k)

    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)

    def get_thumbnail_link(self):
        """ URL to the thumbnail image """
        thumbnail_file = self.thumbnail
        if thumbnail_file is None:
            return 'http://www.arcgis.com/home/images/group-no-image.png'
        else:
            thumbnail_url_path = self._portal.con.baseurl + 'community/groups/' + self.groupid + '/info/' + thumbnail_file
            return thumbnail_url_path

    def _repr_html_(self):
        thumbnail = self.thumbnail
        if self.thumbnail is None or not self._portal.is_logged_in():
            thumbnail = self.get_thumbnail_link()
        else:
            b64 = base64.b64encode(self.get_thumbnail())
            thumbnail = "data:image/png;base64," + str(b64,"utf-8") + "' "
        
        title = 'Not Provided'
        snippet = 'Not Provided'
        description = 'Not Provided'
        owner = 'Not Provided'
        try:
            title = self.title
        except:
            title = 'Not Provided'
            
        try:
            description = self.description
        except:
            description = 'Not Provided'

        try:
            snippet = self.snippet
        except:
            snippet = 'Not Provided'

        try:
            owner = self.owner
        except:
            owner = 'Not available'

        url = self._portal.url  + "/home/group.html?id=" + self.groupid

        return """<div class="item_container">
                    <div class="item_left">
                       <a href='""" + str(url) + """' target='_blank'>
                        <img src='""" + str(thumbnail) + """' class="itemThumbnail">
                       </a>
                    </div>
        
                    <div class="item_right">
                        <a href='""" + str(url) + """' target='_blank'><b>""" + str(title) + """</b>
                        </a>
                        <br>
                        <br><b>Summary</b>: """ + str(snippet) + """
                        <br><b>Description</b>: """ + str(description)  + """
                        <br><b>Owner</b>: """ + str(owner)  + """
                        <br><b>Created</b>: """ + str(datetime.datetime.fromtimestamp(self.created/1000).strftime("%B %d, %Y")) + """
                        
                    </div>
                </div>
                """

    def _repr_html2_(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        
        if self.thumbnail is None:
            return ("<table><tr><td>"
                     "<img src='https://cdn.arcgis.com/cdn/7000/images/group-no-image.png' class='align-left frame' /></a></td><td width='90%'><b>" +
                    self.title + '</b><p>' + self.snippet + "<br/>owned by " + self.owner + "</td></tr></table>")
        else:
            b64 = base64.b64encode(self.get_thumbnail())
            #return "<div class='frame'><a href='http://developers.arcgis.com/javascript/samples/mobile_arcgis/?webmap=" + self.itemid + "' target='_blank'><img src='data:image/png;base64," + str(b64,"utf-8") + "' class='align-left frame' />" + self.title + '</a><p>' + self.snippet + "</div>"
            return ("<table><tr><td>"
                    "<img src='data:image/png;base64," + str(b64,"utf-8") + "' class='align-left frame' /></a></td><td width='90%'><b>" +
                    self.title + '</b><p>' + self.snippet + "<p>owned by "+ self.owner + "<p>" + "</td></tr></table>")
        

    """ Returns information for this group
    def get_attributes(self):
                   
        Arguments                 
            None.
            
        :return:
            a dictionary object with this group's information.  The keys in
            the dictionary object will often include:

            ================  ========================================================
            **Key**           **Value**
            ----------------  --------------------------------------------------------
            title:            The name of the group
            ----------------  --------------------------------------------------------
            isInvitationOnly  If set to true, users can't apply to join the group.
            ----------------  --------------------------------------------------------
            owner:            The owner username of the group
            ----------------  --------------------------------------------------------
            description:      Explains the group
            ----------------  --------------------------------------------------------
            snippet:          A short summary of the group
            ----------------  --------------------------------------------------------
            tags:             User-defined tags that describe the group
            ----------------  --------------------------------------------------------
            phone:            Contact information for group.
            ----------------  --------------------------------------------------------
            thumbnail:        File name relative to
                                       http://<community-url>/groups/<groupId>/info
            ----------------  --------------------------------------------------------
            created:          When group created, ms since 1 Jan 1970
            ----------------  --------------------------------------------------------
            modified:         When group last modified. ms since 1 Jan 1970
            ----------------  --------------------------------------------------------
            access:           Can be private, org, or public.
            ----------------  --------------------------------------------------------
            userMembership:   A dict with keys username and memberType.
            ----------------  --------------------------------------------------------
            memberType:       provides the calling user's access
                              (owner, admin, member, none).
            ================  ========================================================
            
        
        return self._portal.get_group(self.groupid)
    """

    def delete(self):
        """ Deletes this group.

        Returns
            a boolean indicating whether it was successful.

        """
        return self._portal.delete_group(self.groupid)

    def get_thumbnail(self):
        """ Returns the bytes that make up the thumbnail for this group.

        Arguments
            None

        Returns
            bytes that represent the image.

        Example

        .. code-block:: python

            response = group.get_thumbnail()
            f = open(filename, 'wb')
            f.write(response)
        """
        return self._portal.get_group_thumbnail(self.groupid)

    def add_users(self, usernames):
        """ Adds users to this group.
        .. note::
            This method will only work if the user for the
            Portal object is either an administrator for the entire
            Portal or the owner of the group.

        ============  ======================================
        **Argument**  **Description**
        ------------  --------------------------------------
        usernames     required string, comma-separated users
        ============  ======================================

        :return:
             A dictionary with a key of "not_added" which contains the users that were not
             added to the group.
        """
        return self._portal.add_group_users(usernames, self.groupid)

    def remove_users(self, usernames):
        """ Remove users from this group.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        usernames         required string, comma-separated list of users
        ================  ========================================================

        :return:
            a dictionary with a key notRemoved that is a list of users not removed.

        """
        return self._portal.remove_group_users(usernames, self.groupid)

    def invite_users(self, usernames, role='group_member', expiration=10080):
        """ Invites users to this group.

        .. note::
            A user who is invited to this group will see a list of invitations
            in the "Groups" tab of portal listing invitations.  The user
            can either accept or reject the invitation.

        Requires
            The user executing the command must be group owner

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        usernames:        a required string list of users to invite
        ----------------  --------------------------------------------------------
        role:             an optional string, either group_member or group_admin
        ----------------  --------------------------------------------------------
        expiration:       an optional int, specifies how long the invitation is
                          valid for in minutes.
        ================  ========================================================

        :return:
            a boolean that indicates whether the call succeeded.

        """
        return self._portal.invite_group_users(usernames, self.groupid, role, expiration)

    def reassign_to(self, target_owner):
        """ Reassigns this group to another owner.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        target_owner      required string, username of new group owner
        ================  ========================================================

        :return:
            a boolean, indicating success

        """
        return self._portal.reassign_group(self.groupid, target_owner)

    def get_members(self):
        """ Returns members of this group.

        Arguments
            None.

        Returns
            a dictionary with keys: owner, admins, and users.

            ================  ========================================================
            **Key**           **Value**
            ----------------  --------------------------------------------------------
            owner             string value, the group's owner
            ----------------  --------------------------------------------------------
            admins            list of strings, typically this is the same as the owner
            ----------------  --------------------------------------------------------
            users             list of strings, the members of the group
            ================  ========================================================

        Example (to print users in a group)

        .. code-block:: python

            response = group.get_members()
            for user in response['users'] :
                print user

        """
        return self._portal.get_group_members(self.groupid)

    def update(self, title=None, tags=None, description=None, snippet=None, access=None,
               is_invitation_only=None, sort_field=None, sort_order=None, is_view_only=None,
               thumbnail=None):
        """ Updates this group.

        .. note::
            Only provide the values for the arguments you wish to update.

        ==================  =========================================================
        **Argument**        **Description**
        ------------------  ---------------------------------------------------------
        title               optional string, name of the group
        ------------------  ---------------------------------------------------------
        tags                optional string, comma-delimited list of tags
        ------------------  ---------------------------------------------------------
        description         optional string, describes group in detail
        ------------------  ---------------------------------------------------------
        snippet             optional string, <250 characters summarizes group
        ------------------  ---------------------------------------------------------
        access              optional string, can be private, public, or org
        ------------------  ---------------------------------------------------------
        thumbnail           optional string, URL or file location to group image
        ------------------  ---------------------------------------------------------
        is_invitation_only  optional boolean, defines whether users can join by
                            request.
        ------------------  ---------------------------------------------------------
        sort_field          optional string, specifies how shared items with the
                            group are sorted.
        ------------------  ---------------------------------------------------------
        sort_order          optional string, asc or desc for ascending or descending.
        ------------------  ---------------------------------------------------------
        is_view_only        optional boolean, defines whether the group is searchable
        ==================  =========================================================

        :return:
            a boolean indicating success
        """
        return self._portal.update_group(self.groupid, title, tags, description, snippet, access, is_invitation_only, sort_field, sort_order, is_view_only, thumbnail)

    def leave(self):
        """ Removes the logged in user from the specified group.

        Requires:
            User must be logged in.

        Arguments:
             None.

        :return:
             a boolean indicating whether the operation was successful.
        """
        return self._portal.leave_group(self.groupid)


class User(dict):
    """
    Represents a registered user of the GIS (ArcGIS Online, or Portal for ArcGIS).
    """
    def __init__(self, portal, username, userdict=None):
        dict.__init__(self)
        self._portal = portal
        self.username = username
        userdict = self._portal.get_user(self.username)
        if userdict:
            self.__dict__.update(userdict)
            dict.update(userdict)

    # Using http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991

    def __getattr__(self, name): # support user attributes as user.access, user.email, user.role etc
        return dict.__getitem__(self, name)
        """
        userdict = self._portal.get_user(self.username)
        super().update(userdict)
        self.__dict__.update(userdict)
        return userdict[name]
        """

    def __getitem__(self, k): # support user attributes as dictionary keys on this object, eg. user['role']
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            userdict = self._portal.get_user(self.username)
            super().update(userdict)
            self.__dict__.update(userdict)
            return dict.__getitem__(self, k) #userdict[k]

    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)

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
        if self.thumbnail is None or not self._portal.is_logged_in():
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

        return """<div class="item_container">
                    <div class="item_left">
                       <a href='""" + str(url) + """' target='_blank'>
                        <img src='""" + str(thumbnail) + """' class="itemThumbnail">
                       </a>
                    </div>
        
                    <div class="item_right">
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
    

class Item(dict):
    """
    An item (a unit of content) in the GIS. Each item has a unique identifier and a well
    known URL that is independent of the user owning the item.
    An item can have associated binary or textual data that's available via the item data resource.
    For example, an item of type Map Package returns the actual bits corresponding to the 
    map package via the item data resource.
    """
    def __init__(self, portal, itemid, itemdict=None):
        dict.__init__(self)
        self._portal = portal
        self.itemid = itemid
        itemdict = self._portal.get_item(self.itemid)
        if itemdict:
            self.__dict__.update(itemdict)
            dict.update(itemdict)

    def __getattr__(self, name): # support item attributes
        return dict.__getitem__(self, name)
        """
        itemdict = self._portal.get_item(self.itemid)
        super().update(itemdict)
        self.__dict__.update(itemdict)
        return itemdict[name]
        """
    def __getitem__(self, k): # support item attributes as dictionary keys on this object
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            #print("KeyError:" + k)
            itemdict = self._portal.get_item(self.itemid)
            super().update(itemdict)
            self.__dict__.update(itemdict)
            return dict.__getitem__(self, k)

    def download(self, dir_name):
        data_path = 'content/items/' + self.itemid + '/data'
        if data_path:
            return self._portal.con.download_to_folder(data_path, dir_name)

    def get_thumbnail(self):
        """ Returns the bytes that make up the thumbnail for this item.
        
        Arguments
            None.
            
        Returns 
            bytes that represent the item.
            
        Example

        .. code-block:: python
        
            response = item.get_thumbnail()
            f = open(filename, 'wb')
            f.write(response)
        
        """
        thumbnail_file = self.thumbnail
        if thumbnail_file:
            thumbnail_url_path = 'content/items/' + self.itemid + '/info/' + thumbnail_file
            if thumbnail_url_path:
                return self._portal.con.get(thumbnail_url_path, try_json=False)
    
    def get_thumbnail_link(self):
        """ URL to the thumbnail image """
        thumbnail_file = self.thumbnail
        if thumbnail_file is None:
            return 'http://static.arcgis.com/images/desktopapp.png'
        else:
            thumbnail_url_path = self._portal.con.baseurl + 'content/items/' + self.itemid + '/info/' + thumbnail_file
            return thumbnail_url_path
    
    def _get_icon(self):
        if self.type.lower() == "web map":
            return "maps16.png"
        elif self.type.lower() == "web scene":
            return "webscene16.png"
        elif self.type.lower() == "cityengine web scene":
            return "webscene16.png"
        elif self.type.lower() == "pro map":
            return "mapsgray16.png"
        elif self.type.lower() == "feature service":
            return "featureshosted16.png"
        elif self.type.lower() == "map service":
            return "mapimages16.png"
        elif self.type.lower() == "image service":
            return "imagery16.png"
        elif self.type.lower() == "kml":
            return "features16.png"
        elif self.type.lower() == "wms":
            return "mapimages16.png"
        elif self.type.lower() == "feature collection":
            return "features16.png"
        elif self.type.lower() == "feature collection template":
            return "maps16.png"
        elif self.type.lower() == "geodata service":
            return "layers16.png"
        elif self.type.lower() == "globe service":
            return "layers16.png"
        elif self.type.lower() == "shapefile":
            return "datafiles16.png"
        elif self.type.lower() == "web map application":
            return "apps16.png"
        elif self.type.lower() == "map package":
            return "mapsgray16.png"
        elif self.type.lower() == "feature layer":
            return "featureshosted16.png"
        elif self.type.lower() == "map service":
            return "maptiles16.png"
        elif self.type.lower() == "map document":
            return "mapsgray16.png"
        else:
            return "layers16.png"

    def _repr_html_(self):
        thumbnail = self.thumbnail
        if self.thumbnail is None or not self._portal.is_logged_in():
            thumbnail = self.get_thumbnail_link()
        else:
            b64 = base64.b64encode(self.get_thumbnail())
            thumbnail = "data:image/png;base64," + str(b64,"utf-8") + "' width='200' height='133"
        
        snippet = self.snippet
        if snippet is None:
            snippet = ""

        portalurl = self._portal.url  + "/home/item.html?id=" + self.itemid

        locale.setlocale(locale.LC_ALL, '')
        numViews = locale.format("%d", self.numViews, grouping=True)
        return """<div class="item_container">
                    <div class="item_left">
                       <a href='""" + portalurl + """' target='_blank'>
                        <img src='""" + thumbnail + """' class="itemThumbnail">
                       </a>
                    </div>
        
                    <div class="item_right">
                        <a href='""" + portalurl + """' target='_blank'><b>""" + self.title + """</b>
                        </a>
                        <br>""" + snippet + """<img src='http://www.arcgis.com/home/js/jsapi/esri/css/images/item_type_icons/""" + self._get_icon() +"""' style="vertical-align:middle;">""" + self.type + """ by """ + self.owner + """
                        <br>Last Modified: """ + datetime.datetime.fromtimestamp(self.modified/1000).strftime("%B %d, %Y") + """
                        <br>""" + str(self.numComments) + """ comments, """ +  str(numViews) + """ views
                    </div>
                </div>
                """

    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)

    def reassign_to(self, target_owner, target_folder=None):
        """ Allows the administrator to reassign a single item from one user to another.

	    .. note::
             	If you wish to move all of a user's items (and groups) to another user then use the
                user.reassign_to() method.  This method only moves one item at a time.

        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        item_id           required string, unique identifier for the item
        ----------------  --------------------------------------------------------
        target_owner      required string, desired owner of the item
        ----------------  --------------------------------------------------------
        target_folder     optional string, folder to move the item to.
        ================  ========================================================

        :return:
            a boolean, indicating success

        """
        try:
            current_folder = self.ownerFolder
        except:
            current_folder = None
        return self._portal.reassign_item(self.itemid, self.owner, target_owner, current_folder, target_folder)
    
    def share(self, everyone=False, org=False, groups=""):
        """ Shares an item with the specified list of groups
        
        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        everyone          optional boolean, share with everyone
        ----------------  --------------------------------------------------------
        org               optional boolean, share with the organization
        ----------------  --------------------------------------------------------
        groups            optional string, 
                          comma-separated list of group IDs with which the item will be shared.
        ================  ========================================================
            
        :return:
            dict with key "notSharedWith" containing array of groups with which the item could not be shared.

        """
        try:
            folder = self.ownerFolder
        except:
            folder = None
        return self._portal.share_item(self.itemid, self.owner, folder, everyone, org, groups)

    def unshare(self, groups):
        """ Stops sharing the item with the specified list of groups
        
        ================  ========================================================
        **Argument**      **Description**
        ----------------  --------------------------------------------------------
        groups            optional string, 
                          comma-separated list of group IDs with which the item will be unshared.
        ================  ========================================================
            
        :return:
            dict with key "notUnsharedFrom" containing array of groups from which the item could not be unshared.


        
        """
        try:
            folder = self.ownerFolder
        except:
            folder = None
        return self._portal.unshare_item(self.itemid, self.owner, folder, groups)

    def delete(self):
        """ Deletes an item.
            
        :return:
            a boolean, indicating success
        
        """
        try:
            folder = self.ownerFolder
        except:
            folder = None
        return self._portal.delete_item(self.itemid, self.owner, folder)

    def update(self, item_properties=None, data=None, thumbnail=None, metadata=None):
        """ Updates an item in a Portal.  
	
        
        .. note:: 
            That content can be a file (such as a layer package, geoprocessing package,
            map package) or it can be a URL (to an ArcGIS Server service, WMS service,
            or an application).

            If you are uploading a package or other file, provide a path or URL
            to the file in the data argument.

            Only pass in arguments for properties you want to update.
            All other properties will be left as they are.  If you 
            want to update description, then only provide
            the description argument in item_properties.

        
        ============     ====================================================
        **Argument**     **Description**
        ------------     ----------------------------------------------------
        item_properties  optional dictionary, see below for the keys and values
        ------------     ----------------------------------------------------
        data             optional string, either a path or URL to the data
        ------------     ----------------------------------------------------
        thumbnail        optional string, either a path or URL to an image
        ------------     ----------------------------------------------------
        metadata         optional string, either a path or URL to metadata
        ============     ====================================================


        ================  ============================================================================
         **Key**           **Value**
        ----------------  ----------------------------------------------------------------------------
        type              optional string, indicates type of item.  See URL 1 below for valid values.
        ----------------  ----------------------------------------------------------------------------
        typeKeywords      optinal string list.  Lists all sub-types.  See URL 1 for valid values.
        ----------------  ----------------------------------------------------------------------------
        description       optional string.  Description of the item.
        ----------------  ----------------------------------------------------------------------------
        title             optional string.  Name of the item.  
        ----------------  ----------------------------------------------------------------------------
        url               optional string.  URL to item that are based on URLs.
        ----------------  ----------------------------------------------------------------------------
        tags              optional string of comma-separated values.  Used for searches on items.
        ----------------  ----------------------------------------------------------------------------
        snippet           optional string.  Provides a very short summary of the what the item is.
        ----------------  ----------------------------------------------------------------------------
        extent            optional string with comma separated values for min x, min y, max x, max y.
        ----------------  ----------------------------------------------------------------------------
        spatialReference  optional string.  Coordinate system that the item is in.
        ----------------  ----------------------------------------------------------------------------
        accessInformation optional string.  Information on the source of the content.
        ----------------  ----------------------------------------------------------------------------
        licenseInfo       optinal string, any license information or restrictions regarding the content.
        ----------------  ----------------------------------------------------------------------------
        culture           optional string.  Locale, country and language information.
        ----------------  ----------------------------------------------------------------------------
        access            optional string.  Valid values: private, shared, org, or public.
        ----------------  ----------------------------------------------------------------------------
        commentsEnabled   optional boolean.  Default is true.  Controls whether comments are allowed.
        ----------------  ----------------------------------------------------------------------------
        culture           optional string.  Language and country information.
        ================  ============================================================================

            
	URL 1: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000ms000000

        :return:
             a boolean, that indicates success.
        """
        try:
            folder = self.ownerFolder
        except:
            folder = None
        return self._portal.update_item(self.itemid, item_properties, data, thumbnail, metadata, self.owner, folder)

    def get_data(self):
        return self._portal.get_item_data(self.itemid)
    
    """
    def move(self, folder):
        pass

    def get_dependent_items(self):
        pass

    def get_referencing_items(self):
        pass
    """

    def get_item_dependencies(self):
        return self._portal.get_item_dependencies(self.itemid)

    def get_item_dependents_to(self):
        return self._portal.get_item_dependents_to(self.itemid)

    def publish(self, publish_parameters=None, address_fields=None, output_type=None, overwrite=False):
        """
        Publishes a hosted service based on an existing source item (this item).
        Publishers can create feature services as well as tiled map services.
        Feature services can be created using input files of type csv, shapefile, serviceDefinition, featureCollection, and fileGeodatabase.
        CSV files that contain location fields, (ie.address fields or X, Y fields) are spatially enabled during the process of publishing.
        Shapefiles and file geodatabases should be packaged as *.zip files.
        Tiled map services can be created from service definition (*.sd) files, tile packages, and existing feature services.
        Service definitions are authored in ArcGIS for Desktop and contain both the cartographic definition for a map as well as its packaged data together with the definition of the geo-service to be created.
        Use the Analyze operation to generate the default publishing parameters for CSVs.
        address_fields : dict containing mapping of df columns to address fields, eg: { "CountryCode" : "Country"} or { "Address" : "Address" } 

        """
        
       
        params = {
            "f" : "json"
        }
        if self['type'] == 'Service Definition':
           fileType = 'serviceDefinition'
        elif self['type'] == 'Feature Collection':
           fileType = 'featureCollection'
        elif self['type'] == 'CSV':
           fileType = 'CSV'
        elif self['type'] == 'Shapefile':
           fileType = 'shapefile'
        elif self['type'] == 'File Geodatabase':
           fileType = 'fileGeodatabase'

        try:
            folder = self.ownerFolder
        except:
            folder = None
        
        if publish_parameters is None:
            if fileType == 'shapefile':
                publish_parameters =  {"hasStaticData":True, "name":os.path.splitext(self['name'])[0], "maxRecordCount":2000, "layerInfo":{"capabilities":"Query"} }
            elif fileType == 'CSV':
                path = "content/features/analyze"

                postdata = {
                    "f": "pjson",
                    "itemid" : self.itemid,
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
                publish_parameters =  res['publishParameters']
                if address_fields is not None:
                    publish_parameters.update({"addressFields":address_fields})
                publish_parameters = json.dumps(publish_parameters)
                
        ret = self._portal.publish_item(self.itemid, None, None, fileType, publish_parameters, output_type, overwrite, self.owner, folder)
        
        #svc_id = ret[0]['serviceItemId']
        #return Item(self._portal, svc_id)
        
        job_id = ret[0]['jobId']
        serviceitem_id = ret[0]['serviceItemId']
        path = 'content/users/' + self.owner
        if folder is not None:
            path = path + '/' + folder + '/'

        path = path + '/items/' + serviceitem_id + '/status'
        #print(path)
        params = { 
            "f" : "json",
            "jobid" : job_id
                  }
        job_response = self._portal.con.post(path, params)

        # Query and report the Analysis job status.
        #
        num_messages = 0
        print(str(job_response))
        if "status" in job_response:
            while not job_response.get("status") == "completed":
                time.sleep(5)

                job_response = self._portal.con.post(path, params)
                
                #print(str(job_response))
                if job_response.get("status") == "esriJobFailed":
                    raise Exception("Job failed.")
                elif job_response.get("status") == "esriJobCancelled":
                    raise Exception("Job cancelled.")
                elif job_response.get("status") == "esriJobTimedOut":
                    raise Exception("Job timed out.")

        else:
            raise Exception("No job results.")
        
        return Item(self._portal, serviceitem_id)
        return ret

def rot13(s):
    result = ""

    # Loop over characters.
    for v in s:
        # Convert to number with ord.
        c = ord(v)

        # Shift number back or forward.
        if c >= ord('a') and c <= ord('z'):
            if c > ord('m'):
                c -= 13
            else:
                c += 13
        elif c >= ord('A') and c <= ord('Z'):
            if c > ord('M'):
                c -= 13
            else:
                c += 13

        # Append to result.
        result += chr(c)

    # Return transformation.
    return result


from __future__ import absolute_import
import os
import json
import time
import base64
import locale
import datetime
import tempfile
from six.moves.urllib.error import HTTPError
from ._util import _is_shapefile, Error
from ._usermanager import User
from ..lyr import FeatureCollection

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
        self.thumbnail = None
        self._workdir = tempfile.gettempdir()
        # itemdict = self._portal.get_item(self.itemid)
        self._hydrated = False
        if itemdict:
            self.__dict__.update(itemdict)
            dict.update(itemdict)

    def __getattr__(self, name): # support item attributes
        # return dict.__getitem__(self, name)
        if not self._hydrated:
            itemdict = self._portal.get_item(self.itemid)
            self._hydrated = True
            super(Item, self).update(itemdict)
            self.__dict__.update(itemdict)
        return dict.__getitem__(self, name)

    def __getitem__(self, k): # support item attributes as dictionary keys on this object
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            if not self._hydrated:
                itemdict = self._portal.get_item(self.itemid)
                self._hydrated = True
                super(Item, self).update(itemdict)
                self.__dict__.update(itemdict)
            return dict.__getitem__(self, k)

    def download(self, dir):
        data_path = 'content/items/' + self.itemid + '/data'
        if not dir:
            dir = self._workdir
        if data_path:
            return self._portal.con.download_to_folder(data_path, dir)

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

    def download_thumbnail(self, dir=None):
        """ Downloads the item thumbnail for this item, returns file path. """
        thumbnail_file = self.thumbnail

        # Only proceed if a thumbnail exists
        if thumbnail_file:
            thumbnail_url_path = 'content/items/' + self.itemid  + '/info/' + thumbnail_file
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

    def get_thumbnail_link(self):
        """ URL to the thumbnail image """
        thumbnail_file = self.thumbnail
        if thumbnail_file is None:
            return 'http://static.arcgis.com/images/desktopapp.png'
        else:
            thumbnail_url_path = self._portal.con.baseurl + '/content/items/' + self.itemid + '/info/' + thumbnail_file
            return thumbnail_url_path

    def get_metadata(self):
        """ Returns the item metadata for the specified item id. """
        metadataurlpath = 'content/items/' + self.itemid  + '/info/metadata/metadata.xml'
        try:
            return self._portal.con.get(metadataurlpath, try_json=False)

        # If the get operation returns a 400 HTTP Error then the metadata simply
        # doesn't exist, let's just return None in this case
        except HTTPError as e:
            if e.code == 400 or e.code == 500:
                return None
            else:
                raise e

    def download_metadata(self, dir=None):
        """ Downloads the item metadata for the specified item id, returns file path. """
        metadataurlpath = 'content/items/' + self.itemid + '/info/metadata/metadata.xml'
        if not dir:
            dir = self._workdir
        filepath = os.path.join(dir, 'metadata.xml')
        try:
            self._portal.con.download(metadataurlpath, filepath)
            return filepath

        # If the get operation returns a 400 HTTP/IO Error then the metadata
        # simply doesn't exist, let's just return None in this case
        except HTTPError as e:
            if e.code == 400 or e.code == 500:
                return None
            else:
                raise e

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
        if self.thumbnail is None or not self._portal.is_logged_in:
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
        return """<div class="item_container" style="height: auto; overflow: hidden; border: 1px solid #cfcfcf; border-radius: 2px; background: #f6fafa; line-height: 1.21429em; padding: 10px;">
                    <div class="item_left" style="width: 210px; float: left;">
                       <a href='""" + portalurl + """' target='_blank'>
                        <img src='""" + thumbnail + """' class="itemThumbnail">
                       </a>
                    </div>

                    <div class="item_right"     style="float: none; width: auto; overflow: hidden;">
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

    def __repr__(self):
        return '<%s title:"%s" type:%s owner:%s>' % (type(self).__name__, self.title, self.type, self.owner)

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

    def get_data(self, try_json=True):
        """Returns the data for the item. Returns a dict if try_json is True. To convert this
        dict to string using json.dumps(data). Else, returns the data
        as a byte array, that can be converted to string using data.decode('utf-8')"""
        return self._portal.get_item_data(self.itemid, try_json)

    def dependent_upon(self):
        """ Returns items and urls, etc that this items depends upon  """
        return self._portal.get_item_dependencies(self.itemid)

    def dependent_to(self):
        """ Returns items and urls, etc dependend upon this item. """
        return self._portal.get_item_dependents_to(self.itemid)

    _RELATIONSHIP_TYPES = frozenset(['Map2Service', 'WMA2Code',
                                     'Map2FeatureCollection', 'MobileApp2Code', 'Service2Data',
                                     'Service2Service'])

    _RELATIONSHIP_DIRECTIONS = frozenset(['forward', 'reverse'])

    def related_items(self, rel_type, direction="forward"):
        """ Returns items related to this item. Relationsships can be added and deleted using item.add_relationship() and item.delete_relationship() respectively.
        rel_type is one of ['Map2Service', 'WMA2Code', 'Map2FeatureCollection', 'MobileApp2Code', 'Service2Data', 'Service2Service']
        direction is one of ['forward', 'reverse'] """
        if not rel_type in self._RELATIONSHIP_TYPES:
            raise Error('Unsupported relationship type: ' + rel_type)
        if not direction in self._RELATIONSHIP_DIRECTIONS:
            raise Error('Unsupported direction: ' + direction)

        related_items = []

        postdata = { 'f' : 'json' }
        postdata['relationshipType'] = rel_type
        postdata['direction'] = direction
        resp = self._portal.con.post('content/items/' + self.itemid + '/relatedItems', postdata)
        for related_item in resp['relatedItems']:
            related_items.append(Item(self._portal, related_item['id'], related_item))
        return related_items

    def add_relationship(self, rel_item, rel_type):
        """ Adds a relationship from this item to rel_item.
        Relationships are not tied to an item. They are directional links from an origin item
        to a destination item and have a type. The type defines the valid origin and destination
        item types as well as some rules. See Relationship types in REST API help for more information.
        Users don't have to own the items they relate unless so defined by the rules of the
        relationship type.
        Users can only delete relationships they create.
        Relationships are deleted automatically if one of the two items is deleted.

        rel_item is the related item
        rel_type is one of ['Map2Service', 'WMA2Code', 'Map2FeatureCollection', 'MobileApp2Code', 'Service2Data', 'Service2Service']. See Relationship types in REST API help for more information on this parameter
        Returns True if the relationship was added
        """
        if not rel_type in self._RELATIONSHIP_TYPES:
            raise Error('Unsupported relationship type: ' + rel_type)

        postdata = { 'f' : 'json' }
        postdata['originItemId'] = self.itemid
        postdata['destinationItemId'] = rel_item.itemid
        postdata['relationshipType'] = rel_type
        path = 'content/users/' + self.owner

        path += '/addRelationship'
        print
        resp = self._portal.con.post(path, postdata)
        if resp:
            return resp.get('success')

    def delete_relationship(self, rel_item, rel_type):
        """ Deletes a relationship between this item and the rel_item.
        rel_item is the related item
        rel_type is one of ['Map2Service', 'WMA2Code', 'Map2FeatureCollection', 'MobileApp2Code', 'Service2Data', 'Service2Service']
        Returns True if the relationship was deleted
        """
        if not rel_type in self._RELATIONSHIP_TYPES:
            raise Error('Unsupported relationship type: ' + rel_type)
        postdata = { 'f' : 'json' }
        postdata['originItemId'] =  self.itemid
        postdata['destinationItemId'] = rel_item.itemid
        postdata['relationshipType'] = rel_type
        path = 'content/users/' + self.owner


        path += '/deleteRelationship'
        resp = self._portal.con.post(path, postdata)
        if resp:
            return resp.get('success')

    def publish(self, publish_parameters=None, address_fields=None, output_type=None, overwrite=False):
        """
        Publishes a hosted service based on an existing source item (this item).
        Publishers can create feature services as well as tiled map services.
        Feature services can be created using input files of type csv, shapefile, serviceDefinition, featureCollection, and fileGeodatabase.
        CSV files that contain location fields, (ie.address fields or X, Y fields) are spatially enabled during the process of publishing.
        Shapefiles and file geodatabases should be packaged as *.zip files.
        Tiled map services can be created from service definition (*.sd) files, tile packages, and existing feature services.
        Service definitions are authored in ArcGIS for Desktop and contain both the cartographic definition for a map as well as its packaged data together with the definition of the geo-service to be created.
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

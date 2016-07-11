from __future__ import absolute_import
import os
import json
import time
import base64
import locale
import datetime
import tempfile
from ._util import _tempinput, Error
from six.moves.urllib_error import HTTPError
###########################################################################
class Group(dict):
    """
    Represents a group (for example, San Bernardino Fires) within the GIS (ArcGIS Online or Portal for ArcGIS)
    """
    def __init__(self, portal, groupid, groupdict=None):
        dict.__init__(self)
        self._portal = portal
        self.groupid = groupid
        self.thumbnail = None
        self._workdir = tempfile.gettempdir()
        # groupdict = self._portal.get_group(self.groupid)
        self._hydrated = False
        if groupdict:
            self.__dict__.update(groupdict)
            dict.update(groupdict)

    def __getattr__(self, name): # support group attributes as group.access, group.owner, group.phone etc
        # return dict.__getitem__(self, name)
        if not self._hydrated:
            groupdict = self._portal.get_group(self.groupid)
            self._hydrated = True
            super(Group, self).update(groupdict)
            self.__dict__.update(groupdict)
        return dict.__getitem__(self, name)


    def __getitem__(self, k): # support group attributes as dictionary keys on this object, eg. group['owner']
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            if not self._hydrated:
                groupdict = self._portal.get_group(self.groupid)
                self._hydrated = True
                super(Group, self).update(groupdict)
                self.__dict__.update(groupdict)
            return dict.__getitem__(self, k)

    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)

    def __repr__(self):
        return '<%s title:"%s" owner:%s>' % (type(self).__name__, self.title, self.owner)

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
        if self.thumbnail is None or not self._portal.is_logged_in:
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
        return """<div class="9item_container" style="height: auto; overflow: hidden; border: 1px solid #cfcfcf; border-radius: 2px; background: #f6fafa; line-height: 1.21429em; padding: 10px;">
                    <div class="item_left" style="width: 210px; float: left;">
                       <a href='""" + str(url) + """' target='_blank'>
                        <img src='""" + str(thumbnail) + """' class="itemThumbnail">
                       </a>
                    </div>

                    <div class="item_right" style="float: none; width: auto; overflow: hidden;">
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

    def content(self, max_items=1000):
        """Returns a list of items shared with this group."""
        itemlist = []
        items = self._portal.search('group:' + self.groupid, max_results=max_items)
        for item in items:
            itemlist.append(Item(self._portal, item['id'], item))
        return itemlist

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

    def download_thumbnail(self, dir=None):
        """ Downloads the group thumbnail for this group, returns file path. """
        thumbnail_file = self.thumbnail

        # Only proceed if a thumbnail exists
        if thumbnail_file:
            thumbnail_url_path = 'community/groups/' + self.groupid + '/info/' + thumbnail_file
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

    def add_users(self, usernames):
        """ Adds users to this group.
        .. note::
            This method will only work if the user for the
            Portal object is either an administrator for the entire
            Portal or the owner of the group.

        ============  ======================================
        **Argument**  **Description**
        ------------  --------------------------------------
        usernames     list of usernames
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
###########################################################################
class DatastoreItem(dict):
    """
    Represents a datastore item (folder, database or bigdata fileshare) within the GIS's data store
    """
    def __init__(self, datastore, path):
        dict.__init__(self)
        self._datastore = datastore
        self._portal = datastore._portal
        self._admin_url = datastore._admin_url

        self.datapath = path


        params = { "f" : "json" }
        path = self._admin_url + "/data/items" + self.datapath

        datadict = self._portal.con.post(path, params)

        if datadict:
            self.__dict__.update(datadict)
            dict.update(datadict)

    def __getattr__(self, name): # support group attributes as group.access, group.owner, group.phone etc
        return dict.__getitem__(self, name)

    def __getitem__(self, k): # support group attributes as dictionary keys on this object, eg. group['owner']
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            params = { "f" : "json" }
            path = self._admin_url + "/data/items" + self.datapath

            datadict = self._portal.con.post(path, params)
            super(DatastoreItem, self).update(datadict)
            self.__dict__.update(datadict)
            return dict.__getitem__(self, k)

    def __str__(self):
        state = ["   %s=%r" % (attribute, value) for (attribute, value) in self.__dict__.items()]
        return '\n'.join(state)

    def __repr__(self):
        return '<%s title:"%s" type:"%s">' % (type(self).__name__, self.path, self.type)

    @property
    def manifest(self):
        """
        The manifest resource for bigdata fileshares,
        """
        data_item_manifest_url = self._admin_url + '/data/items' + self.datapath + "/manifest"

        params = {
            'f': 'json',
        }
        res = self._portal.con.post(data_item_manifest_url, params)
        return res

    @manifest.setter
    def manifest(self, value):
        """
        Updates the manifest resource for bigdata fileshares,
        """
        manifest_upload_url =  self._admin_url + '/data/items' + self.datapath + '/manifest/update'

        with _tempinput(json.dumps(value)) as tempfilename:
            # Build the files list (tuples)
            files = []
            files.append(('manifest', tempfilename, os.path.basename(tempfilename)))

            postdata = {
                'f' : 'pjson'
            }

            resp = self._portal.con.post(manifest_upload_url, postdata, files)

            if resp['status'] == 'success':
                return True
            else:
                print(str(resp))
                return False

    @property
    def ref_count(self):
        """
        The total number of references to this data item that exist on the server. You can use this property to determine if this data item can be safely deleted (or taken down for maintenance).
        """
        data_item_manifest_url = self._admin_url + '/data/computeTotalRefCount'

        params = {
            'f': 'json',
            'itemPath': self.datapath
        }
        res = self._portal.con.post(data_item_manifest_url, params)
        return res["totalRefCount"]

    def delete(self):
        """
        Unregisters this data item from the data store
        """
        params = {
            "f" : "json" ,
            "itempath" : self.datapath,
            "force": True
        }
        path = self._admin_url + "/data/unregisterItem"

        resp = self._portal.con.post(path, params)
        if resp:
            return resp.get('success')
        else:
            return False

    def update(self, item):
        """
        Edits this data item to update its connection information.

        Input
            item - the dict representation of the updated item
        Output:
              True if successful
        """
        params = {
            "f" : "json" ,
            "item" : item
        }
        path = self._admin_url +  "/data/items" + self.datapath +  "/edit"

        resp = self._portal.con.post(path, params)
        if resp ['status'] == 'success':
            return True
        else:
            return False

    def validate(self):
        """
        Validates that this data item's path (for file shares) or connection string (for databases)
        is accessible to every server node in the site

        Output:
              True if successful
        """
        params = { "f" : "json" }
        path = self._admin_url + "/data/items" + self.datapath

        datadict = self._portal.con.post(path, params)

        params = {
            "f" : "json",
            "item": datadict
        }
        path = self._admin_url + "/data/validateDataItem"

        res = self._portal.con.post(path, params)
        return res['status'] == 'success'

    def list_datasets(self):
        """
        Lists the datasets in a big data file share.
        """
        data_item_manifest_url = self._admin_url + '/data/items' + self.datapath + "/manifest"

        params = {
            'f': 'json',
        }
        res = self._portal.con.post(data_item_manifest_url, params)

        for dataset in res['datasets']:
            print("/server/datastores" + self.datapath + '/' + dataset['path'] + ' ('+ dataset['type'] + ')')

###########################################################################
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
###########################################################################
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
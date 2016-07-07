from __future__ import absolute_import
import os
import base64
import datetime
import tempfile

from ._contentmanager import Item

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

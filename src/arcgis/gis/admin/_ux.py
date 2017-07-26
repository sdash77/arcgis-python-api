from .. import _PortalResourceManager

###########################################################################
class UX(object):
    """Helper class for modifying the portal home page. This class is not created by users directly. An instance of
    the class, called 'ux', is available as a property of the GIS object. Users call methods on this 'ux' object
    to set banner, background, logo, name etc."""
    #----------------------------------------------------------------------
    def __init__(self, gis):
        """Creates helper object to manage portal home page, resources, update resources"""
        self._gis = gis
        self._portal = gis._portal
    #----------------------------------------------------------------------
    def set_banner(self, banner_file=None, is_built_in=False, custom_html = None):
        """
        Configure your home page by setting the organization's banner. You can choose one of the 5 built-in banners or
        upload your own. For best results the dimensions of the banner image should be 960 x 180 pixels. You can also
        specify a custom html for how the banner space should appear. For more information, refer to
        http://server.arcgis.com/en/portal/latest/administer/windows/configure-home.htm

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        banner_file       optional string. If uploading a custom banner, then path to the
                           banner file. If using a built-in banner, valid values are
                           banner-1, banner-2, banner-3, banner-4, banner-5. If None, existing
                           banner is remove.
        ----------------  ---------------------------------------------------------------
        is_built_in       optional bool, default=False. Specify True if using a built-in
                            banner file.
        ----------------  ---------------------------------------------------------------
        custom_html       optional string. Specify exactly how the banner should appear in
                            html. For help on this, refer to
                            http://server.arcgis.com/en/portal/latest/administer/windows/supported-html.htm
        ================  ===============================================================

        :return: True | False
        """
        # check if banner has to be removed
        if not banner_file:
            #remove code
            portal_resources = _PortalResourceManager(self._gis)
            #find existing banner resource file
            resource_list = portal_resources.list()
            e_banner = [banner for banner in resource_list if banner['key'].startswith('banner')]

            #loop through and remove existing banner resource file
            for banner in e_banner:
                try:
                    portal_resources.delete(banner['key'])
                except:
                    continue

            #reset the home page - recurse
            return self.set_banner('banner-2',True)

        # Add resource if using a custom banner file.
        rotator_panel = []
        if not is_built_in:
            # find image extension
            from pathlib import Path
            fpath = Path(banner_file)
            f_splits = fpath.name.split('.')
            if len(f_splits) > 1 and f_splits[1] == 'png':
                key_val = 'banner.png'
            elif len(f_splits) > 1 and f_splits[1] == 'jpg':
                key_val = 'banner.jpg'
            else:
                raise RuntimeError('Invalid image extension')

            portal_resources = _PortalResourceManager(self._gis)
            add_result = portal_resources.add(key_val, banner_file)

            if add_result and custom_html:
                rotator_panel = [{"id": "banner-custom",
                                  "innerHTML": custom_html}]

            elif add_result and not custom_html:
                # set rotator_panel_text
                rotator_panel = [{"id": "banner-custom",
                                  "innerHTML": "<img src='{}/portals/self/resources/{}?token=SECURITY_TOKEN' "
                                               "style='-webkit-border-radius:0 0 10px 10px; -moz-border-radius:0 0 10px 10px;"
                                               " -o-border-radius:0 0 10px 10px; border-radius:0 0 10px 10px; margin-top:0; "
                                               "width:960px;'/>".format(
                                      self._portal.con.baseurl, key_val)}]
        else:  # using built-in
            if not custom_html:  # if no custom html is specified for built-in image
                rotator_panel = [{"id": banner_file,
                                  "innerHTML": "<img src='images/{}.jpg' "
                                               "style='-webkit-border-radius:0 0 10px 10px; -moz-border-radius:0 0 10px 10px; "
                                               "-o-border-radius:0 0 10px 10px; border-radius:0 0 10px 10px; margin-top:0; "
                                               "width:960px; height:180px;'/><div style='position:absolute; bottom:80px; "
                                               "left:80px; max-height:65px; width:660px; margin:0;'>"
                                               "<img src='{}/portals/self/resources/thumbnail.png?token=SECURITY_TOKEN' "
                                               "class='esriFloatLeading esriTrailingMargin025' style='margin-bottom:0; "
                                               "max-height:100px;'/><span style='position:absolute; bottom:0; margin-bottom:0; "
                                               "line-height:normal; font-family:HelveticaNeue,Verdana; font-weight:600; "
                                               "font-size:32px; color:#369;'>{}</span></div>".format(banner_file,
                                                                                                     self._portal.con.baseurl,
                                                                                                     self._gis.properties.name)}]
            else:  # using custom html
                rotator_panel = [{"id": banner_file,
                                  "innerHTML": custom_html}]

        # Update the portal self with these banner values
        update_result = self._gis.update_properties({"rotatorPanels": rotator_panel})
        return update_result
    #----------------------------------------------------------------------
    def set_logo(self, logo_file=None):
        """
        Configure your home page by setting the organization's logo image. For best results the logo file should be
        65 x 65 pixels in dimension.

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-general.htm

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        logo_file         optional string. Specify path to image file. If None, existing thumbnail is removed.
        ================  ===============================================================

        :return: True | False
        """

        # Add resource file
        portal_resources = _PortalResourceManager(self._gis)
        key_val=""
        # find image extension
        if logo_file:
            from pathlib import Path
            fpath = Path(logo_file)
            f_splits = fpath.name.split('.')
            if len(f_splits) > 1 and f_splits[1] == 'png':
                key_val = 'thumbnail.png'
            elif len(f_splits) > 1 and f_splits[1] == 'jpg':
                key_val = 'thumbnail.jpg'
            elif len(f_splits) > 1 and f_splits[1] == 'gif':
                key_val = 'thumbnail.gif'

            add_result = portal_resources.add(key_val, logo_file)
        else:
            for ext in ['.png', '.jpg', '.gif']:
                try:
                    portal_resources.delete('thumbnail' + ext)
                except:
                    continue
            key_val = None

        # Update the portal self with these banner values
        update_result = self._gis.update_properties({"thumbnail": key_val})
        return update_result
    #----------------------------------------------------------------------
    def get_logo(self, download_path):
        """
        Get your organization's logo/thumbnail. You can use the `set_logo()` method to set an image as your logo.
        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        download_path     required string. Folder path to download the logo file.
        ================  ===============================================================

         :return: Path to downloaded logo file.
        """
        portal_resources = _PortalResourceManager(self._gis)
        props = self._gis.properties
        if 'thumbnail' in props:
            resource = props['thumbnail']
            if resource is not None and \
               len(str(resource)) > 0:
                output = portal_resources.get(resource_name=resource,
                                              download_path=download_path)
                return output
        return None
    #----------------------------------------------------------------------
    def get_name(self):
        """
        Returns the site's name.  The name can get defined using the 'set_name()'.

         :return: string of the name of the site
        """
        return self._gis.properties['name']
    #----------------------------------------------------------------------
    def set_name(self, name):
        """
        Allows for the setting of a site's name.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        name              required string. Name of the site.
        ================  ===============================================================


         :return: boolean
        """
        return self._gis.update_properties({"name": name})
    #----------------------------------------------------------------------
    def get_description(self):
        """
        Returns the site's description.  The name can get defined using the 'set_description()'.

         :return: dictionary
        """
        return {'description' : self._gis.properties['description'],
                'visible' : self._gis.properties['showHomePageDescription']}
    #----------------------------------------------------------------------
    def set_description(self, description=None, visible=False):
        """
        Allows for the setting of a site's description.
        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        description       optional string. descriptive text of the site. If None, the
                          value is reset to default.
        ----------------  ---------------------------------------------------------------
        visible           optional boolean. If True, the desciptive text will show on the
                          home page. If False, the descriptive text will not be displayed
        ================  ===============================================================

         :return: boolean
        """
        if description is None:
            description = "<br/>"
        return self._gis.update_properties({'description': description,
                                            'showHomePageDescription' : visible})
    #----------------------------------------------------------------------
    def get_featured_content(self):
        """
        Returns the featured content group information.  The information
        can then be set using the 'set_featured_content()'.

          :return: dictionary

        :Usage Example:

        >>> data = ux.get_featured_content()
        >>> ux.set_featured_content(**data)
        True

        """
        return {'group' : self._gis.properties['homePageFeaturedContent'],
                'count' : self._gis.properties['homePageFeaturedContentCount']}
    #----------------------------------------------------------------------
    def set_featured_content(self, group=None, count=12):
        """
        Sets the featured content group for the homepage.
        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        group             optional string or Group object. The group to show in the
                          featured content section of the homepage.  A value of None will
                          reset to default.
        ----------------  ---------------------------------------------------------------
        visible           optional boolean. If True, the desciptive text will show on the
                          home page. If False, the descriptive text will not be displayed
        ================  ===============================================================

         :return: boolean
        """
        from .. import Group
        if isinstance(group, Group):
            group = group.groupid
        if group is None:
            group = ""
        return self._gis.update_properties({'homePageFeaturedContent': group,
                                            'homePageFeaturedContentCount' : count})
    #----------------------------------------------------------------------
    def set_background(self, background_file=None, is_built_in=True):
        """
        Configure your home page by setting the organization's background image. You can choose no image, a built-in image
        or upload your own. If you upload your own image, the image is positioned at the top and center of the page.
        The image repeats horizontally if it is smaller than the browser or device window. For best results, if you want
        a single, nonrepeating background image, the image should be 1,920 pixels wide (or smaller if your users are on
        smaller screens). The website does not resize the image. You can upload a file up to 1 MB in size.

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-home.htm

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        background_file   optional string. If using a custom background, specify path to image file.
                            To remove an existing background, specify None for this argument and
                            False for is_built_in argument.
        ----------------  ---------------------------------------------------------------
        is_built_in       optional bool, default=True. The built-in background is set by default.
                            If uploading a custom image, this parameter is ignored.
        ================  ===============================================================

        :return: True | False
        """

        # Add resource if using a custom background file.
        background_update_val = None
        if background_file:
            # find image extension
            from pathlib import Path
            fpath = Path(background_file)
            f_splits = fpath.name.split('.')
            if len(f_splits) > 1 and f_splits[1] == 'png':
                key_val = 'background.png'
            elif len(f_splits) > 1 and f_splits[1] == 'jpg':
                key_val = 'background.jpg'
            else:
                raise RuntimeError('Invalid image extension')

            portal_resources = _PortalResourceManager(self._gis)
            add_result = portal_resources.add(key_val, background_file)
            if not add_result:
                raise RuntimeError("Error adding background image as a resource file")
            background_update_val = key_val

        elif is_built_in:  # using built-in
            background_update_val = 'images/arcgis_background.jpg'
        else:
            background_update_val = "none"

        # Update the portal self with these banner values
        update_result = self._gis.update_properties({"backgroundImage": background_update_val})
        return update_result
    #----------------------------------------------------------------------
    def set_name_description(self, name, description):
        """
        Configure your home page by setting the organization's name and description

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-general.htm

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        name              required string. Specify a name for the organization
        ----------------  ---------------------------------------------------------------
        description       required string. Specify a description about the organization
        ================  ===============================================================

        :return: True | False
        """

        # Add resource
        key_val = 'localizedOrgProperties'
        text = {'default':{'name':name,
                           'description':description}}

        portal_resources = _PortalResourceManager(self._gis)
        add_result = portal_resources.add(key_val, text=text)

        # Update the portal self with these banner values
        update_result = self._gis.update_properties(text['default'])
        return update_result
    #----------------------------------------------------------------------
    def get_banner(self, download_path):
        """
        Get your organization's home page banner image. You can use the `set_banner()` method to set an image or custom HTML
        code as your banner.
        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        download_path     required string. Folder path to download the banner file.
        ================  ===============================================================

         :return: Path to downloaded banner file.
        """
        #create a portal resource manager obj
        portal_resources = _PortalResourceManager(self._gis)

        #find existing banner resource file
        resource_list = portal_resources.list()
        e_banner = [banner for banner in resource_list if banner['key'].startswith('banner')]

        #loop through and remove existing banner resource file
        for banner in e_banner:

            try:
                download_path = portal_resources.get(banner['key'], download_path)

            except:
                continue
        return download_path
    #----------------------------------------------------------------------
    def get_background(self, download_path):
        """
        Get your organization's home page background image. You can use the `set_background()` method to set an image
        as the home page background image.

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-home.htm

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        download_path     required string. Folder path to download the background file.
        ================  ===============================================================

        :return: Path to downloaded background file.
        """

        #create a portal resource manager obj
        portal_resources = _PortalResourceManager(self._gis)

        #find existing banner resource file
        resource_list = portal_resources.list()
        e_background = [banner for banner in resource_list if banner['key'].startswith('background')]

        #loop through and remove existing banner resource file
        for background in e_background:

            try:
                download_path = portal_resources.get(background['key'], download_path)

            except:
                continue
        return download_path
    #----------------------------------------------------------------------
    def set_enable_comments(self, enable=False):
        """
        Sets the comments property on the items
        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        enable            optional boolean. If True, the comments for the site are turned
                          on.  False will disable comments (default)
        ================  ===============================================================

         :return: boolean

        """
        return self._gis.update_properties({'commentsEnabled' : enable})
    #----------------------------------------------------------------------
    def get_enable_comments(self, enable=False):
        """
        Turn on item comments
        """
        return self._gis.properties['commentsEnabled']
    #----------------------------------------------------------------------
    def get_default_extent(self):
        """
        returns the site's default extent

          :return: dictionary
        """
        return self._gis.properties['defaultExtent']
    #----------------------------------------------------------------------
    def set_default_extent(self, extent=None):
        """
        defines the site's default extent

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        extent            optional dictionary. The default extent defines where a webmap
                          will open.
                          If a value of None is given, the default extent will be provided.
                          Example Extent (default):
                          {"type":"extent","xmin":-17999999.999994524,"ymin":-11999999.999991827,
                          "xmax":17999999.999994524,"ymax":15999999.999982955,
                          "spatialReference":{"wkid":102100}}
        ================  ===============================================================

          :return: boolean
        """
        if extent is None:
            extent = {"type":"extent","xmin":-17999999.999994524,"ymin":-11999999.999991827,
                      "xmax":17999999.999994524,"ymax":15999999.999982955,
                      "spatialReference":{"wkid":102100}}
        return self._gis.update_properties({'defaultExtent' : extent})
    #----------------------------------------------------------------------
    def get_default_basemap(self):
        """
        returns the site's default extent

          :return: dictionary
        """
        return self._gis.properties['defaultBasemap']
    #----------------------------------------------------------------------
    def set_default_basemap(self, basemap=None):
        """
        The Default Basemap opens when users click New Map. Set the group
        in the Basemap Gallery above and choose the map to open. It will
        open at the default extent you set.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        basemap           optional string. The new default basemap to set. If None, the
                          default value will be set.
        ================  ===============================================================

          :return: boolean
        """
        if basemap is None:
            basemap = ""
        return self._gis.update_properties({'defaultBasemap' : basemap})



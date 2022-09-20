from __future__ import annotations
import os
import json
from arcgis._impl.common._deprecate import deprecated
from arcgis.auth.tools import LazyLoader

_basemap_definitions = LazyLoader("arcgis.mapping._basemap_definitions")
###########################################################################
class UX(object):
    """Helper class for modifying common org settings. This class is not created by users directly. An instance of
    the class, called 'ux', is available as a property of the GIS object. Users call methods on this 'ux' object
    to set informational banner, background, logo, name etc. There are also other helper classes to call from this.
    By calling the 'org_map_editor' or 'homepage_editor' more methods can be found to change org settings specific
    to those categories."""

    # ----------------------------------------------------------------------
    def __init__(self, gis):
        """Creates helper object to manage portal home page, resources, update resources"""
        self._gis = gis
        self._portal = gis._portal
        self._portal_resources = gis.admin.resources

        # Determine if using old or new homepage
        if "homePage" in gis.properties["portalProperties"]:
            self._new_hp = (
                True
                if gis.properties["portalProperties"]["homePage"] == "modernOnly"
                else False
            )
        else:
            self._new_hp = False

    # ----------------------------------------------------------------------
    @property
    def name(self):
        """
        Get/Set the site's name.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        name              required string. Name of the site.
        ================  ===============================================================

        :return: string of the name of the site

        """
        return self._gis.properties["name"]

    # ----------------------------------------------------------------------
    @name.setter
    def name(self, name: str):
        """
        See main ``name`` property docstring
        """
        import json

        if self._gis.properties.name != name:
            rps = [dict(r) for r in self._gis.properties.rotatorPanels]
            for r in rps:
                r["innerHTML"] = r["innerHTML"].replace(self._gis.properties.name, name)

            res = self._gis.update_properties(
                {"name": name, "rotatorPanels": json.dumps(rps)}
            )
            params = {
                "key": "localizedOrgProperties",
                "text": json.dumps({"default": {"name": name, "description": None}}),
                "f": "json",
            }
            url = f"{self._gis._portal.resturl}portals/self/addResource"
            res = self._gis._con.post(url, params)
            return res

    # ----------------------------------------------------------------------
    @property
    def summary(self):
        """
        Allows the get/setting of a brief summary to describe your organization on the sign in page
        associated with its custom apps and sites. This summary has a maximum of 310 characters.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        text              Required string. The brief description of the organization.
        ================  ===============================================================

        :return: string
        """
        try:
            res = json.loads(
                open(self._portal_resources.get("localizedOrgProperties"), "r").read()
            )
        except:
            # if summary has never been set for org then need to create the resource
            self.summary = ""
        return res["default"]["description"]

    # ----------------------------------------------------------------------

    @summary.setter
    def summary(self, text: str):
        """
        See main ``summary`` property docstring
        """
        if text == "":
            text = None
        params = {
            "key": "localizedOrgProperties",
            "text": {"default": {"name": self.name, "description": text}},
            "f": "json",
        }
        self._portal_resources.add(
            key="localizedOrgProperties", text=json.dumps(params["text"])
        )

    # ----------------------------------------------------------------------
    def set_informational_banner(
        self,
        text: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        enabled: bool | None = None,
    ):
        """
        The informational banner that is shown at the top of your organization's page.

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        text                Optional string. The text that the informational banner will display.
                            To set an empty text use: ""
        ----------------    ---------------------------------------------------------------
        bg_color            Optional string. Specifies the background color for the
                            informational banner. This property recognizes common color names
                            (such as red or blue) and hexadecimal color values. While you
                            are able to choose any color for this property, it is recommended
                            that you choose a color that contrasts appropriately with the
                            font_color, as a poor contrast will cause a warning to appear
                            in the Security settings page of yourEnterprise portal
                            alerting you to the insufficient contrast.
        ----------------    ---------------------------------------------------------------
        font_color          Optional string. Specifies the font color for the for the
                            informational banner. This property recognizes common color
                            names (such as red or blue) and hexadecimal color values.
                            While you are able to choose any color for this property,
                            it is recommended that you choose a color that contrasts
                            appropriately with the bg_color, as a poor contrast will
                            cause a warning to appear in the Security settings page of your
                            Enterprise portal alerting you to the insufficient contrast.
        ----------------    ---------------------------------------------------------------
        enabled             Optional bool. Determine whether the informational banner is
                            enabled (True) or disabled (False).
        ================    ===============================================================

        :return: True if updated, else False.
        """
        # if user wants to change one thing, keep other settings
        current_info_banner = self._gis.org_settings["informationalBanner"]
        if text is None:
            text = current_info_banner["text"]
        if bg_color is None:
            bg_color = current_info_banner["bgColor"]
        if font_color is None:
            font_color = current_info_banner["fontColor"]
        if enabled is None:
            enabled = current_info_banner["enabled"]
        informational_banner = {
            "text": text,
            "bgColor": bg_color,
            "fontColor": font_color,
            "enabled": enabled,
        }

        org_settings = self._gis.org_settings
        org_settings["informationalBanner"] = informational_banner
        self._gis.org_settings = org_settings
        return True

    # ----------------------------------------------------------------------
    def get_informational_banner(self):
        """
        Get the informational banner dictionary from the org's setttings.
        """
        return self._gis.org_settings["informationalBanner"]

    # ----------------------------------------------------------------------
    def set_logo(self, logo_file: str | None = None, show_logo: bool | None = None):
        """
        Configure your home page by setting the organization's logo image. For best results the logo file should be
        65 x 65 pixels in dimension.

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-general.htm

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        logo_file           Optional string. Specify path to image file. If None, existing thumbnail is removed.
        ----------------    ---------------------------------------------------------------
        show_logo           Optional bool. Specify whether the logo is visible on the homepage or not.
        ================    ===============================================================

        :return: True | False
        """

        # Add resource file

        from pathlib import Path

        key_val = ""
        # find image extension
        if logo_file is not None and os.path.isfile(logo_file):

            fpath = Path(logo_file)
            f_splits = fpath.name.split(".")
            if len(f_splits) > 1 and f_splits[1] == "png":
                key_val = "thumbnail.png"
            elif len(f_splits) > 1 and f_splits[1] == "jpg":
                key_val = "thumbnail.jpg"
            elif len(f_splits) > 1 and f_splits[1] == "gif":
                key_val = "thumbnail.gif"

            self._portal_resources.add(key_val, logo_file)
        elif logo_file is None:
            if "thumbnail" in dict(self._gis.properties):
                resource = self._gis.properties["thumbnail"]
                if resource and len(resource) > 0:
                    self._portal_resources.delete(resource)
                key_val = ""
        else:
            for ext in [".png", ".jpg", ".gif"]:
                try:
                    self._portal_resources.delete("thumbnail" + ext)
                except:
                    continue
            key_val = None

        if self._new_hp is False:
            # Update the portal self with these banner values
            if logo_file is not None:
                return self._gis.update_properties({"thumbnail": key_val})
            else:
                rp = self._gis.properties["rotatorPanels"]
                for idx, r in enumerate(rp):
                    if r["id"].lower() == "banner-2":
                        r["innerHTML"] = (
                            "<img src='images/banner-2.jpg' style='-webkit-border-radius:0 0 10px 10px;"
                            + " -moz-border-radius:0 0 10px 10px; -o-border-radius:0 0 10px 10px; border-radius:0 0 10px 10px;"
                            + " margin-top:0; width:960px; height:180px;'/><div style='position:absolute; bottom:80px; left:80px;"
                            + " max-height:65px; width:660px; margin:0;'><span style='position:absolute; bottom:0; "
                            "margin-bottom:0; line-height:normal; "
                            + "font-family:HelveticaNeue,Verdana; font-weight:600; font-size:32px; "
                            "color:#369;'>{}</span></div>".format(
                                self._gis.properties.name
                            )
                        )
                return self._gis.update_properties(
                    {"clearEmptyFields": True, "thumbnail": "", "rotatorPanels": rp}
                )
        elif self._new_hp:
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )
            if show_logo:
                hp["header"]["showLogo"] = show_logo
            hp["header"]["logo"] = key_val
            params = {
                "key": "home.page.json",
                "text": hp,
                "f": "json",
            }
            return self._portal_resources.add(
                key="home.page.json", text=json.dumps(params["text"])
            )

    # ----------------------------------------------------------------------
    def get_logo(self, download_path: str):
        """
        Get your organization's logo/thumbnail. You can use the `set_logo()` method to set an image as your logo.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        download_path     required string. Folder path to download the logo file.
        ================  ===============================================================

        :return: Path to downloaded logo file. If None, then logo is not set and nothing was downloaded.

        """
        if self._new_hp is False:
            props = self._gis.properties
            if "thumbnail" in props:
                resource = props["thumbnail"]
        else:
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )
            resource = hp["header"]["logo"]
        if resource is not None and len(str(resource)) > 0:
            output = self._portal_resources.get(
                resource_name=resource, download_path=download_path
            )
            return output
        return None

    # ----------------------------------------------------------------------
    @property
    def enable_comments(self):
        """
        Get/Set item commenting and comments.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        enable            Optional boolean. If True, the comments for the site are turned
                          on.  False will disable comments (default)
        ================  ===============================================================

        :return: True if enabled, False if disabled
        """
        return self._gis.properties["commentsEnabled"]

    # ----------------------------------------------------------------------
    @enable_comments.setter
    def enable_comments(self, enable: bool = False):
        """
        See main ``enable_comments`` property docstring.
        """
        return self._gis.update_properties({"commentsEnabled": enable})

    # ----------------------------------------------------------------------
    @property
    def description_visibility(self):
        """
        Get/Set the site's description visibility

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        visiblity         Required boolean. If True, the desciptive text will show on the
                          home page. If False, the descriptive text will not be displayed
        ================  ===============================================================

        :return: boolean or error

        """
        try:
            return self._gis.properties["showHomePageDescription"]
        except:
            return "This property no longer exists on your org"

    # ----------------------------------------------------------------------
    @description_visibility.setter
    def description_visibility(self, visiblity: bool):
        """
        See main ``description_visibility`` property docstring
        """
        return self._gis.update_properties({"showHomePageDescription": visiblity})

    # ----------------------------------------------------------------------
    @property
    def description(self):
        """
        Get/Set the site's description.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        description       Required string. Descriptive text of the site. If None, the
                          value is reset to default.
        ================  ===============================================================

        :return: dictionary
        """
        return self._gis.properties["description"]

    # ----------------------------------------------------------------------
    @description.setter
    def description(self, description: str | None = None):
        """
        See main ``description`` property docstring
        """
        if description is None:
            description = "<br/>"
        return self._gis.update_properties({"description": description})

    # ----------------------------------------------------------------------
    @property
    def featured_content(self) -> dict:
        """
        Gets/Sets the featured content group information.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        content           Required dictionary, defines the group and count of the feature
                          content area on an organizational site.  A value of None will
                          reset the value back to the install defaults.
                          Example:
                          {'group': <group id>, 'count' : 12}
        ================  ===============================================================

        :return: dictionary


        .. code-block:: python
            *Usage Example*
            >>> data = ux.get_featured_content()
            >>> ux.set_featured_content = data
            True

        """
        return {
            "group": self._gis.properties["homePageFeaturedContent"],
            "count": self._gis.properties["homePageFeaturedContentCount"],
        }

    # ----------------------------------------------------------------------
    @featured_content.setter
    def featured_content(self, content: dict):
        """
        See main ``featured_content`` property docstring
        """
        from .. import Group

        if content is None:
            content = {
                "homePageFeaturedContent": "",
                "homePageFeaturedContentCount": 12,
                "featuredItemsGroupQuery": "",
                "featuredGroupsId": "",
                "clearEmptyFields": True,
            }
        elif "group" in content and isinstance(content["group"], Group):
            gid = content["group"].groupid
            content["homePageFeaturedContent"] = gid
            content["featuredGroupsId"] = f"id:{gid}"
            content["featuredItemsGroupQuery"] = f"id:{gid}"
        elif (
            isinstance(content, dict)
            and "group" in content
            and isinstance(content["group"], str)
        ):
            c = {}
            c["homePageFeaturedContent"] = content["group"]
            c["featuredItemsGroupQuery"] = f"id:{content['group']}"
            c["featuredGroupsId"] = f"id:{content['group']}"
            if "count" in content:
                c["homePageFeaturedContentCount"] = content["count"]
            else:
                c["homePageFeaturedContentCount"] = 12
            content = c
        elif isinstance(content, str):
            c = {}
            c["homePageFeaturedContent"] = content
            c["homePageFeaturedContentCount"] = 12
            c["featuredItemsGroupQuery"] = f"id:{content}"
            c["featuredGroupsId"] = f"id:{content}"
            content = c
        if not "featuredItemsGroupQuery" in self._gis.properties:
            content.pop("featuredItemsGroupQuery", None)
        if not "featuredGroupsId" in self._gis.properties:
            content.pop("featuredGroupsId", None)
        self._gis.update_properties(content)

    # ----------------------------------------------------------------------
    @property
    def homepage_settings(self):
        """
        Get an instance of the HomePageSettings class to make edits to the org's
        homepage such as the background, title, logo, etc.
        """
        return HomePageSettings(gis=self._gis)

    # ----------------------------------------------------------------------
    @property
    def map_settings(self):
        """
        Get an instance of the MapSettings class to make edits to the org's default
        map settings such as extent, basemap, etc.
        """
        return MapSettings(gis=self._gis)

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    def set_background(
        self, background_file: str | None = None, is_built_in: bool = True
    ):
        """
        Configure your home page by setting the organization's background image. You can choose no image, a built-in image
        or upload your own. If you upload your own image, the image is positioned at the top and center of the page.
        The image repeats horizontally if it is smaller than the browser or device window. For best results, if you want
        a single, nonrepeating background image, the image should be 1,920 pixels wide (or smaller if your users are on
        smaller screens). The website does not resize the image. You can upload a file up to 1 MB in size.

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-home.htm

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        background_file     Optional string. If using a custom background, specify path to image file.
                            To remove an existing background, specify None for this argument and
                            False for is_built_in argument.
        ----------------    ---------------------------------------------------------------
        is_built_in         Optional bool, default=True. The built-in background is set by default.
                            If uploading a custom image, this parameter is ignored.
        ================    ===============================================================

        :return: True | False
        """
        return self.homepage_settings.set_background(
            background_file=background_file, is_built_in=is_built_in
        )

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    def get_background(self, download_path: str):
        """
        Get your organization's home page background image. You can use the `set_background()` method to set an image
        as the home page background image.

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-home.htm

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        download_path     required string. Folder path to download the background file.
        ================  ===============================================================

        :return: Path to downloaded background file. If None, then background is not set and nothing was downloaded.
        """
        return self.homepage_settings.get_background(download_path=download_path)

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    def set_banner(
        self,
        banner_file: str | None = None,
        is_built_in: bool = False,
        custom_html: str | None = None,
    ):
        """
        Configure your home page by setting the organization's banner. You can choose one of the 5 built-in banners or
        upload your own. For best results the dimensions of the banner image should be 960 x 180 pixels. You can also
        specify a custom html for how the banner space should appear. For more information, refer to
        http://server.arcgis.com/en/portal/latest/administer/windows/configure-home.htm

        .. note::
            This has now been replaced by the `set_informational_banner` method

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        banner_file         Optional string. If uploading a custom banner, then path to the
                            banner file. If using a built-in banner, valid values are
                            banner-1, banner-2, banner-3, banner-4, banner-5. If None, existing
                            banner is remove.
        ----------------    ---------------------------------------------------------------
        is_built_in         Optional bool, default=False. Specify True if using a built-in
                            banner file.
        ----------------    ---------------------------------------------------------------
        custom_html         Optional string. Specify exactly how the banner should appear in
                            html. For help on this, refer to
                            http://server.arcgis.com/en/portal/latest/administer/windows/supported-html.htm
        ================    ===============================================================

        :return: True | False
        """
        # region check if banner has to be removed
        if not banner_file and not custom_html:
            # remove code

            # find existing banner resource file
            resource_list = self._portal_resources.list()
            e_banner = [
                banner for banner in resource_list if banner["key"].startswith("banner")
            ]

            # loop through and remove existing banner resource file
            for banner in e_banner:
                try:
                    self._portal_resources.delete(banner["key"])
                except:
                    continue

            # reset the home page - recurse
            return self.set_banner("banner-2", True)
        # endregion

        # region: Set banner using banner file - built-in or new image
        if banner_file:
            rotator_panel = []
            if not is_built_in:  # adding a new image file
                # find image extension
                from pathlib import Path

                fpath = Path(banner_file)
                f_splits = fpath.name.split(".")
                if len(f_splits) > 1 and f_splits[1] == "png":
                    key_val = "banner.png"
                elif len(f_splits) > 1 and f_splits[1] == "jpg":
                    key_val = "banner.jpg"
                else:
                    raise RuntimeError("Invalid image extension")

                add_result = self._portal_resources.add(key_val, banner_file)

                if add_result and custom_html:
                    rotator_panel = [{"id": "banner-custom", "innerHTML": custom_html}]

                elif add_result and not custom_html:
                    # set rotator_panel_text
                    rotator_panel = [
                        {
                            "id": "banner-custom",
                            "innerHTML": "<img src='{}/portals/self/resources/{}?token=SECURITY_TOKEN' "
                            "style='-webkit-border-radius:0 0 10px 10px; -moz-border-radius:0 0 10px 10px;"
                            " -o-border-radius:0 0 10px 10px; border-radius:0 0 10px 10px; margin-top:0; "
                            "width:960px;'/>".format(self._portal.con.baseurl, key_val),
                        }
                    ]
            else:  # using built-in image
                if not custom_html:  # if no custom html is specified for built-in image
                    rotator_panel = [
                        {
                            "id": banner_file,
                            "innerHTML": "<img src='images/{}.jpg' "
                            "style='-webkit-border-radius:0 0 10px 10px; -moz-border-radius:0 0 10px 10px; "
                            "-o-border-radius:0 0 10px 10px; border-radius:0 0 10px 10px; margin-top:0; "
                            "width:960px; height:180px;'/><div style='position:absolute; bottom:80px; "
                            "left:80px; max-height:65px; width:660px; margin:0;'>"
                            "<img src='{}/portals/self/resources/thumbnail.png?token=SECURITY_TOKEN' "
                            "class='esriFloatLeading esriTrailingMargin025' style='margin-bottom:0; "
                            "max-height:100px;'/><span style='position:absolute; bottom:0; margin-bottom:0; "
                            "line-height:normal; font-family:HelveticaNeue,Verdana; font-weight:600; "
                            "font-size:32px; color:#369;'>{}</span></div>".format(
                                banner_file,
                                self._portal.con.baseurl,
                                self._gis.properties.name,
                            ),
                        }
                    ]
                else:  # using custom html for built-in image
                    rotator_panel = [{"id": banner_file, "innerHTML": custom_html}]
        # endregion

        # region: Set banner just using a html text
        elif custom_html:
            rotator_panel = [{"id": "banner-html", "innerHTML": custom_html}]
        # endregion

        # Update the portal self with these banner values
        update_result = self._gis.update_properties({"rotatorPanels": rotator_panel})
        return update_result

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    def get_banner(self, download_path: str):
        """
        Get your organization's home page banner image. You can use the `set_banner()` method to set an image or custom HTML
        code as your banner.

        .. note::
            This method has been replaced with the `get_informational_banner` method.

        ================    =================================================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------------------------
        download_path       required string. Folder path to download the banner file.
        ================    =================================================================================

        :return: Path to downloaded banner file. If None, then banner is not set and nothing was downloaded.

        """
        # create a portal resource manager obj

        # find existing banner resource file
        resource_list = self._portal_resources.list()
        e_banner = [
            banner for banner in resource_list if banner["key"].startswith("banner")
        ]

        # loop through and remove existing banner resource file
        banner_path = None
        for banner in e_banner:

            try:
                banner_path = self._portal_resources.get(banner["key"], download_path)

            except:
                continue
        return banner_path

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    @property
    def default_extent(self):
        """
        Get/Set the site's default extent

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        extent            Required dictionary. The default extent defines where a webmap
                          will open.
                          If a value of None is given, the default extent will be provided.
                          Example Extent (default):
                          {"type":"extent","xmin":-17999999.999994524,"ymin":-11999999.999991827,
                          "xmax":17999999.999994524,"ymax":15999999.999982955,
                          "spatialReference":{"wkid":102100}}
        ================  ===============================================================

        :return: dictionary

        """
        return self.map_settings.default_extent

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    @default_extent.setter
    def default_extent(self, extent: dict):
        """
        See main ``default_extent`` property docstring
        """
        self.map_settings.default_extent = extent

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    @property
    def default_basemap(self):
        """
        Get/Set the site's default basemap.

        The Default Basemap opens when users click New Map. Set the group
        in the Basemap Gallery above and choose the map to open. It will
        open at the default extent you set.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        basemap           Required string. The new default basemap to set. If None, the
                          default value will be set.
        ================  ===============================================================

        :return: dictionary

        """
        return self.map_settings.default_basemap

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    @default_basemap.setter
    def default_basemap(self, value: str):
        """
        See main ``default_basemap`` property docstring
        """
        self.map_settings.default_basemap = value

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    @property
    def vector_basemap(self):
        """
        Get/Set the default vector basemap

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        basemap           required dictionary. The new default vector basemap to set for
                          a given site.
        ================  ===============================================================

        :return: The current default vector basemap
        """
        return self.map_settings.vector_basemap

    # ----------------------------------------------------------------------
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    @vector_basemap.setter
    def vector_basemap(self, basemap: dict):
        """
        See main ``vector_basemap`` property docstring
        """
        self.map_settings.vector_basemap = basemap


#############################################################################
class HomePageSettings(object):
    """
    Helper class called from the UX class property: 'homepage_settings'. Make edits to background,
    title, logo, etc.
    """

    # ----------------------------------------------------------------------
    def __init__(self, gis):
        """Creates helper object to manage portal home page, resources, update resources"""
        self._gis = gis
        self._portal = gis._portal
        self._portal_resources = gis.admin.resources

        # Determine if using old or new homepage
        if "homePage" in gis.properties["portalProperties"]:
            self._new_hp = (
                True
                if gis.properties["portalProperties"]["homePage"] == "modernOnly"
                else False
            )
        else:
            self._new_hp = False

    # ----------------------------------------------------------------------
    def set_background(
        self, background_file: str | None = None, is_built_in: bool = True
    ):
        """
        Configure your home page by setting the organization's background image. You can choose no image, a built-in image
        or upload your own. If you upload your own image, the image is positioned at the top and center of the page.
        The image repeats horizontally if it is smaller than the browser or device window. For best results, if you want
        a single, nonrepeating background image, the image should be 1,920 pixels wide (or smaller if your users are on
        smaller screens). The website does not resize the image. You can upload a file up to 1 MB in size.

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-home.htm

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        background_file     Optional string. If using a custom background, specify path to image file.
                            To remove an existing background, specify None for this argument and
                            False for is_built_in argument.
        ----------------    ---------------------------------------------------------------
        is_built_in         Optional bool, default=True. The built-in background is set by default.
                            If uploading a custom image, this parameter is ignored.
        ================    ===============================================================

        :return: True | False
        """
        from pathlib import Path

        if self._new_hp is False:
            # Add resource if using a custom background file.
            background_update_val = None
            if background_file:
                # find image extension
                fpath = Path(background_file)
                f_splits = fpath.name.split(".")
                if len(f_splits) > 1 and f_splits[1] == "png":
                    key_val = "background.png"
                elif len(f_splits) > 1 and f_splits[1] == "jpg":
                    key_val = "background.jpg"
                else:
                    raise RuntimeError("Invalid image extension")

                add_result = self._portal_resources.add(key_val, background_file)
                if not add_result:
                    raise RuntimeError(
                        "Error adding background image as a resource file"
                    )
                background_update_val = key_val

            elif is_built_in:  # using built-in
                background_update_val = "images/arcgis_background.jpg"
            else:
                background_update_val = "none"

            # Update the portal self with these banner values
            return self._gis.update_properties(
                {"backgroundImage": background_update_val}
            )
        elif self._new_hp:
            if background_file:
                fpath = Path(background_file)
                f_splits = fpath.name.split(".")
                if len(f_splits) > 1 and f_splits[1] == "png":
                    key_val = "background.png"
                elif len(f_splits) > 1 and f_splits[1] == "jpg":
                    key_val = "background.jpg"
                else:
                    raise RuntimeError("Invalid image extension")

                add_result = self._portal_resources.add(key_val, background_file)
                if not add_result:
                    raise RuntimeError(
                        "Error adding background image as a resource file"
                    )
                background_update_val = key_val
                cover_type = "custom"
            elif is_built_in:
                cover_type = "stock"
                background_update_val = ""
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )

            hp["header"]["coverImg"] = background_update_val
            hp["header"]["coverType"] = cover_type
            params = {
                "key": "home.page.json",
                "text": hp,
                "f": "json",
            }
            return self._portal_resources.add(
                key="home.page.json", text=json.dumps(params["text"])
            )

    # ----------------------------------------------------------------------
    def get_background(self, download_path: str):
        """
        Get your organization's home page background image. You can use the `set_background()` method to set an image
        as the home page background image.

        For more information, refer to http://server.arcgis.com/en/portal/latest/administer/windows/configure-home.htm

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        download_path     required string. Folder path to download the background file.
        ================  ===============================================================

        :return: Path to downloaded background file. If None, then background is not set and nothing was downloaded.
        """

        # create a portal resource manager obj
        # find existing banner resource file
        bckgrnd_path = None
        if self._new_hp is False:
            resource_list = self._portal_resources.list()
            e_background = [
                banner
                for banner in resource_list
                if banner["key"].startswith("background")
            ]
            for background in e_background:

                try:
                    bckgrnd_path = self._portal_resources.get(
                        background["key"], download_path
                    )

                except:
                    continue
        else:
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )
            background = hp["header"]["coverImg"]
            if background:
                bckgrnd_path = self._portal_resources.get(
                    background["key"], download_path
                )

        return bckgrnd_path

    # ----------------------------------------------------------------------
    def set_title(
        self,
        title: str | None = None,
        show_title: bool | None = None,
        color: str | None = None,
    ):
        """
        Set the homepage title and it's visibility

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        title               Optional string. The title to show on the homepage.
        ----------------    ---------------------------------------------------------------
        show_title          Optional boolean. Determine if title is shown (True) or hidden (False).
        ----------------    ---------------------------------------------------------------
        color               Optional string. Specifies the font color for the for the
                            title. This property recognizes common color
                            names (such as red or blue) and hexadecimal color values.
        ================    ===============================================================

        :return: True | False
        """
        if self._new_hp:
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )
            if title:
                hp["header"]["title"] = title
            if show_title:
                hp["header"]["showTitle"] = show_title
            if color:
                hp["header"]["titleColor"] = color
            params = {
                "key": "home.page.json",
                "text": hp,
                "f": "json",
            }
            return self._portal_resources.add(
                key="home.page.json", text=json.dumps(params["text"])
            )
        else:
            return False

    # ----------------------------------------------------------------------
    def get_title(self):
        """
        Get the title displayed on the homepage if show title is set to True.
        """
        if self._new_hp:
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )
            return hp["header"]["title"]
        else:
            return None


##############################################################################
class MapSettings(object):
    """Helper class that can be called off of UX class using the 'map_settings' property.
    Edit org map settings such as the default extent, default basemap, etc."""

    # ----------------------------------------------------------------------
    def __init__(self, gis):
        """Creates helper object to manage portal home page, resources, update resources"""
        self._gis = gis
        self._portal = gis._portal
        self._portal_resources = gis.admin.resources

        # Determine if using old or new homepage
        if "homePage" in gis.properties["portalProperties"]:
            self._new_hp = (
                True
                if gis.properties["portalProperties"]["homePage"] == "modernOnly"
                else False
            )
        else:
            self._new_hp = False

    # ----------------------------------------------------------------------
    @property
    def default_extent(self):
        """
        Get/Set the site's default extent

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        extent            Required dictionary. The default extent defines where a webmap
                          will open.
                          If a value of None is given, the default extent will be provided.
                          Example Extent (default):
                          {"type":"extent","xmin":-17999999.999994524,"ymin":-11999999.999991827,
                          "xmax":17999999.999994524,"ymax":15999999.999982955,
                          "spatialReference":{"wkid":102100}}
        ================  ===============================================================

        :return: dictionary

        """
        return self._gis.properties["defaultExtent"]

    # ----------------------------------------------------------------------
    @default_extent.setter
    def default_extent(self, extent: dict):
        """
        See main ``default_extent`` property docstring
        """
        if extent is None:
            extent = {
                "type": "extent",
                "xmin": -17999999.999994524,
                "ymin": -11999999.999991827,
                "xmax": 17999999.999994524,
                "ymax": 15999999.999982955,
                "spatialReference": {"wkid": 102100},
            }
        return self._gis.update_properties({"defaultExtent": extent})

    # ----------------------------------------------------------------------
    @property
    def default_basemap(self):
        """
        Get/Set the site's default basemap.

        The Default Basemap opens when users click New Map. Set the group
        in the Basemap Gallery above and choose the map to open. It will
        open at the default extent you set.

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        basemap           Required string. The new default basemap to set. If None, the
                          default value will be set.
        ================  ===============================================================

        :return: dictionary

        """
        return self._gis.properties["defaultBasemap"]

    # ----------------------------------------------------------------------
    @default_basemap.setter
    def default_basemap(self, value: str):
        """
        See main ``default_basemap`` property docstring
        """
        try:
            basemap = {
                "baseMapLayers": _basemap_definitions.basemap_dict[value],
                "title": value.replace("-", " ").title(),
            }
            return self._gis.update_properties({"defaultBasemap": basemap})
        except:
            raise ValueError(
                "Valid Basemaps: 'dark-gray-vector', 'gray-vector', 'hybrid', 'oceans', 'osm', 'satellite', 'streets-navigation-vector', 'streets-night-vector', 'streets-relief-vector', 'streets-vector', 'terrain', 'topo-vector'"
            )

    # ----------------------------------------------------------------------
    @property
    def vector_basemap(self):
        """
        Get/Set the default vector basemap

        ================  ===============================================================
        **Argument**      **Description**
        ----------------  ---------------------------------------------------------------
        basemap           required dictionary. The new default vector basemap to set for
                          a given site.
        ================  ===============================================================

        :return: The current default vector basemap
        """
        return self._gis.properties["defaultVectorBasemap"]

    # ----------------------------------------------------------------------
    @vector_basemap.setter
    def vector_basemap(self, basemap: dict):
        """
        See main ``vector_basemap`` property docstring
        """
        value = {}
        if "title" in basemap:
            value["title"] = basemap["title"].replace("-", " ").title()
        if "layers" in basemap:
            value["baseMapLayers"] = basemap["layers"]
        elif "baseMapLayers" in basemap:
            value["baseMapLayers"] = basemap["baseMapLayers"]
        return self._gis.update_properties({"defaultVectorBasemap": value})

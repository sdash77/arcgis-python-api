from __future__ import annotations
import os
import json
from arcgis._impl.common._deprecate import deprecated
from arcgis.auth.tools import LazyLoader
from arcgis.gis import Group

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
    def set_org_language(self, language: str, format: str | None = None):
        """
        Choose the default language for members of your organization. This
        choice affects the user interface as well as the way time,
        date, and numerical values appear. Individual members can customize
        this choice on their settings page.

        ================        ========================================================
        **Argument**            **Description**
        ----------------        --------------------------------------------------------
        language                Required string. To see all available languages, use
                                the `languages` property in the GIS class.
        ----------------        --------------------------------------------------------
        format                  Optional string. Determine the culture format to be
                                used depending on the language. To see the culture formats
                                available, use the `languages` property in the GIS class
                                and look at the 'cultureFormats' key for each language.
        ================        ========================================================

        :return: True | False
        """
        languages = self._gis.languages
        for lng in languages:
            if lng["language"].lower() == language.lower():
                culture = lng["culture"]
                if "cultureFormats" in lng:
                    if format:
                        for clt_format in lng["cultureFormats"]:
                            if clt_format["name"].lower() == format.lower():
                                culture_format = clt_format["format"]
                    else:
                        culture_format = lng["cultureFormats"][0]["format"]
                    # culture name includes format if available
                    culture = culture + "-" + culture_format
                    break
                else:
                    # default set when no other choices
                    culture_format = "en"
        return self._gis.update_properties(
            {
                "culture": culture,
                "cultureFormat": culture_format,
                "clearEmptyFields": True,
            }
        )

    # ----------------------------------------------------------------------
    @property
    def contact_link(self):
        """
        Get and set the contact link for the site.
        """
        if "links" in self._gis.properties["portalProperties"]:
            return self._gis.properties["portalProperties"]["links"]
        else:
            return None

    # ----------------------------------------------------------------------
    @contact_link.setter
    def contact_link(self, url: str):
        portal_properties = self._gis.properties["portalProperties"]
        if url:
            portal_properties["links"] = {"contactUs": {"url": {url}, "visible": True}}
        else:
            portal_properties["links"] = {"contactUs": {"url": "", "visible": False}}

        self._gis.update_properties({"portalProperties": portal_properties})

    # ----------------------------------------------------------------------
    @property
    def admin_contacts(self):
        """
        An array of chosen administrators listed as points of contact whose
        email addresses will be listed as points of contact in the automatic
        email notifications sent to org members when they request password resets,
        help with their user names, modifications to their accounts, or any issues
        related to the allocation of credits to their accounts.
        """
        return self._gis.properties["contacts"]

    # ----------------------------------------------------------------------
    @admin_contacts.setter
    def admin_contacts(self, users: list[str]):
        admins = []
        if users is None:
            raise ValueError(
                "Cannot set empty list as Administrative contacts. You must have at least one administrator in the list."
            )
        for user in users:
            role = self._gis.users.search(user)[0].role
            if role == "org_admin":
                admins.append(user)
        if len(admins) == 0:
            raise ValueError(
                "None of the usernames provided are org admins. Please provide org admins."
            )
        else:
            self._gis.update_properties({"contacts": admins})

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
        if "informationalBanner" in self._gis.org_settings:
            return self._gis.org_settings["informationalBanner"]
        else:
            return None

    # ----------------------------------------------------------------------
    @property
    def help_source(self):
        """
        Toggle if the help source is turned on (True) or off (False).
        It provides the base URL for your organization's help documentation.
        """
        if "helpBase" in self._gis.properties:
            return self._gis.properties["helpBase"]
        else:
            return None

    # ----------------------------------------------------------------------
    @help_source.setter
    def help_source(self, enabled: bool):
        if enabled is False:
            # this will reset it to default based on language
            self._gis.update_properties({"helpBase": ""})
        else:
            if self._gis._is_agol:
                raise ValueError(
                    "This parameter can only be set for Enterprise 10.8.1+."
                )
            else:
                culture = self._gis.properties["culture"]
                if culture not in [
                    "ar",
                    "pt-BR",
                    "fr",
                    "de",
                    "it",
                    "ja",
                    "ko",
                    "pl",
                    "ru",
                    "zh-CN",
                    "es-es",
                ]:
                    culture = "en"
                self._gis.update_properties(
                    {"helpBase": "https://enterprise.arcgis.com/{culture}"}
                )

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
    def navigation_bar(
        self,
        gallery: str | None = None,
        map: str | None = None,
        scene: str | None = None,
        groups: str | None = None,
        search: str | None = None,
    ):
        """
        Set the visibility of the content in the navigation bar. To get the current navigation
        bar settings do not pass in any values for the parameters.

        .. note::
            The Home link is always visible to everyone. The Content link is always visible to members.
            Member roles determine Organization link visibility.

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        gallery             Optional string.
                            Values: "all" | "members" | "noOne"
        ----------------    ---------------------------------------------------------------
        map                 Optional string.
                            Values: "all" | "members" | "mapCreators"
        ----------------    ---------------------------------------------------------------
        scene               Optional string.
                            Values: "all" | "members" | "sceneCreators"
        ----------------    ---------------------------------------------------------------
        groups              Optional string.
                            Values: "all" | "members"
        ----------------    ---------------------------------------------------------------
        search              Optional string.
                            Values: "all" | "members"
        ================    ===============================================================

        :return: Dictionary of the navigation bar and it's settings.
        """
        portal_properties = self._gis.properties["portalProperties"]
        top_nav = {
            "gallery": "all",
            "map": "all",
            "scene": "all",
            "groups": "all",
            "search": "all",
        }
        if "topNav" in portal_properties:
            # get existing top nav settings
            top_nav = portal_properties["topNav"]

        # only change what is necessary
        if gallery:
            top_nav["gallery"] = gallery
        if map:
            top_nav["map"] = map
        if scene:
            top_nav["scene"] = scene
        if groups:
            top_nav["groups"] = groups
        if search:
            top_nav["search"] = search

        portal_properties["topNav"] = top_nav
        self._gis.update_properties({"portalProperties": portal_properties})
        return top_nav

    # ----------------------------------------------------------------------
    def shared_theme(
        self,
        header: dict[str:str] | None = None,
        button: dict[str:str] | None = None,
        body: dict[str:str] | None = None,
        logo: str | None = None,
    ):
        """
        Use the shared theme to apply your organization's brand colors and
        logo to information products created from ArcGIS Configurable Apps templates,
        Web AppBuilder, and Enterprise Sites. To see the current settings, call the method with
        no parameters passed in.

        ================    ===============================================================
        **Argument**        **Description**
        ----------------    ---------------------------------------------------------------
        header              Optional dict. Composed of two keys: "background" and "text" that
                            determine the shared theme color for each of these keys. Color
                            can be passed in a hexadecimal string.

                            ex: header = {"background" : "#0d7bba", "text" : "#000000"}
        ----------------    ---------------------------------------------------------------
        button              Optional dict. Composed of two keys: "background" and "text" that
                            determine the shared theme color for each of these keys.
        ----------------    ---------------------------------------------------------------
        body                Optional dict. Composed of three keys: "background", "text" and
                            "link" that determine the shared theme color for each of these keys.
        ----------------    ---------------------------------------------------------------
        logo                Optional str. The file path to the image that will be uploaded
                            as the shared theme logo.
                            To remove the logo and not replace it then pass in: "REMOVE"
        ================    ===============================================================

        :return: Dictionary of the shared theme that is set on the org.
        """
        portal_properties = self._gis.properties["portalProperties"]
        shared_theme = {
            "header": {"background": "no-color", "text": "no-color"},
            "button": {"background": "no-color", "text": "no-color"},
            "body": {"background": "no-color", "text": "no-color", "link": "no-color"},
            "logo": {"small": ""},
        }
        if "sharedTheme" in portal_properties:
            shared_theme = portal_properties["sharedTheme"]
        if header:
            if "background" in header:
                shared_theme["header"]["background"] = header["background"]
            if "text" in header:
                shared_theme["header"]["text"] = header["text"]
        if button:
            if "background" in button:
                shared_theme["button"]["background"] = button["background"]
            if "text" in button:
                shared_theme["button"]["text"] = button["text"]
        if body:
            if "background" in body:
                shared_theme["body"]["background"] = body["background"]
            if "text" in body:
                shared_theme["body"]["text"] = body["text"]
            if "link" in body:
                shared_theme["body"]["link"] = body["link"]
            # find image extension
        if logo is not None and os.path.isfile(logo):
            # add item
            item_props = {
                "title": "Shared Theme Logo",
                "description": "This image was uploaded for use as your organizations shared theme logo.",
                "tags": ["SharedTheme", "Logo"],
                "type": "Image",
            }
            im_item = self._gis.content.add(item_props, logo)
            # share to everyone
            im_item.share(everyone=True)
            # set in shared_theme dict
            shared_theme["logo"]["small"] = im_item.homepage + "/data"
        if logo == "REMOVE":
            shared_theme["logo"]["small"] = ""

        portal_properties["sharedTheme"] = shared_theme
        self._gis.update_properties({"portalProperties": portal_properties})
        return shared_theme

    # ----------------------------------------------------------------------
    @property
    def gallery_group(self):
        """
        The gallery highlights your organization's content.
        Choose a group whose content will be shown in the gallery.
        To change the group, assign either an instance of Group or the group id.
        Setting to None will revert to default.
        """
        return self._gis.properties["featuredItemsGroupQuery"]

    # ----------------------------------------------------------------------
    @gallery_group.setter
    def gallery_group(self, group: Group | str | None):
        if isinstance(group, Group):
            group = "id:" + group.id
        elif isinstance(group, str):
            res = self._gis.groups.search(group)
            if len(res) == 0:
                raise ValueError(
                    "The group id provided could not be found in your org."
                )
            else:
                group = "id:" + group
        self._gis.update_properties(
            {"featuredItemsGroupQuery": group, "clearEmptyFields": True}
        )

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
    @property
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
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
    @default_extent.setter
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    def default_extent(self, extent: dict):
        """
        See main ``default_extent`` property docstring
        """
        self.map_settings.default_extent = extent

    # ----------------------------------------------------------------------
    @property
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
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
    @default_basemap.setter
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
    def default_basemap(self, value: str):
        """
        See main ``default_basemap`` property docstring
        """
        self.map_settings.default_basemap = value

    # ----------------------------------------------------------------------
    @property
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
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
    @vector_basemap.setter
    @deprecated(deprecated_in="2.1.0", removed_in="3.0.0", current_version="2.1.0")
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

        :return: Dict or None if using old homepage
        """
        if self._new_hp:
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )
            title = {
                "title": hp["header"]["title"],
                "show_title": hp["header"]["showTitle"],
                "color": hp["header"]["titleColor"],
            }
            return title
        else:
            return None

    # ----------------------------------------------------------------------
    def set_contact_email(
        self, email: str | None = None, show_email: bool | None = None
    ):
        """Set the email shown in the footer of the homepage and whether it is visible."""
        if self._new_hp:
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )
            if email:
                hp["footer"]["contact"] = email
            if show_email:
                hp["footer"]["showContact"] = show_email
            params = {
                "key": "home.page.json",
                "text": hp,
                "f": "json",
            }
            return self._portal_resources.add(
                key="home.page.json", text=json.dumps(params["text"])
            )
        else:
            return None

    # ----------------------------------------------------------------------
    def get_contact_email(self):
        """Get the email and whether it is shown from the footer of the homepage."""
        if self._new_hp:
            hp = json.loads(
                open(self._portal_resources.get("home.page.json"), "r").read()
            )
            contact = {
                "email": hp["footer"]["contact"],
                "show_email": hp["footer"]["showContact"],
            }
            return contact


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
    def use_vector_basemap(self):
        """
        If true, the organization uses the Esri vector basemaps in supported
        ArcGIS apps and basemapGalleryGroupQuery will not be editable
        and will be set to the default query.
        """
        return self._gis.properties["useVectorBasemaps"]

    # ----------------------------------------------------------------------
    @use_vector_basemap.setter
    def use_vector_basemap(self, value: bool):
        if value in [True, False]:
            self._gis.update_properties({"useVectorBasemaps": value})

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

    # ----------------------------------------------------------------------
    @property
    def basemap_gallery_group(self):
        """
        Select the group whose web maps will be shown in the basemap gallery.
        To change the group, assign either an instance of Group or the group id.
        Setting to None will revert to default.
        """
        return self._gis.properties["basemapGalleryGroupQuery"]

    # ----------------------------------------------------------------------
    @basemap_gallery_group.setter
    def basemap_gallery_group(self, group: Group | str | None):
        if isinstance(group, Group):
            group = "id:" + group.id
            value = False
        elif isinstance(group, str):
            res = self._gis.groups.search(group)
            if len(res) == 0:
                raise ValueError(
                    "The group id provided could not be found in your org."
                )
            else:
                group = "id:" + group
                value = False
        elif group is None:
            value = True
        self._gis.update_properties(
            {"basemapGalleryGroupQuery": group, "useVectorBasemaps": value}
        )

    # ----------------------------------------------------------------------
    @property
    def default_mapviewer(self):
        """
        Get/Set whether the org's default Map Viewer is MapViewerClassic or the
        modern Map Viewer.

        Values: "modern" | "classic"
        """
        if "mapViewer" in self._gis.properties["portalProperties"]:
            return self._gis.properties["portalProperties"]["mapViewer"]

    # ----------------------------------------------------------------------
    @default_mapviewer.setter
    def default_mapviewer(self, value: str):
        if value not in ["modern", "classic"]:
            raise ValueError("The two accepted values are 'modern' or 'classi'")

        portal_properties = self._gis.properties["portalProperties"]
        portal_properties["mapViewer"] = value
        self._gis.update_properties({"portalProperties": portal_properties})

    # ----------------------------------------------------------------------
    @property
    def units(self):
        """
        Get/Set the default map units. Either 'english' or 'metric'.
        """
        if "units" in self._gis.properties:
            return self._gis.properties["units"]

    # ----------------------------------------------------------------------
    @units.setter
    def units(self, value: str):
        if value not in ["english", "classic"]:
            raise ValueError("The two accepted values are 'english' and 'metric'")

        self._gis.update_properties({"units": value})

    # ----------------------------------------------------------------------
    def bing_map(self, bing_key: str | None = None, share_public: bool | None = None):
        """
        Provide a Microsoft-supplied Bing Maps key to use Bing Maps in your portal's web maps.

        Bing Map Key: https://www.bingmapsportal.com/

        ======================      ==============================================
        **Argument**                    **Description**
        ----------------------      ----------------------------------------------
        bing_key                    Optional str. The bing key to pass in.
        ----------------------      ----------------------------------------------
        share_public                Optional bool. If True, allows this Bing Maps
                                    key to be used in maps shared publicly by organization members.
        ======================      ==============================================

        :return: Dictionary containing the bing key and whether is is publicly shared
        """
        if bing_key:
            self._gis.update_properties({"bingKey": bing_key})
        if share_public:
            self._gis.update_properties({"canShareBingPublic": share_public})
        bing_dict = {
            "key": self._gis.properties["bingKey"]
            if "bingKey" in self._gis.properties
            else None,
            "public": self._gis.properties["canShareBingPublic"],
        }
        return bing_dict

    # ----------------------------------------------------------------------
    @property
    def config_apps_group(self):
        """
        ArcGIS Configurable Apps contain various settings users can configure
        to create web apps. Map-based apps display one or more maps.
        Choose which group contains the apps you want to use in the configurable apps
        gallery.

        Assign either an instance of Group class, a group id, or None to reset
        to default.
        """
        if "templatesGroupQuery" in self._gis.properties:
            return self._gis.properties["templatesGroupQuery"]
        else:
            return "Default"

    # ----------------------------------------------------------------------
    @config_apps_group.setter
    def config_apps_group(self, group: Group | str | None):
        if isinstance(group, Group):
            group = "id:" + group.id
        elif isinstance(group, str):
            res = self._gis.groups.search(group)
            if len(res) == 0:
                raise ValueError(
                    "The group id provided could not be found in your org."
                )
            else:
                group = "id:" + group

        self._gis.update_properties(
            {"templatesGroupQuery": group, "clearEmptyFields": True}
        )

    # ----------------------------------------------------------------------
    def web_styles(
        self,
        group: Group | str | None = None,
        two_dimensional_map: bool = False,
        three_dimensional_map: bool = False,
    ):
        """
        Web styles are collections of symbols stored in an item. Apps can
        use web styles to symbolize point features with 2D or 3D symbols.
        Select a group to be used in symbol galleries.

        ======================      ==============================================
        **Argument**                **Description**
        ----------------------      ----------------------------------------------
        group                       Optional str or Group. either an instance of Group class,
                                    a group id, or None to reset to default.
        ----------------------      ----------------------------------------------
        two_dimensional_map         Optional bool. If True, the group will be assigned
                                    to 2D Web Style.
        ----------------------      ----------------------------------------------
        three_dimensional_map       Optional bool. If True, the group will be assigned
                                    to 3D Web Style.
        ======================      ==============================================

        """
        if isinstance(group, Group):
            group = "id:" + group.id
        elif isinstance(group, str):
            res = self._gis.groups.search(group)
            if len(res) == 0:
                raise ValueError(
                    "The group id provided could not be found in your org."
                )
            else:
                group = "id:" + group
        if two_dimensional_map:
            res = self._gis.update_properties({"2DStylesGroupQuery": group})
        if three_dimensional_map:
            res = self._gis.update_properties({"stylesGroupQuery": group})
        return res

    # ----------------------------------------------------------------------
    @property
    def analysis_layer_group(self):
        """
        Select the group whose layers will be shown in the Analysis Layer
        gallery for the analysis tools. It is best practice to share feature
        items that contain only a single layer with this group.
        If your feature layer item contains multiple layers, save any of the
        layers as an item and share it with the group.
        """
        if "analysisLayersGroupQuery" in self._gis.properties:
            return self._gis.properties["analysisLayersGroupQuery"]
        else:
            return "Default"

    # ----------------------------------------------------------------------
    @analysis_layer_group.setter
    def analysis_layer_group(
        self,
        group: Group | str | None = None,
    ):
        if isinstance(group, Group):
            group = "id:" + group.id
        elif isinstance(group, str):
            res = self._gis.groups.search(group)
            if len(res) == 0:
                raise ValueError(
                    "The group id provided could not be found in your org."
                )
            else:
                group = "id:" + group
        self._gis.update_properties(
            {"analysisLayersGroupQuery": group, "clearEmptyFields": True}
        )

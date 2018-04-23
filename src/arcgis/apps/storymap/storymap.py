import json
import datetime
from urllib.parse import urlparse
from arcgis import env
from arcgis.gis import GIS
from arcgis.gis import Item
from _ref import reference


class JournalStoryMap(object):
    """
    Represents a Journal StoryMap Template
    """
    _properties = None
    _gis = None
    _itemid = None
    _item = None

    def __init__(self, item=None, gis=None):
        """initializer"""
        if gis is None:
            self._gis = env.active_gis
        else:
            self._gis = gis
        if item and isinstance(item, str):
            self._item = gis.content.get(item)
            self._itemid = self._item.itemid
            self._properties = self._item.get_data()
        elif item and isinstance(item, Item):
            self._item = item
            self._itemid = self._item.itemid
            self._properties = self._item.get_data()
        else:
            self._properties = reference['journal']
    #----------------------------------------------------------------------
    def __str__(self):
        return json.dumps(self._properties)
    #----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()
    #----------------------------------------------------------------------
    def _refresh(self):
        if self._item:
            self._properties = json.loads(self._item.get_data())
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """returns the storymap's JSON"""
        return self._properties
    #----------------------------------------------------------------------
    def add_webpage(self,
                    title,
                    url,
                    content=None,
                    actions=None,
                    visible=True,
                    alt_text="",
                    display='stretch'):
        """
        Adds a webpage to the storymap

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the webpage
        ---------------     --------------------------------------------------------------------
        content             Optional string. The content of the section.
        ---------------     --------------------------------------------------------------------
        actions             Optional list. A collection of actions performed on the section
        ---------------     --------------------------------------------------------------------
        visible             Optional boolean. If True, the section is visible on publish. If
                            False, the section is not displayed.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ===============     ====================================================================


        :return: Boolean

        """
        if actions is None:
            actions = []
        if visible:
            visible = "PUBLISHED"
        else:
            visible = "HIDDEN"
        self._properties['values']['story']['sections'].append(
            {
                "title": title,
                "content": content,
                "contentActions": actions,
                "creaDate": int(datetime.datetime.now().timestamp() * 1000),
                "pubDate": int(datetime.datetime.now().timestamp() * 1000),
                "status": visible,
                "media": {
                    "type": "webpage",
                    "webpage": {
                        "url": url,
                        "type": "webpage",
                        "altText": alt_text,
                        "display": display,
                        "unload": True,
                        "hash": "5"
                    }
                }
            }
        )
        return True
    #----------------------------------------------------------------------
    def add_video(self,
                  url,
                  title,
                  content,
                  actions=None,
                  visible=True,
                  alt_text="",
                  display='stretch'
                  ):
        """
        Adds a video section to the StoryMap.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the image
        ---------------     --------------------------------------------------------------------
        content             Optional string. The content of the section.
        ---------------     --------------------------------------------------------------------
        actions             Optional list. A collection of actions performed on the section
        ---------------     --------------------------------------------------------------------
        visible             Optional boolean. If True, the section is visible on publish. If
                            False, the section is not displayed.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ===============     ====================================================================


        :return: Boolean

        """
        if actions is None:
            actions = []
        if visible:
            visible = "PUBLISHED"
        else:
            visible = "HIDDEN"
        video = {
            "title": title,
            "content": content,
            "contentActions": actions,
            "creaDate": 1523450612336,
            "pubDate": 1523450580000,
            "status": visible,
            "media": {
                "type": "video",
                "video": {
                    "url": url,
                    "type": "video",
                    "altText": alt_text,
                    "display": display
                }
            }
        }
        self._properties['values']['story']['sections'].append(video)
        return True
    #----------------------------------------------------------------------
    def add_webmap(self,
                   item,
                   title,
                   content,
                   actions=None,
                   visible=True,
                   alt_text="",
                   display='stretch'):
        """
        Adds a WebMap to the Section.


        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        item                Required string/Item. The webmap Item Id or Item of a webmap.
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the image
        ---------------     --------------------------------------------------------------------
        content             Optional string. The content of the section.
        ---------------     --------------------------------------------------------------------
        actions             Optional list. A collection of actions performed on the section
        ---------------     --------------------------------------------------------------------
        visible             Optional boolean. If True, the section is visible on publish. If
                            False, the section is not displayed.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ===============     ====================================================================


        :return: Boolean

        """
        if isinstance(item, Item):
            item = item.itemid

        if actions is None:
            actions = []
        if visible:
            visible = "PUBLISHED"
        else:
            visible = "HIDDEN"
        wm = {
            "title": title,
            "content": content,
            "contentActions": actions,
            "creaDate": int(datetime.datetime.now().timestamp() * 1000),
            "pubDate": int(datetime.datetime.now().timestamp() * 1000),
            "status": visible,
            "media": {
                "type": "webmap",
                "webmap": {
                    "id": item,
                    "extent": None,
                    "layers": None,
                    "popup": None,
                    "overview": {
                        "enable": False,
                        "openByDefault": True
                        },
                    "legend": {
                        "enable": False,
                        "openByDefault": False
                        },
                    "geocoder": {
                        "enable": False
                        },
                    "altText": alt_text
                }
            }
        }
        self._properties['values']['story']['sections'].append(wm)
        return True
    #----------------------------------------------------------------------
    def add_image(self,
                  title,
                  image,
                  content=None,
                  actions=None,
                  visible=True,
                  alt_text=None,
                  display='fill'):
        """
        Adds a new image section to the storymap


        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Required string. The title of the section.
        ---------------     --------------------------------------------------------------------
        url                 Required string. The web address of the image
        ---------------     --------------------------------------------------------------------
        content             Optional string. The content of the section.
        ---------------     --------------------------------------------------------------------
        actions             Optional list. A collection of actions performed on the section
        ---------------     --------------------------------------------------------------------
        visible             Optional boolean. If True, the section is visible on publish. If
                            False, the section is not displayed.
        ---------------     --------------------------------------------------------------------
        alt_text            Optional string. Specifies an alternate text for an image.
        ---------------     --------------------------------------------------------------------
        display             Optional string. The image display properties.
        ===============     ====================================================================


        :return: Boolean

        """
        if actions is None:
            actions = []
        if visible:
            visible = "PUBLISHED"
        else:
            visible = "HIDDEN"
        self._properties['values']['story']['sections'].append(
            {
                "title": title,
                "content": content,
                "contentActions": actions,
                "creaDate": int(datetime.datetime.now().timestamp() * 1000),
                "pubDate": int(datetime.datetime.now().timestamp() * 1000),
                "status": visible,
                "media": {
                    "type": "image",
                    "image": {
                        "url": image,
                        "type": "image",
                        "altText": alt_text,
                        "display": display
                    }
                }
            }
        )
        return True
    #----------------------------------------------------------------------
    def remove(self, index):
        """
        Removes a section by index.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        index               Required integer. The position of the section to remove.
        ===============     ====================================================================


        :return: Boolean

        """
        try:
            item = self._properties['values']['story']['sections'][index]
            self._properties['values']['story']['sections'].remove(item)
            return True
        except:
            return False
    #----------------------------------------------------------------------
    def save(self, title=None, tags=None, description=None):
        """
        Saves an Journal StoryMap to the GIS

        Removes a section by index.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        title               Optional string. The title of the StoryMap.
        ---------------     --------------------------------------------------------------------
        tags                Optional string. The tags of the StoryMap.
        ---------------     --------------------------------------------------------------------
        description         Optional string. The description of the StoryMap
        ===============     ====================================================================


        :return: Boolean

        """
        import uuid

        if self._item:
            p = {
                    'text' : json.dumps(self._properties)
                }
            if title:
                p['title'] = title
            if tags:
                p['tags'] = tags
            return self._item.update(item_properties=p)
        else:
            if title is None:
                title = "Journal Map, %s" % uuid.uuid4().hex[:10]
            if tags is None:
                tags = "Story Map,Map Journal"

            item = self._gis.content.add(item_properties={
                'title' : title,
                'tags' : tags,
                'text' : json.dumps(self._properties),
                'itemType' : 'text',
                'type' : "Web Mapping Application",
            })
            parse = urlparse(self._gis._con.baseurl)
            url = "%s://%s/apps/MapJournal/index.html?appid=%s" % (parse.scheme, parse.netloc, item.itemid)
            return item.update(item_properties={
                'url' : url
            })
        return False
    #----------------------------------------------------------------------
    def delete(self):
        """Deletes the saved item on ArcGIS Online/Portal"""
        if self._item:
            return self._item.delete()
        return False
    #----------------------------------------------------------------------
    @property
    def panel(self):
        """
        Gets/Sets the panel state for the Journal Story Map
        """
        return self._properties["values"]["settings"]["layout"]["id"]
    #----------------------------------------------------------------------
    @panel.setter
    def panel(self, value):
        """
        Gets/Sets the panel state for the Journal Story Map
        """
        if value.lower() == "float":
            self._properties["values"]["settings"]["layout"]["id"] = "float"
        else:
            self._properties["values"]["settings"]["layout"]["id"] = "side"
    #----------------------------------------------------------------------
    @property
    def header(self):
        """gets/sets the headers for the Journal StoryMap"""
        default = {
            "social": {
                "bitly": True,
                "twitter": True,
                "facebook": True
                },
            "logoURL": None,
            "linkURL": "https://storymaps.arcgis.com",
            "logoTarget": "",
            "linkText": "A Story Map"
        }
        if 'header' in self._properties['values']['settings']:
            return self._properties['values']['settings']['header']
        else:
            self._properties['values']['settings']['header'] = default
            return default
    #----------------------------------------------------------------------
    @header.setter
    def header(self, value):
        """"""
        if value is None:
            default = {
                "social": {
                    "bitly": True,
                    "twitter": True,
                    "facebook": True
                    },
                "logoURL": None,
                "linkURL": "https://storymaps.arcgis.com",
                "logoTarget": "",
                "linkText": "A Story Map"
            }
            self._properties['values']['settings']['header'] = default
        else:
            self._properties['values']['settings']['header'] = value
    #----------------------------------------------------------------------
    @property
    def theme(self):
        """"""
        default = {
            "colors": {
                "text": "#FFFFFF",
                "name": "float-default-1",
                "softText": "#FFF",
                "media": "#a0a0a0",
                "themeMajor": "black",
                "panel": "#000000",
                "textLink": "#DDD",
                "esriLogo": "white",
                "dotNav": "#000000",
                "softBtn": "#AAA"
                },
            "fonts": {
                "sectionTitle": {
                    "value": "font-family:\'open_sansregular\', sans-serif;",
                    "id": "default"
                    },
                "sectionContent": {
                    "value": "font-family:\'open_sansregular\', sans-serif;",
                    "id": "default"
                }
            }
        }
        if 'theme' in self._properties['values']['settings']:
            return self._properties['values']['settings']['theme']
        else:
            self._properties['values']['settings']['theme'] = default
            return self._properties['values']['settings']['theme']
        return default
    #----------------------------------------------------------------------
    @theme.setter
    def theme(self, value):
        """"""
        default = {
            "colors": {
                "text": "#FFFFFF",
                "name": "float-default-1",
                "softText": "#FFF",
                "media": "#a0a0a0",
                "themeMajor": "black",
                "panel": "#000000",
                "textLink": "#DDD",
                "esriLogo": "white",
                "dotNav": "#000000",
                "softBtn": "#AAA"
                },
            "fonts": {
                "sectionTitle": {
                    "value": "font-family:\'open_sansregular\', sans-serif;",
                    "id": "default"
                    },
                "sectionContent": {
                    "value": "font-family:\'open_sansregular\', sans-serif;",
                    "id": "default"
                }
            }
        }
        if 'theme' in self._properties['values']['settings']:
            self._properties['values']['settings']['theme'] = value
        elif not 'theme' in self._properties['values']['settings']:
            self._properties['values']['settings']['theme'] = value
        elif value is None:
            self._properties['values']['settings']['theme'] = default





if __name__ == "__main__":
    from arcgis.gis import GIS
    jsm = JournalStoryMap(item="a9f6a531f4f9466eb79f74771c2aed22",
                          gis=GIS(username='AndrewSolutions', password='fujiFUJI1'))
    print(jsm)
    print(jsm.save())
    print()
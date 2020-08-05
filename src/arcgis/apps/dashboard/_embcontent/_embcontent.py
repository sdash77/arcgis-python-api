import uuid
import arcgis
from .._utils._basewidget import _BaseWidget
from .._utils._basewidget import NoDataProperties

class EmbeddedContent(_BaseWidget):

    def __init__(self, url, name, title="", description="", content_type="document", refresh_interval=0, item=None, max_features_displayed=50):
        """
        Creates a dashboard Embedded Content Widget.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        url                         Required string. Url of the embedded content.
        -------------------------   -------------------------------------------
        name                        Optional string. Name of the widget.
        -------------------------   -------------------------------------------
        title                       Optional string. Title of the widget.
        -------------------------   -------------------------------------------
        description                 Optional string. Description of the widget.
        -------------------------   -------------------------------------------
        content_type                Optional string. Type of the content.
                                    Choose from "document", "image", "video".
        -------------------------   -------------------------------------------
        refresh_interval            Optional integer. Interval to refresh in
                                    minutes.
        -------------------------   -------------------------------------------
        item                        Optional Portal Item. To show content from
                                    portal.
        -------------------------   -------------------------------------------
        max_features_displayed      Optional integer. Maximum number of features
                                    to display.
        =========================   ===========================================
        """
        super().__init__(title, description)

        data_type = "features"

        if item is None:
            data_type = "static"
        if not name:
            raise Exception("Please specify a name")

        self._item = item
        self.name = name
        self.type = "embeddedContentWidget"

        self._data_type = data_type
        self._url = url

        if content_type not in ["document", "image", "video"]:
            raise Exception("Invalid content type.")

        self._content_type = content_type
        self._max_features_displayed = max_features_displayed
        self._refresh_interval = refresh_interval

        self._no_data = NoDataProperties._nodata_init()
    
    @classmethod
    def _from_json(cls, widget_json):
        gis = arcgis.env.active_gis
        itemid = json_data["datasets"]["datasource"]["itemid"]
        name = json_data["name"]
        item = gis.content.get(itemid)
        title = widget_json["caption"]
        description = widget_json["description"]
        gauge = Gauge(item, name, title, description)

        return gauge

    @property
    def url(self):
        """
        :return: Url of the embedded content.
        """
        return self._url

    @url.setter
    def url(self, value):
        """
        Set Url for the embedded content.
        """
        self._url = value

    @property
    def content_type(self):
        """
        :return: Content type of the embedded content.
        """
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        """
        Set Content type for the embedded content.
        """
        if value in ["document", "image", "video"]:
            self._content_type = value
        else:
            raise Exception("Invalid content type")

    @property
    def max_features(self):
        """
        :return: Max Features to display for feature data.
        """
        return self._max_features_displayed

    @max_features.setter
    def max_features(self, value):
        """
        Set max features to display for data from features.
        """
        self._max_features_displayed = value

    @property
    def refresh_interval(self):
        """
        :return: Refresh interval for image content.
        """
        return self._refresh_interval

    @refresh_interval.setter
    def refresh_interval(self, value):
        """
        Set refresh interval for image content.
        """
        self._refresh_interval = value

    @property
    def no_data(self):
        """
        :return: NoDataProperties Object
        """
        return self._no_data

    def _convert_to_json(self):
        json_data = {
            "type": "embeddedContentWidget",
            "url": self._url,
            "contentType": self._content_type,
            "imageRefreshInterval": self._refresh_interval,
            "videoSettings": {
                "controls": True,
                "autoplay": False,
                "loop": False,
                "muted": False,
                "controlsList": "nodownload"
            },
            "datasets": [],
            "id": self.id,
            "name": self.name,
            "caption": self._title,
            "description": self.description,
            "showLastUpdate": True,
            "noDataVerticalAlignment": self._no_data._alignment,
            "showCaptionWhenNoData": self._no_data._show_title,
            "showDescriptionWhenNoData": self._no_data._show_description
        }

        if self._no_data._text:
            json_data['noDataText'] = self._no_data._text

        if self._background_color:
            json_data['backgroundColor'] = self._background_color

        if self._text_color:
            json_data['textColor'] = self._text_color

        if self._item:
            json_data['datasets'] = [
                {
                    "type": "serviceDataset",
                    "dataSource": {
                        "type": "featureServiceDataSource",
                        "itemId": self._item.itemid,
                        "layerId": 0,
                        "table": True
                    },
                    "outFields": ["*"],
                    "groupByFields": [],
                    "orderByFields": [],
                    "statisticDefinitions": [],
                    "maxFeatures": self._max_features_displayed,
                    "querySpatialRelationship": "esriSpatialRelIntersects",
                    "returnGeometry": False,
                    "clientSideStatistics": False,
                    "name": "main"
                }
            ]

        return json_data

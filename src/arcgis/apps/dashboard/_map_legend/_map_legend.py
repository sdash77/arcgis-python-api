import uuid
from .._utils._basewidget import _BaseWidget

class MapLegend(object):

    def __init__(self, map, name, title="", description=""):
        """
        Create a MapLegend widget for Dashboard

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        map                         Required web map widget. Legend for this
                                    Map widget is displayed.
                                    This map widget needs to be a part of the
                                    final Dashboard as well.
        -------------------------   -------------------------------------------
        name                        Required String. Name of the widget.
        -------------------------   -------------------------------------------
        title                       Optional string. Title of the widget.
        -------------------------   -------------------------------------------
        description                 Optional string. Description of the widget.
        =========================   ===========================================
        """

        super().__init__(title, description)

        self._map_widget_id = map.id
        self.name = name
        self._type = "legendWidget"

    @classmethod
    def _from_json(cls, widget_json):
        map = widget_json["mapWidgetId"]
        name = widget_json["name"]
        title = widget_json["caption"]
        description = widget_json["description"]
        map_legend = MapLegend(map, name, title, description)
        map_legend.id = widget_json["id"]
        map_legend.no_data.alignment = widget_json["noDataVerticalAlignment"]
        map_legend.no_data.show_title =  widget_json["showCaptionWhenNoData"]
        map_legend.no_data.show_description = widget_json["showDescriptionWhenNoData"]

        return map_legend
    
    @property
    def type(self):
        """
        :return: widget type.
        """
        return self._type

    @property
    def title(self):
        """
        :return: widget title.
        """
        return self._title

    @title.setter
    def title(self, value):
        """
        Set widget title.
        """
        self._title = value

    @property
    def description(self):
        """
        :return: widget description.
        """
        return self._description

    @description.setter
    def description(self, value):
        """
        Set widget description.
        """
        self._description = value
    
    def _convert_to_json(self):
        data = {
            "type": "legendWidget",
            "mapWidgetId": self._map_widget_id,
            "id": self.id,
            "name": self.name,
            "caption": self._title,
            "description": self._description,
            "showLastUpdate": True,
            "noDataVerticalAlignment": "middle",
            "showCaptionWhenNoData": True,
            "showDescriptionWhenNoData": True
        }

        if self._background_color:
            data["backgroundColor"] = self._background_color

        if self._text_color:
            data["textColor"] = self._text_color

        return data

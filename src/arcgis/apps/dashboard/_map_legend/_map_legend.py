import uuid
import arcgis
from .._utils._basewidget import _BaseWidget


class MapLegend(_BaseWidget):

    def __init__(self, map_widget, name, title="", description=""):
        """
        Create a MapLegend widget for Dashboard

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        map_widget                  Required web map widget. Legend for this
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

        self._map_widget_id = map_widget.id
        self.name = name
        self._type = "legendWidget"

    @classmethod
    def _from_json(cls, widget_json):
        map_widget = widget_json["mapWidgetId"]
        name = widget_json["name"]
        title = widget_json["caption"]
        description = widget_json["description"]
        map_legend = MapLegend(map_widget, name, title, description)
        map_legend.id = widget_json["id"]
        map_legend.no_data.alignment = widget_json["noDataVerticalAlignment"]
        map_legend.no_data.show_title =  widget_json["showCaptionWhenNoData"]
        map_legend.no_data.show_description = widget_json["showDescriptionWhenNoData"]

        return map_legend
   
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

import uuid
import arcgis
from .._utils._basewidget import _BaseWidget, NoDataProperties

class RichText(object):

    def __init__(self, html_text, name, title='', description=''):
        """
        Creates a dashboard Rich Text widget.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        html_text                   Required HTML text. This text will be
                                    displayed in Rich Text format.
        =========================   ===========================================
        """


        self.name = name
        self._type = "richTextWidget"
        self._title = ""
        self._description = ""
        self._type = "richTextWidget"

        self._text = ""

        self.text = html_text
        self.title = title
        self.description = description

        self._nodata = NoDataProperties._nodata_init()
    
    def _repr_html_(self):
        from arcgis.apps.dashboard import Dashboard
        url = Dashboard._publish_random(self)
        return f"""<iframe src={url} width=900 height=300>"""
    
    @classmethod
    def _from_json(cls, widget_json):
        txt = widget_json["text"]
        name = widget_json["name"]
        title = widget_json["caption"]
        description = widget_json["description"]
        rtxt = RichText(txt, name, title, description)
        rtxt.id = widget_json["id"]
        rtxt.no_data.alignment = widget_json["noDataVerticalAlignment"]
        rtxt.no_data.show_title =  widget_json["showCaptionWhenNoData"]
        rtxt.no_data.show_description = widget_json["showDescriptionWhenNoData"]

        return rtxt

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

    @property
    def text(self):
        """
        :return: text field for rich text
        """
        return self._text
    
    @text.setter
    def text(self, value):
        """
        Set text field for rich text
        """
        self._text = value

    @property
    def no_data(self):
        """
        :return: Nodata Object, set various nodata properties
        """
        return self._nodata

    def _convert_to_json(self):
        json_data = {
            "type": "richTextWidget",
            "text": self.text,
            "id": self.id,
            "name": self.name,
            "showLastUpdate": True,
            "noDataVerticalAlignment": self._nodata.alignment,
            "showCaptionWhenNoData": self._nodata.show_title,
            "showDescriptionWhenNoData": self._nodata.show_description
        }

        if self._text_color:
            json_data["textColor"] = self._text_color

        if self._background_color:
            json_data["backgroundColor"] = self._background_color

        return json_data

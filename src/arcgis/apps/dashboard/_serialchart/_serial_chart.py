import arcgis
from .._utils._basewidget import _BaseWidget
from .._utils._basewidget import Legend
from .._utils._basewidget import NoDataProperties


class SerialChart(_BaseWidget):

    def __init__(self, item, name, layer=0, categories_from="groupByValues", title='', description=''):
        """
        Creates a dashboard Serial Chart widget.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        item                        Required Item object. Item from which the
                                    Indicator is constructed. Item object can 
                                    be a Feature Layer or a MapWidget.
        -------------------------   -------------------------------------------
        name                        Optional string. Name of the serial chart
                                    widget.
        -------------------------   -------------------------------------------
        layer                       Optional integer. Layer number when item is
                                    a mapwidget.
        -------------------------   -------------------------------------------
        categories_from             Optional string. Select from groupByValues,
                                    features or fields.
        -------------------------   -------------------------------------------
        title                       Optional string. Title or Caption for the
                                    widget.
        -------------------------   -------------------------------------------
        description                 Optional string. Description for the widget.
        =========================   ===========================================
        """
        if item.type not in ['Feature Service', 'mapWidget']:
            raise Exception("Please specify an item")

        super().__init__(title, description)

        self.name = name
        self.item = item
        self.layer = layer
        self.type = "serialChartWidget"

        if categories_from in ["groupByValues", "features", "fields"]:
            self._categories_from = categories_from

        self._data = SerialChartData._create_serial_chart_data(categories_from)
        self._max_features = None
        self._category_axis_properties = _CategoryAxisProperties._create_category_axis()
        self._scroll = False
        self._value_axis_properties = _ValueAxisProperties._create_value_axis()
        self._legend = Legend._create_legend()
        self._color = "#474747"
        self._font_size = 11
        self._orientation = 'vertical'
        self._last_update = True
        self._no_data = NoDataProperties._nodata_init()
    
    @classmethod
    def _from_json(cls, widget_json):
        gis = arcgis.env.active_gis
        itemid = json_data["datasets"]["datasource"]["itemid"]
        name = json_data["name"]
        item = gis.content.get(itemid)
        title = widget_json["caption"]
        categories_from = widget_json["categoryType"]
        description = widget_json["description"]
        schart = SerialChart(item, name, 0, categories_from, title, description)
        schart.data.category_field = widget_json["category"]["fieldName"]
        scart.legend.visibility = widget_json["legend"]["enabled"]
        scart.legend.placement = widget_json["legend"]["position"]
        schart.max_features = widget_json["dataset"]["maxFeatures"]
        
        return schart

    @property
    def categories_from(self):
        """
        :return: Selected categories from, groupByValues, features or fields.
        """
        return self._categories_from

    @property
    def data(self):
        """
        :return: Serial Chart Data object. Set data properties, categories and values.
        """

        return self._data

    @property
    def category_axis(self):
        """
        :return: Returns Category Axis Properties object.
        """
        return self._category_axis_properties

    @property
    def value_axis(self):
        """
        :return: Value Axis Properties object.
        """
        return self._value_axis_properties

    @property
    def legend(self):
        """
        :return: Legend Object, set Visibility and placement
        """
        return self._legend


    @property
    def scroll(self):
        """
        :return: True if scroll is enabled else False.
        """
        return self._scroll

    @scroll.setter
    def scroll(self, value):
        """
        Set scroll True or False.
        """
        self._scroll = bool(value)

    @property
    def font_size(self):
        """
        :return: Font Size
        """
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        """
        Set font size.
        """
        self._font_size = value

    @property
    def orientation(self):
        """
        :return: Orientation of the serial chart, "horizontal" or "vertical".
        """
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        """
        Set orientation of the serial chart, "horizontal" or "vertical".
        """
        if value in ["horizontal", "vertical"]:
            self._orientation = value

    @property
    def no_data(self):
        """
        :return: NoDataProperties Object
        """
        return self._no_data

    @property
    def max_features(self):
        """
        :return: Max features to display
        """
        return self._max_features

    @max_features.setter
    def max_features(self, value):
        """
        Set max features to display.
        """
        self._max_features = value

    def _convert_to_json(self):

        common_graph_properties = {"lineColorField": "_lineColor_", "fillColorsField": "_fillColor_",
                                      "type": "column", "fillAlphas": 1, "lineAlpha": 1, "lineThickness": 1,
                                      "bullet": "none", "bulletAlpha": 1, "bulletBorderAlpha": 0,
                                      "bulletBorderThickness": 2, "showBalloon": self.data._show_baloon, "bulletSize": 8}

        if self._data._labels:
            common_graph_properties['labelText'] = "[[value]]"

        json_data = {
            "type": "serialChartWidget",
            "category": {
                "labelOverrides": [],
                "byCategoryColors": False,
                "labelsPlacement": "default", #default, staggered, wrapped, rotated
                "labelRotation": 0,
                "fieldName": self.data.category_field,
                "nullLabel": "Null",
                "blankLabel": "Blank",
                "defaultColor": "#d6d6d6",
                "nullColor": "#d6d6d6",
                "blankColor": "#d6d6d6"
            },
            "valueFormat": {
                "name": "value",
                "type": "decimal",
                "prefix": True,
                "pattern": "#,###.#"
            },
            "labelFormat": {
                "name": "label",
                "type": "decimal",
                "prefix": True,
                "pattern": "#,###.#"
            },
            "datePeriodPatterns": [{"period": "ss", "pattern": "HH:mm:ss"}, {"period": "mm", "pattern": "HH:mm"},
                                   {"period": "hh", "pattern": "HH:mm"}, {"period": "DD", "pattern": "MMM d"},
                                   {"period": "MM", "pattern": "MMM"}, {"period": "YYYY", "pattern": "yyyy"}],
            "chartScrollbar": {
                "enabled": self._scroll,
                "dragIcon": "dragIconRoundSmall",
                "dragIconHeight": 20,
                "dragIconWidth": 20,
                "scrollbarHeight": 15
            },
            "categoryAxis": self._category_axis_properties._convert_to_json(),
            "valueAxis": self._value_axis_properties._convert_to_json(),
            "legend": {
                "enabled": self._legend.visibility,
                "position": "right" if self._legend.placement == "side" else self._legend.placement,
                "markerSize": 15,
                "markerType": "circle",
                "align": "center",
                "labelWidth": 100,
                "valueWidth": 0
            },
            "graphs": [
                series for series in self.data._series
            ],
            "guides": [],
            "splitBy": {"defaultColor": "#d6d6d6", "seriesProperties": []},
            "rotate": False if self._orientation == "vertical" else True,
            "commonGraphProperties": common_graph_properties,
            "selectionMode": "multi",
            "categoryType": self.data.categories_from,
            "datasets": [],
            "id": self.id,
            "name": self.name,
            "caption": self.title,
            "description": self.description,
            "showLastUpdate": self._last_update,
            "noDataVerticalAlignment": self._no_data._alignment,
            "showCaptionWhenNoData": self._no_data._show_title,
            "showDescriptionWhenNoData": self._no_data._show_description
        }

        if self._no_data._text:
            json_data['noDataText'] = self._no_data._text
        
        if self.item.type == 'mapWidget':
            wlayer = self.item.layers[self.layer]
            widget_id = self.item.id
            layer_id = wlayer["id"]
            self._datasource = {"id":str(widget_id)+'#'+str(layer_id)}
        else:
            self._datasource = {
                        "type": "featureServiceDataSource",
                        "itemId": self.item.itemid,
                        "layerId": 0,
                        "table": True
                    }

        dataset = {
            "type": "serviceDataset",
            "dataSource": self._datasource,
            "outFields": ["*"],
            "groupByFields": [],
            "orderByFields": ["date asc"],
            "statisticDefinitions": [],
            "querySpatialRelationship": "esriSpatialRelIntersects",
            "returnGeometry": False,
            "clientSideStatistics": False,
            "name": "main"
        }

        if self._max_features:
            dataset['maxFeatures'] = self._max_features

        if self._color:
            json_data['color'] = self._color

        if self._font_size:
            json_data['fontSize'] = self._font_size

        if self._data._categories_from == "groupByValues":
            if self._data._category_field:
                dataset['groupByFields'].append(self._data._category_field)
            if self._data._split_by_field:
                json_data['splitBy']['fieldName'] = self._split_by_field
                dataset['groupByFields'].append(self._data._split_by_field)

            dataset['statisticDefinitions'].append({"onStatisticField": "FID", "outStatisticFieldName": "value", "statisticType": self._data.statistic})
        elif self._data._categories_from == "fields":
            for category in self._category_fields:
                dataset['statisticDefinitions'].append({"onStatisticField": category, "outStatisticFieldName": category, "statisticType": self._data.statistic})

        json_data['datasets'] = [dataset]

        return json_data


class _CategoryAxisProperties(object):

    @classmethod
    def _create_category_axis(cls):
        category_axis = cls()
        category_axis._title = ""

        category_axis._title_rotation = 0
        category_axis._font_size = 12
        category_axis._grid_thickness = 1
        category_axis._grid_opacity = 0.15
        category_axis._grid_color = "#ffffff"
        category_axis._axis_thickness = 1
        category_axis._axis_opacity = 0.5
        category_axis._axis_color = "#000000"
        category_axis._title_size = 12
        category_axis._labels = True
        category_axis._parse_dates = True
        category_axis._min_period = "DD"
        category_axis._grid_position = "start"

        category_axis._requirements = {
            'title': [str],
            'gridThickness': [int, 1, 10],
            'gridAlpha': [(int, float), 0, 1],
            'axisThickness': [int, 1, 10],
            'axisAlpha': [(int, float), 0, 1],
            'labelsEnabled': [bool],
            'parseDates': [bool],
            'titleFontSize': [int, 0, 1000],
            'fontSize': [int, 0, 1000],
            'gridColor': [str],
            'axisColor': [str]

        }

        category_axis._translations = {
            'axisAlpha': 'axisOpacity',
            'gridAlpha': 'gridOpacity'
        }

        category_axis._translations_inverse = {value: key for key, value in category_axis._translations.items()}

        category_axis._hidden = ['minPeriod', 'titleRotation', 'gridPosition']

        return category_axis

    @property
    def title(self):
        """
        :return: Category axis Title
        """
        return self._title

    @title.setter
    def title(self, value):
        """
        Set Category axis Title
        """
        if self._validation("title", value):
            self._title = value

    @property
    def grid_thickness(self):
        """
        :return: Category axis grid thickness.
        """
        return self._grid_thickness

    @grid_thickness.setter
    def grid_thickness(self, value):
        """
        Set Category axis grid thickness.
        """
        if self._validation("gridThickness", value):
            self._grid_thickness = value

    @property
    def grid_opacity(self):
        """
        :return: Category axis grid opacity.
        """
        return self._grid_opacity

    @grid_opacity.setter
    def grid_opacity(self, value):
        """
        Set Category axis grid opacity.
        """
        if self._validation("gridOpacity", value):
            self._grid_opacity = value

    @property
    def axis_thickness(self):
        """
        :return: Category axis thickness.
        """
        return self._axis_thickness

    @axis_thickness.setter
    def axis_thickness(self, value):
        """
        Set Category axis thickness.
        """
        if self._validation("axisThickness", value):
            self._axis_thickness = value

    @property
    def axis_opacity(self):
        """
        :return: Category axis opacity.
        """
        return self._axis_opacity

    @axis_opacity.setter
    def axis_opacity(self, value):
        """
        Set Category axis opacity.
        """
        if self._validation("axisOpacity", value):
            self._axis_opacity = value

    @property
    def title_size(self):
        """
        :return: Category axis title size.
        """
        return self._title_size

    @title_size.setter
    def title_size(self, value):
        """
        Set Category axis title size.
        """
        if self._validation('titleFontSize', value):
            self._title_size = value

    @property
    def font_size(self):
        """
        :return: Font size
        """
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        """
        Set font size.
        """
        self._font_size = value

    @property
    def grid_color(self):
        """
        :return: Category axis grid color, hex code.
        """
        return self._grid_color

    @grid_color.setter
    def grid_color(self, value):
        """
        Set Category axis grid color, hex code.
        """
        self._grid_color = value

    @property
    def axis_color(self):
        """
        :return: Category axis color, hex code.
        """
        return self._axis_color

    @axis_color.setter
    def axis_color(self, value):
        """
        Set Category axis color, hex code.
        """
        self._axis_color = value

    @property
    def labels(self):
        """
        :return: Labels Object. Set visibility True or False.
        """
        return self._labels

    @labels.setter
    def labels(self, value):
        """
        Set labels True or False.
        """
        self._labels = bool(value)

    def __init__(self):
        self._item = {
            "title": '',
            "titleFontSize": 12,
            "fontSize": 12,
            "gridColor": "#ffffff",
            "axisColor": "#ffffff",
            "titleRotation": 0,
            "gridPosition": "start",
            "gridThickness": 1,
            "gridAlpha": 0.15,
            "axisThickness": 1,
            "axisAlpha": 0.5,
            "labelsEnabled": False,
            "parseDates": True,
            "minPeriod": "DD"
        }

    def _validation(self, key, value):
        if self._requirements.get(key):
            requirements = self._requirements.get(key)
        elif self._requirements.get(self._translations_inverse.get(key)):
            requirements = self._requirements.get(self._translations_inverse.get(key))
        else:
            return False

        if len(requirements) == 1 and isinstance(value, requirements[0]):
            pass
        elif len(requirements) == 3 and isinstance(value, requirements[0]) and value >= requirements[1] and value <= requirements[2]:
            pass
        else:
            return False

        return True

    def _convert_to_json(self):
        return {
            "title": self._title,
            "titleRotation": 0,
            'titleFontSize': self._title_size,
            "fontSize": self._font_size,
            "gridThickness": self._grid_thickness,
            "gridAlpha": self._grid_opacity,
            "gridColor": self._grid_color,
            "axisThickness": self._axis_thickness,
            "axisAlpha": self._axis_opacity,
            "axisColor": self._axis_color,
            "labelsEnabled": self._labels,
            "gridPosition": "start",
            "parseDates": True,
            "minPeriod": "DD"
        }


class _ValueAxisProperties(object):

    @classmethod
    def _create_value_axis(cls):
        value_axis = cls()
        value_axis._title = ""

        value_axis._title_rotation = 270
        value_axis._font_size = 12
        value_axis._title_size = 12
        value_axis._grid_thickness = 1
        value_axis._grid_opacity = 0.15
        value_axis._grid_color = "#ffffff"
        value_axis._axis_thickness = 1
        value_axis._axis_opacity = 0.5
        value_axis._axis_color = "#000000"
        value_axis._minimum = None
        value_axis._maximum = None

        value_axis._labels = False

        value_axis._stackType = "none"
        value_axis._integers_only = False
        value_axis._logarithmic = False

        value_axis._requirements = {
            'title': [str],
            'gridThickness': [int, 1, 10],
            'gridAlpha': [(int, float), 0, 1],
            'axisThickness': [int, 1, 10],
            'axisAlpha': [(int, float), 0, 1],
            'labelsEnabled': [bool],
            'parseDates': [bool],
            'titleFontSize': [int, 0, 1000],
            'fontSize': [int, 0, 1000],
            'gridColor': [str],
            'axisColor': [str]

        }

        value_axis._translations = {
            'axisAlpha': 'axisOpacity',
            'gridAlpha': 'gridOpacity'
        }

        value_axis._translations_inverse = {value: key for key, value in value_axis._translations.items()}

        value_axis._hidden = ['stackType', 'titleRotation']

        return value_axis

    @property
    def title(self):
        """
        :return: Value axis Title
        """
        return self._title

    @title.setter
    def title(self, value):
        """
        Set Value axis Title
        """
        if self._validation("title", value):
            self._title = value

    @property
    def grid_thickness(self):
        """
        :return: Value axis grid thickness.
        """
        return self._grid_thickness

    @grid_thickness.setter
    def grid_thickness(self, value):
        """
        Set Value axis grid thickness.
        """
        if self._validation("gridThickness", value):
            self._grid_thickness = value

    @property
    def grid_opacity(self):
        """
        :return: Value axis grid opacity.
        """
        return self._grid_opacity

    @grid_opacity.setter
    def grid_opacity(self, value):
        """
        Set Value axis grid opacity.
        """
        if self._validation("gridOpacity", value):
            self._grid_opacity = value

    @property
    def axis_thickness(self):
        """
        :return: Value axis thickness.
        """
        return self._axis_thickness

    @axis_thickness.setter
    def axis_thickness(self, value):
        """
        Set Value axis thickness.
        """
        if self._validation("axisThickness", value):
            self._axis_thickness = value

    @property
    def axis_opacity(self):
        """
        :return: Value axis opacity.
        """
        return self._axis_opacity

    @axis_opacity.setter
    def axis_opacity(self, value):
        """
        Set Value axis opacity.
        """
        if self._validation("axisOpacity", value):
            self._axis_opacity = value

    @property
    def labels(self):
        """
        :return: Labels Object. Set visibility True or False.
        """
        return self._labels

    @labels.setter
    def labels(self, value):
        """
        Set labels True or False.
        """
        self._labels = bool(value)

    @property
    def title_size(self):
        """
        :return: Value axis title size.
        """
        return self._title_size

    @title_size.setter
    def title_size(self, value):
        """
        Set value axis title size.
        """
        if self._validation('titleFontSize', value):
            self._title_size = value

    @property
    def grid_color(self):
        """
        :return: Value axis grid color, hex code.
        """
        return self._grid_color

    @grid_color.setter
    def grid_color(self, value):
        """
        Set value axis grid color, hex code.
        """
        self._grid_color = value

    @property
    def axis_color(self):
        """
        :return: Value axis color, hex code.
        """
        return self._axis_color

    @axis_color.setter
    def axis_color(self, value):
        """
        Set value axis color, hex code.
        """
        self._axis_color = value

    @property
    def only_integers(self):
        """
        :return: True if only integers are allowed.
        """
        return self._integers_only

    @only_integers.setter
    def only_integers(self, value):
        """
        Set if only integers are allowed.
        """
        self._integers_only = bool(value)

    @property
    def logarithmic(self):
        """
        :return: True if logarithmic.
        """
        return self._logarithmic

    @logarithmic.setter
    def logarithmic(self, value):
        """
        Set if only integers are allowed.
        """
        self._logarithmic = bool(value)

    @property
    def minimum(self):
        """
        :return: Filter by specifying minimum value possible.
        """
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        """
        Set minimum value to filter data.
        """
        self._minimum = int(value)

    @property
    def maximum(self):
        """
        :return: Filter by specifying maximum value possible.
        """
        return self._maximum

    @maximum.setter
    def maximum(self, value):
        """
        Set maximum value to filter data.
        """
        self._maximum = int(value)

    def _validation(self, key, value):
        if self._requirements.get(key):
            requirements = self._requirements.get(key)
        elif self._requirements.get(self._translations_inverse.get(key)):
            requirements = self._requirements.get(self._translations_inverse.get(key))
        else:
            return False

        if len(requirements) == 1 and isinstance(value, requirements[0]):
            pass
        elif len(requirements) == 3 and isinstance(value, requirements[0]) and value >= requirements[1] and value <= requirements[2]:
            pass
        else:
            return False

        return True

    def _convert_to_json(self):
        return {
            "title": self._title,
            "titleRotation": 270,
            "fontSize": self._title_size,
            "gridThickness": self._grid_thickness,
            "gridAlpha": self._grid_opacity,
            "gridColor": self._grid_color,
            "axisThickness": self._axis_thickness,
            "axisAlpha": self._axis_opacity,
            "axisColor": self._axis_color,
            "labelsEnabled": self._labels,
            "stackType": "none",
            "integersOnly": self._integers_only,
            "logarithmic": self._logarithmic
        }


class SerialChartData(object):

    @classmethod
    def _create_serial_chart_data(cls, categories_from):
        schart_data = SerialChartData()

        schart_data._categories_from = None
        if categories_from in ["groupByValues", "features", "fields"]:
            schart_data._categories_from = categories_from
        else:
            raise Exception('Invalid option, choose from "groupByValues", "features", "fields"')

        if categories_from == "features":
            schart_data._series = []
        elif categories_from == "groupByValues":
            schart_data._split_by_field = None

        schart_data._show_baloon = False
        schart_data._parse_dates = True
        schart_data._statistic = "count"
        schart_data._stacking = "off"
        schart_data._labels = True

        schart_data._category_field = None
        if schart_data._categories_from == "fields":
            schart_data._category_field = "category"

        schart_data._split_by_field = None

        return schart_data

    @property
    def categories_from(self):
        """
        :return: Categories from groupByValues, features or fields.
        """
        return self._categories_from

    @property
    def category_field(self):
        """
        :return: Category field from dataset. For groupByValues or features.
        """
        return self._category_field

    @category_field.setter
    def category_field(self, value):
        """
        Set category field from dataset. For groupByValues or features.
        """
        if self._categories_from == "fields":
            raise Exception("Can't set this attribute for 'fields' categories.")

        self._category_field = value

    @property
    def parse_dates(self):
        """
        :return: True if input category field of type date is to be parsed.
        """
        return self._parse_dates

    @parse_dates.setter
    def parse_dates(self, value):
        """
        Set True to parse input category fields of type date. For groupByValues and features.
        """
        self._parse_dates = bool(value)

    @property
    def statistic(self):
        """
        :return: statistic used for input category fields. For values from fields.
        """
        return self._statistic

    @statistic.setter
    def statistic(self, value):
        """
        Set statistic to 'count', 'avg', 'min', 'max', 'stddev', 'sum'
        """
        if value in ['count', 'avg', 'min', 'max', 'stddev', 'sum']:
            self._statistic = value

    @property
    def split_by_field(self):
        """
        :return: Field to split by for groupByValues.
        """
        return self._split_by_field

    @split_by_field.setter
    def split_by_field(self, value):
        """
        Set field name from the dataset to split data by, for groupByValues.
        """
        self._split_by_field = value

    def add_value_field(
            self,
            value_field,
            label=None,
            graph_type='line',
            line_thickness=1,
            line_color="#ffaa00",
            fill_opacity=0,
            line_opacity=1,
    ):
        """
         Add value field to serial chart.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        value_field                 Required field or list of fields from input item.
                                    For groupByValues only one field is accepted.
                                    For series, add multiple fields one by one.
                                    For fields, add a list of fields.
        -------------------------   -------------------------------------------
        label                       Optional string. Label to show on the graph.
        -------------------------   -------------------------------------------
        graph_type                  Optional string. Choose from "line", "bar"
                                    "smoothed_line"
        -------------------------   -------------------------------------------
        line_thickness              Optional integer. Thickness of the lines
                                    between 1 to 10.
        -------------------------   -------------------------------------------
        line_color                  Optional string. Hex code for line color.
        -------------------------   -------------------------------------------
        fill_opacity                Optional float. Between 0 and 1.
        -------------------------   -------------------------------------------
        line_opacity                Optional float. Between 0 and 1.
        =========================   ===========================================
        """

        data = {
            "valueField": value_field[0] if isinstance(value_field, list) else value_field,
            "title": label if label else None,
            "lineColor": line_color,
            "lineColorField": "_lineColor_",
            "fillColorsField": "_fillColor_",
            "type": graph_type,
            "fillAlphas": fill_opacity,
            "lineAlpha": line_opacity,
            "lineThickness": line_thickness,
            "bullet": "round",
            "bulletAlpha": 1,
            "bulletBorderAlpha": 0,
            "bulletBorderThickness": 2,
            "showBalloon": True,
            "bulletSize": 8
        }
        if self._categories_from == "features":
            if not isinstance(self._series, list):
                self._series = []
            if not data['title']:
                data['title'] = value_field
            self._series.append(data)
        elif self._categories_from == "groupByValues":
            self._series = data
        elif self._categories_from == "fields":
            if isinstance(value_field, list):
                self._category_fields = value_field
            else:
                self._category_fields = [value_field]

            data['valueField'] = "value"
            self._series = data

    @property
    def stacking(self):
        """
        :return: "off", "stacked", stack 100%"
        """
        return self._stacking

    @stacking.setter
    def stacking(self, value):
        """
        Set stacking to "off", "stacked", "stack 100%"
        """

        if value in ["off", "stacked", "stack 100%"]:
            if value == "off":
                self._stacking = "none"
            elif value == "stacked":
                self._stacking = "regular"
            else:
                self._stacking = "100%"

    @property
    def hover_text(self):
        """
        :return: True if series hover text is enabled else False
        """
        return self._show_baloon

    @hover_text.setter
    def hover_text(self, value):
        """
        Set true to show hover text on series.
        """
        self._show_baloon = bool(value)

    @property
    def labels(self):
        """
        :return: Labels Object. Set visibility True or False.
        """
        return self._labels

    @labels.setter
    def labels(self, value):
        """
        Set labels True or False.
        """
        self._labels = bool(value)

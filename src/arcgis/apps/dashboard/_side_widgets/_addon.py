import uuid


class DatePicker(object):

    def __init__(self, range=False, operator='is', min_value=None, max_value=None, label="Pick Date"):
        """
        Creates a Date Selector widget for Side Panel or Header.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        range                       Optional boolean. True to create a range
                                    selector.
        -------------------------   -------------------------------------------
        operator                    Optional String. Operator for non range
                                    datepicker.
                                    Options: "is", "is not", "is before",
                                    "is or is before", "is after",
                                    "is or is after".
        -------------------------   -------------------------------------------
        min_value                   Optional. Min default value.
                                    Options:
                                    "today"
                                    Or
                                    A tuple containing
                                    (year, month, day, minutes)
        -------------------------   -------------------------------------------
        max_value                   Optional. Max default value.
                                    Options:
                                    "today"
                                    Or
                                    A tuple containing
                                    (year, month, day, minutes)
        -------------------------   -------------------------------------------
        label                       Optional String. Label for the widget.
        =========================   ===========================================
        """
        self.id = str(uuid.uuid4())
        self.type = "dateSelectorWidget"

        self._operator_mapping = {
            'is': 'is_on',
            'is not': 'is_not_on',
            'is before': 'is_before',
            'is or is before': 'is_on_before',
            'is after': 'is_after',
            'is or is after': 'is_on_after'
        }

        if range:
            self.selection_type = "range"
            self.operator = "between"
        else:
            self.selection_type = "single"
            self.operator = self._operator_mapping.get(operator, 'is_on')

        self.min_value = None
        self.max_value = None

        self.label = label

        if min_value:
            if min_value == "today":
                self.min_value = {"type": "date", "includeTime": False, "defaultToToday": True}
            else:
                self.min_value = {"type": "date", "includeTime": False, "defaultToToday": False, "year": min_value[0], "month": min_value[1], "date": min_value[2], "hours": min_value[3] if len(min_value) > 3 else 0, "minutes": min_value[4] if len(min_value) > 3 else 0, "seconds": 0, "milliSeconds": 0}

        if max_value:
            if max_value == "today":
                self.max_value = {"type": "date", "includeTime": False, "defaultToToday": True}
            else:
                self.max_value = {"type": "date", "includeTime": False, "defaultToToday": False, "year": max_value[0], "month": max_value[1], "date": max_value[2], "hours": max_value[3] if len(max_value) > 3 else 0, "minutes": max_value[4] if len(max_value) > 3 else 0, "seconds": 0, "milliSeconds": 0}

    def _convert_to_json(self):
        return {
            "type": "dateSelectorWidget",
            "optionType": "datePicker",
            "datePickerOption": {
                "type": "datePicker",
                "selectionType": self.selection_type,
                "operator": "between",
                "minDefaultValue": self.min_value,
                "maxDefaultValue": self.max_value
            },
            "id": self.id,
            "name": "Date Selector (1)",
            "caption": self.label,
            "showLastUpdate": True,
            "noDataVerticalAlignment": "middle",
            "showCaptionWhenNoData": True,
            "showDescriptionWhenNoData": True
        }


class NumberSelector(object):

    def __init__(self, range=False, display_type="spinner"):
        """
        Creates a Number Selector widget for Side Panel or Header.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        range                       Optional boolean. True to create a range
                                    selector.
        -------------------------   -------------------------------------------
        display_type                Optional Portal Item. Item is required for
                                    categories from "spinner", "slider", "input".
        =========================   ===========================================
        """

        self._json = {}
        self._display_type = display_type
        self.type = "categorySelectorWidget"
        self.id = str(uuid.uuid4())
        self._label = ""
        self._increment = 1
        self._lower_limit = 0
        self._upper_limit = 100
        self._lower_default = 0
        self._upper_default = 100
        self._range = range
        self._operator = "equal"

        self._left_placeholder_text = ""
        self._right_placeholder_text = ""

        self._dataset = None
        self._operator_mapping = {
            "equal": "equal",
            "not equal": "not_equal",
            "greater than": "greater",
            "greater than or equal": "greater_or_equal",
            "less than": "less",
            "less than or equal": "less_or_equal"
        }

        self._constraint = {
            "type": "fixed",
            "lowerLimit": self._lower_limit,
            "upperLimit": self._upper_limit,
            "firstDefault": self._lower_default,
            "secondDefault": self._upper_default
        }

    @property
    def label(self):
        """
        :return: Label for the selector
        """
        return self._label

    @label.setter
    def label(self, value):
        """
        Set label for the selector.
        """
        self._label = value

    @property
    def placeholder_text(self):
        """
        :return: Text for left place holder in range type or default place holder.
        """
        return self._left_placeholder_text

    @placeholder_text.setter
    def placeholder_text(self, value):
        """
        Text for left place holder in range type or default place holder.
        """
        self._left_placeholder_text = value

    @property
    def right_placeholder_text(self):
        """
        :return: Text for right place holder in range type.
        """
        return self._right_placeholder_text

    @right_placeholder_text.setter
    def right_placeholder_text(self, value):
        """
        Text for right place holder in range type.
        """
        self._right_placeholder_text = value

    @property
    def operator(self):
        """
        :return: Operator for non range input.
        """
        return self._operator

    @operator.setter
    def operator(self, value):
        """
        :return: Set operator for non range input.
        """
        self._operator = self._operator_mapping.get(value, "equal")

    def set_limits(self, item, field, default="min"):
        """
        Set the item to pick values from for spinner and slider display type.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        item                        Required Portal Item. Item to pick values from.
        -------------------------   -------------------------------------------
        field                       Required String. Field from the Portal Item.
        -------------------------   -------------------------------------------
        default                     Optional String. Default value statistic.
                                    Options: "min", "max", "avg"
        =========================   ===========================================
        """

        self._dataset = {
            "type": "serviceDataset",
            "dataSource": {
                "type": "featureServiceDataSource",
                "itemId": item.itemid,
                "layerId": 0,
                "table": True
            },
            "outFields": ["*"],
            "groupByFields": [],
            "orderByFields": [],
            "statisticDefinitions": [
                {"onStatisticField": field, "outStatisticFieldName": "lowerLimit",
                 "statisticType": "min"},
                {"onStatisticField": field, "outStatisticFieldName": "upperLimit",
                 "statisticType": "max"},
                {"onStatisticField": field, "outStatisticFieldName": "averageStatisticValue",
                 "statisticType": "avg"}
            ],
            "maxFeatures": 50,
            "querySpatialRelationship": "esriSpatialRelIntersects",
            "returnGeometry": False,
            "clientSideStatistics": False,
            "name": "main"
        }

        self._constraint = {"type": "statistic", "defaultStatistic": "min"}

        if default in ["min", "max", "avg"]:
            self._constraint["defaultStatistic"] = default

    @property
    def lower_limit(self):
        """
        :return: Returns the minimum lower value allowed.
        """
        return self._lower_limit

    @lower_limit.setter
    def lower_limit(self, value):
        """
        Set lower limit of the selector.
        """
        self._lower_limit = value
        self._constraint = {
            "type": "fixed",
            "lowerLimit": self._lower_limit,
            "upperLimit": self._upper_limit,
            "firstDefault": self._lower_default,
            "secondDefault": self._upper_default
        }

    @property
    def upper_limit(self):
        """
        :return: Returns the maximum value allowed for spinner and slider.
        """
        return self._upper_limit

    @upper_limit.setter
    def upper_limit(self, value):
        """
        Set maximum limit of the selector for spinner and slider.
        """
        self._upper_limit = value
        self._constraint = {
            "type": "fixed",
            "lowerLimit": self._lower_limit,
            "upperLimit": self._upper_limit,
            "firstDefault": self._lower_default,
            "secondDefault": self._upper_default
        }

    @property
    def lower_default(self):
        """
        :return: Returns the left placeholder default value.
        """
        return self._lower_default

    @lower_default.setter
    def lower_default(self, value):
        """
        Set left placeholder default of the selector.
        """
        self._lower_default = value
        self._constraint = {
            "type": "fixed",
            "lowerLimit": self._lower_limit,
            "upperLimit": self._upper_limit,
            "firstDefault": self._lower_default,
            "secondDefault": self._upper_default
        }

    @property
    def upper_default(self):
        """
        :return: Returns the right placeholder default value for range.
        """
        return self._upper_default

    @upper_default.setter
    def upper_default(self, value):
        """
        Set right placeholder default of the selector for range.
        """
        self._upper_default = value
        self._constraint = {
            "type": "fixed",
            "lowerLimit": self._lower_limit,
            "upperLimit": self._upper_limit,
            "firstDefault": self._lower_default,
            "secondDefault": self._upper_default
        }

    @property
    def increment_factor(self):
        """
        :return: Increment factor of the selector for spinner and slider.
        """
        return self._increment

    @increment_factor.setter
    def increment_factor(self, value):
        """
        Set increment factor of the selector for spinner and slider.
        """
        self._increment = value

    def _convert_to_json(self):
        json = {
            "type": "numericSelectorWidget",
            "displayType": self._display_type,
            "increment": self._increment,
            "valueLabelFormat": {"name": "value", "type": "decimal", "prefix": False, "pattern": "#,###"},
            "selection": {"type": "single" if not self._range else "range"},
            "datasets": [],
            "id": self.id,
            "name": "Number Selector (1)",
            "caption": self._label,
            "showLastUpdate": True,
            "noDataVerticalAlignment": "middle",
            "showCaptionWhenNoData": True,
            "showDescriptionWhenNoData": True
        }

        if not self._range:
            json['selection']['operator'] = self._operator

        if self._constraint:
            json["constraint"] = self._constraint

        if self._display_type == "input":
            json['selection']['placeholderText'] = self._left_placeholder_text
            if self._range:
                json['selection']['rightPlaceHolderText'] = self._right_placeholder_text

        if self._dataset:
            json["datasets"].append(self._dataset)

        return json


class CategorySelector(object):

    def __init__(self):
        """
        Creates a Category Selector widget for Side Panel or Header.
        """

        self._categories_from = 'static'

        self.id = str(uuid.uuid4())
        self._selector = CategorySelectorProperties._create_selector_properties()

        self._dataset = None

    def set_defined_values(self, key_value_pairs, value_type="string"):
        """
        Set defined values for the dropdown.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        key_value_pairs             Optional list of tuples. The tuple should
                                    contain labels and their corresponding values.
        -------------------------   -------------------------------------------
        value_type                  Optional String.
                                    The data type of the values in the tuple.
                                    "integer" or "string
        =========================   ===========================================
        """
        type_caster = str
        self._categories_from = "static"
        if value_type == "integer":
            type_caster = int

        if value_type not in ["string", "integer"]:
            value_type = "string"

        self._dataset = {
            "type":"staticDataset",
            "data": {
                "type": "staticValues",
                "dataType": value_type,
                "values": []
            },
            "name": "main"
        }

        id = 0
        for pair in key_value_pairs:
            self._dataset['data']['values'].append({
                "type":" labelledValue",
                "id": str(id),
                "label": pair[0],
                "value": type_caster(pair[1])
            })
            id = id + 1

    def set_feature_options(self, item, line_item_text="", max_features=50):
        """
        Set feature values for dropdown.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        item                        Required Portal Item.
                                    Dropdown values will be populated from this.
        -------------------------   -------------------------------------------
        line_item_text              Optional String.
                                    This text will be displayed with options.
        -------------------------   -------------------------------------------
        max_features                Optional Integer.
                                    Set max features to display.
        =========================   ===========================================
        """
        self._categories_from = "features"

        self._line_item_text = line_item_text

        self._dataset = {
            "type": "serviceDataset",
            "dataSource": {
                "type": "featureServiceDataSource",
                "itemId": item.itemid,
                "layerId": 0,
                "table": True
            },
            "outFields": ["*"],
            "groupByFields": [],
            "orderByFields": [],
            "statisticDefinitions": [],
            "maxFeatures": max_features,
            "querySpatialRelationship": "esriSpatialRelIntersects",
            "returnGeometry": False,
            "clientSideStatistics": False,
            "name": "main"
        }

    def set_group_by_values(self, item, category_field, max_features=50):
        """
        Set group by values for dropdown.

        =========================   ===========================================
        **Argument**                **Description**
        -------------------------   -------------------------------------------
        item                        Required Portal Item.
                                    Dropdown values will be populated from this.
        -------------------------   -------------------------------------------
        category_field              Optional String.
                                    This
        -------------------------   -------------------------------------------
        max_features                Optional Integer.
                                    Set max features to display.
        =========================   ===========================================
        """
        self._categories_from = "groupByValues"

        self._dataset = {
            "type": "serviceDataset",
            "dataSource": {
                "type": "featureServiceDataSource",
                "itemId": item.itemid,
                "layerId": 0,
                "table": True
            },
            "outFields": ["*"],
            "groupByFields": [category_field],
            "orderByFields": [category_field + " asc"],
            "statisticDefinitions": [
                {
                    "onStatisticField": category_field,
                    "outStatisticFieldName": "count_result",
                    "statisticType": "count"
                }
            ],
            "maxFeatures": max_features,
            "querySpatialRelationship": "esriSpatialRelIntersects",
            "returnGeometry": False,
            "clientSideStatistics": False,
            "name": "main"
        }

    @property
    def selector(self):
        """
        :return: Selector Properties Object, set label, preferred display, display threshold, operator etc.
        """
        return self._selector

    def _convert_to_json(self):
        json = {
            "type": "categorySelectorWidget",
            "category": {},
            "selection": {"type": self._selector._selection_type, "defaultSelection": "0", "operator": self._selector._operator},
            "preferredDisplayType": self._selector._preferred_display, #dropdown, button_bar, radio_buttons
            "displayThreshold": self._selector._display_threshold,
            "datasets": [],
            "id": self.id,
            "name": "Category Selector (1)",
            "caption": self._selector._label,
            "showLastUpdate": True,
            "noDataVerticalAlignment": "middle",
            "showCaptionWhenNoData": True,
            "showDescriptionWhenNoData": True
        }

        if self._selector._none_option:
            json["noneLabelPlacement"] = self._selector._none_placement
            json["noneLabel"] = self._selector._none_label

        if self._categories_from == "static":
            json["category"] = {"type": "static"}
        elif self._categories_from == "features":
            json["category"] = {"type": "features", "itemText": self._line_item_text}
        elif self._categories_from == "groupByValues":
            json["category"] = {"type": "groupByValues", "nullLabel": "Null", "blankLabel": "Blank", "labelOverrides": []}

        if self._dataset:
            json["datasets"].append(self._dataset)

        return json


class CategorySelectorProperties(object):

    @classmethod
    def _create_selector_properties(cls):
        selector = cls()
        selector._preferred_display = "dropdown"
        selector._default_selection = 0
        selector._label = ""
        selector._selection_type = "single"
        selector._operator = "equal"
        selector._display_threshold = 10

        selector._none_option = False
        selector._none_placement = "first"
        selector._none_label = "None"

        return selector

    @property
    def preferred_display(self):
        """
        :return: Preferred display for the selector.
        """
        return self._preferred_display

    @preferred_display.setter
    def preferred_display(self, value):
        """
        Set preferred display from "dropdown", "button_bar" or "radio_buttons"
        """
        if value not in ["dropdown", "button_bar", "radio_buttons"]:
            raise Exception("Invalid preferred display")

        self._preferred_display = value

    @property
    def label(self):
        """
        :return: Label Text
        """
        return self._label

    @label.setter
    def label(self, value):
        """
        Set label text.
        """
        self._label = value

    @property
    def multiple_selection(self):
        """
        :return: True or False for multiple selection
        """
        if self._selection_type == "single":
            return False

        return True

    @multiple_selection.setter
    def multiple_selection(self, value):
        """
        Set selection type to True or False.
        """
        if value:
            self._selection_type = "multiple"
            if self._operator == "equal":
                self._operator = "is_in"
            elif self._operator == "not_equal":
                self._operator = "is_not_in"
        else:
            self._selection_type = "single"
            if self._operator == "is_in":
                self._operator = "equal"
            elif self._operator == "is_not_in":
                self._operator = "not_equal"

    @property
    def include_values(self):
        """
        :return: True if values selected are to be taken.
        """
        if self._operator in ["is_in", "equal"]:
            return True

        return False

    @include_values.setter
    def include_values(self, value):
        """
        Set True to take selected values, False to take unselected values.
        """
        if value:
            if self._selection_type == "multiple":
                self._operator = "is_in"
            else:
                self._operator = "equal"
        else:
            if self._selection_type == "multiple":
                self._operator = "is_not_in"
            else:
                self._operator = "not_equal"

    @property
    def display_threshold(self):
        """
        :return: Return display threshold.
        """
        return self._display_threshold

    @display_threshold.setter
    def display_threshold(self, value):
        """
        Set Dropdown display threshold
        """
        self._display_threshold = value

    @property
    def none(self):
        """
        :return: Label for None option if set else None.
        """
        return self._none_label if self._none_option == True else None

    @none.setter
    def none(self, value):
        """
        Set Label for None option. Set None to disable
        """
        if value is None:
            self._none_option = False
            self._none_label = ""
        else:
            self._none_option = True
            self._none_label = value

    @property
    def none_placement(self):
        """
        :return: None Placement "first" or "last".
        """
        return self._none_placement

    @none_placement.setter
    def none_placement(self, value):
        """
        Set none option placement to "first" or "last".
        """

        if value not in ["first", "last"]:
            raise Exception("Invalid value")

        self._none_placement = value

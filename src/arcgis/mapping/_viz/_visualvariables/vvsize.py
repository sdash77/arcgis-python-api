class SizeVariable(object):
    _type = "sizeInfo"
    _valueExpression = None
    _valueTitle = None
    _valueUnit = "unknown"
    _field = None
    _maxDataValue = 100#9223372036854775807
    _maxSize = 40
    _minDataValue = 0#-9223372036854775808
    _min_size = 1
    _normalizationField = None
    _stops = None
    _target = None
    def __init__(self, expression=None, field=None, stops=None):
        self._valueExpression = expression
        self._field = field
        self._stops = stops
    @property
    def expression(self):
        """
        An Arcade expression evaluating to a number
        """
        return self._valueExpression
    @expression.setter
    def expression(self, expression):
        """
        An Arcade expression evaluating to a number
        """
        if expression is None:
            expression = ""
        self._valueExpression = expression
    @property
    def field(self):
        """
        Get/Sets the data field to reference for size

        :returns: string
        """
        return self._field
    @field.setter
    def field(self, field):
        """
        Get/Sets the data field to reference for size
        """
        self._field = field
    @property
    def unit(self):
        """
        Get/Sets the data field value's unit

        :returns: string
        """
        return self._valueUnit
    @unit.setter
    def unit(self, unit):
        """
        Get/Sets the data field value's unit
        """
        self._valueUnit = unit
    @property
    def min_data(self):
        """
        The minimum data value
        """
        return self._minDataValue
    @min_data.setter
    def min_data(self, data):
        """
        The minimum data value
        """
        self._minDataValue = data
    @property
    def max_data(self):
        """
        The maximum data value.
        """
        return self._maxDataValue
    @max_data.setter
    def max_data(self, data):
        """
        The maximum data value.
        """
        self._maxDataValue = data

    @property
    def min_size(self):
        """
        Specifies the smallest marker size to use at any given map scale
        """
        return self._min_size
    @min_size.setter
    def min_size(self, size):
        """
        Specifies the smallest marker size to use at any given map scale
        """
        self._min_size = size
    @property
    def max_size(self):
        """
        Specifies the largest marker size to use at any given map scale
        """
        return self._maxSize
    @max_size.setter
    def max_size(self, size):
        """
        Specifies the largest marker size to use at any given map scale
        """
        self._maxSize = size
    @property
    def stops(self):
        """Returns the Stops for each size"""
        return self._stops
    def add_stop(self, size, value):
        """appends a new stop to the stops list"""
        if self._stops is None:
            self._stops = []
        self._stops.append({
          "value": value,
          "size": size
        })
        return True
    def remove_stop(self, size):
        """Removes a stop based on it's size"""
        if self._stops is None:
            self._stops = []
        self._size = [s for s in self._stops if s['size'] != size]
        return True
    def _to_dict(self):
        """returns the value as a dictionary"""
        if self.expression or (self.stops and self.field):
            v = {
                 "type": "sizeInfo",
                 "field": self.field or "",
                 "valueUnit": self.unit,
                 "stops": self.stops or [],
                 "minSize": self.min_size,
                 "maxSize": self.max_size,
                 "minDataValue": self.min_data,
                 "maxDataValue": self.max_data,
                 'valueExpression' : self.expression or ""
             }
            return v
        elif (self.stops is None or (isinstance(self.stops, list) and \
             len(self.stops) == 0)) and self.field:
            v = {
                 "type": "sizeInfo",
                 "field": self.field or "",
                 "valueUnit": self.unit,
                 "minSize": self.min_size,
                 "maxSize": self.max_size,
                 "minDataValue": self.min_data,
                 "maxDataValue": self.max_data,
                 'valueExpression' : self.expression or ""
             }
            return v
        else:
            return None





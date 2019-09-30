class TransparencyVariable(object):
    """
    The transparency visual variable defines the transparency, or opacity,
    of each feature's symbol based on a numeric attribute field value.


    field	Attribute field used for setting the transparency of a feature if no valueExpression is provided.
    legendOptions	Options available for the legend.
    normalizationField	Attribute field used to normalize the data.
    stops	An array of transparencyStop objects.
    valueExpression	An Arcade expression evaluating to a number.
    valueExpressionTitle	The title identifying and describing the associated Arcade expression as defined in the valueExpression property.
    """
    _type = "transparencyInfo"
    _field = None
    _legendOptions = None
    _normalizationField = None
    _stops = None
    _expression = None
    _title = None
    def __init___(self):
        """initializer"""
        self._type = "transparencyInfo"
    #----------------------------------------------------------------------
    @property
    def expression(self):
        """
        An Arcade expression evaluating to a number.
        """
        return self._expression
    @expression.setter
    def expression(self, arcade):
        """
        An Arcade expression evaluating to a number.
        """
        self._expression = arcade
    #----------------------------------------------------------------------
    @property
    def normalization(self):
        """
        Attribute field used to normalize the data.
        """
        return self._normalizationField
    @normalization.setter
    def normalization(self, field):
        """
        Attribute field used to normalize the data.
        """
        self._normalizationField = field
    #----------------------------------------------------------------------
    @property
    def field(self):
        """
        Attribute field used for setting the transparency of a feature if no expression is provided.
        """
        return self._field
    @field.setter
    def field(self, field):
        """
        Attribute field used for setting the transparency of a feature if no expression is provided.
        """
        self._field = field
    #----------------------------------------------------------------------
    @property
    def stops(self):
        """An array of transparencyStop objects."""
        return self._stops
    def add_stop(self, transparency, value, label=None):
        """Adds a stop to the transparency array"""
        if self._stops is not None:
            self._stops.append(
                {
                    "value": value,
                    "transparency": transparency,
                    "label" : label or ""
                }
            )
        else:
            self._stops = [{
                "value": value,
                "transparency": transparency,
                "label" : label or ""
            }]
    def clear_stops(self):
        """removes all stops in the transparency array"""
        self._stops = None
    def remove_stop(self, value):
        """Deletes a stop to the transparency array"""
        vals = [s['value'] for s in self._stops]
        if value in vals:
            idx = vals.index(value)
            self._stops.pop(idx)
    def _to_dict(self):
        """returns the value as a dictionary"""
        if self.expression or (self.stops and self.field):
            v = {
                 "type": self._type,
                 "field": self.field or "",
                 "normalizationField": self.normalization or "",
                 "stops": self.stops,
                 'valueExpressionTitle' : self._title or "",
                 'valueExpression' : self.expression or ""
             }
            return v
        elif (self.stops is None or len(self.stops) == 0) and \
             self.field:
            v = {
                 "type": self._type,
                 "field": self.field,
                 "normalizationField": self.normalization or "",
                 'valueExpressionTitle' : self._title or "",
                 'valueExpression' : self.expression or ""
             }
            return v
        else:
            return None










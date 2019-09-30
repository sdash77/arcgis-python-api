class RotationVariable(object):
    """
    The rotation visual variable defines how features rendered with marker symbols are rotated.
    """
    _field = None
    _rotationType = "geographic"
    _type = "rotationInfo"
    _expression = None

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self._rotationType = "geographic"
        self._type = "rotationInfo"
    #----------------------------------------------------------------------
    @property
    def field(self):
        """
        Attribute field used for setting the rotation of a symbol if no `expression` is provided.
        """
        return self._field
    #----------------------------------------------------------------------
    @field.setter
    def field(self, field):
        """
        Attribute field used for setting the rotation of a symbol if no `expression` is provided.
        """
        self._field = field
    #----------------------------------------------------------------------
    @property
    def rotation(self):
        """
        Defines the origin and direction of rotation depending on how the angle
        of rotation was measured. Possible values are geographic which rotates
        the symbol from the north in a clockwise direction and arithmetic which
        rotates the symbol from the east in a counter-clockwise direction.

        It must be one of the following values:

            + geographic
            + arithmetic


        """
        return self._rotationType
    #----------------------------------------------------------------------
    @rotation.setter
    def rotation(self, method):
        """
        Defines the origin and direction of rotation depending on how the angle
        of rotation was measured. Possible values are geographic which rotates
        the symbol from the north in a clockwise direction and arithmetic which
        rotates the symbol from the east in a counter-clockwise direction.

        It must be one of the following values:

            + geographic
            + arithmetic


        """
        if method.lower() in ['geographic', 'arithmetic']:
            self._rotationType = method
        elif method is None:
            self._rotationType = None
    #----------------------------------------------------------------------
    @property
    def expression(self):
        """
        An Arcade expression evaluating to a number.
        """
        return self._expression
    #----------------------------------------------------------------------
    @expression.setter
    def expression(self, arcade):
        """
        An Arcade expression evaluating to a number.
        """
        self._expression = arcade
    #----------------------------------------------------------------------
    def _to_dict(self):
        if self._rotationType and self.field:
            v = {
                "type": "rotationInfo",
                "rotationType": self.rotation,
                "field": self._field or "",
            }
            return v
        elif self._rotationType and self.expression:
            v = {
                "type": "rotationInfo",
                "rotationType": self.rotation,
                "valueExpression" : self.expression
            }
            return v
        return None
import json
from ._symbol._simple import SimpleFill, SimpleLine, SimpleMarker
from ._base import _Renderer
from ._visualvariables import SizeVariable, TransparencyVariable, RotationVariable

class SimpleRenderer(_Renderer):
    """
    
    A simple renderer is a renderer that uses one symbol only.
    
    """
    _type = "simple"
    _symbol = None
    _label = None
    _description = None
    _rt = "arithmetic"
    _vv_rotation = None
    _vv_size = None
    _vv_transparency = None
    _expression = None
    _expression_title = None
    #----------------------------------------------------------------------
    def __init__(self, geometry_type, color=None, label=None, description=None):
        """initializer"""
        if color is None:
            color = 'red'
        self._description = description
        self._label = label

        if geometry_type.lower() in ["point", "multipoint"]:
            symbol = SimpleMarker(color=color)
        elif geometry_type.lower() in ['polygon']:
            symbol = SimpleFill(color=color)
        elif geometry_type.lower() in ['polyline', 'line']:
            symbol = SimpleLine(color=color)
        self._symbol = symbol

        self._dict = {
            "type" : self._type,
            "symbol" : symbol._to_dict(),
            "visualVariables" : [],
            "label" : self._label or "",
            "description" : self._description or "",

        }
        self._vv_color = None
        self._vv_rotation = None
        self._vv_size = None
        self._vv_transparency = None

    #----------------------------------------------------------------------
    @property
    def expression(self):
        """An Arcade expression evaluating to either a string or a number."""
        return self._expression
    @expression.setter
    def expression(self, expression):
        """An Arcade expression evaluating to either a string or a number."""
        self._expression = expression
    #----------------------------------------------------------------------
    @property
    def expression_title(self):
        """The title identifying and describing the associated Arcade expression as defined in the expression property."""
        return self._expression_title
    @expression_title.setter
    def expression_title(self, title):
        """The title identifying and describing the associated Arcade expression as defined in the expression property."""
        self._expression_title = title
    #----------------------------------------------------------------------
    def add_transparency_variable(self, field=None, expression=None, stops=None):
        """
        Defines the transparency for the renderer.

        """
        self._vv_transparency = TransparencyVariable()
        if field is None and expression is None:
            raise ValueError("A field or expression must be provided in order to use `opacity_variable`")
        if field:
            self._vv_transparency.field = field
        if expression:
            self._vv_transparency.expression = expression
        self._vv_transparency.stops = stops
    @property
    def transparency_variable(self):
        """Gets/Sets the Transparency Visual Variable"""
        if self._vv_transparency is None:
            self._vv_transparency = TransparencyVariable()
        return self._vv_transparency
    @transparency_variable.setter
    def transparency_variable(self, trans):
        """Gets/Sets the Transparency Visual Variable"""
        if isinstance(trans, TransparencyVariable):
            self._vv_transparency = trans
        elif trans is None:
            self._vv_transparency = TransparencyVariable()
        else:
            raise ValueError("Input must be of type `TransparencyVariable`")
    #----------------------------------------------------------------------
    def add_size_variable(self, field=None, expression=None):
        """
        Defines how size is applied to features based on the values of a
        numeric field attribute. The minimum and maximum values of the
        data should be indicated along with their respective size values.

        :returns: Boolean

        """
        if field is None and expression is None:
            raise ValueError("A field or expression must be specified inorder to use `size_variable`")
        if self._vv_size is None:
            from ._visualvariables.vvsize import SizeVariable
            self._vv_size = SizeVariable(expression=expression, field=field)
            return True
        return False
    @property
    def size_variable(self):
        """Gets/Sets the Size Visual Variable"""
        if self._vv_size is None:
            self._vv_size = SizeVariable()
        return self._vv_size
    @size_variable.setter
    def size_variable(self, size):
        """Gets/Sets the Size Visual Variable"""
        if isinstance(size, SizeVariable) or size is None:
            self._vv_size = size
        else:
            raise ValueError("Input must be of type `SizeVariable`")
    #----------------------------------------------------------------------
    @property
    def rotation_variable(self):
        """
        Defines how features rendered with marker symbols are rotated
        """
        if self._vv_rotation is None:
            self._vv_rotation = RotationVariable()
        return self._vv_rotation
    @rotation_variable.setter
    def rotation_variable(self, rotation):
        """
        Defines how features rendered with marker symbols are rotated
        """
        if isinstance(rotation, RotationVariable):
            self._vv_rotation = rotation
        elif rotation is None:
            self._vv_rotation = RotationVariable()
        else:
            raise ValueError("The `rotation` must be of type RotationVariable")
    #----------------------------------------------------------------------
    @property
    def symbol(self):
        """
        gets/sets the symbol
        """
        return self._symbol
    #----------------------------------------------------------------------
    @symbol.setter
    def symbol(self, symbol):
        """gets/sets the symbol"""
        self._symbol = symbol
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """returns the renderer as JSON"""
        return self._to_dict()
    #----------------------------------------------------------------------
    @property
    def json(self):
        """returns the renderer as JSON"""
        return json.dumps(self._to_dict())
    #----------------------------------------------------------------------
    def _to_dict(self):
        """returns the renderer dictionary"""
        self._dict = {
            "type" : self._type,
            "symbol" : self.symbol._to_dict(),
            "visualVariables" : [],
            "label" : self._label or "",
            "labelingInfo" : None,
            "description" : self._description or ""
        }
        if self.expression:
            self._dict['valueExpression'] = self.expression
        if self._expression_title:
            self._dict['valueExpressionTitle'] = self._expression_title
        if self.size_variable and \
           self.size_variable._to_dict():
            self._dict['visualVariables'].append(self.size_variable._to_dict())
        if self.transparency_variable and \
           self.transparency_variable._to_dict():
            self._dict['visualVariables'].append(self.transparency_variable._to_dict())
        if self.rotation_variable and \
           self.rotation_variable._to_dict():
            self._dict['visualVariables'].append(self.rotation_variable._to_dict())
        if len(self._dict['visualVariables']) == 0:
            self._dict.pop('visualVariables')
        return self._dict
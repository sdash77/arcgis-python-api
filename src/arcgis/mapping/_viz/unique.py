from ._symbol import SimpleFill, SimpleLine, SimpleMarker
from ._base import _Renderer
from ._visualvariables import SizeVariable, TransparencyVariable, RotationVariable

from arcgis.features import FeatureSet, FeatureLayer, FeatureCollection
from arcgis._impl.common._mixins import PropertyMap
import pandas as pd
import itertools, json

###########################################################################
def _cmap2rgb(colors, step, alpha=1):
    """converts a color map to RGBA list"""
    from matplotlib import cm
    t = getattr(cm, colors)(step, bytes=True)
    t = [int(i) for i in t]
    t[-1] = alpha * 255
    return t
###########################################################################
def _breaks(gt, cmap, n, alpha=1, ):
    """calculates the breaks in the number line"""
    step_size = 256 // n
    colors = []
    for i in range(n):
        color = list(_cmap2rgb(colors=cmap, step=i * step_size, alpha=alpha))
        if gt in ['point', 'multipoint']:
            yield SimpleMarker(color=color)
        elif gt in ['line', 'polyline']:
            yield SimpleLine(color=color)
        elif gt in ['fill', 'polygon']:
            yield SimpleFill(color=color)

###########################################################################
class UniqueRenderer(_Renderer):
    """
    This renderer symbolizes features based on one or more matching string attributes.
    """
    _field1 = None
    _field2 = None
    _field3 = None
    _default_label = None
    _default_symbol = None
    _delimiter = None
    _vv_rotation = None
    _vv_size = None
    _vv_transparency = None
    _type = "uniqueValue"
    _unique_infos = None
    _expression = None
    _expression_title = None
    _rotation_type = None
    _rotation_expression = None
    _unique_value_info = None
    _cmap = None
    _max_values = None
    _background_symbol = None
    _geometry_type = None
    _gt = None
    _title = None
    _expression = None
    _expression_title = None

    #----------------------------------------------------------------------
    def __init__(self, geometry_type,
                 data, field1,
                 field2=None, field3=None,
                 cmap='jet'):
        """Constructor"""
        self._gt = geometry_type.lower()
        if geometry_type.lower() in  ["point", "multipoint"]:
            self._default_symbol = SimpleMarker()
        elif geometry_type.lower() in  ["polyline", "line"]:
            self._default_symbol = SimpleLine()
        else:
            self._default_symbol = SimpleFill()
        self._data = data
        self._cmap = cmap
        self.fields = field1, field2, field3
        self._calculate_unique_colors()

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
        else:
            raise ValueError("The `rotation` must be of type RotationVariable")
    #----------------------------------------------------------------------
    @property
    def default_symbol(self):
        """
        gets/sets the default symbol
        
        ===============  ==================================================
        **Arguement**    **Description**
        ---------------  --------------------------------------------------
        symbol           Required Symbol.  This default symbol for the renderer.
        ===============  ==================================================
        
        """
        return self._default_symbol
    #----------------------------------------------------------------------
    @default_symbol.setter
    def default_symbol(self, symbol):
        """
        gets/sets the default symbol
        
        ===============  ==================================================
        **Arguement**    **Description**
        ---------------  --------------------------------------------------
        symbol           Required Symbol.  This default symbol for the renderer.
        ===============  ==================================================
        
        """
        self._default_symbol = symbol
    #----------------------------------------------------------------------
    @property
    def background_symbol(self):
        """
        gets/sets the symbol.  This only applies to polygon geometries
        
        ===============  ==================================================
        **Arguement**    **Description**
        ---------------  --------------------------------------------------
        symbol           Required Symbol.  This symbol must be a polygon symbol.
        ===============  ==================================================
        
        :returns: Symbol or None
        
        """
        if self._gt.lower() == "polygon":
            return self._background_symbol
        return None
    #----------------------------------------------------------------------
    @background_symbol.setter
    def background_symbol(self, symbol):
        """
        gets/sets the symbol.  This only applies to polygon geometries
        
        
        ===============  ==================================================
        **Arguement**    **Description**
        ---------------  --------------------------------------------------
        symbol           Required Symbol.  This symbol must be a polygon symbol.
        ===============  ==================================================
        
        """
        if self._gt.lower() == "polygon":
            self._background_symbol = symbol
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """returns the renderer as JSON"""
        return self._to_dict()
    #----------------------------------------------------------------------
    @property
    def color_scheme(self):
        """gets/sets the number of stop breaks"""
        return self._cmap
    @color_scheme.setter
    def color_scheme(self, cmap):
        """gets/sets the number of stop breaks"""
        if cmap != self._cmap:
            self._cmap = cmap
            self._calculate_unique_colors()
    #----------------------------------------------------------------------
    @property
    def unique_values(self):
        """
        An list of unique color/value dictionaries to assist with renderering the data
        
        =============  ==================================================
        **keys**       **description**
        -------------  --------------------------------------------------
        description    String value used to describe the drawn symbol.
        -------------  --------------------------------------------------
        label	       String value used to label the drawn symbol.
        -------------  --------------------------------------------------
        symbol	       An object used to display the value.
        -------------  --------------------------------------------------
        value	       String value indicating the unique value.
        =============  ==================================================
        
        :returns: List
        
        """
        return self._unique_value_info
    @unique_values.setter
    def unique_values(self, values):
        """
        An list of unique color/value dictionaries to assist with renderering the data
        
        =============  ==================================================
        **keys**       **description**
        -------------  --------------------------------------------------
        description    String value used to describe the drawn symbol.
        -------------  --------------------------------------------------
        label	       String value used to label the drawn symbol.
        -------------  --------------------------------------------------
        symbol	       An object used to display the value.
        -------------  --------------------------------------------------
        value	       String value indicating the unique value.
        =============  ==================================================
        
        
        
        """
        self._unique_value_info = values
    #----------------------------------------------------------------------
    @property
    def fields(self):
        """Gets/Sets the classification fields"""
        return self._field1, self._field2, self._field3
    @fields.setter
    def fields(self, fields):
        """
        Gets/Sets the classification fields

        fields should be a list of strings
        """
        if isinstance(fields, str):
            self._field1 = fields
            self._field2 = None
            self._field3 = None
            self._calculate_unique_colors()
        elif isinstance(fields, (list, tuple)) and len(fields) == 1:
            self._field1 = fields[0]
            self._field2 = None
            self._field3 = None
            self._calculate_unique_colors()
        elif isinstance(fields, (list, tuple)) and len(fields) == 2:
            self._field1 = fields[0]
            self._field2 = fields[1]
            self._field3 = None
            self._calculate_unique_colors()
        elif isinstance(fields, (list, tuple)) and len(fields) == 3:
            self._field1 = fields[0]
            self._field2 = fields[1]
            self._field3 = fields[2]
            self._calculate_unique_colors()
        elif len(fields) > 3:
            raise ValueError("UniqueRenderer only accepts 3 classification fields")
    #----------------------------------------------------------------------
    def _calculate_unique_colors(self):
        '''calculates the color steps'''
        self._unique_value_info = []
        if isinstance(self._data, pd.DataFrame):
            counter = 0
            values = []
            unique_values = []
            if self._field1:
                values.append(self._data[self._field1].unique().tolist())
            if self._field2:
                values.append(self._data[self._field2].unique().tolist())
            if self._field3:
                values.append(self._data[self._field3].unique().tolist())
            perms = itertools.product(*values)
            n = len(list(perms))
            syms = _breaks(self._gt, self.color_scheme, n, alpha=1)
            for perm in itertools.product(*values):

                value = ','.join(map(str, perm))
                self._unique_value_info.append({ #PropertyMap(
                    "value" : value,
                    "label" : value,
                    "description" : "",
                    "symbol" : next(syms)
                })#)
            return self._unique_value_info
        elif isinstance(self._data, FeatureLayer):
            fields = ",".join([field for field in self.fields if field is not None])
            old = self._data
            self._data = self._data.query(where="1=1", out_fields=fields, as_df=True)
            self._calculate_unique_colors()
            self._data = old
        elif isinstance(self._data, FeatureSet):
            old = self._data
            self._data = self._data.sdf
            self._calculate_unique_colors()
            self._data = old
        else:
            return None
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """returns the renderer as JSON"""
        return self._to_dict()
    #----------------------------------------------------------------------
    def _to_dict(self):
        """returns the renderer dictionary"""
        import copy
        self._dict = {
            "type" : self._type,
            'backgroundFillSymbol' : self.background_symbol or None,
            "defaultLabel" :"",
            "defaultSymbol" : self.default_symbol._to_dict(),
            "field1" : self.fields[0],
            "fieldDelimiter" : ',',
            "uniqueValueInfos" : self.unique_values,
            "valueExpression" : self.expression or "",
            "valueExpressionTitle" : self._expression_title or "",
            "visualVariables" : []
        }
        copied = copy.deepcopy(self._dict['uniqueValueInfos'])
        for u in copied:
            u['symbol'] = u['symbol']._to_dict()
        self._dict["uniqueValueInfos"] = copied
        if self.fields[1]:
            self._dict["field2"]  = self.fields[1]
        if self.fields[2]:
            self._dict["field3"] = self.fields[2]

        if self._dict['backgroundFillSymbol'] is None:
            self._dict.pop('backgroundFillSymbol')
        elif isinstance(self._dict['backgroundFillSymbol'], (SimpleFill, SimpleLine, SimpleMarker)):
            self._dict['backgroundFillSymbol'] = self._dict['backgroundFillSymbol']._to_dict()
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




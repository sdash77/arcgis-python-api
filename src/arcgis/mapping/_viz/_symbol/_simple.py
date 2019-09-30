from ._color import color_lookup
###########################################################################
_POINT_STYLES = {
    "o" : "esriSMSCircle", #default
    "+" : "esriSMSCross",
    "d" : "esriSMSDiamond",
    "s" : "esriSMSSquare",
    "x" : "esriSMSX",
    #"^" : "esriSMSTriangle" # Does not render in web maps
}
###########################################################################
_LINE_STYLES = {
    's' : 'esriSLSSolid', # default
    '-' : 'esriSLSDash',
    '-.' : 'esriSLSDashDot',
    '-..' : 'esriSLSDashDotDot',
    '.' : 'esriSLSDot',
    '--' : "esriSLSLongDash",
    "--.": "esriSLSLongDashDot",
    'n' :  "esriSLSNull",
    's-' : "esriSLSShortDash",
    's-.' : "esriSLSShortDashDot",
    's-..' : "esriSLSShortDashDotDot",
    's.' : "esriSLSShortDot"
}
###########################################################################
_POLYGON_STYLES = {
    '\\' : "esriSFSBackwardDiagonal",
    "/" : "esriSFSForwardDiagonal",
    "|" : "esriSFSVertical",
    "-" : "esriSFSHorizontal",
    "x" : "esriSFSDiagonalCross",
    "+" : "esriSFSCross",
    "s" : "esriSFSSolid" # default
}
###########################################################################
class _BaseSymbol(object):
    _color = None
    #----------------------------------------------------------------------
    @property
    def alpha(self):
        return self._color[-1]
    @alpha.setter
    def alpha(self, value):
        if self._color is None:
            self.color = 'red'
        if value >= 1:
            value = 0
        elif value < 1 and value > 0:
            value = int(value * 255)
        elif value == 0:
            value = 255
        self._color[-1] = value
    #----------------------------------------------------------------------
    @property
    def color(self):
        if self._color is None:
            self.color = 'red'
        return self._color
    @color.setter
    def color(self, color):
        if isinstance(color, (tuple, list)) and len(color) == 4:
            self._color = list(color)
        elif isinstance(color, str):
            try:
                self._color = color_lookup(color)
            except:
                raise ValueError("Color %s not found, please use RGBA" % color )
        else:
            raise ValueError("Color %s not found, please use [R,G,B,A]" % color )
###########################################################################
class SimpleLine(_BaseSymbol):
    """Represents a Simple Marker Symbol"""
    _type = "esriSLS"
    _style = None
    _color = None
    _width = None
    def __init__(self, style='s', color='black', width=.75, alpha=.75):
        self._style = _LINE_STYLES[style]
        self._width = width
        self.color = color
        self.alpha = alpha
    #----------------------------------------------------------------------
    def __str__(self):
        return "<Line Symbol style: %s color: %s width: %s>" % (self._style, self._color, self._width)
    #----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()
    #----------------------------------------------------------------------
    @property
    def style(self):
        return self._style
    @style.setter
    def style(self, style):
        if style.lower() in _LINE_STYLES.keys():
            self._style = _LINE_STYLES[style.lower()]
    #----------------------------------------------------------------------
    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, width):
        if width >= 0:
            self._width = width
    #----------------------------------------------------------------------
    def _to_dict(self):
        """converts the object to a dictionary"""
        return {
            "type": self._type,
            "color": self.color,
            "width": self.width,
            "style": self.style
        }
###########################################################################
class SimpleMarker(_BaseSymbol):
    """Represents a Simple Marker Symbol"""
    _type = "esriSMS"
    _style = None
    _color = None
    _size = None
    outline = None
    _angle = 0
    _xoffset = 0
    _yoffset = 0

    def __init__(self, style='o', color='red', size=8, alpha=.75, outline='black'):
        self._style = _POINT_STYLES[style]
        self.size = size
        self.alpha = alpha
        self.outline = SimpleLine(color=outline, width=.75, alpha=alpha)
        self.color = color
    #----------------------------------------------------------------------
    def __str__(self):
        return "<Marker Symbol style: %s color: %s size: %s>" % (self._style, self._color, self._size)
    #----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()
    #----------------------------------------------------------------------
    @property
    def style(self):
        return self._style
    @style.setter
    def style(self, style):
        if style.lower() in _POINT_STYLES.keys():
            self._style = _POINT_STYLES[style.lower()]
    #----------------------------------------------------------------------
    @property
    def xoffset(self):
        return self._xoffset
    @xoffset.setter
    def xoffset(self, x):
        if x >= 0:
            self._xoffset = x
    #----------------------------------------------------------------------
    @property
    def yoffset(self):
        return self._yoffset
    @yoffset.setter
    def yoffset(self, y):
        if y >= 0:
            self._yoffset = y
    #----------------------------------------------------------------------
    @property
    def angle(self):
        return self._angle
    @angle.setter
    def angle(self, angle):
        if angle >= 0:
            self._angle = angle
    #----------------------------------------------------------------------
    @property
    def size(self):
        return self._size
    @size.setter
    def size(self, size):
        if size >= 0:
            self._size = size
    #----------------------------------------------------------------------
    def _to_dict(self):
        """converts the object to a dictionary"""
        return {
            "type": "esriSMS",
            "color": self.color,
            "angle": self.angle,
            "xoffset": self.xoffset,
            "yoffset": self.yoffset,
            "size": self.size,
            "style": self.style,
            "outline": self.outline._to_dict()
        }

###########################################################################
class SimpleFill(_BaseSymbol):
    """Simple Fill Symbol for Polygons"""
    _type = "esriSFS"
    _style = None
    _color = None
    _size = None
    _outline = None
    def __init__(self, style='s', color='yellow', outline='black', size=8, alpha=.75):
        self._style = _POLYGON_STYLES[style]
        self.outline = SimpleLine(color=outline, width=.75, alpha=alpha)
        self.alpha = alpha
        self.color = color
    #----------------------------------------------------------------------
    def __str__(self):
        return "<Fill Symbol style: %s color: %s size: %s>" % (self._style, self._color, self._size)
    #----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()
    #----------------------------------------------------------------------
    @property
    def style(self):
        return self._style
    @style.setter
    def style(self, style):
        if style.lower() in _POLYGON_STYLES.keys():
            self._style = _POLYGON_STYLES[style.lower()]
    #----------------------------------------------------------------------
    def _to_dict(self):
        return {
            "type": "esriSFS",
            "color": self.color,
            "outline": self.outline._to_dict(),
            "style": self.style
        }
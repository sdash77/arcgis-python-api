import copy
import json
from ._symbol._simple import SimpleFill, SimpleLine, SimpleMarker
from ._base import _Renderer
from ._visualvariables import SizeVariable, TransparencyVariable, RotationVariable
import pandas as pd
import numpy as np
#https://developers.arcgis.com/web-map-specification/objects/classBreaksRenderer/

_METHOD = {
    "Natural Breaks" : "esriClassifyNaturalBreaks",
    "Natural_Breaks" : "esriClassifyNaturalBreaks",
    "nb" : "esriClassifyNaturalBreaks",
    "Equal Interval" : "esriClassifyEqualInterval",
    "Equal_Interval" : "esriClassifyEqualInterval",
    "ei" : "esriClassifyEqualInterval",
    "Quantile" : "esriClassifyQuantile",
    "q" : "esriClassifyQuantile",
    "Standard Deviation" : "esriClassifyStandardDeviation",
    "Standard_Deviation" : "esriClassifyStandardDeviation",
    "std" : "esriClassifyStandardDeviation",
    "Manual" : "esriClassifyManual"
}
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
class _ClassBreaks(_Renderer):
    """
    Class Breaks Renderer Class
    """
    _type = 'classBreaks'
    _method = None
    _ramp = None
    _background_fill_symbol = None
    _number_breaks = None
    _breaks = None
    _min_value = None
    _max_value = None
    _normalize_field = None
    _norm_total = None
    _norm_type = None
    _expression = None
    _expression_title = None
    _vv_rotation = None
    _vv_size = None
    _vv_transparency = None
    _field = None
    _bins = None
    _alpha = 1
    def __init__(self, data, classes=5):
        self._data = data
        self._classes = classes
    #----------------------------------------------------------------------
    @property
    def alpha(self):
        """get/sets the transparency for a symbol"""
        return self._alpha
    @alpha.setter
    def alpha(self, a):
        """get/sets the transparency for a symbol"""
        if self._alpha != a and a >= 0 and a <= 1:
            self._alpha = a
        else:
            raise ValueError("Alpha should be between 0 and 1")
    #----------------------------------------------------------------------
    @property
    def bins(self):
        if self._bins is None:
            self._set_bins()
        return self._bins
    def _set_bins(self):
        raise NotImplementedError("Not Implemented on Base Class")
    @property
    def classes(self):
        """
        Gets/Sets the number of classes associated with the renderer
        :returns: Integer
        """
        return self._classes
    @classes.setter
    def classes(self, c:int):
        """
        Gets/Sets the number of classes associated with the renderer
        """
        assert isinstance(c, int)
        self._classes = c
        self._set_bins()

class ManualBreaksRenderer(_ClassBreaks):
    _field = None
    _type = "classBreak"
    default_symbol = None # default symbol
    _data = None
    _min_value = None
    _gt = None
    _bins = None
    _classes = None
    _class_break_info = None
    normalization_field = None
    def __init__(self, data, geometry_type, field, set_default_symbol=True):
        super().__init__(data=data, classes=None)
        if color_scheme is None:
            color_scheme = 'jet'
        self._cmap = color_scheme
        self.field = field
        self._gt = geometry_type
        self.data = data
        # default symbol
        if set_default_symbol:
            if geometry_type.lower() in ["point", "multipoint"]:
                symbol = SimpleMarker(color='gray')
            elif geometry_type.lower() in ['polygon']:
                symbol = SimpleFill(color='gray')
            elif geometry_type.lower() in ['polyline', 'line']:
                symbol = SimpleLine(color='gray')
            symbol.alpha = .6
            self.default_symbol = symbol
        self.classes = None
    #----------------------------------------------------------------------
    @property
    def class_breaks(self):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info is None or len(self._class_break_info) == 0:
            self._class_break_info = []
        return self._class_break_info
    @class_breaks.setter
    def class_breaks(self, value):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info != value and isinstance(value, (list, tuple)) and \
           any(isinstance(item, dict) for item in value):
            self.classes = len(value)
            self._class_break_info = list(value)
        elif self._class_break_info != value and isinstance(value, (list, tuple)):
            pass
            #if self._class_break_info is None:
                #self._class_break_info = []
                #bins = self.bins
                #symbols = [sym for sym in _breaks(gt=self._gt, cmap=self._cmap,
                                                          #n=len(bins), alpha=self.alpha ) if sym is not None]
                #for i in range(len(bins)):
                    #b = bins[i]
                    #if i == 0:
                        #self._class_break_info.append({
                                    #'symbol': symbols[i],
                                        #'label': '< %.3f' % float(b),
                                        #"classMaxValue" : float(b)
                                #})
                    #elif i == len(bins) - 1:
                        #self._class_break_info.append({
                                    #'symbol': symbols[i],
                                        #'label': '> %.3f' % float(b),
                                        #"classMinValue" : float(bins[i-1]),
                                        #"classMaxValue" : float(b)
                                #})
                    #else:
                        #self._class_break_info.append({
                                    #'symbol': symbols[i],
                                        #'label': '> %.3f -  %.3f' % (self._class_break_info[i-1]['classMaxValue'], float(b)),
                                        #"classMaxValue" : float(b)
                                #})
        else:
            raise ValueError("The `value` must be a list of")

    def add_class_break(self, label, min_val, max_val, symbol=None):
        {"classMinValue": min_val, "classMaxValue": max_val, "label": label}
        pass
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """returns the renderer"""
        return self._to_dict()
    #----------------------------------------------------------------------
    def _to_dict(self):
        """create the renderer internally"""
        cbi = copy.deepcopy(self.class_breaks)
        for cb in cbi:
            cb['symbol'] = cb['symbol']._to_dict()

        r =  {'authoringInfo': {'type': 'classedColor',
                                'classificationMethod': 'esriClassifyManual'},
                'type': self._type,
                'field': self.field,
                'minValue': self._min_value or None,
                'classBreakInfos': cbi,
                'classificationMethod': 'esriClassifyManual'}
        if self.default_symbol:
            r['defaultSymbol'] = self.default_symbol._to_dict()
        if self.normalization_field:
            r['normalizationField'] = self.normalization_field
        return r
###########################################################################
class NaturalBreaksRenderer(_ClassBreaks):
    """
    Classes are based on natural groupings inherent in the data. The Jenk's Algorithm
    identifies break points by picking the class breaks that best group similar
    values and maximize the differences between classes. The features are divided into
    classes whose boundaries are set where there are relatively big jumps in the data
    values.

    """
    _field = None
    _type = "classBreak"
    default_symbol = None # default symbol
    _data = None
    _min_value = None
    _gt = None
    _bins = None
    _classes = None
    _class_break_info = None
    normalization_field = None
    _cmap = None
    def __init__(self,
                 geometry_type:str,
                 data:pd.DataFrame,
                 field:str,
                 color_scheme:str=None,
                 classes:int=5,
                 set_default_symbol:bool=True):
        """Constructor"""
        super().__init__(data=data, classes=classes)
        if color_scheme is None:
            color_scheme = 'jet'
        self._cmap = color_scheme
        self.field = field
        self._gt = geometry_type
        self.data = data
        # default symbol
        if set_default_symbol:
            if geometry_type.lower() in ["point", "multipoint"]:
                symbol = SimpleMarker(color='gray')
            elif geometry_type.lower() in ['polygon']:
                symbol = SimpleFill(color='gray')
            elif geometry_type.lower() in ['polyline', 'line']:
                symbol = SimpleLine(color='gray')
            symbol.alpha = .6
            self.default_symbol = symbol
        self.classes = classes
    #----------------------------------------------------------------------
    @property
    def alpha(self):
        """get/sets the transparency for a symbol"""
        return self._alpha
    @alpha.setter
    def alpha(self, a):
        """get/sets the transparency for a symbol"""
        if self._alpha != a and a >= 0 and a <= 1:
            self._alpha = a
        else:
            raise ValueError("Alpha should be between 0 and 1")
    #----------------------------------------------------------------------
    @property
    def field(self):
        """get/sets the numeric field"""
        return self._field
    @field.setter
    def field(self, value):
        """get/sets the numeric field"""
        if self._field != value:
            self._field = value
    #----------------------------------------------------------------------
    @property
    def class_breaks(self):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info is None or len(self._class_break_info) == 0:
            self._calculate_breaks()
        return self._class_break_info
    @class_breaks.setter
    def class_breaks(self, value):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info != value and isinstance(value, (list, tuple)):
            self.classes = len(value)
            self._class_break_info = list(value)
    #----------------------------------------------------------------------
    @property
    def data(self):
        """get/sets the data value.  This should be a list, tuple, or pd.Series"""
        return self._data
    @data.setter
    def data(self, data):
        """get/sets the data value.  This should be a list, tuple, or pd.Series"""
        self._bins = None
        self._class_break_info = None
        if isinstance(data, (np.ndarray, list, tuple)):
            data = pd.Series(data)
        assert isinstance(data, (pd.DataFrame, pd.Series))
        self._data = data
        if isinstance(data, pd.DataFrame):
            self._min_value = data[self.field].min()
        else:
            self._min_value = data.min()
    #----------------------------------------------------------------------
    def _set_bins(self):
        """defines the class breaks bins for equal interval"""
        from ._alg import jenks
        self._bins = jenks(self.data, self.classes)

    #----------------------------------------------------------------------
    def _calculate_breaks(self):
        """calculates the quantile breaks"""
        if self._bins is None:
            self._set_bins()
        bins = self._bins
        self._class_break_info = copy.deepcopy(self._bins)
        symbols = [sym for sym in _breaks(gt=self._gt, cmap=self._cmap,
                                          n=len(bins), alpha=self.alpha ) if sym is not None]
        for i in range(self.classes):
            self._class_break_info[i]['symbol'] = symbols[i]
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """returns the renderer"""
        return self._to_dict()
    #----------------------------------------------------------------------
    def _to_dict(self):
        """create the renderer internally"""
        cbi = copy.deepcopy(self.class_breaks)
        for cb in cbi:
            cb['symbol'] = cb['symbol']._to_dict()

        r =  {'authoringInfo': {'type': 'classedColor',
                                'classificationMethod': 'esriClassifyNaturalBreaks'},
                'type': self._type,
                'field': self.field,
                'minValue': self._min_value or None,
                'classBreakInfos': cbi,
                'classificationMethod': 'esriClassifyNaturalBreaks'}
        if self.default_symbol:
            r['defaultSymbol'] = self.default_symbol._to_dict()
        if self.normalization_field:
            r['normalizationField'] = self.normalization_field
        return r
###########################################################################
class QuantileRenderer(_ClassBreaks):
    _field = None
    _type = "classBreak"
    default_symbol = None # default symbol
    _data = None
    _min_value = None
    _gt = None
    _bins = None
    _classes = None
    _class_break_info = None
    normalization_field = None
    _cmap = None
    def __init__(self,
                 geometry_type:str,
                 data:pd.DataFrame,
                 field:str,
                 color_scheme:str=None,
                 classes:int=5,
                 set_default_symbol:bool=True):
        """Constructor"""
        super().__init__(data=data, classes=classes)
        if color_scheme is None:
            color_scheme = 'jet'
        self._cmap = color_scheme
        self.field = field
        self._gt = geometry_type
        self.data = data
        # default symbol
        if set_default_symbol:
            if geometry_type.lower() in ["point", "multipoint"]:
                symbol = SimpleMarker(color='gray')
            elif geometry_type.lower() in ['polygon']:
                symbol = SimpleFill(color='gray')
            elif geometry_type.lower() in ['polyline', 'line']:
                symbol = SimpleLine(color='gray')
            symbol.alpha = .6
            self.default_symbol = symbol
        self.classes = classes
    #----------------------------------------------------------------------
    @property
    def alpha(self):
        """get/sets the transparency for a symbol"""
        return self._alpha
    @alpha.setter
    def alpha(self, a):
        """get/sets the transparency for a symbol"""
        if self._alpha != a and a >= 0 and a <= 1:
            self._alpha = a
        else:
            raise ValueError("Alpha should be between 0 and 1")
    #----------------------------------------------------------------------
    @property
    def field(self):
        """get/sets the numeric field"""
        return self._field
    @field.setter
    def field(self, value):
        """get/sets the numeric field"""
        if self._field != value:
            self._field = value
    #----------------------------------------------------------------------
    @property
    def class_breaks(self):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info is None or len(self._class_break_info) == 0:
            self._calculate_breaks()
        return self._class_break_info
    @class_breaks.setter
    def class_breaks(self, value):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info != value and isinstance(value, (list, tuple)):
            self.classes = len(value)
            self._class_break_info = list(value)
    #----------------------------------------------------------------------
    @property
    def data(self):
        """get/sets the data value.  This should be a list, tuple, or pd.Series"""
        return self._data
    @data.setter
    def data(self, data):
        """get/sets the data value.  This should be a list, tuple, or pd.Series"""
        self._bins = None
        self._class_break_info = None
        if isinstance(data, (np.ndarray, list, tuple)):
            data = pd.Series(data)
        assert isinstance(data, (pd.DataFrame, pd.Series))
        self._data = data
        if isinstance(data, pd.DataFrame):
            self._min_value = data[self.field].min()
        else:
            self._min_value = data.min()
    #----------------------------------------------------------------------
    def _set_bins(self):
        """defines the class breaks bins for equal interval"""
        from ._alg import quantiles
        self._bins = quantiles(self.data, self.classes)
    #----------------------------------------------------------------------
    def _calculate_breaks(self):
        """calculates the quantile breaks"""
        if self._bins is None:
            self._set_bins()
        bins = self._bins
        self._class_break_info = copy.deepcopy(self._bins)
        symbols = [sym for sym in _breaks(gt=self._gt, cmap=self._cmap,
                                          n=len(bins), alpha=self.alpha ) if sym is not None]
        for i in range(self.classes):
            self._class_break_info[i]['symbol'] = symbols[i]
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """returns the renderer"""
        return self._to_dict()
    #----------------------------------------------------------------------
    def _to_dict(self):
        """create the renderer internally"""
        cbi = copy.deepcopy(self.class_breaks)
        for cb in cbi:
            cb['symbol'] = cb['symbol']._to_dict()

        r =  {'authoringInfo': {'type': 'classedColor',
                                'classificationMethod': 'esriClassifyQuantile'},
                'type': self._type,
                'field': self.field,
                'minValue': self._min_value or None,
                'classBreakInfos': cbi,
                'classificationMethod': 'esriClassifyQuantile'}
        if self.default_symbol:
            r['defaultSymbol'] = self.default_symbol._to_dict()
        if self.normalization_field:
            r['normalizationField'] = self.normalization_field
        return r

###########################################################################
class StandardDeviationRenderer(_ClassBreaks):
    _field = None
    _type = "classBreak"
    default_symbol = None # default symbol
    _data = None
    _min_value = None
    _gt = None
    _bins = None
    classes = None
    _class_break_info = None
    normalization_field = None
    _cmap = None
    def __init__(self,
                 geometry_type:str,
                 data:pd.DataFrame,
                 field:str,
                 color_scheme:str=None,
                 classes:int=5,
                 set_default_symbol:bool=True):
        """Constructor"""
        super().__init__(data=data, classes=classes)
        if color_scheme is None:
            color_scheme = 'jet'
        self._cmap = color_scheme
        self.field = field
        self._gt = geometry_type
        self.data = data
        # default symbol
        if set_default_symbol:
            if geometry_type.lower() in ["point", "multipoint"]:
                symbol = SimpleMarker(color='gray')
            elif geometry_type.lower() in ['polygon']:
                symbol = SimpleFill(color='gray')
            elif geometry_type.lower() in ['polyline', 'line']:
                symbol = SimpleLine(color='gray')
            symbol.alpha = .6
            self.default_symbol = symbol
        self.classes = classes
    #----------------------------------------------------------------------
    @property
    def alpha(self):
        """get/sets the transparency for a symbol"""
        return self._alpha
    @alpha.setter
    def alpha(self, a):
        """get/sets the transparency for a symbol"""
        if self._alpha != a and a >= 0 and a <= 1:
            self._alpha = a
        else:
            raise ValueError("Alpha should be between 0 and 1")
    #----------------------------------------------------------------------
    @property
    def field(self):
        """get/sets the numeric field"""
        return self._field
    @field.setter
    def field(self, value):
        """get/sets the numeric field"""
        if self._field != value:
            self._field = value
    #----------------------------------------------------------------------
    @property
    def class_breaks(self):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info is None or len(self._class_break_info) == 0:
            self._calculate_breaks()
        return self._class_break_info
    @class_breaks.setter
    def class_breaks(self, value):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info != value and isinstance(value, (list, tuple)):
            self.classes = len(value)
            self._class_break_info = list(value)
    #----------------------------------------------------------------------
    @property
    def data(self):
        """get/sets the data value.  This should be a list, tuple, or pd.Series"""
        return self._data
    @data.setter
    def data(self, data):
        """get/sets the data value.  This should be a list, tuple, or pd.Series"""
        self._bins = None
        self._class_break_info = None
        if isinstance(data, (np.ndarray, list, tuple)):
            data = pd.Series(data)
        assert isinstance(data, (pd.DataFrame, pd.Series))
        self._data = data
        if isinstance(data, pd.DataFrame):
            self._min_value = data[self.field].min()
        else:
            self._min_value = data.min()
    #----------------------------------------------------------------------
    def _set_bins(self):
        """defines the class breaks bins for equal interval"""
        from ._alg import std
        self._bins = std(self.data)
    #----------------------------------------------------------------------
    def _calculate_breaks(self):
        """calculates the quantile breaks"""
        if self._bins is None:
            self._set_bins()
        bins = self._bins
        self._class_break_info = copy.deepcopy(self._bins)
        symbols = [sym for sym in _breaks(gt=self._gt, cmap=self._cmap,
                                          n=len(bins), alpha=self.alpha ) if sym is not None]
        for i in range(self.classes):
            self._class_break_info[i]['symbol'] = symbols[i]
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """returns the renderer"""
        return self._to_dict()
    #----------------------------------------------------------------------
    def _to_dict(self):
        """create the renderer internally"""
        cbi = copy.deepcopy(self.class_breaks)
        for cb in cbi:
            cb['symbol'] = cb['symbol']._to_dict()

        r =  {'authoringInfo': {'type': 'classedColor',
                                'classificationMethod': 'standard-deviation'},
                'type': self._type,
                'field': self.field,
                'minValue': self._min_value or None,
                'classBreakInfos': cbi,
                'classificationMethod': 'standard-deviation'}
        if self.default_symbol:
            r['defaultSymbol'] = self.default_symbol._to_dict()
        if self.normalization_field:
            r['normalizationField'] = self.normalization_field
        return r

###########################################################################
class EqualIntervalRenderer(_ClassBreaks):
    """
    The range of values is divided into equally sized classes where you
    specify the number of classes. Use this method to emphasize the
    relative amount of attribute values compared to other values. It is
    best applied to familiar data ranges such as percentages and temperature.
    """
    _field = None
    _type = "classBreak"
    default_symbol = None # default symbol
    _data = None
    _min_value = None
    _gt = None
    _bins = None
    _classes = None
    _class_break_info = None
    normalization_field = None
    def __init__(self,
                 geometry_type:str,
                 data:pd.DataFrame,
                 field:str,
                 color_scheme:str=None,
                 classes:int=5,
                 set_default_symbol:bool=True):
        """Constructor"""
        super().__init__(data=data, classes=classes)
        if color_scheme is None:
            self._cmap = 'jet'
        else:
            self._cmap = color_scheme
        self.field = field
        self._gt = geometry_type
        self.data = data
        # default symbol
        if set_default_symbol:
            if geometry_type.lower() in ["point", "multipoint"]:
                symbol = SimpleMarker(color='gray')
            elif geometry_type.lower() in ['polygon']:
                symbol = SimpleFill(color='gray')
            elif geometry_type.lower() in ['polyline', 'line']:
                symbol = SimpleLine(color='gray')
            symbol.alpha = .6
            self.default_symbol = symbol
        self.classes = classes
    #----------------------------------------------------------------------
    @property
    def alpha(self):
        """get/sets the transparency for a symbol"""
        return self._alpha
    @alpha.setter
    def alpha(self, a):
        """get/sets the transparency for a symbol"""
        if self._alpha != a and a >= 0 and a <= 1:
            self._alpha = a
        else:
            raise ValueError("Alpha should be between 0 and 1")
    #----------------------------------------------------------------------
    @property
    def field(self):
        """get/sets the numeric field"""
        return self._field
    @field.setter
    def field(self, value):
        """get/sets the numeric field"""
        if self._field != value:
            self._field = value
    #----------------------------------------------------------------------
    @property
    def class_breaks(self):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info is None or len(self._class_break_info) == 0:
            self._calculate_breaks()
        return self._class_break_info
    @class_breaks.setter
    def class_breaks(self, value):
        """get/sets the class breaks information associated with the renderer."""
        if self._class_break_info != value and isinstance(value, (list, tuple)):
            self.classes = len(value)
            self._class_break_info = list(value)
    #----------------------------------------------------------------------
    @property
    def data(self):
        """get/sets the data value.  This should be a list, tuple, or pd.Series"""
        return self._data
    @data.setter
    def data(self, data):
        """get/sets the data value.  This should be a list, tuple, or pd.Series"""
        series = pd.Series(data)
        self._data = series
        self._min_value = series.min()
    #----------------------------------------------------------------------
    def _set_bins(self):
        """defines the class breaks bins for equal interval"""
        y = self.data
        classes = self.classes
        max_y = max(y)
        min_y = min(y)
        rg = max_y - min_y
        width = rg * 1.0 / classes
        cuts = np.arange(min_y + width, max_y + width, width)
        if len(cuts) > self.classes:  # handle overshooting
            cuts = cuts[0:classes]
        cuts[-1] = max_y
        bins = cuts.copy()
        self._bins = bins
    #----------------------------------------------------------------------
    def _calculate_breaks(self):
        """calculates the equal iterval breaks"""
        if self._class_break_info is None:
            self._class_break_info = []
        bins = self.bins
        symbols = [sym for sym in _breaks(gt=self._gt, cmap=self._cmap,
                                          n=len(bins), alpha=self.alpha ) if sym is not None]
        for i in range(len(bins)):
            b = bins[i]
            if i == 0:
                self._class_break_info.append({
                    'symbol': symbols[i],
                    'label': '< %.3f' % float(b),
                    "classMaxValue" : float(b)
                })
            elif i == len(bins) - 1:
                self._class_break_info.append({
                    'symbol': symbols[i],
                    'label': '> %.3f' % float(b),
                    "classMinValue" : float(bins[i-1]),
                    "classMaxValue" : float(b)
                })
            else:
                self._class_break_info.append({
                    'symbol': symbols[i],
                    'label': '> %.3f -  %.3f' % (self._class_break_info[i-1]['classMaxValue'], float(b)),
                    "classMaxValue" : float(b)
                })
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """returns the renderer"""
        return self._to_dict()
    #----------------------------------------------------------------------
    def _to_dict(self):
        """create the renderer internally"""
        cbi = copy.deepcopy(self.class_breaks)
        for cb in cbi:
            cb['symbol'] = cb['symbol']._to_dict()

        r =  {'authoringInfo': {'type': 'classedColor',
                                'classificationMethod': 'esriClassifyEqualInterval'},
                'type': self._type,
                'field': self.field,
                'minValue': self._min_value or None,
                'classBreakInfos': cbi,
                'classificationMethod': 'esriClassifyEqualInterval'}
        if self.default_symbol:
            r['defaultSymbol'] = self.default_symbol._to_dict()
        if self.normalization_field:
            r['normalizationField'] = self.normalization_field
        return r

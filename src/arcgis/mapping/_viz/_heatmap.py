from ._base import _Renderer
###########################################################################
def _cmap2rgb(colors, step, alpha=1):
    """converts a color map to RGBA list"""
    from matplotlib import cm
    t = getattr(cm, colors)(step, bytes=True)
    t = [int(i) for i in t]
    t[-1] = alpha * 255
    return t
###########################################################################
def _breaks(cmap, n, alpha=1):
    """calculates the breaks in the number line"""
    step_size = 256 // n
    for i in range(n + 1):
        if i == 0:
            cm = _cmap2rgb(colors=cmap, step=i * step_size)
            cm[-1] = 0
            yield {"color" : cm,
                    "ratio" : i * (1/n)}
        yield {"color" : _cmap2rgb(colors=cmap, step=i * step_size),
                "ratio" : i * (1/n)}


class HeatMapRenderer(_Renderer):
    """
    Unique Renderer Class
    """
    _radius = None
    _stops = None
    _max_inten = 10
    _min_inten = 0
    _type = 'heatmap'
    _cmap = None
    _field = None
    def __init__(self,
                 color_scheme='jet',
                 radius=10,
                 number_stops=5,
                 stops=None):
        """Constructor"""
        self._radius = radius
        self._cmap = color_scheme
        if self._cmap is None:
            self._cmap = 'jet'
        if stops and isinstance(stops, list):
            self._stops = stops
        elif color_scheme:
            self._stops = [stop for stop in _breaks(cmap=color_scheme, n=number_stops)]
        else:
            raise ValueError("A color_schema or an array of stops must be provided.")
    #----------------------------------------------------------------------
    @property
    def radius(self):
        """
        The radius (in pixels) of the circle over which the majority of each point's value is spread.
        """
        return self._radius
    @radius.setter
    def radius(self, radius:float):
        """
        The radius (in pixels) of the circle over which the majority of each point's value is spread.
        """
        self._radius = radius
    #----------------------------------------------------------------------
    @property
    def field(self):
        """
        This is optional as this renderer can be created if no field is specified. Each feature gets the same value/importance/weight or with a field where each feature is weighted by the field's value.
        """
        return self._field
    @field.setter
    def field(self, field:str):
        """
        This is optional as this renderer can be created if no field is specified. Each feature gets the same value/importance/weight or with a field where each feature is weighted by the field's value.
        """
        self._field = field
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
            self._stops = [stop for stop in _breaks(cmap=cmap, n=self.number_stops)]
    #----------------------------------------------------------------------
    @property
    def number_stops(self):
        """gets/sets the number of stop breaks"""
        return len(self._stops)
    @number_stops.setter
    def number_stops(self, n):
        """gets/sets the number of stop breaks"""
        if isinstance(n, int) and n != len(self._stops):
            self._stops = [stop for stop in _breaks(cmap=self._cmap, n=n)]
    #----------------------------------------------------------------------
    @property
    def stops(self):
        """
        An array of dicts describing the renderer's color
        ramp with more specificity than just colors.
        """
        return self._stops
    @stops.setter
    def stops(self, ramp):
        """
        An array of dicts describing the renderer's color
        ramp with more specificity than just colors.
        """
        if isinstance(ramp, (list, tuple)):
            self._stops = ramp
    #----------------------------------------------------------------------
    @property
    def intensity(self):
        """
        The pixel intensity value assigns the initial and final color for the color ramp.

        :returns: tuple (min, max)
        """
        return self._min_inten, self._max_inten
    @intensity.setter
    def intensity(self, intensity):
        """
        The pixel intensity value assigns the initial and final color for the color ramp.

        :returns: tuple (min, max)
        """
        if isinstance(intensity, (tuple, list)):

            self._min_inten, self._max_inten = intensity
    #----------------------------------------------------------------------
    @property
    def renderer(self):
        """generates the renderer JSON"""
        return self._to_dict()
    #----------------------------------------------------------------------
    def _to_dict(self):
        """returns the renderer"""
        return {
            'renderer' : 'autocast',
            "type" : "heatmap",
            "maxPixelIntensity" : self._max_inten,
            "minPixelIntensity" : self._min_inten,
            "field" : self._field or "",
            "colorStops" : self.stops,
            'blurRadius' : self.radius
        }








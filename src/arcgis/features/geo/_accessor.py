"""
Holds Delegate and Accessor Logic
"""
import os
import copy
import time
import datetime
import pandas as pd
import numpy as np
try:
    import arcpy
    HASARCPY = True
except:
    HASARCPY = False
from ._internals import register_dataframe_accessor, register_series_accessor
from ._array import GeoType
from ._io.fileops import to_featureclass, from_featureclass
from arcgis.geometry import Geometry, SpatialReference, Envelope, Point
#--------------------------------------------------------------------------
def delegated_method(method, index, name, *args, **kwargs):
    return pd.Series(method(*args, **kwargs), index, name=name)
###########################################################################
class Delegated:
    # Descriptor for delegating attribute access to from
    # a Series to an underlying array

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, type=None):
        index = object.__getattribute__(obj, '_index')
        name = object.__getattribute__(obj, '_name')
        result = self._get_result(obj)
        return pd.Series(result, index)
###########################################################################
class DelegatedSeriesProperty(Delegated):
    def _get_result(self, obj, type=None):
        return getattr(object.__getattribute__(obj, '_data'), self.name)
###########################################################################
class DelegatedProperty(Delegated):
    def _get_result(self, obj, type=None):
        return getattr(object.__getattribute__(obj, '_data')[obj._name].values, self.name)
###########################################################################
class DelegatedMethod(Delegated):
    def __get__(self, obj, type=None):
        index = object.__getattribute__(obj, '_index')
        name = object.__getattribute__(obj, '_name')
        method = getattr(object.__getattribute__(obj, '_data')[obj._name].values, self.name)
        return delegated_method(method, index, name)
#--------------------------------------------------------------------------
def _is_geoenabled(df):
    """
    Checks if a Panda's DataFrame is 'geo-enabled'.

    This means that a spatial column is defined and is a GeoArray

    :returns: boolean
    """
    if isinstance(df, pd.DataFrame) and \
       hasattr(df, 'spatial') and \
       df.spatial._name and \
       df[df.spatial._name].dtype.name.lower() == 'geometry':
        return True
    else:
        return False
###########################################################################
@pd.api.extensions.register_series_accessor("geom")
class GeoSeriesAccessor:
    """
    """
    _data = None
    _index = None
    _name = None
    #----------------------------------------------------------------------
    def __init__(self, obj):
        """initializer"""
        self._validate(obj)
        self._data = obj.values
        self._index = obj.index
        self._name = obj.name
    #----------------------------------------------------------------------
    def _call_method(self, name, is_ga=False, **kwargs):
        """accesses a method on the geometry object"""
        vals = [getattr(g, name, None)(**kwargs) \
                for g in self._data]
        if is_ga:
            from ._array import GeoArray
            return pd.Series(GeoArray(vals))
        return pd.Series(vals)
    #----------------------------------------------------------------------
    @staticmethod
    def _validate(obj):
        if not is_geometry_type(obj):
            raise AttributeError("Cannot use 'spatial' accessor on objects of "
                                 "dtype '{}'.".format(obj.dtype))
    ##---------------------------------------------------------------------
    ##   Accessor Properties
    ##---------------------------------------------------------------------
    area = DelegatedSeriesProperty('area')
    #----------------------------------------------------------------------
    as_arcpy = DelegatedSeriesProperty("as_arcpy")
    #----------------------------------------------------------------------
    as_shapely = DelegatedSeriesProperty("as_shapely")
    #----------------------------------------------------------------------
    centroid = DelegatedSeriesProperty("centroid")
    #----------------------------------------------------------------------
    extent = DelegatedSeriesProperty('extent')
    #----------------------------------------------------------------------
    first_point = DelegatedSeriesProperty('first_point')
    #----------------------------------------------------------------------
    geoextent = DelegatedSeriesProperty("geoextent")
    #----------------------------------------------------------------------
    geometry_type = DelegatedSeriesProperty("geometry_type")
    #----------------------------------------------------------------------
    hull_rectangle = DelegatedSeriesProperty("hull_rectangle")
    #----------------------------------------------------------------------
    is_empty = DelegatedSeriesProperty("is_empty")
    #----------------------------------------------------------------------
    is_multipart = DelegatedSeriesProperty("is_multipart")
    #----------------------------------------------------------------------
    is_valid = DelegatedSeriesProperty("is_valid")
    #----------------------------------------------------------------------
    JSON = DelegatedSeriesProperty("JSON")
    #----------------------------------------------------------------------
    label_point = DelegatedSeriesProperty("label_point")
    #----------------------------------------------------------------------
    last_point = DelegatedSeriesProperty("last_point")
    #----------------------------------------------------------------------
    length = DelegatedSeriesProperty("length")
    #----------------------------------------------------------------------
    length3D = DelegatedSeriesProperty("length3D")
    #----------------------------------------------------------------------
    part_count = DelegatedSeriesProperty("part_count")
    #----------------------------------------------------------------------
    point_count = DelegatedSeriesProperty("point_count")
    #----------------------------------------------------------------------
    spatial_reference = DelegatedSeriesProperty("spatial_reference")
    #----------------------------------------------------------------------
    true_centroid = DelegatedSeriesProperty("true_centroid")
    #----------------------------------------------------------------------
    WKB = DelegatedSeriesProperty("WKB")
    #----------------------------------------------------------------------
    WKT = DelegatedSeriesProperty("WKT")
    ##---------------------------------------------------------------------
    ##  Accessor Geometry Method
    ##---------------------------------------------------------------------
    def angle_distance_to(self, second_geometry, method="GEODESIC"):
        """
        Returns a tuple of angle and distance to another point using a
        measurement type.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required Geometry.  A arcgis.Geometry object.
        ---------------     --------------------------------------------------------------------
        method              Optional String. PLANAR measurements reflect the projection of geographic
                            data onto the 2D surface (in other words, they will not take into
                            account the curvature of the earth). GEODESIC, GREAT_ELLIPTIC,
                            LOXODROME, and PRESERVE_SHAPE measurement types may be chosen as
                            an alternative, if desired.
        ===============     ====================================================================

        :returns: a tuple of angle and distance to another point using a measurement type.
        """
        return self._call_method(name='angle_distance_to',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry,
                                    'method' : method})
    #----------------------------------------------------------------------
    def boundary(self):
        """
        Constructs the boundary of the geometry.

        :returns: arcgis.geometry.Polyline
        """

        return self._call_method(name='boundary', is_ga=True)
    #----------------------------------------------------------------------
    def buffer(self, distance):
        """
        Constructs a polygon at a specified distance from the geometry.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        distance            Required float. The buffer distance. The buffer distance is in the
                            same units as the geometry that is being buffered.
                            A negative distance can only be specified against a polygon geometry.
        ===============     ====================================================================

        :returns: arcgis.geometry.Polygon
        """
        return self._call_method(name='buffer',
                                 is_ga=True,
                                 **{'distance' : distance})
    #----------------------------------------------------------------------
    def clip(self, envelope):
        """
        Constructs the intersection of the geometry and the specified extent.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        envelope            required tuple. The tuple must have (XMin, YMin, XMax, YMax) each value
                            represents the lower left bound and upper right bound of the extent.
        ===============     ====================================================================

        :returns: output geometry clipped to extent

        """
        return self._call_method(name='clip',
                                 is_ga=True,
                                 **{'envelope' : envelope})
    #----------------------------------------------------------------------
    def contains(self, second_geometry, relation=None):
        """
        Indicates if the base geometry contains the comparison geometry.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ---------------     --------------------------------------------------------------------
        relation            Optional string. The spatial relationship type.

                            + BOUNDARY - Relationship has no restrictions for interiors or boundaries.
                            + CLEMENTINI - Interiors of geometries must intersect. Specifying CLEMENTINI is equivalent to specifying None. This is the default.
                            + PROPER - Boundaries of geometries must not intersect.
        ===============     ====================================================================

        :returns: boolean
        """
        return self._call_method(name='contains',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry,
                                    'relation' : relation})
    #----------------------------------------------------------------------
    def convex_hull(self):
        """
        Constructs the geometry that is the minimal bounding polygon such
        that all outer angles are convex.
        """
        return self._call_method(name='convex_hull',
                                 is_ga=True)
    #----------------------------------------------------------------------
    def crosses(self, second_geometry):
        """
        Indicates if the two geometries intersect in a geometry of a lesser
        shape type.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :returns: boolean

        """
        return self._call_method(name='crosses',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def cut(self, cutter):
        """
        Splits this geometry into a part left of the cutting polyline, and
        a part right of it.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        cutter              Required Polyline. The cuttin polyline geometry
        ===============     ====================================================================

        :returns: a list of two geometries

        """
        return self._call_method(name='cut',
                                 is_ga=True,
                                 **{'cutter' : cutter})
    #----------------------------------------------------------------------
    def densify(self, method, distance, deviation):
        """
        Creates a new geometry with added vertices

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        method              Required String. The type of densification, DISTANCE, ANGLE, or GEODESIC
        ---------------     --------------------------------------------------------------------
        distance            Required float. The maximum distance between vertices. The actual
                            distance between vertices will usually be less than the maximum
                            distance as new vertices will be evenly distributed along the
                            original segment. If using a type of DISTANCE or ANGLE, the
                            distance is measured in the units of the geometry's spatial
                            reference. If using a type of GEODESIC, the distance is measured
                            in meters.
        ---------------     --------------------------------------------------------------------
        deviation           Required float. Densify uses straight lines to approximate curves.
                            You use deviation to control the accuracy of this approximation.
                            The deviation is the maximum distance between the new segment and
                            the original curve. The smaller its value, the more segments will
                            be required to approximate the curve.
        ===============     ====================================================================

        :returns: arcgis.geometry.Geometry

        """
        return self._call_method(name='densify',
                                 is_ga=True,
                                 **{'method' : method,
                                    'distance' : distance,
                                    'deviation' : deviation})
    #----------------------------------------------------------------------
    def difference(self, second_geometry):
        """
        Constructs the geometry that is composed only of the region unique
        to the base geometry but not part of the other geometry. The
        following illustration shows the results when the red polygon is the
        source geometry.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :returns: arcgis.geometry.Geometry

        """
        return self._call_method(name='difference',
                                 is_ga=True,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def disjoint(self, second_geometry):
        """
        Indicates if the base and comparison geometries share no points in
        common.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :returns: boolean

        """
        return self._call_method(name='disjoint',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def distance_to(self, second_geometry):
        """
        Returns the minimum distance between two geometries. If the
        geometries intersect, the minimum distance is 0.
        Both geometries must have the same projection.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :returns: float

        """
        return self._call_method(name='distance_to',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def equals(self, second_geometry):
        """
        Indicates if the base and comparison geometries are of the same
        shape type and define the same set of points in the plane. This is
        a 2D comparison only; M and Z values are ignored.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :returns: boolean


        """
        return self._call_method(name='equals',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def generalize(self, max_offset):
        """
        Creates a new simplified geometry using a specified maximum offset
        tolerance.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        max_offset          Required float. The maximum offset tolerance.
        ===============     ====================================================================

        :returns: arcgis.geometry.Geometry

        """
        return self._call_method(name='generalize',
                                 is_ga=True,
                                 **{'max_offset' : max_offset})
    #----------------------------------------------------------------------
    def get_area(self, method, units=None):
        """
        Returns the area of the feature using a measurement type.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        method              Required String. LANAR measurements reflect the projection of
                            geographic data onto the 2D surface (in other words, they will not
                            take into account the curvature of the earth). GEODESIC,
                            GREAT_ELLIPTIC, LOXODROME, and PRESERVE_SHAPE measurement types
                            may be chosen as an alternative, if desired.
        ---------------     --------------------------------------------------------------------
        units               Optional String. Areal unit of measure keywords: ACRES | ARES | HECTARES
                            | SQUARECENTIMETERS | SQUAREDECIMETERS | SQUAREINCHES | SQUAREFEET
                            | SQUAREKILOMETERS | SQUAREMETERS | SQUAREMILES |
                            SQUAREMILLIMETERS | SQUAREYARDS
        ===============     ====================================================================

        :returns: float

        """
        return self._call_method(name='get_area',
                                 is_ga=False,
                                 **{'method' : method,
                                    'units' : units})
    #----------------------------------------------------------------------
    def get_length(self, method, units):
        """
        Returns the length of the feature using a measurement type.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        method              Required String. PLANAR measurements reflect the projection of
                            geographic data onto the 2D surface (in other words, they will not
                            take into account the curvature of the earth). GEODESIC,
                            GREAT_ELLIPTIC, LOXODROME, and PRESERVE_SHAPE measurement types
                            may be chosen as an alternative, if desired.
        ---------------     --------------------------------------------------------------------
        units               Required String. Linear unit of measure keywords: CENTIMETERS |
                            DECIMETERS | FEET | INCHES | KILOMETERS | METERS | MILES |
                            MILLIMETERS | NAUTICALMILES | YARDS
        ===============     ====================================================================

        :returns: float

        """
        return self._call_method(name='get_length',
                                 is_ga=False,
                                 **{'method' : method,
                                    'units' : units})
    #----------------------------------------------------------------------
    def get_part(self, index=None):
        """
        Returns an array of point objects for a particular part of geometry
        or an array containing a number of arrays, one for each part.

        **requires arcpy**

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        index               Required Integer. The index position of the geometry.
        ===============     ====================================================================

        :return: arcpy.Array

        """
        return self._call_method(name='get_part',
                                 is_ga=False,
                                 **{'index' : index})
    #----------------------------------------------------------------------
    def intersect(self, second_geometry, dimension=1):
        """
        Constructs a geometry that is the geometric intersection of the two
        input geometries. Different dimension values can be used to create
        different shape types. The intersection of two geometries of the
        same shape type is a geometry containing only the regions of overlap
        between the original geometries.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ---------------     --------------------------------------------------------------------
        dimension           Required Integer. The topological dimension (shape type) of the
                            resulting geometry.

                            + 1  -A zero-dimensional geometry (point or multipoint).
                            + 2  -A one-dimensional geometry (polyline).
                            + 4  -A two-dimensional geometry (polygon).

        ===============     ====================================================================

        :returns: boolean

        """
        return self._call_method(name='intersect',
                                 is_ga=True,
                                 **{'second_geometry' : second_geometry,
                                    'dimension' : dimension})
    #----------------------------------------------------------------------
    def measure_on_line(self, second_geometry, as_percentage=False):
        """
        Returns a measure from the start point of this line to the in_point.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ---------------     --------------------------------------------------------------------
        as_percentage       Optional Boolean. If False, the measure will be returned as a
                            distance; if True, the measure will be returned as a percentage.
        ===============     ====================================================================

        :return: float

        """
        return self._call_method(name='measure_on_line',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry,
                                    'as_percentage' : as_percentage})
    #----------------------------------------------------------------------
    def overlaps(self, second_geometry):
        """
        Indicates if the intersection of the two geometries has the same
        shape type as one of the input geometries and is not equivalent to
        either of the input geometries.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :return: boolean

        """
        return self._call_method(name='overlaps',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def point_from_angle_and_distance(self, angle, distance, method='GEODESCIC'):
        """
        Returns a point at a given angle and distance in degrees and meters
        using the specified measurement type.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        angle               Required Float. The angle in degrees to the returned point.
        ---------------     --------------------------------------------------------------------
        distance            Required Float. The distance in meters to the returned point.
        ---------------     --------------------------------------------------------------------
        method              Optional String. PLANAR measurements reflect the projection of geographic
                            data onto the 2D surface (in other words, they will not take into
                            account the curvature of the earth). GEODESIC, GREAT_ELLIPTIC,
                            LOXODROME, and PRESERVE_SHAPE measurement types may be chosen as
                            an alternative, if desired.
        ===============     ====================================================================

        :return: arcgis.geometry.Geometry


        """
        return self._call_method(name='point_from_angle_and_distance',
                                 is_ga=True,
                                 **{'angle' : angle,
                                    'distance' : distance,
                                    'method' : method})
    #----------------------------------------------------------------------
    def position_along_line(self, value, use_percentage=False):
        """
        Returns a point on a line at a specified distance from the beginning
        of the line.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        value               Required Float. The distance along the line.
        ---------------     --------------------------------------------------------------------
        use_percentage      Optional Boolean. The distance may be specified as a fixed unit
                            of measure or a ratio of the length of the line. If True, value
                            is used as a percentage; if False, value is used as a distance.
                            For percentages, the value should be expressed as a double from
                            0.0 (0%) to 1.0 (100%).
        ===============     ====================================================================

        :return: arcgis.gis.Geometry

        """
        return self._call_method(name='position_along_line',
                                 is_ga=True,
                                 **{'value' : value,
                                    'use_percentage' : use_percentage})
    #----------------------------------------------------------------------
    def project_as(self, spatial_reference, transformation_name=None):
        """
        Projects a geometry and optionally applies a geotransformation.

        ====================     ====================================================================
        **Argument**             **Description**
        --------------------     --------------------------------------------------------------------
        spatial_reference        Required SpatialReference. The new spatial reference. This can be a
                                 SpatialReference object or the coordinate system name.
        --------------------     --------------------------------------------------------------------
        transformation_name      Required String. The geotransformation name.
        ====================     ====================================================================

        :returns: arcgis.geometry.Geometry
        """
        return self._call_method(name='project_as',
                                 is_ga=True,
                                 **{'spatial_reference' : spatial_reference,
                                    'transformation_name' : transformation_name}
                                 )
    #----------------------------------------------------------------------
    def query_point_and_distance(self, second_geometry,
                                 use_percentage=False):
        """
        Finds the point on the polyline nearest to the in_point and the
        distance between those points. Also returns information about the
        side of the line the in_point is on as well as the distance along
        the line where the nearest point occurs.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ---------------     --------------------------------------------------------------------
        as_percentage       Optional boolean - if False, the measure will be returned as
                            distance, True, measure will be a percentage
        ===============     ====================================================================

        :return: tuple

        """
        return self._call_method(name='query_point_and_distance',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry,
                                    'use_percentage' : use_percentage})
    #----------------------------------------------------------------------
    def segment_along_line(self, start_measure,
                           end_measure, use_percentage=False):
        """
        Returns a Polyline between start and end measures. Similar to
        Polyline.positionAlongLine but will return a polyline segment between
        two points on the polyline instead of a single point.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        start_measure       Required Float. The starting distance from the beginning of the line.
        ---------------     --------------------------------------------------------------------
        end_measure         Required Float. The ending distance from the beginning of the line.
        ---------------     --------------------------------------------------------------------
        use_percentage      Optional Boolean. The start and end measures may be specified as
                            fixed units or as a ratio.
                            If True, start_measure and end_measure are used as a percentage; if
                            False, start_measure and end_measure are used as a distance. For
                            percentages, the measures should be expressed as a double from 0.0
                            (0 percent) to 1.0 (100 percent).
        ===============     ====================================================================

        :returns: Geometry

        """
        return self._call_method(name='segment_along_line',
                                 is_ga=True,
                                 **{'start_measure' : start_measure,
                                    'end_measure' : end_measure,
                                    'use_percentage' : use_percentage})
    #----------------------------------------------------------------------
    def snap_to_line(self, second_geometry):
        """
        Returns a new point based on in_point snapped to this geometry.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :return: arcgis.gis.Geometry

        """
        return self._call_method(name='snap_to_line',
                                 is_ga=True,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def symmetric_difference (self, second_geometry):
        """
        Constructs the geometry that is the union of two geometries minus the
        instersection of those geometries.

        The two input geometries must be the same shape type.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :return: arcgis.gis.Geometry
        """
        return self._call_method(name='symmetric_difference',
                                 is_ga=True,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def touches(self, second_geometry):
        """
        Indicates if the boundaries of the geometries intersect.


        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :return: boolean
        """
        return self._call_method(name='touches',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def union(self, second_geometry):
        """
        Constructs the geometry that is the set-theoretic union of the input
        geometries.


        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ===============     ====================================================================

        :return: arcgis.gis.Geometry
        """
        return self._call_method(name='union',
                                 is_ga=True,
                                 **{'second_geometry' : second_geometry})
    #----------------------------------------------------------------------
    def within(self, second_geometry, relation=None):
        """
        Indicates if the base geometry is within the comparison geometry.

        ===============     ====================================================================
        **Argument**        **Description**
        ---------------     --------------------------------------------------------------------
        second_geometry     Required arcgis.geometry.Geometry. A second geometry
        ---------------     --------------------------------------------------------------------
        relation            Optional String. The spatial relationship type.

                            - BOUNDARY  - Relationship has no restrictions for interiors or boundaries.
                            - CLEMENTINI  - Interiors of geometries must intersect. Specifying CLEMENTINI is equivalent to specifying None. This is the default.
                            - PROPER  - Boundaries of geometries must not intersect.

        ===============     ====================================================================

        :return: boolean

        """
        return self._call_method(name='within',
                                 is_ga=False,
                                 **{'second_geometry' : second_geometry,
                                    'relation' : relation})


#--------------------------------------------------------------------------
def is_geometry_type(obj):
    t = getattr(obj, 'dtype', obj)
    try:
        return isinstance(t, GeoType) or issubclass(t, GeoType)
    except Exception:
        return False
###########################################################################
@register_dataframe_accessor("spatial")
class GeoAccessor(object):
    """
    The DataFrame Accessor is a namespace that performs dataset operations.
    This includes visualization, spatial indexing, IO and dataset level properties.
    """
    _sr = None
    _data = None
    _name = None
    _index = None
    _sindex = None
    _stype = None
    _sfname = None
    #----------------------------------------------------------------------
    def __init__(self, obj):
        self._data = obj
        self._index = obj.index
        self._name = None
    #----------------------------------------------------------------------
    def _call_method(self, name, is_ga=False, **kwargs):
        """accesses a method on the geometry object"""
        vals = [getattr(g, name, None)(**kwargs) \
                for g in self._data[self._name]]
        if is_ga:
            from ._array import GeoArray
            return pd.Series(GeoArray(vals))
        return pd.Series(vals)
    #----------------------------------------------------------------------
    def set_geometry(self, col):
        """Assigns the Geometry Column by Name or by List"""
        from ._array import GeoArray
        if isinstance(col, str) and  \
           col in self._data.columns and \
           self._data[col].dtype.name.lower() != 'geometry':
            self._name = col
            self._data[col] = GeoArray(self._data[col])
        elif isinstance(col, str) and  \
             col in self._data.columns and \
             self._data[col].dtype.name.lower() == 'geometry':
            self._name = col
            self._data[col] = self._data[col]
        elif isinstance(col, str) and \
             col not in self._data.columns:
            raise ValueError(
                "Column {name} does not exist".format(name=col))
        elif isinstance(col, pd.Series):
            self._data['SHAPE'] = GeoArray(col.values)
            self._name = "SHAPE"
        elif isinstance(col, GeoArray):
            self._data['SHAPE'] = col
            self._name = "SHAPE"
        elif isinstance(col, (list, tuple)):
            self._data['SHAPE'] = GeoArray(values=col)
            self._name = "SHAPE"
        else:
            raise ValueError(
                "Column {name} is not valid. Please ensure it is of type Geometry".format(name=col))
    #----------------------------------------------------------------------
    def validate(self, strict=False):
        """
        Determines if the Geo Accessor is Valid with Geometries in all values
        """
        if self._name is None:
            return False
        if strict:
            return len(pd.unique(self._data[self._name].geom.geometry_type)) == 1
        else:
            return all(pd.unique(self._data[self._name].geom.is_valid))
        return True
    #----------------------------------------------------------------------
    def spatial_join(self, right_df, how='inner', op='intersects',
                     left_tag="_left", right_tag="_right"):
        """
        Joins the current DataFrame to another spatially enabled dataframes based
        on spatial location based.

        .. note::
            requires the SEDF to be in the same coordinate system


        ======================    =========================================================
        **Argument**              **Description**
        ----------------------    ---------------------------------------------------------
        right_df                  Required pd.DataFrame. Spatially enabled dataframe to join.
        ----------------------    ---------------------------------------------------------
        how                       Required string. The type of join:

                                    + `left` - use keys from current dataframe and retains only current geometry column
                                    + `right` - use keys from right_df; retain only right_df geometry column
                                    + `inner` - use intersection of keys from both dfs and retain only current geometry column

        ----------------------    ---------------------------------------------------------
        op                        Required string. The operation to use to perform the join.
                                  The default is `intersects`.

                                  supported perations: `intersects`, `within`, and `contains`
        ----------------------    ---------------------------------------------------------
        left_tag                  Optional String. If the same column is in the left and
                                  right dataframe, this will append that string value to
                                  the field.
        ----------------------    ---------------------------------------------------------
        right_tag                 Optional String. If the same column is in the left and
                                  right dataframe, this will append that string value to
                                  the field.
        ======================    =========================================================

        :returns:
          Spatially enabled Pandas' DataFrame
        """
        import numpy as np
        import pandas as pd
        allowed_hows = ['left', 'right', 'inner']
        allowed_ops = ['contains', 'within', 'intersects']
        if how not in allowed_hows:
            raise ValueError("`how` is an invalid inputs of %s, but should be %s" % (how, allowed_hows))
        if op not in allowed_ops:
            raise ValueError("`how` is an invalid inputs of %s, but should be %s" % (op, allowed_ops))
        if self.sr != right_df.spatial.sr:
            raise Exception("Difference Spatial References, aborting operation")
        index_left = 'index_{}'.format(left_tag)
        index_right = 'index_{}'.format(right_tag)
        if (any(self._data.columns.isin([index_left, index_right]))
            or any(right_df.columns.isin([index_left, index_right]))):
            raise ValueError("'{0}' and '{1}' cannot be names in the frames being"
                             " joined".format(index_left, index_right))
        # Setup the Indexes in temporary coumns
        #
        left_df = self._data.copy()
        left_df.spatial.set_geometry(self._name)
        left_df.index = left_df.index.rename(index_left)
        left_df = left_df.reset_index()
        left_df.spatial.set_geometry(self._name)
        shape_right = right_df.spatial._name
        right_df = right_df.copy()
        right_df.index = right_df.index.rename(index_right)
        right_df = right_df.reset_index()
        right_df.spatial.set_geometry(shape_right)

        if op == "within":
            # within implemented as the inverse of contains; swap names
            left_df, right_df = right_df, left_df

        tree_idx = right_df.spatial.sindex("quadtree")

        idxmatch = (self._data[self._name]
                    .apply(lambda x: x.extent)
                    .apply(lambda x: list(tree_idx.intersect(x))))
        idxmatch = idxmatch[idxmatch.apply(len) > 0]

        if idxmatch.shape[0] > 0:
            # if output from join has overlapping geometries
            r_idx = np.concatenate(idxmatch.values)
            l_idx = np.concatenate([[i] * len(v) for i, v in idxmatch.iteritems()])

            # Vectorize predicate operations
            def find_intersects(a1, a2):
                return a1.disjoint(a2) == False

            def find_contains(a1, a2):
                return a1.contains(a2)

            predicate_d = {'intersects': find_intersects,
                           'contains': find_contains,
                           'within': find_contains}

            check_predicates = np.vectorize(predicate_d[op])

            result = (
                pd.DataFrame(
                          np.column_stack(
                              [l_idx,
                               r_idx,
                               check_predicates(
                                   left_df[self._name]
                                   .apply(lambda x: x)[l_idx],
                                   right_df[right_df.spatial._name][r_idx])
                               ]))
            )

            result.columns = ['_key_left', '_key_right', 'match_bool']
            result = (
                pd.DataFrame(result[result['match_bool']==1])
                      .drop('match_bool', axis=1)
            )
        else:
            # when output from the join has no overlapping geometries
            result = pd.DataFrame(columns=['_key_left', '_key_right'], dtype=float)

        if op == "within":
                # within implemented as the inverse of contains; swap names
                left_df, right_df = right_df, left_df
                result = result.rename(columns={'_key_left': '_key_right',
                                                '_key_right': '_key_left'})


        if how == 'inner':
            result = result.set_index('_key_left')
            joined = (
                      left_df
                      .merge(result, left_index=True, right_index=True)
                      .merge(right_df.drop(right_df.spatial._name, axis=1),
                          left_on='_key_right', right_index=True,
                          suffixes=('_%s' % left_tag, '_%s' % right_tag))
                     )
            joined = joined.set_index(index_left).drop(['_key_right'], axis=1)
            joined.index.name = None
        elif how == 'left':
            result = result.set_index('_key_left')
            joined = (
                      left_df
                      .merge(result, left_index=True, right_index=True, how='left')
                      .merge(right_df.drop(right_df.spatial._name, axis=1),
                          how='left', left_on='_key_right', right_index=True,
                          suffixes=('_%s' % left_tag, '_%s' % right_tag))
                     )
            joined = joined.set_index(index_left).drop(['_key_right'], axis=1)
            joined.index.name = None
        else:  # how == 'right':
            joined = (
                      left_df
                      .drop(left_df.spatial._name, axis=1)
                      .merge(result.merge(right_df,
                          left_on='_key_right', right_index=True,
                          how='right'), left_index=True,
                          right_on='_key_left', how='right')
                      .set_index(index_right)
                     )
            joined = joined.drop(['_key_left', '_key_right'], axis=1)
        try:
            joined.spatial.set_geometry(self._name)
        except:
            raise Exception("Could not create spatially enabled dataframe.")
        return joined
    #----------------------------------------------------------------------
    def plot(self, map_widget=None, **kwargs):
        """

        Plot draws the data on a web map. The user can describe in simple terms how to
        renderer spatial data using symbol.  To make the process simplier a pallette
        for which colors are drawn from can be used instead of explicit colors.


        ======================  =========================================================
        **Explicit Argument**   **Description**
        ----------------------  ---------------------------------------------------------
        map_widget              optional WebMap object. This is the map to display the
                                data on.
        ----------------------  ---------------------------------------------------------
        palette                 optional string/dict.  Color mapping.  For simple renderer,
                                just provide a string.  For more robust renderers like
                                unique renderer, a dictionary can be given.
        ----------------------  ---------------------------------------------------------
        renderer_type           optional string.  Determines the type of renderer to use
                                for the provided dataset. The default is 's' which is for
                                simple renderers.

                                Allowed values:

                                + 's' - is a simple renderer that uses one symbol only.
                                + 'u' - unique renderer symbolizes features based on one
                                        or more matching string attributes.
                                + 'c' - A class breaks renderer symbolizes based on the
                                        value of some numeric attribute.
                                + 'h' - heatmap renders point data into a raster
                                        visualization that emphasizes areas of higher
                                        density or weighted values.
        ----------------------  ---------------------------------------------------------
        symbol_type             optional string. This is the type of symbol the user
                                needs to create.  Valid inputs are: simple, picture, text,
                                or carto.  The default is simple.
        ----------------------  ---------------------------------------------------------
        symbol_type             optional string. This is the symbology used by the
                                geometry.  For example 's' for a Line geometry is a solid
                                line. And '-' is a dash line.

                                Allowed symbol types based on geometries:

                                **Point Symbols**

                                 + 'o' - Circle (default)
                                 + '+' - Cross
                                 + 'D' - Diamond
                                 + 's' - Square
                                 + 'x' - X

                                 **Polyline Symbols**

                                 + 's' - Solid (default)
                                 + '-' - Dash
                                 + '-.' - Dash Dot
                                 + '-..' - Dash Dot Dot
                                 + '.' - Dot
                                 + '--' - Long Dash
                                 + '--.' - Long Dash Dot
                                 + 'n' - Null
                                 + 's-' - Short Dash
                                 + 's-.' - Short Dash Dot
                                 + 's-..' - Short Dash Dot Dot
                                 + 's.' - Short Dot

                                 **Polygon Symbols**

                                 + 's' - Solid Fill (default)
                                 + '\' - Backward Diagonal
                                 + '/' - Forward Diagonal
                                 + '|' - Vertical Bar
                                 + '-' - Horizontal Bar
                                 + 'x' - Diagonal Cross
                                 + '+' - Cross

        ----------------------  ---------------------------------------------------------
        col                     optional string/list. Field or fields used for heatmap,
                                class breaks, or unique renderers.
        ----------------------  ---------------------------------------------------------
        pallette                optional string. The color map to draw from in order to
                                visualize the data.  The default pallette is 'jet'. To
                                get a visual representation of the allowed color maps,
                                use the **display_colormaps** method.
        ----------------------  ---------------------------------------------------------
        alpha                   optional float.  This is a value between 0 and 1 with 1
                                being the default value.  The alpha sets the transparancy
                                of the renderer when applicable.
        ======================  =========================================================

        ** Render Syntax **

        The render syntax allows for users to fully customize symbolizing the data.

        ** Simple Renderer**

        A simple renderer is a renderer that uses one symbol only.

        ======================  =========================================================
        **Optional Argument**   **Description**
        ----------------------  ---------------------------------------------------------
        symbol_type             optional string. This is the type of symbol the user
                                needs to create.  Valid inputs are: simple, picture, text,
                                or carto.  The default is simple.
        ----------------------  ---------------------------------------------------------
        symbol_type             optional string. This is the symbology used by the
                                geometry.  For example 's' for a Line geometry is a solid
                                line. And '-' is a dash line.

                                **Point Symbols**

                                + 'o' - Circle (default)
                                + '+' - Cross
                                + 'D' - Diamond
                                + 's' - Square
                                + 'x' - X

                                **Polyline Symbols**

                                + 's' - Solid (default)
                                + '-' - Dash
                                + '-.' - Dash Dot
                                + '-..' - Dash Dot Dot
                                + '.' - Dot
                                + '--' - Long Dash
                                + '--.' - Long Dash Dot
                                + 'n' - Null
                                + 's-' - Short Dash
                                + 's-.' - Short Dash Dot
                                + 's-..' - Short Dash Dot Dot
                                + 's.' - Short Dot

                                **Polygon Symbols**

                                + 's' - Solid Fill (default)
                                + '\' - Backward Diagonal
                                + '/' - Forward Diagonal
                                + '|' - Vertical Bar
                                + '-' - Horizontal Bar
                                + 'x' - Diagonal Cross
                                + '+' - Cross
        ----------------------  ---------------------------------------------------------
        description             Description of the renderer.
        ----------------------  ---------------------------------------------------------
        rotation_expression     A constant value or an expression that derives the angle
                                of rotation based on a feature attribute value. When an
                                attribute name is specified, it's enclosed in square
                                brackets.
        ----------------------  ---------------------------------------------------------
        rotation_type           String value which controls the origin and direction of
                                rotation on point features. If the rotationType is
                                defined as arithmetic, the symbol is rotated from East in
                                a counter-clockwise direction where East is the 0 degree
                                axis. If the rotationType is defined as geographic, the
                                symbol is rotated from North in a clockwise direction
                                where North is the 0 degree axis.

                                Must be one of the following values:

                                + arithmetic
                                + geographic

        ----------------------  ---------------------------------------------------------
        visual_variables        An array of objects used to set rendering properties.
        ======================  =========================================================

        **Heatmap Renderer**

        The HeatmapRenderer renders point data into a raster visualization that emphasizes
        areas of higher density or weighted values.

        ======================  =========================================================
        **Optional Argument**   **Description**
        ----------------------  ---------------------------------------------------------
        blur_radius             The radius (in pixels) of the circle over which the
                                majority of each point's value is spread.
        ----------------------  ---------------------------------------------------------
        field                   This is optional as this renderer can be created if no
                                field is specified. Each feature gets the same
                                value/importance/weight or with a field where each
                                feature is weighted by the field's value.
        ----------------------  ---------------------------------------------------------
        max_intensity           The pixel intensity value which is assigned the final
                                color in the color ramp.
        ----------------------  ---------------------------------------------------------
        min_intensity           The pixel intensity value which is assigned the initial
                                color in the color ramp.
        ----------------------  ---------------------------------------------------------
        ratio                   A number between 0-1. Describes what portion along the
                                gradient the colorStop is added.
        ======================  =========================================================

        **Unique Renderer**

        This renderer symbolizes features based on one or more matching string attributes.

        ======================  =========================================================
        **Optional Argument**   **Description**
        ----------------------  ---------------------------------------------------------
        background_fill_symbol  A symbol used for polygon features as a background if the
                                renderer uses point symbols, e.g. for bivariate types &
                                size rendering. Only applicable to polygon layers.
                                PictureFillSymbols can also be used outside of the Map
                                Viewer for Size and Predominance and Size renderers.
        ----------------------  ---------------------------------------------------------
        default_label           Default label for the default symbol used to draw
                                unspecified values.
        ----------------------  ---------------------------------------------------------
        default_symbol          Symbol used when a value cannot be matched.
        ----------------------  ---------------------------------------------------------
        field1, field2, field3  Attribute field renderer uses to match values.
        ----------------------  ---------------------------------------------------------
        field_delimiter         String inserted between the values if multiple attribute
                                fields are specified.
        ----------------------  ---------------------------------------------------------
        rotation_expression     A constant value or an expression that derives the angle
                                of rotation based on a feature attribute value. When an
                                attribute name is specified, it's enclosed in square
                                brackets. Rotation is set using a visual variable of type
                                rotation info with a specified field or value expression
                                property.
        ----------------------  ---------------------------------------------------------
        rotation_type           String property which controls the origin and direction
                                of rotation. If the rotation type is defined as
                                arithmetic the symbol is rotated from East in a
                                counter-clockwise direction where East is the 0 degree
                                axis. If the rotation type is defined as geographic, the
                                symbol is rotated from North in a clockwise direction
                                where North is the 0 degree axis.
                                Must be one of the following values:

                                + arithmetic
                                + geographic

        ----------------------  ---------------------------------------------------------
        arcade_expression       An Arcade expression evaluating to either a string or a
                                number.
        ----------------------  ---------------------------------------------------------
        arcade_title            The title identifying and describing the associated
                                Arcade expression as defined in the valueExpression
                                property.
        ----------------------  ---------------------------------------------------------
        visual_variables        An array of objects used to set rendering properties.
        ======================  =========================================================

        **Class Breaks Renderer**

        A class breaks renderer symbolizes based on the value of some numeric attribute.

        ======================  =========================================================
        **Optional Argument**   **Description**
        ----------------------  ---------------------------------------------------------
        background_fill_symbol  A symbol used for polygon features as a background if the
                                renderer uses point symbols, e.g. for bivariate types &
                                size rendering. Only applicable to polygon layers.
                                PictureFillSymbols can also be used outside of the Map
                                Viewer for Size and Predominance and Size renderers.
        ----------------------  ---------------------------------------------------------
        default_label           Default label for the default symbol used to draw
                                unspecified values.
        ----------------------  ---------------------------------------------------------
        default_symbol          Symbol used when a value cannot be matched.
        ----------------------  ---------------------------------------------------------
        method                  Determines the classification method that was used to
                                generate class breaks.

                                Must be one of the following values:

                                + esriClassifyDefinedInterval
                                + esriClassifyEqualInterval
                                + esriClassifyGeometricalInterval
                                + esriClassifyNaturalBreaks
                                + esriClassifyQuantile
                                + esriClassifyStandardDeviation
                                + esriClassifyManual

        ----------------------  ---------------------------------------------------------
        field                   Attribute field used for renderer.
        ----------------------  ---------------------------------------------------------
        min_value               The minimum numeric data value needed to begin class
                                breaks.
        ----------------------  ---------------------------------------------------------
        normalization_field     Used when normalizationType is field. The string value
                                indicating the attribute field by which the data value is
                                normalized.
        ----------------------  ---------------------------------------------------------
        normalization_total     Used when normalizationType is percent-of-total, this
                                number property contains the total of all data values.
        ----------------------  ---------------------------------------------------------
        normalization_type      Determine how the data was normalized.

                                Must be one of the following values:

                                + esriNormalizeByField
                                + esriNormalizeByLog
                                + esriNormalizeByPercentOfTotal
        ----------------------  ---------------------------------------------------------
        rotation_expression     A constant value or an expression that derives the angle
                                of rotation based on a feature attribute value. When an
                                attribute name is specified, it's enclosed in square
                                brackets.
        ----------------------  ---------------------------------------------------------
        rotation_type           A string property which controls the origin and direction
                                of rotation. If the rotation_type is defined as
                                arithmetic, the symbol is rotated from East in a
                                couter-clockwise direction where East is the 0 degree
                                axis. If the rotationType is defined as geographic, the
                                symbol is rotated from North in a clockwise direction
                                where North is the 0 degree axis.

                                Must be one of the following values:

                                + arithmetic
                                + geographic

        ----------------------  ---------------------------------------------------------
        arcade_expression       An Arcade expression evaluating to a number.
        ----------------------  ---------------------------------------------------------
        arcade_title            The title identifying and describing the associated
                                Arcade expression as defined in the arcade_expression
                                property.
        ----------------------  ---------------------------------------------------------
        visual_variables        An object used to set rendering options.
        ======================  =========================================================



        ** Symbol Syntax **

        =======================  =========================================================
        **Optional Argument**    **Description**
        -----------------------  ---------------------------------------------------------
        symbol_type              optional string. This is the type of symbol the user
                                 needs to create.  Valid inputs are: simple, picture, text,
                                 or carto.  The default is simple.
        -----------------------  ---------------------------------------------------------
        symbol_type              optional string. This is the symbology used by the
                                 geometry.  For example 's' for a Line geometry is a solid
                                 line. And '-' is a dash line.

                                 **Point Symbols**

                                 + 'o' - Circle (default)
                                 + '+' - Cross
                                 + 'D' - Diamond
                                 + 's' - Square
                                 + 'x' - X

                                 **Polyline Symbols**

                                 + 's' - Solid (default)
                                 + '-' - Dash
                                 + '-.' - Dash Dot
                                 + '-..' - Dash Dot Dot
                                 + '.' - Dot
                                 + '--' - Long Dash
                                 + '--.' - Long Dash Dot
                                 + 'n' - Null
                                 + 's-' - Short Dash
                                 + 's-.' - Short Dash Dot
                                 + 's-..' - Short Dash Dot Dot
                                 + 's.' - Short Dot

                                 **Polygon Symbols**

                                 + 's' - Solid Fill (default)
                                 + '\' - Backward Diagonal
                                 + '/' - Forward Diagonal
                                 + '|' - Vertical Bar
                                 + '-' - Horizontal Bar
                                 + 'x' - Diagonal Cross
                                 + '+' - Cross
        -----------------------  ---------------------------------------------------------
        cmap                     optional string or list.  This is the color scheme a user
                                 can provide if the exact color is not needed, or a user
                                 can provide a list with the color defined as:
                                 [red, green blue, alpha]. The values red, green, blue are
                                 from 0-255 and alpha is a float value from 0 - 1.
                                 The default value is 'jet' color scheme.
        -----------------------  ---------------------------------------------------------
        cstep                    optional integer.  If provided, its the color location on
                                 the color scheme.
        =======================  =========================================================

        **Simple Symbols**

        This is a list of optional parameters that can be given for point, line or
        polygon geometries.

        ====================  =========================================================
        **Argument**          **Description**
        --------------------  ---------------------------------------------------------
        marker_size           optional float.  Numeric size of the symbol given in
                              points.
        --------------------  ---------------------------------------------------------
        marker_angle          optional float. Numeric value used to rotate the symbol.
                              The symbol is rotated counter-clockwise. For example,
                              The following, angle=-30, in will create a symbol rotated
                              -30 degrees counter-clockwise; that is, 30 degrees
                              clockwise.
        --------------------  ---------------------------------------------------------
        marker_xoffset        Numeric value indicating the offset on the x-axis in points.
        --------------------  ---------------------------------------------------------
        marker_yoffset        Numeric value indicating the offset on the y-axis in points.
        --------------------  ---------------------------------------------------------
        line_width            optional float. Numeric value indicating the width of the line in points
        --------------------  ---------------------------------------------------------
        outline_style         Optional string. For polygon point, and line geometries , a
                              customized outline type can be provided.

                              Allowed Styles:

                              + 's' - Solid (default)
                              + '-' - Dash
                              + '-.' - Dash Dot
                              + '-..' - Dash Dot Dot
                              + '.' - Dot
                              + '--' - Long Dash
                              + '--.' - Long Dash Dot
                              + 'n' - Null
                              + 's-' - Short Dash
                              + 's-.' - Short Dash Dot
                              + 's-..' - Short Dash Dot Dot
                              + 's.' - Short Dot
        --------------------  ---------------------------------------------------------
        outline_color         optional string or list.  This is the same color as the
                              cmap property, but specifically applies to the outline_color.
        ====================  =========================================================

        **Picture Symbol**

        This type of symbol only applies to Points, MultiPoints and Polygons.

        ====================  =========================================================
        **Argument**          **Description**
        --------------------  ---------------------------------------------------------
        marker_angle          Numeric value that defines the number of degrees ranging
                              from 0-360, that a marker symbol is rotated. The rotation
                              is from East in a counter-clockwise direction where East
                              is the 0 axis.
        --------------------  ---------------------------------------------------------
        marker_xoffset        Numeric value indicating the offset on the x-axis in points.
        --------------------  ---------------------------------------------------------
        marker_yoffset        Numeric value indicating the offset on the y-axis in points.
        --------------------  ---------------------------------------------------------
        height                Numeric value used if needing to resize the symbol. Specify a value in points. If images are to be displayed in their original size, leave this blank.
        --------------------  ---------------------------------------------------------
        width                 Numeric value used if needing to resize the symbol. Specify a value in points. If images are to be displayed in their original size, leave this blank.
        --------------------  ---------------------------------------------------------
        url                   String value indicating the URL of the image. The URL should be relative if working with static layers. A full URL should be used for map service dynamic layers. A relative URL can be dereferenced by accessing the map layer image resource or the feature layer image resource.
        --------------------  ---------------------------------------------------------
        image_data            String value indicating the base64 encoded data.
        --------------------  ---------------------------------------------------------
        xscale                Numeric value indicating the scale factor in x direction.
        --------------------  ---------------------------------------------------------
        yscale                Numeric value indicating the scale factor in y direction.
        --------------------  ---------------------------------------------------------
        outline_color         optional string or list.  This is the same color as the
                              cmap property, but specifically applies to the outline_color.
        --------------------  ---------------------------------------------------------
        outline_style         Optional string. For polygon point, and line geometries , a
                              customized outline type can be provided.

                              Allowed Styles:

                              + 's' - Solid (default)
                              + '-' - Dash
                              + '-.' - Dash Dot
                              + '-..' - Dash Dot Dot
                              + '.' - Dot
                              + '--' - Long Dash
                              + '--.' - Long Dash Dot
                              + 'n' - Null
                              + 's-' - Short Dash
                              + 's-.' - Short Dash Dot
                              + 's-..' - Short Dash Dot Dot
                              + 's.' - Short Dot
        --------------------  ---------------------------------------------------------
        outline_color         optional string or list.  This is the same color as the
                              cmap property, but specifically applies to the outline_color.
        --------------------  ---------------------------------------------------------
        line_width            optional float. Numeric value indicating the width of the line in points
        ====================  =========================================================

        **Text Symbol**

        This type of symbol only applies to Points, MultiPoints and Polygons.

        ====================  =========================================================
        **Argument**          **Description**
        --------------------  ---------------------------------------------------------
        font_decoration       The text decoration. Must be one of the following values:
                              - line-through
                              - underline
                              - none
        --------------------  ---------------------------------------------------------
        font_family           Optional string. The font family.
        --------------------  ---------------------------------------------------------
        font_size             Optional float. The font size in points.
        --------------------  ---------------------------------------------------------
        font_style            Optional string. The text style.
                              - italic
                              - normal
                              - oblique
        --------------------  ---------------------------------------------------------
        font_weight           Optional string. The text weight.
                              Must be one of the following values:
                              - bold
                              - bolder
                              - lighter
                              - normal
        --------------------  ---------------------------------------------------------
        background_color      optional string/list. Background color is represented as
                              a four-element array or string of a color map.
        --------------------  ---------------------------------------------------------
        halo_color            Optional string/list. Color of the halo around the text.
                              The default is None.
        --------------------  ---------------------------------------------------------
        halo_size             Optional integer/float. The point size of a halo around
                              the text symbol.
        --------------------  ---------------------------------------------------------
        horizontal_alignment  optional string. One of the following string values
                              representing the horizontal alignment of the text.
                              Must be one of the following values:
                              - left
                              - right
                              - center
                              - justify
        --------------------  ---------------------------------------------------------
        kerning               optional boolean. Boolean value indicating whether to
                              adjust the spacing between characters in the text string.
        --------------------  ---------------------------------------------------------
        line_color            optional string/list. Outline color is represented as
                              a four-element array or string of a color map.
        --------------------  ---------------------------------------------------------
        line_width            optional integer/float. Outline size.
        --------------------  ---------------------------------------------------------
        marker_angle          optional int. A numeric value that defines the number of
                              degrees (0 to 360) that a text symbol is rotated. The
                              rotation is from East in a counter-clockwise direction
                              where East is the 0 axis.
        --------------------  ---------------------------------------------------------
        marker_xoffset        optional int/float.Numeric value indicating the offset
                              on the x-axis in points.
        --------------------  ---------------------------------------------------------
        marker_yoffset        optional int/float.Numeric value indicating the offset
                              on the x-axis in points.
        --------------------  ---------------------------------------------------------
        right_to_left         optional boolean. Set to true if using Hebrew or Arabic
                              fonts.
        --------------------  ---------------------------------------------------------
        rotated               optional boolean. Boolean value indicating whether every
                              character in the text string is rotated.
        --------------------  ---------------------------------------------------------
        text                  Required string.  Text Value to display next to geometry.
        --------------------  ---------------------------------------------------------
        vertical_alignment    Optional string. One of the following string values
                              representing the vertical alignment of the text.
                              Must be one of the following values:
                              - top
                              - bottom
                              - middle
                              - baseline
        ====================  =========================================================

        **Cartographic Symbol**

        This type of symbol only applies to line geometries.

        ====================  =========================================================
        **Argument**          **Description**
        --------------------  ---------------------------------------------------------
        line_width            optional float. Numeric value indicating the width of the line in points
        --------------------  ---------------------------------------------------------
        cap                   Optional string.  The cap style.
        --------------------  ---------------------------------------------------------
        join                  Optional string. The join style.
        --------------------  ---------------------------------------------------------
        miter_limit           Optional string. Size threshold for showing mitered line joins.
        ====================  =========================================================

        The kwargs parameter accepts all parameters of the create_symbol method and the
        create_renderer method.


        """
        from ._viz.mapping import plot
        if map_widget is None:
            from arcgis.gis import GIS
            from arcgis.env import active_gis
            gis = active_gis
            if gis is None:
                gis = GIS()
            map_widget = gis.map()
        plot(df=self._data,
             map_widget=map_widget,
             name=kwargs.pop('name', "Feature Collection Layer"),
             renderer_type=kwargs.pop("renderer_type", None),
             symbol_type=kwargs.pop('symbol_type', None),
             symbol_style=kwargs.pop('symbol_style', None),
             col=kwargs.pop('col', None),
             colors=kwargs.pop('cmap', None) or kwargs.pop('colors', None) or kwargs.pop('pallette', 'jet'),
             alpha=kwargs.pop('alpha', 1),
             **kwargs)
        return True
    #----------------------------------------------------------------------
    def to_featureclass(self, location, overwrite=True):
        """exports a geo enabled dataframe to a feature class."""
        return to_featureclass(geo=self,
                               location=location,
                               overwrite=overwrite)
    # ----------------------------------------------------------------------
    @staticmethod
    def from_df(df, address_column="address", geocoder=None, sr=None):
        """
        Returns a SpatialDataFrame from a dataframe with an address column.

        ====================    =========================================================
        **Argument**            **Description**
        --------------------    ---------------------------------------------------------
        df                      Required Pandas DataFrame. Source dataset
        --------------------    ---------------------------------------------------------
        address_column          Optional String. The default is "address". This is the
                                name of a column in the specified dataframe that contains
                                addresses (as strings). The addresses are batch geocoded
                                using the GIS's first configured geocoder and their
                                locations used as the geometry of the spatial dataframe.
                                Ignored if the 'geometry' parameter is also specified.
        --------------------    ---------------------------------------------------------
        geocoder                Optional Geocoder. The geocoder to be used. If not
                                specified, the active GIS's first geocoder is used.
        --------------------    ---------------------------------------------------------
        sr                      Optional integer. The WKID of the spatial reference.
        ====================    =========================================================

        :returns: DataFrame



        NOTE: Credits will be consumed for batch_geocoding, from
        the GIS to which the geocoder belongs.

        """
        import arcgis
        from arcgis.geocoding import get_geocoders, geocode, batch_geocode
        if geocoder is None:
            geocoder = arcgis.env.active_gis._tools.geocoders[0]
        sr = dict(geocoder.properties.spatialReference)
        geoms = []
        if address_column in df.columns:
            batch_size = geocoder.properties.locatorProperties.MaxBatchSize
            N = len(df)
            geoms = []
            for i in range(0, N, batch_size):
                start = i
                stop = i + batch_size if i + batch_size < N else N
                res = batch_geocode(list(df[start:stop][address_column]), geocoder=geocoder)
                for index in range(len(res)):
                    address = df.ix[start + index, address_column]
                    try:
                        loc = res[index]['location']
                        x = loc['x']
                        y = loc['y']
                        geoms.append(arcgis.geometry.Geometry({'x': x, 'y': y, 'spatialReference': sr}))

                    except:
                        x, y = None, None
                        try:
                            loc = geocode(address, geocoder=geocoder)[0]['location']
                            x = loc['x']
                            y = loc['y']
                        except:
                            print('Unable to geocode address: ' + address)
                            pass
                        geoms.append(None)
        else:
            raise ValueError("Address column not found in dataframe")
        df['SHAPE'] = geoms
        df.spatial.set_geometry("SHAPE")
        return df
    # ----------------------------------------------------------------------
    @staticmethod
    def from_xy(df, x_column, y_column, sr=4326):
        """
        Converts a Pandas DataFrame into a Spatial DataFrame by providing the X/Y columns.

        ====================    =========================================================
        **Argument**            **Description**
        --------------------    ---------------------------------------------------------
        df                      Required Pandas DataFrame. Source dataset
        --------------------    ---------------------------------------------------------
        x_column                Required string.  The name of the X-coordinate series
        --------------------    ---------------------------------------------------------
        y_column                Required string.  The name of the Y-coordinate series
        --------------------    ---------------------------------------------------------
        sr                      Optional int.  The wkid number of the spatial reference.
                                4326 is the default value.
        ====================    =========================================================

        :returns: DataFrame

        """
        from ._io.fileops import _from_xy
        return _from_xy(df=df, x_column=x_column,
                        y_column=y_column, sr=sr)
    #----------------------------------------------------------------------
    @staticmethod
    def from_layer(layer):
        """imports a FeatureLayer to a Spatially Enabled DataFrame"""
        from arcgis.features.geo._io.serviceops import from_layer
        return from_layer(layer=layer)
    #----------------------------------------------------------------------
    @staticmethod
    def from_featureclass(location):
        """import a geo enabled dataframe to a feature class."""
        return from_featureclass(filename=location)
    #----------------------------------------------------------------------
    def sindex(self, stype, reset=False, **kwargs):
        """
        Creates a spatial index for the given dataset.

        **By default the spatial index is a QuadTree spatial index.**

        If r-tree indexes should be used for large datasets.  This will allow
        users to create very large out of memory indexes.  To use r-tree indexes,
        the r-tree library must be installed.  To do so, install via conda using
        the following command: `conda install -c conda-forge rtree`

        """
        from arcgis.features.geo._index._impl import SpatialIndex
        c = 0
        filename = kwargs.pop('filename', None)
        if reset:
            self._sindex = None
            self._sfname = None
            self._stype = None
        if self._sindex:
            return self._sindex
        bbox = self.full_extent
        if self._name and \
           filename and \
           os.path.isfile(filename + ".dat") and \
           os.path.isfile(filename + ".idx"):
            l = len(self._data[self._name])
            self._sindex = SpatialIndex(stype=stype,
                                        filename=filename,
                                        bbox=self.full_extent)
            for idx, g in zip(self._index, self._data[self._name]):
                if g.type.lower() == 'point':
                    ge = g.geoextent
                    gext = (ge[0] -.001,ge[1] -.001, ge[2] + .001, ge[3] -.001)
                    self._sindex.insert(oid=idx, bbox=gext)
                else:
                    self._sindex.insert(oid=idx, bbox=g.geoextent)
                if c >= int(l/4) + 1:
                    self._sindex.flush()
                    c = 0
                c += 1
            self._sindex.flush()
            return self._sindex
        elif self._name:
            c = 0
            l = len(self._data[self._name])
            self._sindex = SpatialIndex(stype=stype,
                                        filename=filename,
                                        bbox=self.full_extent)
            for idx, g in zip(self._index, self._data[self._name]):
                if g.type.lower() == 'point':
                    ge = g.geoextent
                    gext = (ge[0] -.001,ge[1] -.001, ge[2] + .001, ge[3] -.001)
                    self._sindex.insert(oid=idx, bbox=gext)
                else:
                    self._sindex.insert(oid=idx, bbox=g.geoextent)
                if c >= int(l/4) + 1:
                    self._sindex.flush()
                    c = 0
                c += 1
            self._sindex.flush()
            return self._sindex
        else:
            raise ValueError(("The Spatial Column must "
                             "be set, call df.spatial.set_geometry."))
    #----------------------------------------------------------------------
    @property
    def __geo_interface__(self):
        """returns the object as an Feature Collection JSON string"""
        template = {
            "type": "FeatureCollection",
            "features": []
        }
        for index, row in self._data.iterrows():
            geom = row[self._name]
            del row[self._name]
            gj = copy.copy(geom.__geo_interface__)
            gj['attributes'] = pd.io.json.loads(pd.io.json.dumps(row)) # ensures the values are converted correctly
            template['features'].append(gj)
        return pd.io.json.dumps(template)
    #----------------------------------------------------------------------
    @property
    def __feature_set__(self):
        """returns a dictionary representation of an Esri FeatureSet"""
        import arcgis
        cols_norm = [col for col in self._data.columns]
        cols_lower = [col.lower() for col in self._data.columns]
        fields = []
        features = []
        date_fields = []
        _geom_types = {
            arcgis.geometry._types.Point :  "esriGeometryPoint",
            arcgis.geometry._types.Polyline : "esriGeometryPolyline",
            arcgis.geometry._types.MultiPoint : "esriGeometryMultipoint",
            arcgis.geometry._types.Polygon : "esriGeometryPolygon"
        }
        if self.sr is None:
            sr = {'wkid' : 4326}
        else:
            sr = self.sr
        fs = {
            "objectIdFieldName" : "",
            "globalIdFieldName" : "",
            "displayFieldName" : "",
            "geometryType" : _geom_types[type(self._data[self._name][self._data[self._name].first_valid_index()])],
            "spatialReference" : sr,
            "fields" : [],
            "features" : []
        }
        if 'objectid' in cols_lower:
            fs['objectIdFieldName'] = cols_norm[cols_lower.index('objectid')]
            fs['displayFieldName'] = cols_norm[cols_lower.index('objectid')]
        elif 'fid' in cols_lower:
            fs['objectIdFieldName'] = cols_norm[cols_lower.index('fid')]
            fs['displayFieldName'] = cols_norm[cols_lower.index('fid')]
        elif 'oid' in cols_lower:
            fs['objectIdFieldName'] = cols_norm[cols_lower.index('oid')]
            fs['displayFieldName'] = cols_norm[cols_lower.index('oid')]
        else:
            self._data['OBJECTID'] = list(range(1, self._data.shape[0] + 1))
            res = self.__feature_set__
            del self._data['OBJECTID']
            return res
        if 'objectIdFieldName' in fs:
            fields.append({
                "name" : fs['objectIdFieldName'],
                "type" : "esriFieldTypeOID",
                "alias" : fs['objectIdFieldName']
            })
            cols_norm.pop(cols_norm.index(fs['objectIdFieldName']))
        if 'globalIdFieldName' in fs and len(fs['globalIdFieldName']) > 0:
            fields.append({
                "name" : fs['globalIdFieldName'],
                "type" : "esriFieldTypeGlobalID",
                "alias" : fs['globalIdFieldName']
            })
            cols_norm.pop(cols_norm.index(fs['globalIdFieldName']))
        elif 'globalIdFieldName' in fs and \
             len(fs['globalIdFieldName']) == 0:
            del fs['globalIdFieldName']
        if self._name in cols_norm:
            cols_norm.pop(cols_norm.index(self._name))
        for col in cols_norm:
            try:
                idx = self._data[col].first_valid_index()
                col_val = self._data[col].loc[idx]
            except:
                col_val = ""
            if isinstance(col_val, (str, np.str)):
                l = self._data[col].str.len().max()
                if str(l) == 'nan':
                    l = 255

                fields.append({
                    "name" : col,
                    "type" : "esriFieldTypeString",
                    "length" : int(l),
                    "alias" : col
                })
                if fs['displayFieldName'] == "":
                    fs['displayFieldName'] = col
            elif isinstance(col_val, (datetime.datetime,
                                      pd.Timestamp,
                                      np.datetime64,
                                      pd.datetime)):
                fields.append({
                    "name" : col,
                    "type" : "esriFieldTypeDate",
                    "alias" : col
                })
                date_fields.append(col)
            elif isinstance(col_val, (np.int32, np.int16, np.int8)):
                fields.append({
                    "name" : col,
                    "type" : "esriFieldTypeSmallInteger",
                    "alias" : col
                })
            elif isinstance(col_val, (int, np.int, np.int64)):
                fields.append({
                    "name" : col,
                    "type" : "esriFieldTypeInteger",
                    "alias" : col
                })
            elif isinstance(col_val, (float, np.float64)):
                fields.append({
                    "name" : col,
                    "type" : "esriFieldTypeDouble",
                    "alias" : col
                })
            elif isinstance(col_val, (np.float32)):
                fields.append({
                    "name" : col,
                    "type" : "esriFieldTypeSingle",
                    "alias" : col
                })
        fs['fields'] = fields
        for row in self._data.to_dict('records'):
            geom = {}
            if self._name in row:
                geom = row[self._name]
                del row[self._name]
            for f in date_fields:
                try:
                    row[f] = int(row[f].to_pydatetime().timestamp() * 1000)
                except:
                    row[f] = None
            features.append(
                {
                    "geometry" : dict(geom),
                    "attributes" : row
                }
            )
            del row
            del geom
        fs['features'] = features
        return fs
    #----------------------------------------------------------------------
    @property
    def sr(self):
        """gets/sets the spatial reference of the dataframe"""
        srs = pd.DataFrame([g['spatialReference'] \
                            for g in self._data[self._name]])['wkid'].unique().tolist()
        if len(srs) > 1:
            rsrs = []
            for sr in srs:
                if isinstance(sr, int):
                    rsrs.append(SpatialReference({'wkid' : sr}))
                else:
                    rsrs.append(SpatialReference({'wkt' : sr}))
            return rsrs
        else:
            return SpatialReference({'wkid' : srs[0]})
    #----------------------------------------------------------------------
    @sr.setter
    def sr(self, ref):
        """Sets the spatial reference"""
        sr = self.sr
        if 'wkid' in sr:
            wkid = sr['wkid']
        if 'wkt' in sr:
            wkt = sr['wkt']
        if isinstance(ref, SpatialReference):
            if ref != sr:
                self._data[self._name] = self._data[self._name].geom.project_as(ref)
        elif isinstance(ref, int):
            if ref != wkid:
                self._data[self._name] = self._data[self._name].geom.project_as(ref)
        elif isinstance(ref, str):
            if ref != wkt:
                self._data[self._name] = self._data[self._name].geom.project_as(ref)
        elif isinstance(ref, dict):
            nsr = SpatialReference(ref)
            if sr != nsr:
                self._data[self._name] = self._data[self._name].geom.project_as(ref)
    #----------------------------------------------------------------------
    def to_featureset(self):
        """
        Converts a spatial dataframe to a feature set object
        """
        from arcgis.features import FeatureSet
        return FeatureSet.from_dataframe(self._data)
    #----------------------------------------------------------------------
    def to_feature_collection(self,
                              name=None,
                              drawing_info=None,
                              extent=None,
                              global_id_field=None):
        """
        Converts a spatially enabled pd.DataFrame to a Feature Collection

        =====================  ===============================================================
        **optional argument**  **Description**
        ---------------------  ---------------------------------------------------------------
        name                   optional string. Name of the Feature Collection
        ---------------------  ---------------------------------------------------------------
        drawing_info           Optional dictionary. This is the rendering information for a
                               Feature Collection.  Rendering information is a dictionary with
                               the symbology, labelling and other properties defined.  See:
                               http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Renderer_objects/02r30000019t000000/
        ---------------------  ---------------------------------------------------------------
        extent                 Optional dictionary.  If desired, a custom extent can be
                               provided to set where the map starts up when showing the data.
                               The default is the full extent of the dataset in the Spatial
                               DataFrame.
        ---------------------  ---------------------------------------------------------------
        global_id_field        Optional string. The Global ID field of the dataset.
        =====================  ===============================================================

        :returns: FeatureCollection object
        """
        from arcgis.features import FeatureCollection
        import uuid
        import string
        import random

        if name is None:
            name = random.choice(string.ascii_letters) + uuid.uuid4().hex[:5]
        template = {
            'showLegend' : True,
            'layers' : []
        }
        if extent is None:
            ext = self.full_extent
            extent = {
                "xmin" : ext[0],
                "ymin" : ext[1],
                "xmax" : ext[2],
                "ymax" : ext[3],
                "spatialReference" : self.sr
            }
        fs = self.__feature_set__
        fields = []
        for fld in fs['fields']:
            if fld['name'].lower() == fs['objectIdFieldName'].lower():
                fld['editable'] = False
                fld['sqlType'] = "sqlTypeOther"
                fld['domain'] = None
                fld['defaultValue'] = None
                fld['nullable'] = False
            else:
                fld['editable'] = True
                fld['sqlType'] = "sqlTypeOther"
                fld['domain'] = None
                fld['defaultValue'] = None
                fld['nullable'] = True
        if drawing_info is None:
            di = {
                'renderer' : {
                    'labelingInfo' : None,
                    'label' : "",
                    'description' : "",
                    'type' : 'simple',
                    'symbol' : None

                }
            }
            symbol = None
            if symbol is None:
                if fs['geometryType'] in ["esriGeometryPoint", "esriGeometryMultipoint"]:
                    di['renderer']['symbol'] = {"color":[0,128,0,128],"size":18,"angle":0,
                                                "xoffset":0,"yoffset":0,
                                                "type":"esriSMS",
                                                "style":"esriSMSCircle",
                                                "outline":{"color":[0,128,0,255],"width":1,
                                                           "type":"esriSLS","style":"esriSLSSolid"}}
                elif fs['geometryType'] == 'esriGeometryPolyline':
                    di['renderer']['symbol'] = {
                        "type": "esriSLS",
                        "style": "esriSLSDot",
                        "color": [0,128,0,128],
                        "width": 1
                    }
                elif fs['geometryType'] == 'esriGeometryPolygon':
                    di['renderer']['symbol'] = {
                        "type": "esriSFS",
                        "style": "esriSFSSolid",
                        "color": [0,128,0,128],
                        "outline": {
                            "type": "esriSLS",
                            "style": "esriSLSSolid",
                            "color": [110,110,110,255],
                            "width": 1
                        }
                    }
            else:
                di['renderer']['symbol'] = symbol
        else:
            di = drawing_info
        layer = {
            'featureSet' : {'features' : fs['features'],
                            'geometryType' : fs['geometryType']
                            },
            'layerDefinition' : {
                'htmlPopupType' : 'esriServerHTMLPopupTypeNone',
                'objectIdField' : fs['objectIdFieldName'] or "OBJECTID",
                #'types' : [],
                'defaultVisibility' : True,
                'supportsValidateSql' : True,
                'supportsAttachmentsByUploadId' : True,
                'useStandardizedQueries' : False,
                'supportsApplyEditsWithGlobalIds' : True,
                'standardMaxRecordCount' : 32000,
                'supportsTruncate' : False,
                'extent' : extent,
                'maxScale' : 0,
                'supportsAppend' : True,
                'supportsCalculate' : True,
                'copyrightText' : "",
                #'templates' : [],
                'description' : "",
                #'relationships' : [],
                'supportsRollbackOnFailureParameter' : True,
                'hasM' : False,
                'displayField' : "",
                'drawingInfo' : di,
                'type' : 'Feature Layer',
                'supportedQueryFormats' : 'JSON, geoJSON',
                'isDataVersioned' : False,
                'maxRecordCount' : 2000,
                'minScale' : 0,
                'supportsStatistics' : True,
                'hasAttachments' : False,
                #'indexes' : [],
                'tileMaxRecordCount' : 8000,
                'supportsAdvancedQueries' : True,
                #'globalIdField' : "",
                'hasZ' : False,
                'name' : name,
                'id' : 0,
                'allowGeometryUpdates' : True,
                #'typeIdField' : "",
                'geometryType' : fs['geometryType'],
                'currentVersion' : 10.51,
                #'maxRecordCountFactor' : 1,
                'supportsCoordinatesQuantization' : True,
                'fields' : fs['fields'],
                'hasStaticData' : True,# False
                'capabilities' : 'Create,Delete,Query,Update,Editing,Extract,Sync',
                'advancedQueryCapabilities' :  {'supportsReturningGeometryCentroid': False,
                                                'supportsQueryRelatedPagination': True,
                                                'supportsHavingClause': True,
                                                'supportsOrderBy': True,
                                                'supportsPaginationOnAggregatedQueries': True,
                                                'supportsQueryWithDatumTransformation': True,
                                                'supportsAdvancedQueryRelated': True,
                                                'supportsOutFieldSQLExpression': True,
                                                'supportsPagination': True,
                                                'supportsStatistics': True,
                                                'supportsSqlExpression': True,
                                                'supportsQueryWithDistance': True,
                                                'supportsReturningQueryExtent': True,
                                                'supportsDistinct': True,
                                                'supportsQueryWithResultType': True},

            }
        }
        if global_id_field is not None:
            layer['layerDefinition']['globalIdField'] = global_id_field
        return FeatureCollection(layer)
    #----------------------------------------------------------------------
    @property
    def full_extent(self):
        """
        Returns the extent of the dataframe

        :returns: tuple

        >>> df.spatial.full_extent
        (-118, 32, -97, 33)

        """
        array = np.array(self._data[self._name].geom.geoextent.tolist())
        return (int(array[:,0].min()),
                int(array[:,1].min()),
                int(array[:,2].max()),
                int(array[:,3].max()))
    #----------------------------------------------------------------------
    @property
    def area(self):
        """
        Returns the total area of the dataframe

        :returns: float

        >>> df.spatial.area
        143.23427

        """
        return self._data[self._name].geom.area.sum()
    #----------------------------------------------------------------------
    @property
    def length(self):
        """
        Returns the total length of the dataframe

        :returns: float

        >>> df.spatial.length
        1.23427

        """
        return self._data[self._name].geom.length.sum()
    #----------------------------------------------------------------------
    @property
    def centroid(self):
        """
        Returns the centroid of the dataframe

        :returns: Geometry

        >>> df.spatial.centroid
        (-14.23427, 39)

        """
        df = pd.DataFrame(data=self._data[self._name].geom.centroid.tolist(), columns=['x','y'])
        return df['x'].mean(), df['y'].mean()
    #----------------------------------------------------------------------
    @property
    def true_centroid(self):
        """
        Returns the true centroid of the dataframe

        :returns: Geometry

        >>> df.spatial.true_centroid
        (1.23427, 34)

        """
        df = pd.DataFrame(data=self._data[self._name].geom.true_centroid.tolist(), columns=['x','y'])
        return df['x'].mean(), df['y'].mean()
    #----------------------------------------------------------------------
    @property
    def geometry_type(self):
        """
        Returns a list Geometry Types for the DataFrame
        """
        gt = self._data[self._name].geom.geometry_type
        return pd.unique(gt).tolist()
    #----------------------------------------------------------------------
    @property
    def bbox(self):
        """
        Returns the total length of the dataframe

        :returns: Polygon

        >>> df.spatial.bbox
        {'rings' : [[[1,2], [2,3], [3,3],....]], 'spatialReference' {'wkid': 4326}}
        """
        fe = self.full_extent
        return Geometry(
            {'rings' : [[[fe[0], fe[1]], [fe[0],fe[3]], [fe[2],fe[3]], [fe[2],fe[1]], [fe[0],fe[1]]]],
             'spatialReference' : self.sr})
    #----------------------------------------------------------------------
    def project(self, spatial_reference, transformation_name=None):
        """
        Reprojects the who dataset into a new spatial reference. This is an inplace operation meaning
        that it will update the defined geometry column from the `set_geometry`.

        ====================     ====================================================================
        **Argument**             **Description**
        --------------------     --------------------------------------------------------------------
        spatial_reference        Required SpatialReference. The new spatial reference. This can be a
                                 SpatialReference object or the coordinate system name.
        --------------------     --------------------------------------------------------------------
        transformation_name      Required String. The geotransformation name.
        ====================     ====================================================================

        :returns: boolean
        """
        try:
            self._data[self._name] = self._call_method(name='project_as',
                                                   is_ga=True,
                                                   **{'spatial_reference' : spatial_reference,
                                                      'transformation_name' : transformation_name})
            return True
        except:
            return False

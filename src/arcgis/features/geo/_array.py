import operator
import json
import numpy as np

from pandas.core.arrays import ExtensionArray
from pandas.core.dtypes.dtypes import ExtensionDtype
from arcgis.geometry import Geometry
import pandas as pd
from .parser import _to_geo_array



class NumPyBackedExtensionArrayMixin(ExtensionArray):
    """
    Geo-Specific Extension Array Mixin
    """
    @property
    def dtype(self):
        """The dtype for this extension array, GeoType"""
        return self._dtype

    @classmethod
    def _constructor_from_sequence(cls, scalars):
        return cls(scalars)

    @classmethod
    def _from_factorized(cls, values, original):
        return cls(values)

    @property
    def shape(self):
        return (len(self.data),)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, *args):
        result = operator.getitem(self.data, *args)
        if isinstance(result, (dict, Geometry)):
            return result
        elif not isinstance(result, GeoArray):
            return GeoArray(result)
        return result


    def setitem(self, indexer, value):
        """Set the 'value' inplace.
        """

        self[indexer] = value
        return self

    @property
    def nbytes(self):
        return self._itemsize * len(self)

    def _formatting_values(self):
        return np.array(self._format_values(), dtype='object')

    def copy(self, deep=False):
        return type(self)(self.data.copy())

    @classmethod
    def _concat_same_type(cls, to_concat):
        return cls(np.concatenate([array.data for array in to_concat]))

    def tolist(self):
        return self.data.tolist()

    def argsort(self, axis=-1, kind='quicksort', order=None):
        return self.data.argsort()

    def unique(self):
        _, indices = np.unique(self.data, return_index=True)
        data = self.data.take(np.sort(indices))
        return self._from_ndarray(data)


class GeoType(ExtensionDtype):
    name = 'geometry'
    type = Geometry
    kind = 'O'
    _record_type = np.dtype('O')
    na_value = None

    @classmethod
    def construct_from_string(cls, string):
        if string == cls.name:
            return cls()
        else:
            raise TypeError("Cannot construct a '{}' from "
                            "'{}'".format(cls, string))

class GeoArray(NumPyBackedExtensionArrayMixin):
    """Array for Geometry data.
    """
    _dtype = GeoType()
    _itemsize = 8
    ndim = 1
    can_hold_na = True

    def __init__(self, values, copy=True):
        self.data = np.array(values, dtype='O', copy=copy)

    @classmethod
    def _from_ndarray(cls, data, copy=False):
        return cls(data, copy=copy)

    @property
    def na_value(self):
        return self.dtype.na_value

    def __repr__(self):
        formatted = self._format_values()
        return "GeoArray({!r})".format(formatted)

    def __str__(self):
        return self.__repr__()

    def _format_values(self):
        return [_format(x) for x in self.data]

    @classmethod
    def from_geometry(cls, data, copy=False):
        """"""
        if copy:
            data = data.copy()
        new = GeoArray([])
        new.data = np.array(data)
        return new

    def __setitem__(self, key, value):
        value = Geometry(value)
        self.data[key] = value

    def __iter__(self):
        return iter(self.data.tolist())

    def __eq__(self, other):
        return self.data == other

    def equals(self, other):
        if not isinstance(other, type(self)):
            raise TypeError
        return (self.data == other.data).all()

    def _values_for_factorize(self):
        # Should hit pandas' UInt64Hashtable
        return self, 0

    def isna(self):
        return (self.data == self._dtype.na_value)

    @property
    def _parser(self):
        return lambda x: x

    def take(self, indexer, allow_fill=True, fill_value=None):
        mask = indexer == -1
        result = self.data.take(indexer)
        result[mask] = self.dtype.na_value
        return type(self)(result, copy=False)

    def _formatting_values(self):
        return np.array(self._format_values(), dtype='object')

    @classmethod
    def _concat_same_type(cls, to_concat):
        return cls(np.concatenate([array.data for array in to_concat]))

    def take_nd(self, indexer, allow_fill=True, fill_value=None):
        return self.take(indexer, allow_fill=allow_fill, fill_value=fill_value)

    def copy(self, deep=False):
        return type(self)(self.data.copy())

    from arcgis.geometry import BaseGeometry
    @property
    def is_valid(self):
        """Checks if the Geometry is Valid"""
        return pd.Series([g.is_valid for g in self])

    #----------------------------------------------------------------------
    def _call_property(self, prop, as_ga=False):
        """accesses a property on a dataframe"""
        vals = [getattr(g, prop, None) for g in self]
        if as_ga:
            s = pd.Series(GeoArray(values=vals))
        else:
            s = pd.Series(vals)
        s.name = prop
        return s
    #----------------------------------------------------------------------
    def _call_method(self, name, is_ga=True, **kwargs):
        """accesses method on the geometry object"""
        vals = [getattr(g, name, None)(**kwargs) for g in self]
        if is_ga:
            return pd.Series(GeoArray(vals))
        return pd.Series(vals)
    #----------------------------------------------------------------------
    @property
    def area(self):
        """returns the geometry area"""
        return self._call_property('area')
    #----------------------------------------------------------------------
    @property
    def as_arcpy(self):
        """returns the geometry area"""
        return self._call_property('as_arcpy')
    #----------------------------------------------------------------------
    @property
    def as_shapely(self):
        """returns the geometry area"""
        return self._call_property('as_shapely')
    #----------------------------------------------------------------------
    @property
    def centroid(self):
        """returns Geometry centroid"""
        return self._call_property('centroid')
    #----------------------------------------------------------------------
    @property
    def extent(self):
        """returns the extent of the geometry"""
        return self._call_property("extent")
    #----------------------------------------------------------------------
    @property
    def first_point(self):
        """
        The first coordinate point of the geometry for each entry.
        """
        return self._call_property("first_point", as_ga=True)
    #----------------------------------------------------------------------
    @property
    def geoextent(self):
        return self._call_property("geoextent")
    #----------------------------------------------------------------------
    @property
    def geometry_type(self):
        return self._call_property("geometry_type")
    #----------------------------------------------------------------------
    @property
    def hull_rectangle(self):
        return self._call_property("hull_rectangle")
    #----------------------------------------------------------------------
    @property
    def is_empty(self):
        return self._call_property("is_empty")
    #----------------------------------------------------------------------
    @property
    def is_multipart(self):
        return self._call_property("is_multipart")
    #----------------------------------------------------------------------
    @property
    def is_valid(self):
        return self._call_property("is_valid")
    #----------------------------------------------------------------------
    @property
    def JSON(self):
        return self._call_property("JSON")
    #----------------------------------------------------------------------
    @property
    def label_point(self):
        return self._call_property("label_point", as_ga=True)
    #----------------------------------------------------------------------
    @property
    def last_point(self):
        return self._call_property("last_point", as_ga=True)
    #----------------------------------------------------------------------
    @property
    def length(self):
        return self._call_property("length", as_ga=False)
    #----------------------------------------------------------------------
    @property
    def length3D(self):
        return self._call_property("length3D", as_ga=False)
    #----------------------------------------------------------------------
    @property
    def part_count(self):
        return self._call_property("part_count")
    #----------------------------------------------------------------------
    @property
    def point_count(self):
        return self._call_property("point_count")
    #----------------------------------------------------------------------
    @property
    def spatial_reference(self):
        return self._call_property("spatial_reference")
    #----------------------------------------------------------------------
    @property
    def true_centroid(self):
        return self._call_property("true_centroid", as_ga=True)
    #----------------------------------------------------------------------
    @property
    def WKB(self):
        return self._call_property("WKB")
    #----------------------------------------------------------------------
    @property
    def WKT(self):
        return self._call_property("WKT")



def _format(g):
    return json.dumps(g)


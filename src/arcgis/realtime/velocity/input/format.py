from . import *
from dataclasses import dataclass, asdict, field
from typing import Dict, Union, Optional, Any, ClassVar, TypeVar


# common keys used in the format configuration
_FORMAT_NAME_KEY = "formatName"

@dataclass
class _FormatBase(object):
    # abstract variables that need to be implemented by Derived Classes
    name: ClassVar[str]

    # methods to be implemented by every Format
    def _build(self) -> dict:
        """
        abstract method that needs to be implemented by derived class.
        :return: Configuration properties in a dictionary that will be used to make the Rest call to the backend application
        """
        raise NotImplementedError

    @classmethod
    def _from_config(cls, config: dict) -> object:
        raise NotImplementedError


@dataclass
class GeoRssFormat(_FormatBase):
    T = TypeVar('GeoRssFormat')
    name: ClassVar[str] = "geo-rss-format"

    # format keys
    _DATE_FORMAT_KEY: str = field(init=False, default=f"{name}.dateFormat")

    # this format's instance properties
    date_format: Optional[str] = None

    def _build(self) -> dict:
        result_dict = {_FORMAT_NAME_KEY: GeoRssFormat.name}
        if self.date_format is not None:
            result_dict |= {
                "properties": {
                    f"{GeoRssFormat.name}.{GeoRssFormat._DATE_FORMAT_KEY}": self.date_format
                }
            }

        return result_dict

    @classmethod
    def _from_config(cls, config: dict) -> T:
        properties = config["properties"]
        obj = cls(date_format=properties.get(GeoRssFormat._DATE_FORMAT_KEY))
        return obj

@dataclass
class RssFormat(_FormatBase):
    T = TypeVar('RssFormat')
    name: ClassVar[str] = "rss-format"

    # TODO: move all the Geometry fields to a base class so that it is common for all formats.
    # format keys
    _BUILD_GEOMETRY_FROM_FIELDS_KEY: str = field(init=False, default=f"{name}.buildGeometryFromFields")
    _X_FIELD_KEY: str = field(init=False, default=f"{name}.xField")
    _Y_FIELD_KEY: str = field(init=False, default=f"{name}.yField")
    _HAS_Z_FIELD_KEY_KEY: str = field(init=False, default=f"{name}.hasZField")
    _Z_FIELD_KEY: str = field(init=False, default=f"{name}.zField")
    _Z_UNIT_KEY: str = field(init=False, default=f"{name}.zUnit")
    _GEOMETRY_FIELD_KEY: str = field(init=False, default=f"{name}.geometryField")
    _GEOMETRY_FIELD_FORMAT_KEY: str = field(init=False, default=f"{name}.geometryFieldFormat")
    _DATE_FORMAT_KEY: str = field(init=False, default=f"{name}.dateFormat")

    # this format's instance properties
    build_geometry_from_fields: Optional[bool] = None
    x_field: Optional[str] = None
    y_field: Optional[str] = None
    has_z_field: Optional[bool] = None
    z_field: Optional[str] = None
    z_unit: Optional[int] = None
    geometry_field: Optional[str] = None
    geometry_field_format: Optional[str] = None
    date_format: Optional[str] = None

    def _build(self) -> dict:
        result_dict = {_FORMAT_NAME_KEY: self.name}
        properties_dict = {}

        if self.build_geometry_from_fields is not None:
            properties_dict[
                RssFormat._BUILD_GEOMETRY_FROM_FIELDS_KEY
            ] = self.build_geometry_from_fields
        if self.x_field is not None:
            properties_dict[RssFormat._X_FIELD_KEY] = self.x_field
        if self.y_field is not None:
            properties_dict[RssFormat._Y_FIELD_KEY] = self.y_field
        if self.has_z_field is not None:
            properties_dict[RssFormat._HAS_Z_FIELD_KEY_KEY] = self.has_z_field
        if self.z_field is not None:
            properties_dict[RssFormat._Z_FIELD_KEY] = self.z_field
        if self.z_unit is not None:
            properties_dict[RssFormat._Z_UNIT_KEY] = self.z_unit
        if self.geometry_field is not None:
            properties_dict[RssFormat._GEOMETRY_FIELD_KEY] = self.geometry_field
        if self.geometry_field_format is not None:
            properties_dict[
                RssFormat._GEOMETRY_FIELD_FORMAT_KEY
            ] = self.geometry_field_format
        if self.date_format is not None:
            properties_dict[_DATE_FORMAT_KEY] = self.date_format

        if bool(properties_dict):
            result_dict["properties"] = properties_dict

        return result_dict

    @classmethod
    def _from_config(cls, config: dict) -> T:
        properties = config["properties"]
        obj = RssFormat(
            build_geometry_from_fields=properties.get(
                RssFormat._BUILD_GEOMETRY_FROM_FIELDS_KEY
            ),
            x_field=properties.get(RssFormat._X_FIELD_KEY),
            y_field=properties.get(RssFormat._Y_FIELD_KEY),
            has_z_field=properties.get(RssFormat._HAS_Z_FIELD_KEY_KEY),
            z_field=properties.get(RssFormat._Z_FIELD_KEY),
            z_unit=properties.get(RssFormat._Z_UNIT_KEY),
            geometry_field=properties.get(RssFormat._GEOMETRY_FIELD_KEY),
            geometry_field_format=properties.get(RssFormat._GEOMETRY_FIELD_FORMAT_KEY),
            date_format=properties.get(RssFormat._DATE_FORMAT_KEY),
        )
        return obj


def _format_from_config(config: dict) -> Union[GeoRssFormat, RssFormat]:
    """
    Identifies and instantiates a format object from a feed configuration json dict
    :param config:
    :return:
    """
    if _FORMAT_NAME_KEY in config:
        if config[_FORMAT_NAME_KEY] == GeoRssFormat.name:
            return GeoRssFormat._from_config(config)
        elif config[_FORMAT_NAME_KEY] == RssFormat.name:
            return RssFormat._from_config(config)
        else:
            return None
    else:
        return None

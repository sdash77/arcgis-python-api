from dataclasses import dataclass, asdict, field
from typing import Dict, Union, Optional, Any, ClassVar


@dataclass(init=False, frozen=True)
class _Unit:
    _distance: ClassVar[Dict[str, int]] = {
        "Kilometers": 9036,
        "Meters": 9001,
        "Centimeters": 1033,
        "Millimeters": 1025,
        "Fathoms": 9014,
        "Miles": 9035,
        "NauticalMiles": 9030,
        "Yards": 9096,
        "Feet": 9003,
        "Inches": 109009,
    }

    @staticmethod
    def _validate_distance(key: str) -> None:
        allowed_z_units = _Unit._distance.keys()
        if key not in allowed_z_units:
            raise ValueError(
                f"`{key}` is an invalid distance unit. Allowed values are - {', '.join(allowed_z_units)}"
            )


@dataclass(frozen=True)
class SingleFieldGeometry:
    """
    :param geometry_field:
    :param geometry_type: esriGeometryPoint, esriGeometryPolyline, esriGeometryPolygon, esriGeometryMulti
    :param geometry_format: coordinates, esrijson, geojson, wkt
    :param wkid: default
    :return:
    """

    geometry_field: str
    geometry_type: str
    geometry_format: str
    wkid: int

    def __post_init__(self):
        allowed_geometry_types = [
            "esriGeometryPoint",
            "esriGeometryPolyline",
            "esriGeometryPolygon",
            "esriGeometryMulti",
        ]
        if self.geometry_type not in allowed_geometry_types:
            raise ValueError(
                f"`{self.geometry_type}` is an invalid geometry_type. Allowed values are - {', '.join(allowed_geometry_types)}"
            )

        allowed_geometry_formats = ["coordinates", "esrijson", "geojson", "wkt"]
        if self.geometry_format not in allowed_geometry_formats:
            raise ValueError(
                f"`{self.geometry_format}` is an invalid gemetry_type. Allowed values are - {', '.join(allowed_geometry_formats)}"
            )


@dataclass(frozen=True)
class XYZGeometry:
    """
    :param x_field:
    :param y_field:
    :param wkid:
    :param z_field:
    :param z_unit: allowed values - Kilometers, Meters, Centimeters, Millimeters, Fathoms, Miles, NauticalMiles, Yards, Feet, Inches
    :return:
    """

    x_field: str
    y_field: str
    wkid: int
    z_field: str = None
    z_unit: str = None

    def __post_init__(self):
        if self.z_field is not None:
            _Unit._validate_distance(self.z_unit)


class _HasGeometry:
    # ---> Inheriting classes MUST declare the following Optional fields. <---
    # These are commented variables because of a limitation in dataclass where base class properties get ordered before
    # the derived class properties. Since these are optional properties, the init will order them before the non-optional
    # derived class properties leading to errors like - TypeError: non-default argument 'rss_url' follows default argument
    #
    # geometry: Optional[Union[XYZGeometry, SingleFieldGeometry]] = None

    def set_geometry_config(
        self, geometry: Union[XYZGeometry, SingleFieldGeometry]
    ) -> bool:
        """
        Configures the geometry for a feed
        :param geometry: geometry object used to configure the feed
        :return: true if the operation is a success
        """
        if isinstance(geometry, XYZGeometry):
            self.data_format.x_field = geometry.x_field
            self.data_format.y_field = geometry.y_field
            if geometry.z_field is not None:
                self.data_format.has_z_field = True
                self.data_format.z_field = geometry.z_field
                if geometry.z_unit:
                    _Unit._validate_distance(geometry.z_unit)
                    z_unit_code = _Unit._distance.get(geometry.z_unit)
                    self.data_format.z_unit = z_unit_code
            self.data_format.build_geometry_from_fields = True

            self._fields["geometry"] = {
                "geometryType": "esriGeometryPoint",
                "spatialReference": {"wkid": geometry.wkid},
                "hasZ": self.data_format.has_z_field,
            }

            return True
        elif isinstance(geometry, SingleFieldGeometry):
            self.data_format.geometry_field = geometry.geometry_field
            self.data_format.geometry_field_format = geometry.geometry_format
            self.data_format.build_geometry_from_fields = False

            self._fields["geometry"] = {
                "geometryType": geometry.geometry_type,
                "spatialReference": {"wkid": geometry.wkid},
            }

            return True

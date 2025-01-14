from __future__ import annotations
import json
from arcgis.auth.tools import LazyLoader

_arcgis = LazyLoader("arcgis")
_arcgis_gis = LazyLoader("arcgis.gis")
_arcgis_gp = LazyLoader("arcgis.geoprocessing")
_arcgis_features = LazyLoader("arcgis.features")
_common_utils = LazyLoader("arcgis._impl.common._utils")


def snap_to_roads(
    points: _arcgis_features.FeatureSet | dict,
    travel_mode: str | None = None,
    return_lines: bool = True,
    road_properties_on_snapped_points: list | None = None,
    road_properties_on_lines: list | None = None,
    return_location_fields: bool = False,
    context: dict | None = None,
    gis: _arcgis_gis.GIS | None = None,
) -> tuple:
    """
    The Snap to Roads service can be used to snap a series of GPS track
    points to the underlying roads. You can return just the snapped points,
    or lines representing the roads that were traversed. In addition to the
    geometry, you can have the service return properties of the roads like
    the street name and posted speed limit in case you need this to perform
    route adherence.To use the snap to roads service, you need to pass in a
    set of point features that you want to snap to roads. In addition to
    the point geometry, you can include additional GPS-related data to
    better guide the snapping. You can also specify if you want to return
    properties from the underlying roads and if you want to aggregate them
    on the output points or lines returned.

    ======================================  ===========================================================================================================================================
    **Parameter**                           **Description**
    --------------------------------------  -------------------------------------------------------------------------------------------------------------------------------------------
    points                                  Required FeatureSet or Feature Layer. Specifies the points that you want to snap to the most likely road. These are typically the GPS
                                            points from a navigation device, the Field Maps feature service, or some other set of points that were collected while driving the vehicle.
                                            The distance between the points will affect the performance and final quality of the output. If the points are close together, the
                                            algorithm will have a better chance of deducing the probable roads at the expense of processing time. Fewer points will process faster, but
                                            may result in the route that was deduced potentially taking different roads. When specifying the points, you can set properties for each
                                            such as speed of the vehicle when the point was collected using attributes.
    --------------------------------------  -------------------------------------------------------------------------------------------------------------------------------------------
    travel_mode                             Optional dict.  Choose the mode of transportation, such as driving or walking for the analysis. Travel modes are essentially templates consisting of a long list of travel settings that are used by the service when snapping the input points to the roads that were traversed. The value for the travel_mode parameter should be a JSON object representing travel mode settings.
    --------------------------------------  -------------------------------------------------------------------------------------------------------------------------------------------
    return_lines                            Boolean. Specify whether or not the service will return lines representing the roads traversed. True-The output lines will be returned. False-The output lines will not be returned.
    --------------------------------------  -------------------------------------------------------------------------------------------------------------------------------------------
    road_properties_on_snapped_points       List[str]. Specify the names of the properties from the roads that you wish returned on the output snapped points.
    --------------------------------------  -------------------------------------------------------------------------------------------------------------------------------------------
    road_properties_on_lines                List[str]. Specify the road properties that the service should return on the output_lines output.
    --------------------------------------  -------------------------------------------------------------------------------------------------------------------------------------------
    return_location_fields                  Bool. Specify whether the service will return fields on the output_snapped_points and output_lines defining the snapped point's location with respect to the road.

                                            `True`-The output points and lines will contain these additional location fields and they will be populated.
                                            `false`-The location fields will not be included in the outputs.
    --------------------------------------  ------------------------------------------------------------------------------------------------------------------------------------------
    context                                     Optional dict. This parameter contains additional settings that affect task operation, for example, the spatial reference of the output features.
    --------------------------------------  ------------------------------------------------------------------------------------------------------------------------------------------
    gis                                     Optional, the :class:`~arcgis.gis.GIS` on which this tool runs. If not specified, the active GIS is used.
    ======================================  ===========================================================================================================================================
    """
    if gis is None:
        gis = _arcgis.env.active_gis
    if "snapToRoads" not in gis.properties["helperServices"]:
        raise Exception("GIS not configured with Snap To Roads.")
    url: str = gis.properties["helperServices"]["snapToRoads"]["url"]
    url = _common_utils._validate_url(url, gis)
    tbx = _arcgis_gp.import_toolbox(url, gis=gis)

    params = {
        "points": points,
        "travel_mode": json.dumps(travel_mode),
        "return_lines": return_lines,
        "road_properties_on_snapped_points": road_properties_on_snapped_points,
        "road_properties_on_lines": road_properties_on_lines,
        "return_location_fields": return_location_fields,
    }
    params = _common_utils.inspect_function_inputs(tbx.snap_to_roads, **params)
    return tbx.snap_to_roads(**params)

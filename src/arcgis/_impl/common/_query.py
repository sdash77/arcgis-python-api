from __future__ import annotations
from typing import Union, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from arcgis._impl.common._filters import GeometryFilter, StatisticFilter
from arcgis._impl.common._utils import _date_handler
from arcgis.geometry import Geometry
import concurrent.futures
import copy
from arcgis.auth.tools import LazyLoader

arcgis_features = LazyLoader("arcgis.features")


class QueryParameters(BaseModel):
    model_config = ConfigDict(
        extra="ignore", use_enum_values=True, populate_by_name=True
    )
    where: str = Field(
        "1=1",
        alias="where",
        description="""Optional string. SQL-92 WHERE clause syntax on the fields in the layer
                    is supported for most data sources. Some data sources have restrictions
                    on what is supported. Hosted feature services in ArcGIS Enterprise running
                    on a spatiotemporal data source only support a subset of SQL-92.
                    Below is a list of supported SQL-92 with spatiotemporal-based feature services:

                    ('<=' | '>=' | '<' | '>' | '=' | '!=' | '<>' | LIKE)
                    (AND | OR)
                    (IS | IS_NOT)
                    (IN | NOT_IN) ( '(' ( expr ( ',' expr )* )? ')' )
                    COLUMN_NAME BETWEEN LITERAL_VALUE AND LITERAL_VALUE
                    """,
    )
    out_fields: Optional[Union[str, list[str]]] = Field(
        "*",
        alias="outFields",
        description="""Optional list of fields to be included in the returned result set.
                    This list is a comma-delimited list of field names. You can also specify
                    the wildcard "*" as the value of this parameter. In this case, the query
                    results include all the field values.

                    .. note::
                        If specifying `return_count_only`, `return_id_only`, or `return_extent_only`
                        as True, do not specify this parameter in order to avoid errors.
                    """,
    )
    text: Optional[str] = Field(
        None,
        alias="text",
        description="Optional String. A literal search text. If the layer has a display field associated with it, the server searches for this text in this field. Only used when querying a Map Feature Layer.",
    )
    time_filter: Optional[list[datetime]] = Field(
        None,
        alias="timeFilter",
        description="""Optional list. The format is of [<startTime>, <endTime>] using
                    datetime.date, datetime.datetime or timestamp in milliseconds.
                    Syntax: time_filter=[<startTime>, <endTime>] ; specified as
                            datetime.date, datetime.datetime or timestamp in
                            milliseconds.
                    """,
    )
    geometry_filter: Optional[dict] = Field(
        None,
        alias="geometryFilter",
        description="Optional from :attr:`~arcgis.geometry.filters`. Allows for the information to be filtered on spatial relationship with another geometry.",
    )
    return_geometry: Optional[bool] = Field(
        True,
        alias="returnGeometry",
        description="Optional boolean. If true, geometry is returned with the query.",
    )
    return_count_only: Optional[bool] = Field(
        False,
        alias="returnCountOnly",
        strict=True,
        description="""Optional boolean. If true, the response only includes the count
                    (number of features/records) that would be returned by a query.
                    Otherwise, the response is a feature set. The default is false. This
                    option supersedes the returnIdsOnly parameter. If
                    returnCountOnly = true, the response will return both the count and
                    the extent.
                    """,
    )
    return_ids_only: Optional[bool] = Field(
        False,
        alias="returnIdsOnly",
        description="""Optional boolean. Default is False.  If true, the response only
                                            includes an array of object IDs. Otherwise, the response is a
                                            feature set. When object_ids are specified, setting this parameter to
                                            true is invalid.
                    """,
    )
    return_distinct_values: Optional[bool] = Field(
        False,
        alias="returnDistinctValues",
        description="""Optional boolean.  If true, it returns distinct values based on the
                    fields specified in out_fields. This parameter applies only if the
                    `supportsAdvancedQueries` property of the layer is true. This parameter
                    can be used with return_count_only to return the count of distinct
                    values of subfields.

                    .. note::
                        Make sure to set return_geometry to False if this is set to True.
                        Otherwise, reliable results will not be returned.
                    """,
    )
    return_extent_only: Optional[bool] = Field(
        False,
        alias="returnExtentOnly",
        description="""Optional boolean. If true, the response only includes the extent of
                    the features that would be returned by the query. If
                    returnCountOnly=true, the response will return both the count and
                    the extent.
                    The default is false. This parameter applies only if the
                    `supportsReturningQueryExtent` property of the layer is true.
                    """,
    )
    group_by_fields_for_statistics: Optional[str] = Field(
        None,
        alias="groupByFieldsForStatistics",
        description="""Optional string. One or more field names on which the values need to
                    be grouped for calculating the statistics.
                    example: STATE_NAME, GENDER
                    """,
    )
    statistic_filter: Optional[dict] = Field(
        None,
        alias="statisticFilter",
        description="""Optional ``StatisticFilter`` instance. The definitions for one or more field-based
                    statistics can be added, e.g. statisticType, onStatisticField, or
                    outStatisticFieldName.

                    Syntax:

                    sf = StatisticFilter()
                    sf.add(statisticType="count", onStatisticField="1", outStatisticFieldName="total")
                    sf.filter
                    """,
    )
    result_offset: Optional[int] = Field(
        None,
        alias="resultOffset",
        description="""Optional integer. This option can be used for fetching query results
                    by skipping the specified number of records and starting from the
                    next record (that is, resultOffset + 1th). This option is ignored
                    if return_all_records is True (i.e. by default).
                    """,
    )
    result_record_count: Optional[int] = Field(
        None,
        alias="resultRecordCount",
        description="""Optional integer. This option can be used for fetching query results
                    up to the result_record_count specified. When result_offset is
                    specified but this parameter is not, the map service defaults it to
                    max_record_count. The maximum value for this parameter is the value
                    of the layer's max_record_count property. This option is ignored if
                    return_all_records is True (i.e. by default).
                    """,
    )
    object_ids: Optional[Union[list[str], str]] = Field(
        None,
        alias="objectIds",
        description="""Optional string. The object IDs of this layer or table to be queried.
                    The object ID values should be a comma-separated string.

                    .. note::
                        There might be a drop in performance if the layer/table data
                        source resides in an enterprise geodatabase and more than
                        1,000 object_ids are specified.
                    """,
    )
    distance: Optional[int] = Field(
        None,
        alias="distance",
        description="""Optional integer. The buffer distance for the input geometries.
                    The distance unit is specified by units. For example, if the
                    distance is 100, the query geometry is a point, units is set to
                    meters, and all points within 100 meters of the point are returned.
                    """,
    )
    units: Optional[
        Literal[
            "esriSRUnit_Meter",
            "esriSRUnit_StatuteMile",
            "esriSRUnit_Foot",
            "esriSRUnit_Kilometer",
            "esriSRUnit_NauticalMile",
            "esriSRUnit_USNauticalMile",
        ]
    ] = Field(
        None,
        alias="units",
        description="""Optional string. The unit for calculating the buffer distance. If
                    unit is not specified, the unit is derived from the geometry spatial
                    reference. If the geometry spatial reference is not specified, the
                    unit is derived from the feature service data spatial reference.
                    This parameter only applies if `supportsQueryWithDistance` is true.
                    """,
    )
    max_allowable_offset: Optional[int] = Field(
        None,
        alias="maxAllowableOffset",
        description="""Optional float. This option can be used to specify the
                    max_allowable_offset to be used for generalizing geometries returned
                    by the query operation.
                    The max_allowable_offset is in the units of out_sr. If out_sr is not
                    specified, max_allowable_offset is assumed to be in the unit of the
                    spatial reference of the layer.
                    """,
    )
    out_sr: Optional[Union[dict[str, int], str, int]] = Field(
        None,
        alias="outSR",
        description="Optional Integer. The WKID for the spatial reference of the returned geometry.",
    )
    geometry_precision: Optional[int] = Field(
        None,
        alias="geometryPrecision",
        description="""Optional Integer. This option can be used to specify the number of
                    decimal places in the response geometries returned by the query
                    operation.
                    This applies to X and Y values only (not m or z-values).
                    """,
    )
    gdb_version: Optional[str] = Field(
        None,
        alias="gdbVersion",
        description="""Optional string. The geodatabase version to query. This parameter
                    applies only if the isDataVersioned property of the layer is true.
                    If this is not specified, the query will apply to the published
                    map's version.
                    """,
    )
    order_by_fields: Optional[str] = Field(
        None,
        alias="orderByFields",
        description="""Optional string. One or more field names on which the
                    features/records need to be ordered. Use ASC or DESC for ascending
                    or descending, respectively, following every field to control the
                    ordering.
                    example: STATE_NAME ASC, RACE DESC, GENDER

                    .. note::
                        If specifying `return_count_only`, `return_id_only`, or `return_extent_only`
                        as True, do not specify this parameter in order to avoid errors.
                    """,
    )
    out_statistics: Optional[list[dict[str, Any]]] = Field(
        None,
        alias="outStatistics",
        description="""Optional list of dictionaries. The definitions for one or more field-based
                    statistics to be calculated.

                    Syntax:

                    [
                        {
                            "statisticType": "<count | sum | min | max | avg | stddev | var>",
                            "onStatisticField": "Field1",
                            "outStatisticFieldName": "Out_Field_Name1"
                        },
                        {
                            "statisticType": "<count | sum | min | max | avg | stddev | var>",
                            "onStatisticField": "Field2",
                            "outStatisticFieldName": "Out_Field_Name2"
                        }
                    ]
                    """,
    )
    return_z: Optional[bool] = Field(
        False,
        alias="returnZ",
        description="Optional boolean. If true, Z values are included in the results if the features have Z values. Otherwise, Z values are not returned.",
    )
    return_m: Optional[bool] = Field(
        False,
        alias="returnM",
        description="Optional boolean. If true, M values are included in the results if the features have M values. Otherwise, M values are not returned.",
    )
    multipatch_option: Optional[tuple] = Field(
        None,
        alias="multipatchOption",
        description="Optional x/y footprint. This option dictates how the geometry of a multipatch feature will be returned.",
    )
    quantization_parameters: Optional[dict[str, Any]] = Field(
        None,
        alias="quantizationParameters",
        description="Optional dict. Used to project the geometry onto a virtual grid, likely representing pixels on the screen.",
    )
    return_centroid: Optional[bool] = Field(
        False,
        alias="returnCentroid",
        description="""Optional boolean. Used to return the geometry centroid associated
                    with each feature returned. If true, the result includes the geometry
                    centroid. The default is false. Only supported on layer with
                    polygon geometry type.
                    """,
    )
    return_all_records: Optional[bool] = Field(
        True,
        alias="returnAllRecords",
        description="""Optional boolean. When True, the query operation will call the
                    service until all records that satisfy the where_clause are
                    returned. Note: result_offset and result_record_count will be
                    ignored if return_all_records is True. Also, if return_count_only,
                    return_ids_only, or return_extent_only are True, this parameter
                    will be ignored. If this parameter is set to False but no other limit is
                    specified, the default is True.
                    """,
    )
    result_type: Optional[Literal["standard", "tile"]] = Field(
        None,
        alias="resultType",
        description="Optional string. The result_type parameter can be used to control the number of features returned by the query operation.",
    )
    historic_moment: Optional[Union[int, datetime]] = Field(
        None,
        alias="historicMoment",
        description="""Optional integer. The historic moment to query. This parameter
                    applies only if the layer is archiving enabled and the
                    supportsQueryWithHistoricMoment property is set to true. This
                    property is provided in the layer resource.

                    If historic_moment is not specified, the query will apply to the
                    current features.
                    """,
    )
    sql_format: Optional[Literal["standard", "native"]] = Field(
        None,
        alias="sqlFormat",
        description="""Optional string.  The sql_format parameter can be either standard
                    SQL92 standard or it can use the native SQL of the underlying
                    datastore native. The default is none which means the sql_format
                    depends on useStandardizedQuery parameter.
                    """,
    )
    return_true_curves: Optional[bool] = Field(
        False,
        alias="returnTrueCurves",
        description="""Optional boolean. When set to true, returns true curves in output
                    geometries. When set to false, curves are converted to densified
                    polylines or polygons.
                    """,
    )
    return_exceeded_limit_features: Optional[bool] = Field(
        None,
        alias="returnExceededLimitFeatures",
        description="""Optional boolean. Optional parameter which is true by default. When
                    set to true, features are returned even when the results include
                    'exceededTransferLimit': True.

                    When set to false and querying with resultType = tile features are
                    not returned when the results include 'exceededTransferLimit': True.
                    This allows a client to find the resolution in which the transfer
                    limit is no longer exceeded without making multiple calls.
                    """,
    )
    datum_transformation: Optional[Union[int, dict[str, Any]]] = Field(
        None,
        alias="datumTransformation",
        description="""Optional Integer/Dictionary.  This parameter applies a datum transformation while
                    projecting geometries in the results when out_sr is different than the layer's spatial
                    reference. When specifying transformations, you need to think about which datum
                    transformation best projects the layer (not the feature service) to the `outSR` and
                    `sourceSpatialReference` property in the layer properties. For a list of valid datum
                    transformation ID values ad well-known text strings, see `Coordinate systems and
                    transformations <https://developers.arcgis.com/net/latest/wpf/guide/coordinate-systems-and-transformations.htm>`_.
                    For more information on datum transformations, please see the transformation
                    parameter in the `Project operation <https://developers.arcgis.com/rest/services-reference/project.htm>`_.

                    **Examples**


                        ===========     ===================================
                        Inputs          Description
                        -----------     -----------------------------------
                        WKID            Integer. Ex: datum_transformation=4326
                        -----------     -----------------------------------
                        WKT             Dict. Ex: datum_transformation={"wkt": "<WKT>"}
                        -----------     -----------------------------------
                        Composite       Dict. Ex: datum_transformation=```{'geoTransforms':[{'wkid':<id>,'forward':<true|false>},{'wkt':'<WKT>','forward':<True|False>}]}```
                        ===========     ===================================
                    """,
    )
    range_values: Optional[dict[str, Any]] = Field(
        None,
        alias="rangeValues",
        description="""Optional List. Allows you to filter features from the layer that are
                    within the specified range instant or extent. Only used when querying a Map Feature Layer.

                    .. code-block:: python

                        >>> range_values = [
                                            {
                                                "name": "range name" ,
                                                # single value or a value-range
                                                "value": <value> or [ <value1>, <value2> ]

                                            },
                                            {
                                                "name": "range name 2",
                                                "value": <value> or  [ <value3>, <value4> ]
                                            }
                                            ]


                    .. note::

                        `None` is allowed in value-range case to indicate infinity

                        .. code-block:: python

                            # all features with values <= 1500
                            >>> range_values = [
                                                {"name" : "range name",
                                                    "value" : [None, 1500]}
                                                ]

                            # all features with values >= 1000
                            >>> range_values = [
                                                {"name" : "range name",
                                                    "value" : [1000, None]}
                                                ]
                    """,
    )
    parameter_values: Optional[dict[str, Any]] = Field(
        None,
        alias="parameterValues",
        description="""Optional Dict. Allows you to filter the layers by specifying
                    value(s) to an array of pre-authored parameterized filters for those
                    layers. When value is not specified for any parameter in a request,
                    the default value, that is assigned during authoring time, gets used
                    instead. Only used when querying a Map Feature Layer.

                    When a `parameterInfo` allows multiple values, you must pass them in
                    an array.

                    .. note::
                        Check `parameterValues` at the `Query (Map Service/Layer) <https://developers.arcgis.com/rest/services-reference/enterprise/query-map-service-layer-.htm#GUID-403AC0F3-4B48-45BD-B473-E52E790FD296>`_
                        for details on parameterized filters.
                    """,
    )
    format_3d_objects: Optional[
        Literal[
            "3D_dae",
            "3D_dwg",
            "3D_fbx",
            "3D_glb",
            "3D_gltf",
            "3D_ifc",
            "3D_obj",
            "3D_shapebuffer",
            "3D_shapebufferg",
            "3D_usdc",
            "3D_usdz",
        ]
    ] = Field(
        None,
        alias="formatOf3DObjects",
        description="""Optional string. Specifies the 3D format that will be used to request
                    a feature. If set to a valid format ID (see layer resource), the geometry
                    of the feature response will be a 3D envelope of the 3D object and will
                    include asset maps for the 3D object. Since formats are created asynchronously,
                    review the flags field in the asset map to determine if the format is available
                    (conversionStatus is COMPLETED). If conversionStatus is INPROGRESS, the format
                    is not ready. Request the feature again later.

                    If a feature does not have the specified format, the feature will still be returned
                    according to the query parameters (such as the where clause), but the
                    asset mapping will be missing.
                    """,
    )
    time_reference_unknown_client: Optional[bool] = Field(
        None,
        alias="timeReferenceUnknownClient",
        description="""Optional boolean. Setting `time_reference_unknown_client` as True
                    indicates that the client is capable of working with data values that
                    are not in UTC. If its not set to true, and the service layer's
                    datesInUnknownTimeZone property is true, then an error is returned.
                    The default is False

                    Its possible to define a service's time zone of date fields as unknown.
                    Setting the time zone as unknown means that date values will be returned
                    as-is from the database, rather than as date values in UTC. Non-hosted
                    feature services can be set to use an unknown time zone using
                    ArcGIS Server Manager. Setting the time zones to unknown also
                    sets the datesInUnknownTimeZone layer property as true. Currently,
                    hosted feature services do not support this setting. This setting does
                    not apply to editor tracking date fields which are stored and returned
                    in UTC even when the time zone is set to unknown.

                    Most clients released prior to ArcGIS Enterprise 10.9 will not be able
                    to work with feature services that have an unknown time setting.
                    """,
    )

    @field_validator("statistic_filter", mode="before")
    def validate_statistic_filter(cls, value):
        if value and isinstance(value, StatisticFilter):
            return value.filter  # Assumes `filter` is a method on StatisticFilter
        return value

    @field_validator("time_filter", mode="before")
    def validate_time_filter(cls, value):
        if isinstance(value, list):
            starttime = _date_handler(value[0])
            endtime = _date_handler(value[1])
            if starttime is None:
                starttime = "null"
            if endtime is None:
                endtime = "null"
            value = "%s,%s" % (starttime, endtime)
        return value

    @field_validator("geometry_filter", mode="before")
    def validate_geometry_filter(cls, value):
        if isinstance(value, GeometryFilter):
            return value.filter
        return value

    @field_validator("out_fields", mode="before")
    def validate_out_fields(cls, value):
        if isinstance(value, (list, tuple)):
            return ",".join(value)
        return value
    
    @field_validator("object_ids", mode="before")
    def validate_object_ids(cls, value):
        if isinstance(value, (list, tuple)):
            return ",".join(map(str,value))
        return value

    @model_validator(mode="before")
    def check_parameters(cls, values):
        # If either return_ids_only or return_count_only or return_extent_only is True, set return_all_records to False
        if (
            values.get("return_ids_only")
            or values.get("return_count_only")
            or values.get("return_extent_only")
            or values.get("result_record_count") is not None
        ):
            values["return_all_records"] = False

        # Check the conditions for order_by_fields
        if not values.get("return_all_records") or values.get("out_statistics") is None:
            if (
                values.get("return_count_only")
                or values.get("return_extent_only")
                or values.get("return_ids_only")
            ):
                # Set order_by_fields to None if the conditions are met
                values["order_by_fields"] = None

        return values


def _common_query(
    layer,
    is_layer: bool,
    parameters: QueryParameters,
    as_df: bool = False,
    query_3d: bool = False,
):
    raw = True if query_3d else False
    url = _get_url(layer, query_3d=query_3d)
    params = _create_parameters(
        layer=layer, is_layer=is_layer, parameters=parameters, query_3d=query_3d
    )

    # Two workflows: Return as FeatureSet or return as DataFrame
    if as_df:
        return _query_df(layer, url, params)
    else:
        return _query(layer, url, params, raw)


def _get_url(layer, query_3d: bool = False):
    if query_3d and hasattr(layer, "_is_3d") and layer._is_3d:
        url = layer._url + "/query3D"
    elif layer._dynamic_layer is None:
        url = layer._url + "/query"
    else:
        url = "%s/query" % layer._url.split("?")[0]
    return url


def _create_parameters(
    layer,
    is_layer: bool,
    parameters: QueryParameters,
    query_3d: bool,
):
    # create parameters dictionary
    params: dict[str, Any] = parameters.model_dump(
        mode="json", exclude_none=True, by_alias=True
    )
    params["f"] = "json"

    # add optional parameters
    if layer._dynamic_layer is not None:
        params["layer"] = layer._dynamic_layer

    # Remove parameters that are not supported by 3D feature query
    if query_3d:
        del params["returnDistinctValues"]
        del params["returnCountOnly"]
        del params["returnIdsOnly"]

    # Remove parameters that are not supported by table query
    if is_layer is False:
        del params["returnCentroid"]
        del params["returnExtentOnly"]
        del params["returnGeometry"]
        del params["returnZ"]
        del params["returnM"]

    # layer specific workflows
    if parameters.out_fields != "*" and parameters.return_distinct_values is False:
        try:
            # Check if object id field is in out_fields.
            # If it isn't, add it
            object_id_field = [
                x.name for x in layer.properties.fields if x.type == "esriFieldTypeOID"
            ][0]
            if object_id_field not in out_fields.split(","):
                out_fields = object_id_field + "," + out_fields
            # update out_fields parameter
            params["outFields"] = out_fields
        except (IndexError, AttributeError):
            pass

    if parameters.time_filter is None and layer.time_filter:
        params["time"] = layer.time_filter

    return params


def _query(layer, url, params, raw=False):
    """Returns results of the query for the provided layer and URL."""
    try:
        # Perform the initial query
        if params.get("objectIds"):
            result = {"features":_fetch_all_features_by_id(layer, url, params)}
        else:
            result = layer._con._session.get(url, params=params).json()
        return _process_query_result(result, params, raw, layer, url)
    except Exception as query_exception:
        return _handle_query_exception(query_exception, layer, url, params, raw)


def _process_query_result(result, params, raw, layer, url):
    """Processes the query result based on the parameters and handles pagination."""
    # Handle errors in the result
    if "error" in result:
        raise ValueError(result)

    # Determine the type of result to return
    if _is_true(params.get("returnCountOnly")):
        return result["count"]
    elif _is_true(params.get("returnIdsOnly")) or _is_true(
        params.get("returnExtentOnly")
    ):
        return result
    elif _is_true(raw):
        return result

    # Handle features and exceeded transfer limit
    features = result.get("features", [])
    if _needs_more_features(result, params, features):
        if params.get("resultOffset") or params.get("resultRecordCount") or params.get("objectIds"):
            # When a user specifies either of these we go by id to make it more efficient
            features = _fetch_all_features_by_id(layer, url, params)
        else:
            # A simple query to fetch features based on pagination
            features = _fetch_all_features_simple(layer, url, params, features, result)

    result["features"] = features
    return arcgis_features.FeatureSet.from_dict(result)


def _needs_more_features(result, params, features):
    """Checks if more features need to be fetched."""
    return result.get("exceededTransferLimit") or (params.get("resultRecordCount") and
        params.get("resultRecordCount") != len(features)
    )


# Works as multi-threaded but simple query
def _fetch_all_features_simple(layer, url, params, features, result):
    """Fetches all features by handling pagination."""
    original_offset = params.get("resultOffset", 0)

    page_size = 1000
    # Step 1: Preliminary query to determine total count
    if params.get("resultRecordCount") is None:
        count_params = copy.deepcopy(params)
        count_params["returnCountOnly"] = True
        count_params["returnAllRecords"] = False  # must be false when above True
        count_result = layer._con._session.get(url, params=count_params).json()
        total_count = count_result.get("count")
        params["resultRecordCount"] = page_size  # Adjust page size as necessary
    else:
        total_count = params.get("resultRecordCount")

    # Step 3: Define function to fetch a page of features
    def fetch_page(offset, params):
        page_params = copy.deepcopy(params)  # Copy params to avoid conflicts
        page_params["resultOffset"] = offset
        return layer._con._session.get(url, params=page_params).json()

    # Step 4: Use ThreadPoolExecutor to send multiple requests concurrently
    with concurrent.futures.ThreadPoolExecutor(5) as executor:
        futures = []
        # Calculate the number of requests needed, using page_size for offset increment
        for offset in range(original_offset + len(features), total_count, page_size):
            futures.append(executor.submit(fetch_page, offset, params))

        # Step 5: Process the results
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            features += result.get("features", [])

    return features


def _fetch_all_ids(layer, url, params):
    """Query to create a list of object ids."""
    ids = []
    id_params = copy.deepcopy(params)
    id_params["returnIdsOnly"] = True
    id_params["returnAllRecords"] = False  # must be false when above True
    original_offset = id_params.get("resultOffset", 0)

    # Get the total count of ids
    if id_params.get("resultRecordCount") is None:
        count_params = copy.deepcopy(params)
        count_params["returnCountOnly"] = True
        count_params["returnAllRecords"] = False  # must be false when above True
        count_result = layer._con._session.get(url, params=count_params).json()
        total_count = count_result.get("count")
    else:
        total_count = id_params.get("resultRecordCount")

    # Perform query until all ids are fetched
    while True:
        result = layer._con._session.get(url, params=id_params).json()
        ids.extend(result.get("objectIds", []))

        if len(ids) >= total_count:
            break
        id_params["resultOffset"] = original_offset + len(ids)
        if id_params.get("resultRecordCount") is not None:
            id_params["resultRecordCount"] = total_count - len(ids)
    return ids


def _fetch_all_features_by_id(layer, url, params):
    """Fetches all the features by handling pagination and uses the ids of the features."""
    features = []  # start from an empty list
    # Step 1: Query for all the ids using the parameters set
    ids = params.get("objectIds") or _fetch_all_ids(layer, url, params)
    params["resultRecordCount"] = (
        None  # we got the number of ids, so no need to limit the records
    )
    params["resultOffset"] = 0  # reset the offset to 0

    # Step 2: Define function to fetch a page of features
    def fetch_page(ids_subset):
        page_params = copy.deepcopy(params)
        page_params["objectIds"] = ids_subset
        return layer._con._session.get(url, params=page_params)

    # Step 3: Use ThreadPoolExecutor to send multiple requests concurrently
    with concurrent.futures.ThreadPoolExecutor(5) as executor:
        futures = []
        # Calculate the number of requests needed, using page_size for offset increment
        page_size = 100
        for i in range(0, len(ids), page_size):
            ids_subset = ",".join(str(i) for i in ids[i : i + page_size])
            futures.append(executor.submit(fetch_page, ids_subset))

        # Step 4: Process the results
        for future in concurrent.futures.as_completed(futures):
            result = future.result().json()
            features += result.get("features", [])
    return features


def _handle_query_exception(query_exception, layer, url, params, raw):
    """Handles exceptions raised during the query process."""
    error_messages = [
        "Error performing query operation",
        "HTTP Error 504: GATEWAY_TIMEOUT",
    ]

    if _is_invalid_token_error(query_exception):
        params.pop("token", None)
        return _query(layer, url, params, raw)

    if _is_known_error(query_exception, error_messages):
        return _retry_query_with_fewer_records(layer, url, params, raw)

    raise query_exception


def _is_invalid_token_error(exception):
    """Checks if the exception is due to an invalid token."""
    return (
        isinstance(exception.args[0], str)
        and "invalid token" in exception.args[0].lower()
    )


def _is_known_error(exception, error_messages):
    """Checks if the exception contains a known error message."""
    return any(msg in str(exception) for msg in error_messages)


def _retry_query_with_fewer_records(layer, url, params, raw):
    """Retries the query with a reduced result record count."""
    max_record = params.get("resultRecordCount", 1000)
    offset = params.get("resultOffset", 0)

    if max_record < 250:
        raise Exception("Max record count too low; query still failing.")

    result = None
    max_rec = (max_record + 1) // 2  # Halve the record count
    i = 0

    while max_rec * i < max_record:
        params["resultRecordCount"] = min(max_rec, max_record - max_rec * i)
        params["resultOffset"] = offset + max_rec * i

        try:
            records = _query(layer, url, params, raw=True)
            if result:
                result["features"].extend(records["features"])
            else:
                result = records
            i += 1
        except Exception as retry_exception:
            raise retry_exception

    return result


def _is_true(x):
    if isinstance(x, bool) and x:
        return True
    elif isinstance(x, str) and x.lower() == "true":
        return True
    else:
        return False


# ----------------------------------------------------------------------
def _query_df(layer, url, params, **kwargs):
    """returns results of a query as a pd.DataFrame"""
    import pandas as pd
    import numpy as np

    if [float(i) for i in pd.__version__.split(".")] < [1, 0, 0]:
        _fld_lu = {
            "esriFieldTypeSmallInteger": np.int32,
            "esriFieldTypeInteger": np.int32,
            "esriFieldTypeSingle": float,
            "esriFieldTypeDouble": float,
            "esriFieldTypeFloat": float,
            "esriFieldTypeString": str,
            "esriFieldTypeDate": pd.datetime,
            "esriFieldTypeOID": np.int64,
            "esriFieldTypeGeometry": object,
            "esriFieldTypeBlob": object,
            "esriFieldTypeRaster": object,
            "esriFieldTypeGUID": str,
            "esriFieldTypeGlobalID": str,
            "esriFieldTypeXML": object,
            "esriFieldTypeTimeOnly": pd.datetime,
            "esriFieldTypeDateOnly": pd.datetime,
            "esriFieldTypeTimestampOffset": pd.datetime,
        }
    else:
        _fld_lu = {
            "esriFieldTypeSmallInteger": pd.Int32Dtype(),
            "esriFieldTypeInteger": pd.Int32Dtype(),
            "esriFieldTypeSingle": pd.Float64Dtype(),
            "esriFieldTypeDouble": pd.Float64Dtype(),
            "esriFieldTypeFloat": pd.Float64Dtype(),
            "esriFieldTypeString": pd.StringDtype(),
            "esriFieldTypeDate": "<M8[ns]",
            "esriFieldTypeOID": pd.Int64Dtype(),
            "esriFieldTypeGeometry": object,
            "esriFieldTypeBlob": object,
            "esriFieldTypeRaster": object,
            "esriFieldTypeGUID": pd.StringDtype(),
            "esriFieldTypeGlobalID": pd.StringDtype(),
            "esriFieldTypeXML": object,
            "esriFieldTypeTimeOnly": pd.StringDtype(),
            "esriFieldTypeDateOnly": "<M8[ns]",
            "esriFieldTypeTimestampOffset": object,
            "esriFieldTypeBigInteger": pd.Int64Dtype(),
        }

    def feature_to_row(feature, sr):
        """:return: a feature from a dict"""
        geom = feature["geometry"] if "geometry" in feature else None
        attribs = feature["attributes"] if "attributes" in feature else {}
        if "centroid" in feature:
            if attribs is None:
                attribs = {"centroid": feature["centroid"]}
            elif "centroid" in attribs:
                import uuid

                fld = "centroid_" + uuid.uuid4().hex[:2]
                attribs[fld] = feature["centroid"]
            else:
                attribs["centroid"] = feature["centroid"]
        if geom:
            if "spatialReference" not in geom:
                geom["spatialReference"] = sr
            attribs["SHAPE"] = Geometry(geom)
        return attribs

    try:
        # Perform the initial query
        result = layer._con.post(url, params, token=layer._token)
        # Handle features and exceeded transfer limit
        features = result.get("features", [])
        if params.get("resultOffset") or params.get("resultRecordCount"):
            # When a user specifies either of these we go by id to make it more efficient
            features = _fetch_all_features_by_id(layer, url, params, result)
        else:
            # A simple query to fetch features based on pagination
            features = _fetch_all_features_simple(layer, url, params, features, result)

        result["features"] = features
    except Exception as query_exception:
        return _handle_query_exception(query_exception, layer, url, params, False)

    if len(result["features"]) == 0:
        # create columns even if empty dataframe
        columns = {}
        for fld in layer.properties.fields:
            fld = dict(fld)
            columns[fld["name"]] = _fld_lu[fld["type"]]
        if (
            "geometryType" in layer.properties
            and layer.properties.geometryType is not None
        ):
            columns["SHAPE"] = object
        if "return_geometry" in params and params["return_geometry"] == False:
            columns.pop("SHAPE", None)
        df = pd.DataFrame([], columns=columns.keys()).astype(columns, True)
        if "out_fields" in params and params["out_fields"] != "*":
            df = df[params["out_fields"].split(",")].copy()

        if "SHAPE" in df.columns:
            df["SHAPE"] = arcgis_features.geo._array.GeoArray([])
            df.spatial.set_geometry("SHAPE")
            df.spatial.renderer = layer.renderer
            df.spatial._meta.source = layer

        return pd.DataFrame([], columns=columns).astype(columns)
    sr = None
    if "spatialReference" in result:
        sr = result["spatialReference"]

    rows = [feature_to_row(row, sr) for row in result["features"]]
    if len(rows) == 0:
        return None
    df = pd.DataFrame.from_records(data=rows)
    # set based on layer
    df.spatial.renderer = layer.renderer
    df.spatial._meta.source = layer.url

    if "SHAPE" in df.columns:
        df.loc[df.SHAPE.isna(), "SHAPE"] = None
        df.spatial.set_geometry("SHAPE")

    # work with the fields and their data types
    dfields = []
    dtypes = {}
    if "fields" in result:
        fields = result["fields"]
        for fld in fields:
            if fld["type"] != "esriFieldTypeGeometry":
                dtypes[fld["name"]] = _fld_lu[fld["type"]]
            if fld["type"] in [
                "esriFieldTypeDate",
                "esriFieldTypeDateOnly",
                "esriFieldTypeTimestampOffset",
            ]:
                dfields.append(fld["name"])

    if len(dfields) > 0:
        for fld in [fld for fld in dfields if fld in df.columns]:
            if not pd.api.types.is_datetime64_any_dtype(df[fld]):
                try:
                    df[fld] = pd.to_datetime(
                        df[fld] / 1000,
                        errors="coerce",
                        unit="s",
                    )
                except Exception:
                    df[fld] = pd.to_datetime(
                        df[fld],
                        errors="coerce",
                    )

    if dtypes:
        df = df.astype(dtypes)

    return df

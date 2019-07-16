"""
The Summarize Data module contains functions that calculate total counts, lengths, areas, and basic descriptive statistics of features and their attributes within areas or near other features.

aggregate_points calculates statistics about points that fall within specified areas or bins.
join_features calculates statistics about features that share a spatial, temporal, or attribute relationship with other features.
reconstruct_tracks calculates statistics about points or polygons that belong to the same track and reconstructs inputs into tracks.
summarize_attributes calculates statistics about feature or tabular data that share attributes.
summarize_within calculates statistics for area features and attributes that overlap each other.
"""

import json as _json
import datetime
from datetime import datetime as _datetime
import logging as _logging
import arcgis as _arcgis
from arcgis.features import FeatureSet as _FeatureSet
from arcgis.geoprocessing._support import _execute_gp_tool
from arcgis.geoprocessing import DataFile
from ._util import _id_generator, _feature_input, _set_context, _create_output_service, GAJob

_log = _logging.getLogger(__name__)

# url = "https://dev003153.esri.com/gax/rest/services/System/GeoAnalyticsTools/GPServer"

_use_async = True

def build_multivariable_grid(input_layers,
                             variable_calculations,
                             bin_size,
                             bin_unit="Meters",
                             bin_type="Square",
                             output_name=None,
                             gis=None,
                             future=False):
    """

    .. image:: _static/images/Grid/Grid.png

    The ``build_multivariable_grid`` task works with one or more layers of point, line, or polygon features.
    The task generates a grid of square or hexagonal bins and compiles information about each input layer into each bin.
    For each input layer, this information can include the following variables:

        * ``Distance to Nearest`` - The distance from each bin to the nearest feature.
        * ``Attribute of Nearest`` - An attribute value of the feature nearest to each bin.
        * ``Attribute Summary of Related`` - A statistical summary of all features within ``search_distance`` of each bin.

    Only variables you specify in ``variable_calculations`` will be included in the result layer. These variables can help
    you understand the proximity of your data throughout the extent of your analysis. The results can help you answer
    questions such as the following:

        * Given multiple layers of public transportation infrastructure, what part of the city is least accessible by public transportation?
        * Given layers of lakes and rivers, what is the name of the water body closest to each location in the U.S.?
        * Given a layer of household income, where in the U.S. is the variation of income in the surrounding 50 miles the greatest?

    The result of ``build_multivariable_grid`` can also be used in prediction and classification workflows. The task allows you
    to calculate and compile information from many different data sources into a single, spatially continuous layer in one step.
    This layer can then be used with the Enrich From Multi-Variable Grid task to quickly enrich point features with the variables
    you have calculated, reducing the amount of effort required to build prediction and classification models from point data.

    ===================================================================    =============================================================================
    **Argument**                                                                                    **Description**
    -------------------------------------------------------------------    -----------------------------------------------------------------------------
    input_layers                                                           Required list of layers. A list of input layers that will be used in analysis.
                                                                           See :ref:`Feature Input<FeatureInput>`.
    -------------------------------------------------------------------    -----------------------------------------------------------------------------
    variable_calculations                                                  Required list of dicts. A dict containing objects that describe
                                                                           the variables that will be calculated for each layer in ``input_layers``.

                                                                           [
                                                                                {
                                                                                    "layer":<index>,
                                                                                    "variables":[
                                                                                        {
                                                                                            "type":"DistanceToNearest",
                                                                                            "outFieldName":"<output field name>",
                                                                                            "searchDistance":<number>,
                                                                                            "searchDistanceUnit":"<unit>",
                                                                                            "filter":"<filter>"
                                                                                        },
                                                                                        {
                                                                                            "type":"AttributeOfNearest",
                                                                                            "outFieldName":"<output field name>",
                                                                                            "attributeField":"<field name>",
                                                                                            "searchDistance":<number>,
                                                                                            "searchDistanceUnit":"<unit>",
                                                                                            "filter":"<filter>"
                                                                                        },
                                                                                        {
                                                                                            "type":"AttributeSummaryOfRelated",
                                                                                            "outFieldName":"<output field name>",
                                                                                            "statisticType":"<statistic type>",
                                                                                            "statisticField":"<field name>",
                                                                                            "searchDistance":<number>,
                                                                                            "searchDistanceUnit":"<unit>",
                                                                                            "filter":"<filter>"
                                                                                        },
                                                                                        ...
                                                                                    ]
                                                                                },
                                                                                ...
                                                                            ]

                                                                           layer is the index of the layer in ``input_layers`` that will be
                                                                           used to calculate the specified variables.

                                                                           Variables is an array of dict objects that describe the variables
                                                                           you want to include in the result layer. The array must contain at least
                                                                           one variable for each layer.

                                                                           type can be one of the following variable types:

                                                                                * DistanceToNearest
                                                                                * AttributeOfNearest
                                                                                * AttributeSummaryOfRelated

                                                                           Each type must be configured with a unique set of parameters:

                                                                            * ``outFieldName`` is the name of the field that will be created in the result
                                                                              layer to store a variable. This is required.
                                                                            * ``searchDistance`` and searchDistanceUnit are a number and linear unit.
                                                                              For DistanceToNearest and AttributeOfNearest, searchDistance and searchDistanceUnit
                                                                              are required and define the maximum distance that the tool will search from the
                                                                              center of each bin to find a feature in the layer. If no feature is within the
                                                                              distance, null is returned. For AttributeSummaryOfRelated, searchDistance and
                                                                              searchDistanceUnit are optional and define the radius of a circular neighborhood
                                                                              surrounding each bin. All features that intersect this neighborhood will be used
                                                                              to calculate statisticType. If a distance is not defined, only features that
                                                                              intersect a bin will be used to calculate statisticType.
                                                                            * ``attributeField`` is required by AttributeOfNearest and is the name of a field `
                                                                              in the input layer. The value of this field in the closest feature to each bin will
                                                                              be included in the result layer.
                                                                            * ``statisticField`` is required by AttributeSummaryOfRelated and is the name of a
                                                                              field in the input layer. This field's values will be used to calculate statisticType.
                                                                            * ``statisticType`` is required by AttributeSummaryOfRelated and is one of the following
                                                                              when statisticField is a numeric field:

                                                                                * ``Count`` - Totals the number of features near or intersecting each bin.
                                                                                * ``Sum`` - Adds the total value of all features near or intersecting each bin.
                                                                                * ``Mean`` - Calculates the average of all features near or intersecting each bin.
                                                                                * ``Min`` - Finds the smallest value of all features near or intersecting each bin.
                                                                                * ``Max`` - Finds the largest value of all features near or intersecting each bin.
                                                                                * ``Range`` - Finds the difference between Min and Max.
                                                                                * ``Stddev`` - Finds the standard deviation of all features near or intersecting each bin.
                                                                                * ``Var`` - Finds the variance of all features near or intersecting each bin.

                                                                            * ``statisticType`` is one of the following when statisticField is a string field:

                                                                                * Count Totals the number of strings for all features near or intersecting each bin.
                                                                                * Any Returns a sample string of all features near or intersecting each bin.

                                                                            * ``filter`` is optional for all variable types and is formatted as described in the Feature Input topic.
    -------------------------------------------------------------------    -----------------------------------------------------------------------------
    bin_size                                                               Required float. The distance for the bins of type ``bin_type`` in the output polygon layer.
                                                                           ``variable_calculations`` will be calculated at the center of each bin. When generating bins,
                                                                           for Square, the number and units specified determine the height and length of the square.
                                                                           For Hexagon, the number and units specified determine the distance between parallel sides.
    -------------------------------------------------------------------    -----------------------------------------------------------------------------
    bin_unit                                                               Optional string. The distance unit for the bins that will be used to calculate ``variable_calculations``.

                                                                           Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']
    -------------------------------------------------------------------    -----------------------------------------------------------------------------
    bin_type                                                               Optional string. The type of bin that will be used to generate the result grid. Bin options are the following:

                                                                           Choice list: ['Hexagon', 'Square']

                                                                           .. Note::
                                                                            Analysis using Square or Hexagon bins requires a projected coordinate system.
                                                                            When aggregating layers into bins, the input layers or processing extent (``processSR``)
                                                                            must have a projected coordinate system. If a projected coordinate system is not
                                                                            specified when running analysis, the World Cylindrical Equal Area (WKID 54034) projection
                                                                            will be used. At 10.7 or later, if a projected coordinate system is not specified when
                                                                            running analysis, a projection will be picked based on the extent of the data.
    -------------------------------------------------------------------    -----------------------------------------------------------------------------
    output_name                                                            Optional string. The task will create a feature service of the results. You define the name of the service.
    -------------------------------------------------------------------    -----------------------------------------------------------------------------
    context                                                                Optional string. The context parameter contains additional settings that affect task execution. For this task, there are four settings:

                                                                           #. Extent (``extent``) A bounding box that defines the analysis area. Only those features that intersect the bounding box will be analyzed.
                                                                           #. Processing spatial reference (``processSR``) The features will be projected into this coordinate system for analysis.
                                                                           #. Output spatial reference (``outSR``) The features will be projected into this coordinate system after the analysis to be saved. The output spatial reference for the spatiotemporal big data store is always WGS84.
                                                                           #. Data store (``dataStore``) Results will be saved to the specified data store. The default is the spatiotemporal big data store.
    ===================================================================    =============================================================================

    :returns: boolean

    .. code-block:: python

            # Usage Example: To create multivariable grid by summarizing information such as distance to nearest

            variables = [ { "layer":0,
                            "variables":[
                                { "type":"DistanceToNearest",
                                  "outFieldName":"road",
                                  "searchDistance":10,
                                  "searchDistanceUnit":"Kilometers"
                                }
                            ]
                          },
                          { "layer":1,
                          "variables":[
                              { "type":"AttributeSummaryOfRelated",
                                "outFieldName":"MeanPopAge",
                                "statisticType":"Mean",
                                "statisticField":"Age",
                                "searchDistance":50,
                                "searchDistanceUnit":"Kilometers"
                              }
                          ]
                          }
                        ]
            grid = build_multivariable_grid(input_layers=[lyr0, lyr1],
                                            variable_calculations=variables,
                                            bin_size=100,
                                            bin_unit='Meters',
                                            bin_type='Square',
                                            output_name="multi_variable_grid")
    """
    kwargs=locals()

    gis=_arcgis.env.active_gis if gis is None else gis
    url=gis.properties.helperServices.geoanalytics.url

    params={}
    for key, value in kwargs.items():
        if key == 'variable_calculations':
            import json
            params[key] = json.dumps(value)
        elif value is not None:
            params[key]=value

    if output_name is None:
        output_service_name='Build Multi Variable Grid_' + _id_generator()
        output_name=output_service_name.replace(' ', '_')
    else:
        output_service_name=output_name.replace(' ', '_')

    output_service=_create_output_service(gis, output_name, output_service_name, 'Build Multi Variable Grid ')

    params['output_name']=_json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db={
        "input_layers": (_FeatureSet, "inputLayers"),
        "variable_calculations" : (str, "variableCalculations"),
        "bin_type": (str, "binType"),
        "bin_size": (float, "binSize"),
        "bin_unit": (str, "binSizeUnit"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values=[
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        if future:

            gpjob = _execute_gp_tool(gis, "BuildMultiVariableGrid", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, "BuildMultiVariableGrid", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise


def aggregate_points(point_layer,
                     bin_type=None,
                     bin_size=None,
                     bin_size_unit=None,
                     polygon_layer=None,
                     time_step_interval=None,
                     time_step_interval_unit=None,
                     time_step_repeat_interval=None,
                     time_step_repeat_interval_unit=None,
                     time_step_reference=None,
                     summary_fields=None,
                     output_name=None,
                     gis=None,
                     future=False):
    """
    .. image:: _static/images/aggregate_points/aggregate_points.png

    This ``aggregate_points`` tool works with a layer of point features and a layer of areas.
    The layer of areas can be an input polygon layer or it can be square or hexagonal bins calculated
    when the task is run. The tool first determines which points fall within each specified area.
    After determining this point-in-area spatial relationship, statistics about all points in the
    area are calculated and assigned to the area. The most basic statistic is the count of the
    number of points within the area, but you can get other statistics as well.

    For example, suppose you have point features of coffee shop locations and area features of counties,
    and you want to summarize coffee sales by county. Assuming the coffee shops have a TOTAL_SALES attribute,
    you can get the sum of all TOTAL_SALES within each county, the minimum or maximum TOTAL_SALES within each
    county, or other statistics like the count, range, standard deviation, and variance.

    This tool can also work on data that is time-enabled. If time is enabled on the input points, then
    the time slicing options are available. Time slicing allows you to calculate the point-in area relationship
    while looking at a specific slice in time. For example, you could look at hourly intervals, which would
    result in outputs for each hour.

    For an example with time, suppose you had point features of every transaction made at a coffee shop location and no area layer.
    The data has been recorded over a year, and each transaction has a location and a time stamp. Assuming each transaction has a
    TOTAL_SALES attribute, you can get the sum of all TOTAL SALES within the space and time of interest. If these transactions are
    for a single city, we could generate areas that are one kilometer grids, and look at weekly time slices to summarize the
    transactions in both time and space.

    =================================================     ========================================================================
    **Argument**                                          **Description**
    -------------------------------------------------     ------------------------------------------------------------------------
    point_layer                                           Required point feature layer. The point features that will be aggregated
                                                          into the polygons in the ``polygon_layer`` or bins of the specified ``bin_size``.
                                                          See :ref:`Feature Input<FeatureInput>`.
    -------------------------------------------------     ------------------------------------------------------------------------
    bin_type                                              Optional string. If ``polygon_layer`` is not defined, it is required.

                                                          The type of bin that will be generated and into which points will be aggregated.

                                                          Choice list:['Square', 'Hexagon'].

                                                          The default value is "Square".

                                                          When generating bins for Square, the number and units specified determine the height
                                                          and length of the square. For Hexagon, the number and units specified determine the
                                                          distance between parallel sides. Either ``bin_type`` or ``polygon_layer`` must be specified.
                                                          If ``bin_type`` is chosen, ``bin_size`` and ``bin_size_unit`` specifying the size of the bins must be included.
    -------------------------------------------------     ------------------------------------------------------------------------
    bin_size (Required if ``bin_type`` is used)           Optional float. The distance for the bins of type binType that
                                                          the ``point_layer`` will be aggregated into. When generating bins, for Square,
                                                          the number and units specified determine the height and length of the square.
                                                          For Hexagon, the number and units specified determine the distance between parallel sides.
    -------------------------------------------------     ------------------------------------------------------------------------
    bin_size_unit (Required if ``bin_size`` is used)      Optional string. The distance unit for the bins that the ``point_layer`` will be aggregated into.

                                                          Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

                                                          When generating bins for Square, the number and units specified determine the height and
                                                          length of the square. For Hexagon, the number and units specified determine the distance
                                                          between parallel sides. Either ``bin_type`` or ``polygon_layer`` must be specified.
                                                          If ``bin_type`` is chosen, ``bin_size`` and ``bin_size_unit`` specifying the size of the bins must be included.
    -------------------------------------------------     ------------------------------------------------------------------------
    polygon_layer                                         Optional polygon feature layer. The polygon features (areas) into which the input points will be aggregated.
                                                          See :ref:`Feature Input<FeatureInput>`.

                                                          One of ``polygon_layer`` or bins ``bin_size`` and  ``bin_size_unit`` is required.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_interval                                    Optional integer. A numeric value that specifies duration of the time step interval. This option is only
                                                          available if the input points are time-enabled and represent an instant in time.

                                                          The default value is 'None'.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_interval_unit                               Optional string. A string that specifies units of the time step interval. This option is only available if the
                                                          input points are time-enabled and represent an instant in time.

                                                          Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

                                                          The default value is 'None'.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_repeat_interval                             Optional integer. A numeric value that specifies how often the time step repeat occurs.
                                                          This option is only available if the input points are time-enabled and of time type instant.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_repeat_interval_unit                        Optional string. A string that specifies the temporal unit of the step repeat.
                                                          This option is only available if the input points are time-enabled and of time type instant.

                                                          Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

                                                          The default value is 'None'.
    -------------------------------------------------     ------------------------------------------------------------------------
    time_step_reference                                   Optional datetime. A date that specifies the reference time to align the time slices to, represented in milliseconds from epoch.
                                                          The default is January 1, 1970, at 12:00 a.m. (epoch time stamp 0). This option is only available if the
                                                          input points are time-enabled and of time type instant.
    -------------------------------------------------     ------------------------------------------------------------------------
    summary_fields                                        Optional list of dicts. A list of field names and statistical summary types that you want to calculate
                                                          for all points within each polygon or bin. Note that the count of points within each polygon is always
                                                          returned. By default, all statistics are returned.

                                                          Example: [{"statisticType": "Count", "onStatisticField": "fieldName1"}, {"statisticType": "Any", "onStatisticField": "fieldName2"}]

                                                          fieldName is the name of the fields in the input point layer.

                                                          statisticType is one of the following for numeric fields:

                                                              * ``Count`` -Totals the number of values of all the points in each polygon.
                                                              * ``Sum`` -Adds the total value of all the points in each polygon.
                                                              * ``Mean`` -Calculates the average of all the points in each polygon.
                                                              * ``Min`` -Finds the smallest value of all the points in each polygon.
                                                              * ``Max`` -Finds the largest value of all the points in each polygon.
                                                              * ``Range`` -Finds the difference between the Min and Max values.
                                                              * ``Stddev`` -Finds the standard deviation of all the points in each polygon.
                                                              * ``Var`` -Finds the variance of all the points in each polygon.

                                                          statisticType is one of the following for string fields:

                                                              * ``Count`` -Totals the number of strings for all the points in each polygon.
                                                              * ``Any` `-Returns a sample string of a point in each polygon.
    -------------------------------------------------     ------------------------------------------------------------------------
    output_name                                           Optional string. The method will create a feature service of the results. You define the name of the service.
    -------------------------------------------------     ------------------------------------------------------------------------
    gis                                                   Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------------------------------     ------------------------------------------------------------------------
    context                                               Optional dict. The context parameter contains additional settings that affect task execution. For this task, there are four settings:

                                                              * Extent (``extent``) A bounding box that defines the analysis area. Only those features that intersect the bounding box will be analyzed.
                                                              * Processing spatial reference (``processSR``) The features will be projected into this coordinate system for analysis.
                                                              * Output spatial reference (``outSR``) The features will be projected into this coordinate system after the analysis to be saved. The output spatial reference for the spatiotemporal big data store is always WGS84.
                                                              * Data store (``dataStore``) Results will be saved to the specified data store. The default is the spatiotemporal big data store.
    -------------------------------------------------     ------------------------------------------------------------------------
    future                                                optional Boolean. If True, a GPJob is returned instead of
                                                          results. The GPJob can be queried on the status of the execution.
    =================================================     ========================================================================

    :returns: result_layer : Output Features as feature layer item.

    .. code-block:: python

            # Usage Example: To aggregate number of 911 calls within 1 km summarized by Day count.

            agg_result = aggregate_points(calls,
                                          bin_size=1,
                                          bin_size_unit='Kilometers',
                                          time_step_interval=1,
                                          time_step_interval_unit="Years",
                                          summary_fields=[{"statisticType": "Count", "onStatisticField": "Day"}],
                                          output_name='testaggregatepoints01')
    """

    kwargs = locals()

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url

    params = {}
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Aggregate Points Analysis_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Aggregate Points')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})
    if isinstance(summary_fields, list):
        import json
        summary_fields = json.dumps(summary_fields)
    _set_context(params)

    param_db = {
        "point_layer": (_FeatureSet, "pointLayer"),
        "bin_type": (str, "binType"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "polygon_layer": (_FeatureSet, "polygonLayer"),
        "time_step_interval": (int, "timeStepInterval"),
        "time_step_interval_unit": (str, "timeStepIntervalUnit"),
        "time_step_repeat_interval": (int, "timeStepRepeatInterval"),
        "time_step_repeat_interval_unit": (str, "timeStepRepeatIntervalUnit"),
        "time_step_reference": (_datetime, "timeStepReference"),
        "summary_fields": (str, "summaryFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        _execute_gp_tool(gis, "AggregatePoints", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise

aggregate_points.__annotations__ = {
                     'bin_type': str,
                     'bin_size': float,
                     'bin_size_unit': str,
                     'time_step_interval': int,
                     'time_step_interval_unit': str,
                     'time_step_repeat_interval': int,
                     'time_step_repeat_interval_unit': str,
                     'time_step_reference': _datetime,
                     'summary_fields': str,
                     'output_name': str
                }

def describe_dataset(input_layer,
                     extent_output=False,
                     sample_size=None,
                     output_name=None,
                     gis=None,
                     future=False):
    """
    The Describe Dataset task provides an overview of your big data. The tool outputs a JSON
    detailing the input layer's geometry and time settings, schema, and summary statistics for each
    field. Optionally, the tool can output two types of descriptive feature layers: a feature layer
    representing a sample of your input features, and a single polygon feature layer that
    represents the extent of the input features. You can choose to output one or both.

        Usage Notes:

        Only available at ArcGIS Enterprise 10.7 and later.

    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    input_layer       required FeatureLayer. The point, line or polygon features.
    ----------------  ---------------------------------------------------------------
    extent_output     Optional Boolean. The task will output a single rectangle
                      feature representing the extent of the input_layer if this value
                      is set to true. The default is False.
    ----------------  ---------------------------------------------------------------
    sample_size       Optional integer. The task will output a feature layer
                      representing a sample of features from the input_layer. Specify
                      the number of sample features to return. If the input value is
                      0 or empty then no sample layer will be created. The output
                      will have the same schema, geometry, and time type as the input
                      layer. The default is None.
    ----------------  ---------------------------------------------------------------
    output_name       optional string. The task will create a feature service of the results. You define the name of the service.
    ----------------  ---------------------------------------------------------------
    gis               optional GIS. The GIS object where the analysis will take place.
    ----------------  ---------------------------------------------------------------
    future            optional Boolean. If True, a GPJob is returned instead of
                      results. The GPJob can be queried on the status of the execution.
    ================  ===============================================================

    :returns: FeatureLayer

    """
    kwargs = locals()
    tool_name = "DescribeDataset"
    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url
    params = {
        "f" : "json",
    }
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Describe_Dataset_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Merge Layers')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "extent_output" : (bool, "extentOutput"),
        "sample_size" : (int, "sampleSize"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "output"),
    }

    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        if future:
            gpjob = _execute_gp_tool(gis, tool_name, params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, tool_name, params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise
    return


def join_features(target_layer,
                  join_layer,
                  join_operation = """JoinOneToOne""",
                  join_fields = None,
                  summary_fields = None,
                  spatial_relationship = None,
                  spatial_near_distance = None,
                  spatial_near_distance_unit = None,
                  temporal_relationship = None,
                  temporal_near_distance = None,
                  temporal_near_distance_unit = None,
                  attribute_relationship = None,
                  join_condition = None,
                  output_name = None,
                  gis=None,
                  future=False):
    """
    Using either feature layers or tabular data, you can join features and records based on
    specific relationships between the input layers or tables. Joins will be determined by
    spatial, temporal, and attribute relationships, and summary statistics can be optionally
    calculated.

    For example

    * Given point locations of crime incidents with a time, join the crime data to itself
      specifying a spatial relationship of crimes within 1 kilometer of each other and that
      occurred within 1 hour of each other to determine if there are a sequence of crimes
      close to each other in space and time.

    * Given a table of ZIP Codes with demographic information and area features representing
      residential buildings, join the demographic information to the residences so each
      residence now has the information.

    The Join Features task works with two layers. Join Features joins attributes from one
    feature to another based on spatial, temporal, and attribute relationships or some
    combination of the three. The tool determines all input features that meet the specified
    join conditions and joins the second input layer to the first. You can optionally join
    all features to the matching features or summarize the matching features.

    Join Features can be applied to points, lines, areas, and tables. A temporal join
    requires that your input data is time-enabled, and a spatial join requires that your
    data has a geometry.


    ================================  ===============================================================
    **Argument**                      **Description**
    --------------------------------  ---------------------------------------------------------------
    target_layer                      Required FeatureLayer. Target Features (feature input)
    --------------------------------  ---------------------------------------------------------------
    join_layer                        Required FeatureLayer. Join Features (feature input).
    --------------------------------  ---------------------------------------------------------------
    join_operation                    Required String. The join operation. Allowed values:
                                      JoinOneToOne and JoinOneToMany
    --------------------------------  ---------------------------------------------------------------
    join_fields                       Optional String. Join Fields
    --------------------------------  ---------------------------------------------------------------
    summary_fields                    Optional String. Summary Statistics
    --------------------------------  ---------------------------------------------------------------
    spatial_relationship              Optional String. The spatial relationship. Choice list: ['Equals',
                                      'Intersects', 'Contains', 'Within', 'Crosses', 'Touches',
                                      'Overlaps', 'Near', 'NearGeodesic']
    --------------------------------  ---------------------------------------------------------------
    spatial_near_distance             Optional Float. Near Spatial Distance. This is required if the
                                      `spatial_relationship` is defined as `NearGeodesic`.
    --------------------------------  ---------------------------------------------------------------
    spatial_near_distance_unit        Optional String. Near Spatial Distance Unit. This is required
                                      if the `spatial_relationship` is defined as `NearGeodesic`.
                                      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers',
                                                   'NauticalMiles']
    --------------------------------  ---------------------------------------------------------------
    temporal_relationship             Optional String. Temporal Relationship.
                                      Choice list : ['Equals', 'Intersects', 'During', 'Contains',
                                                     'Finishes', 'FinishedBy', 'Meets', 'MetBy',
                                                     'Overlaps', 'OverlappedBy', 'Starts',
                                                     'StartedBy', 'Near']
    --------------------------------  ---------------------------------------------------------------
    temporal_near_distance            Optional Integer. Near Temporal Distance (int)
    --------------------------------  ---------------------------------------------------------------
    temporal_near_distance_unit       Optional String.Near Temporal Distance Unit
                                      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours',
                                                  'Minutes', 'Seconds', 'Milliseconds']
    --------------------------------  ---------------------------------------------------------------
    attribute_relationship            Optional String. Attribute Relationships
    --------------------------------  ---------------------------------------------------------------
    join_condition                    Optional String. Join Condition
    --------------------------------  ---------------------------------------------------------------
    output_name                       Optional String. The task will create a feature service of the
                                      results. You define the name of the service.
    --------------------------------  ---------------------------------------------------------------
    gis                               Optional GIS. The GIS object where the analysis will take place.
    --------------------------------  ---------------------------------------------------------------
    future                            Optional Boolean. If True, a GPJob is returned instead of
                                      results. The GPJob can be queried on the status of the execution.
    ================================  ===============================================================



    :Returns: Output Features as Feature Layer Collection Item


    """
    kwargs = locals()

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url

    params = {}
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Join Features Analysis_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Join Features')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db = {
        "target_layer": (_FeatureSet, "targetLayer"),
        "join_layer": (_FeatureSet, "joinLayer"),
        "join_operation": (str, "joinOperation"),
        "join_fields": (str, "joinFields"),
        "summary_fields": (str, "summaryFields"),
        "spatial_relationship": (str, "spatialRelationship"),
        "spatial_near_distance": (float, "spatialNearDistance"),
        "spatial_near_distance_unit": (str, "spatialNearDistanceUnit"),
        "temporal_relationship": (str, "temporalRelationship"),
        "temporal_near_distance": (int, "temporalNearDistance"),
        "temporal_near_distance_unit": (str, "temporalNearDistanceUnit"),
        "attribute_relationship": (str, "attributeRelationship"),
        "join_condition": (str, "joinCondition"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        if future:
            gpjob = _execute_gp_tool(gis, "JoinFeatures", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, "JoinFeatures", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise

join_features.__annotations__ = {
                  'join_operation': str,
                  'join_fields': str,
                  'summary_fields': str,
                  'spatial_relationship': str,
                  'spatial_near_distance': float,
                  'spatial_near_distance_unit': str,
                  'temporal_relationship': str,
                  'temporal_near_distance': int,
                  'temporal_near_distance_unit': str,
                  'attribute_relationship': str,
                  'join_condition': str,
                  'output_name': str}

def reconstruct_tracks(input_layer,
                       track_fields,
                       method = """Planar""",
                       buffer_field = None,
                       summary_fields = None,
                       distance_split=None,
                       distance_split_unit=None,
                       time_boundary_split=None,
                       time_boundary_split_unit=None,
                       time_boundary_reference=None,
                       output_name = None,
                       gis=None,
                       future=False):
    """

    Using a time-enabled layer of point or polygon features that represent an instant in time, this tool determines which input features belong in a track and will order the inputs sequentially in time. Statistics are optionally calculated for the input features within each track.

    For example

    * Given point locations and time of hurricane measurements, calculate the mean wind speed and max wind pressure of the hurricane.

    * Find the highest and lowest monthly revenues for franchise locations using 100 km bins.

        This tool works with a time-enabled layer of either point or polygon features that represent an instant in time. It first determines which features belong to a track using an identifier. Using the time at each location, the tracks are ordered sequentially and transformed into a line or polygon representing the path of movement over time. Optionally, the input may be buffered by a field, which will create a polygon at each location. These buffered points, or if the inputs are polygons, are then joined sequentially to create a track as a polygon where the width is representative of the attribute of interest. Resulting tracks have a start and end time, which represent temporally the first and last feature in a given track. When the tracks are created, statistics about the input features are calculated and assigned to the output track. The most basic statistic is the count of points within the area, but other statistics can be calculated as well.

    Features in time-enabled layers can be represented in one of two ways:

    Instant-A single moment in time
    Interval-A start and end time
    For example, suppose you have GPS measurements of hurricanes every 10 minutes. Each GPS measurement records the hurricane's name, location, time of recording, and wind speed. With this information, you could create tracks for each hurricane using the name for track identification, and tracks for each hurricane would be generated. Additionally, you could calculate statistics such as the mean, max, and minimum wind speed of each hurricane, as well as the count of measurements within each track.

    Using the same example, you could buffer your tracks by the wind speed. This would buffer each measurement by the wind speed field at that location, and join the buffered areas together, creating a polygon representative of the track path, as well as the changes in wind speed as the hurricanes progressed.

    Parameters:

   input_layer: Input Features (feature input). Required parameter.

   track_fields: Track Fields (str). Required parameter.

   method: Method (str). Required parameter.
      Choice list:['Geodesic', 'Planar']

   buffer_field: Buffer Distance Field (str). Optional parameter.

   summary_fields: Summary Statistics (str/list). Optional parameter.

   time_boundary_split: Duration Split Threshold (int). Optional parameter.

   time_boundary_split_unit: Duration Split Threshold Unit (str). Optional parameter.
      Choice list:['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']

   time_boundary_reference: Starting time location (datetime.datetime). Optional parameter.

   distance_split: A distance used to split tracks. Any features in the inputLayer that are in the same track and are greater than this distance apart will be split into a new track. The units of the distance values are supplied by the distance_unit parameter.

   distance_split_unit: The distance unit to be used with the distance value specified in distanceSplit.
       Values: Meters,Kilometers,Feet,Miles,NauticalMiles, or Yards

   output_name: Output Features Name (str). Required parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

   future: Optional, if True, the return value will be a GPJob.

Returns:
   output - Output Features as a Feature Layer Collection Item


    """
    kwargs = locals()

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url

    params = {}
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Reconstructed Tracks_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Reconstruct Tracks')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    if isinstance(summary_fields, list):
        import json
        summary_fields = json.dumps(summary_fields)
    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "track_fields": (str, "trackFields"),
        "method": (str, "method"),
        "buffer_field": (str, "bufferField"),
        "summary_fields": (str, "summaryFields"),
        "time_boundary_split" : (int, "timeBoundarySplit"),
        "time_boundary_split_unit" : (str, "timeBoundarySplitUnit"),
        "time_boundary_reference" : (datetime.datetime, "timeBoundaryReference"),
        "distance_split": (int, "distanceSplit"),
        "distance_split_unit": (str, "distanceSplitUnit"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]
    try:
        if future:
            gpjob = _execute_gp_tool(gis, "ReconstructTracks", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, "ReconstructTracks", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise


reconstruct_tracks.__annotations__ = {
                       'track_fields':str,
                       'method': str,
                       'buffer_field': str,
                       'summary_fields': str,
                       'time_split': int,
                       'time_split_unit': str,
                       'output_name': str}

def summarize_attributes(input_layer,
                         fields = None,
                         summary_fields = None,
                         output_name = None,
                         gis=None,
                         future=False):
    """
    Using either feature or tabular data, this tool summarizes statistics for specified fields.

    For example

    * Given locations of grocery stores with a field COMPANY_NAME, summarize the stores by the company name to determine statistics for each company.

    * Given a table of grocery stores with fields COMPANY_NAME and COUNTY, summarize the stores by the company name and county to determine statistics for each company within each county.

    This tool summarizes all the matching values in one or more fields and calculates statistics on them. The most basic statistic is the count of features that have been summarized together, but you can calculate more advanced statistics as well.

    For example, suppose you have point features of store locations with a field representing the DISTRICT_MANAGER_NAME and you want to summarize coffee sales by manager. You can specify the field DISTRICT_MANAGER_NAME as the field to dissolve on, and all rows of data representing individual managers will be summarized. This means all store locations that are managed by Manager1 will be summarized into one row with summary statistics calculated. In this instance, statistics like the count of the number of stores and the sum of TOTAL_SALES for all stores that Manager1 manages would be calculated as well as for any other manager listed in the DISTRICT_MANAGER_NAME field.

    Parameters:

   input_layer: Input Features (feature input). Required parameter.

   fields: Summary Fields (str). Required parameter.

   summary_fields: Summary Statistics (str/list). Optional parameter.

   output_name: Output Features Name (str). Required parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

   future: Optional, if True, the response is returned as a GPJob.
Returns:
   output - Output Features as a _FeatureSet


    """
    kwargs = locals()


    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url

    params = {}
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Summarize Attributes_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Summarize Attributes')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    if isinstance(summary_fields, list):
        import json
        summary_fields = json.dumps(summary_fields)

    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "fields": (str, "fields"),
        "summary_fields": (str, "summaryFields"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]
    try:
        if future:
            gpjob = _execute_gp_tool(gis, "SummarizeAttributes", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, "SummarizeAttributes", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise

summarize_attributes.__annotations__ = {
                         'fields': str,
                         'summary_fields': str,
                         'output_name': str}

def summarize_within(summarized_layer,
                     summary_polygons=None,
                     bin_type = None,
                     bin_size = None,
                     bin_size_unit = None,
                     standard_summary_fields = None,
                     weighted_summary_fields = None,
                     sum_shape = True,
                     shape_units = None,
                     group_by_field=None,
                     minority_majority=False,
                     percent_shape=False,
                     output_name = None,
                     gis=None,
                     future=False):
    """
    Finds areas (and portions of areas) that overlap between two layers and calculates statistics about the overlap.

    For example

    * Given a layer of watershed areas and a layer of land-use areas by land-use type, calculate total acreage of land-use type for each watershed.

    * Given a layer of parcels in a county and a layer of city boundaries, summarize the average value of vacant parcels within each city.




   Parameters:

   summarized_layer: Layer To Summarize (feature input). Required parameter.

   summary_polygons: Summary Polygons Layer (feature input). Optional parameter.

   bin_type: Output Bin Type (str). Optional parameter.
      Choice list:['Square', 'Hexagon']

   bin_size: Output Bin Size (float). Optional parameter.

   bin_size_unit: Output Bin Size Unit (str). Optional parameter.
      Choice list:['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'NauticalMiles']

   standard_summary_fields: Unweighted Summary Statistics (str). Optional parameter.

   weighted_summary_fields: Proportional Summary Statistics (str). Optional parameter.

   sum_shape: Summarize Shape (bool). Optional parameter.

   shape_units: Shape Measure Output Unit (str). Optional parameter.
      Choice list:['Meters', 'Kilometers', 'Feet', 'Yards', 'Miles', 'SquareMeters', 'SquareKilometers', 'Hectares', 'SquareFeet', 'SquareYards', 'SquareMiles', 'Acres']

   group_by_field: This is a field of the summarized_layer features that you can use to calculate statistics separately for each unique attribute value. For example, suppose the sumWithinLayer contains city boundaries and the summaryPolygons features are parcels. One of the fields of the parcels is Status which contains two values: VACANT and OCCUPIED. To calculate the total area of vacant and occupied parcels within the boundaries of cities, use Status as the groupByField field. This parameter is available at ArcGIS Enterprise 10.6.1+.

   minority_majority: This boolean parameter is applicable only when a group_by_field is specified. If true, the minority (least dominant) or the majority (most dominant) attribute values for each group field are calculated. Two new fields are added to the resultLayer prefixed with Majority_ and Minority_. This parameter is available at ArcGIS Enterprise 10.6.1+. The default is false.

   percent_shape: This boolean parameter is applicable only when a group_by_field is specified. If set to true, the percentage of each unique group_by_field value is calculated for each sum within layer polygon. The default is false. This parameter is available at ArcGIS Enterprise 10.6.1+.

   output_name: Output Features Name (str). Required parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.


Returns:
   output - Output Features as a layer Item


    """
    kwargs = locals()


    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url

    params = {}
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Summarize Within_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Summarize Within')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db = {
        "summary_polygons": (_FeatureSet, "summaryPolygons"),
        "bin_type": (str, "binType"),
        "bin_size": (float, "binSize"),
        "bin_size_unit": (str, "binSizeUnit"),
        "summarized_layer": (_FeatureSet, "summarizedLayer"),
        "standard_summary_fields": (str, "standardSummaryFields"),
        "weighted_summary_fields": (str, "weightedSummaryFields"),
        "sum_shape": (bool, "sumShape"),
        "shape_units": (str, "shapeUnits"),
        "group_by_field": (str, "groupByField"),
        "minority_majority" : (bool, "minorityMajority"),
        "percent_shape" : (bool, "percentShape"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Features"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]

    try:
        if future:
            gpjob = _execute_gp_tool(gis, "SummarizeWithin", params, param_db, return_values, _use_async, url, True, future=future)
            return GAJob(gpjob=gpjob, return_service=output_service)
        _execute_gp_tool(gis, "SummarizeWithin", params, param_db, return_values, _use_async, url, True, future=future)
        return output_service
    except:
        output_service.delete()
        raise

summarize_within.__annotations__ = {
                     'bin_type': str,
                     'bin_size': float,
                     'bin_size_unit': str,
                     'standard_summary_fields': str,
                     'weighted_summary_fields': str,
                     'sum_shape': bool,
                     'shape_units': str,
                     'group_by_field': str,
                     'minority_majority' : bool,
                     'percent_shape' : bool,
                     'output_name': str
                }


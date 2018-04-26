"""

These tools are used for the day-to-day management of geographic and tabular data.

copy_to_data_store copies data to your ArcGIS Data Store and creates a layer in your web GIS.
"""
import json as _json
import logging as _logging
import arcgis as _arcgis
from arcgis.features import FeatureSet as _FeatureSet
from arcgis.geoprocessing._support import _execute_gp_tool
from ._util import _id_generator, _feature_input, _set_context, _create_output_service

_log = _logging.getLogger(__name__)

_use_async = True

def overlay_data(input_layer, overlay_layer, overlay_type="intersect", output_name=None, gis=None):
    """
    Only available at ArcGIS Enterprise 10.6.1 and later.

    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    input_layer       required FeatureLayer. The point, line or polygon features.
    ----------------  ---------------------------------------------------------------
    overlay_layer     required FeatureLayer. The features that will be overlaid with the input_layer features.
    ----------------  ---------------------------------------------------------------
    overlay_type      optional string. The type of overlay to be performed.
                      Values: intersect, erase

                      + intersect - Computes a geometric intersection of the input layers. Features or portions of features that overlap in both the inputLayer and overlayLayer layers will be written to the output layer. This is the default.
                      + erase - Only those features or portions of features in the overlay_layer that are not within the features in the input_layer layer are written to the output.
    ----------------  ---------------------------------------------------------------
    output_name       optional string. The task will create a feature service of the results. You define the name of the service.
    ----------------  ---------------------------------------------------------------
    gis               optional GIS. The GIS object where the analysis will take place.
    ================  ===============================================================

    :returns: FeatureLayer
    """
    kwargs = locals()
    tool_name = "OverlayLayers"
    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url
    params = {
        "f" : "json",
        "outputType" : "Input",
        'tolerance' : 0,
        'snapToInput' : 'false'
    }
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Overlay_Layers_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Overlay Layers')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "overlay_layer": (_FeatureSet, "overlayLayer"),
        "outputType" : (str, 'outputType'),
        "overlay_type" : (str, "overlayType"),
        "output_name": (str, "OutputName"),
        "context": (str, "context"),
        'tolerance' : (int, 'tolerance'),
        "output": (_FeatureSet, "output"),
        'snapToInput' : (str, 'snapToInput')
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]
    try:
        _execute_gp_tool(gis, tool_name, params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

    return


def append_data(input_layer, append_layer, field_mapping=None, gis=None):
    """
    Only available at ArcGIS Enterprise 10.6.1 and later.

    The Append Data task appends tabular, point, line, or polygon data to an existing layer.
    The input layer must be a hosted feature layer. The tool will add the appended data as
    rows to the input layer. No new output layer is created.

    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    input_layer       required FeatureLayer , The table, point, line or polygon features.
    ----------------  ---------------------------------------------------------------
    append_layer      required FeatureLayer. The table, point, line, or polygon features
                      to be appended to the input_layer. To append geometry, the
                      append_layer must have the same geometry type as the
                      input_layer. If the geometry types are not the same, the
                      append_layer geometry will be removed and all other matching
                      fields will be appended. The geometry of the input_layer will
                      always be maintained.
    ----------------  ---------------------------------------------------------------
    field_mapping     Defines how the fields in append_layer are appended to the
                      input_layer.

                      The following are set by default:

                        - All append_layer fields that match input_layer schema will be appended.
                        - Fields that exist in the input_layer and not in the append_layer will be appended with null values.
                        - Fields that exist in the append_layer and not in the input_layer will not be appended.

                      Optionally choose how input_layer fields will be appended from the following:

                      - AppendField - Matches the input_layer field with an append_layer field of a different name. Field types must match.
                      - Expression - Calculates values for the resulting field. Values are calculated using Arcade expressions. To assign null values, use 'null'.
    ----------------  ---------------------------------------------------------------
    gis               optional GIS, the GIS on which this tool runs. If not
                      specified, the active GIS is used.
    ================  ===============================================================

    :returns: boolean

    """
    kwargs = locals()
    tool_name = "AppendData"
    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url
    params = {
        "f" : "json"
    }
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    _set_context(params)

    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "append_layer": (_FeatureSet, "appendLayer"),
        "field_mapping" : (str, "fieldMapping"),
        "context": (str, "context")
    }
    return_values = [
    ]
    try:
        _execute_gp_tool(gis, tool_name, params, param_db, return_values, _use_async, url, True)
        return True
    except:
        raise

    return False


def calculate_fields(input_layer,
                     field_name,
                     data_type,
                     expression,
                     track_aware=False,
                     track_fields=None,
                     output_name=None,
                     gis=None
                     ):
    """
    The Calculate Field task works with a layer to create and populate a
    new field. The output is a new feature layer, that is the same as the
    input features, with the additional field added.

    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    input_layer       required service , The table, point, line or polygon features
                      containing potential incidents.
    ----------------  ---------------------------------------------------------------
    field_name        required string, A string representing the name of the new
                      field. If the name already exists in the dataset, then a
                      numeric value will be appended to the field name.
    ----------------  ---------------------------------------------------------------
    data_type         required string, the type for the new field.
                      Values: Date |Double | Integer | String
    ----------------  ---------------------------------------------------------------
    expression        required string, An Arcade expression used to calculate the new
                      field values. You can use any of the Date, Logical,
                      Mathematical or Text function available with Arcade.
    ----------------  ---------------------------------------------------------------
    track_aware       optional boolean, Boolean value denoting if the expression is
                      track aware.
                      Default: False
    ----------------  ---------------------------------------------------------------
    track_fields      optional string, The fields used to identify distinct tracks.
                      There can be multiple track_fields. track_fields are only
                      required when track_aware is true.
    ----------------  ---------------------------------------------------------------
    output_name       optional string, The task will create a feature service of the
                      results. You define the name of the service.
    ----------------  ---------------------------------------------------------------
    gis               optional GIS, the GIS on which this tool runs. If not
                      specified, the active GIS is used.
    ================  ===============================================================

    :returns:
       Feature Layer
    """
    kwargs = locals()
    tool_name = "CalculateField"
    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url
    params = {
        "f" : "json"
    }
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Calculate_Fields_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Calculate Fields')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "field_name" : (str, "fieldName"),
        "data_type" : (str, "dataType"),
        "expression" : (str, "expression"),
        "track_aware" : (bool, "trackAware"),
        "track_fields" : (str, "trackFields"),
        "output_name": (str, "outputName"),
        "output": (_FeatureSet, "output"),
        "context": (str, "context")
    }
    return_values = [
        {"name": "output", "display_name": "Output Features", "type": _FeatureSet},
    ]
    try:
        _execute_gp_tool(gis, tool_name, params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

    return

def copy_to_data_store(
    input_layer,
    output_name = None,
    gis = None):
    """

    Copies an input feature layer or table to an ArcGIS Data Store and creates a layer in your web GIS.

    For example

    * Copy a collection of .csv files in a big data file share to the spatiotemporal data store for visualization.

    * Copy the features in the current map extent that are stored in the spatiotemporal data store to the relational data store.

    This tool will take an input layer and copy it to a data store. Data will be copied to the ArcGIS Data Store and will be stored in your relational or spatiotemporal data store.

    For example, you could copy features that are stored in a big data file share to a relational data store and specify that only features within the current map extent will be copied. This would create a hosted feature service with only those features that were within the specified map extent.

   Parameters:

   input_layer: Input Layer (feature layer). Required parameter.

   output_name: Output Layer Name (str). Required parameter.

   gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.


Returns:
   output - Output Layer as a feature layer collection item


    """
    kwargs = locals()

    gis = _arcgis.env.active_gis if gis is None else gis
    url = gis.properties.helperServices.geoanalytics.url

    params = {}
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value

    if output_name is None:
        output_service_name = 'Data Store Copy_' + _id_generator()
        output_name = output_service_name.replace(' ', '_')
    else:
        output_service_name = output_name.replace(' ', '_')

    output_service = _create_output_service(gis, output_name, output_service_name, 'Copy To Data Store')

    params['output_name'] = _json.dumps({
        "serviceProperties": {"name" : output_name, "serviceUrl" : output_service.url},
        "itemProperties": {"itemId" : output_service.itemid}})

    _set_context(params)

    param_db = {
        "input_layer": (_FeatureSet, "inputLayer"),
        "output_name": (str, "outputName"),
        "context": (str, "context"),
        "output": (_FeatureSet, "Output Layer"),
    }
    return_values = [
        {"name": "output", "display_name": "Output Layer", "type": _FeatureSet},
    ]
    try:
        _execute_gp_tool(gis, "CopyToDataStore", params, param_db, return_values, _use_async, url, True)
        return output_service
    except:
        output_service.delete()
        raise

copy_to_data_store.__annotations__ = {
    'output_name': str}






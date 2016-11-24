"""
These functions are used for both the day-to-day management of geographic data and for combining data prior to analysis.

dissolve_boundaries merges together areas that share a common boundary and a common attribute value.
extract_data creates new datasets by extracting features from your existing data.
merge_layers copies all the features from two or more existing layers into a new layer.
overlay_layers combines two or more layers into one single layer. You can think of overlay as peering through a stack of
maps and creating a single map containing all the information found in the stack.
"""
import arcgis as _arcgis

def dissolve_boundaries(
        input_layer,
        dissolve_fields=[],
        summary_fields=[],
        output_name=None,
        context=None,
        gis=None):
    """
    Dissolve features based on specified fields.

    Parameters
    ----------
    input_layer : Required layer (see Feature Input in documentation)
        The layer containing polygon features that will be dissolved.
    dissolve_fields : Optional list of strings
        One or more fields from the input that control which polygons are merged. If no fields are supplied, all
        polygons that overlap or shared a common border will be dissolved into one polygon.
    summary_fields : Optional list of strings
        A list of field names and statistical types that will be used to summarize the output. Supported statistics
        include: Sum, Mean, Min, Max, and Stddev.
    output_name : Optional string
        Additional properties such as output feature service name.
    context : Optional string
        Additional settings such as processing extent and output spatial reference.
    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

    Returns
    -------
    dissolved_layer : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.dissolve_boundaries(
        input_layer,
        dissolve_fields,
        summary_fields,
        output_name,
        context)


def extract_data(
        input_layers,
        extent=None,
        clip=False,
        data_format=None,
        output_name=None,
        context=None,
        gis=None):
    """
    Select and download data for a specified area of interest. Layers that you select will be added to a zip file or
    layer package.

    Parameters
    ----------
    input_layers : Required list of strings
        The layers from which you can extract features.
    extent : Optional string
        The area that defines which features will be included in the output zip file or layer package.
    clip : Optional bool
        Select features that intersect the extent or clip features within the extent.
    data_format : Optional string
        Format of the data that will be extracted and downloaded.  Layer packages will always include file geodatabases.
    output_name : Optional string
        Additional properties such as output feature service name.
    context : Optional string
        Additional settings such as processing extent and output spatial reference.
    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

    Returns
    -------
    content_id : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.extract_data(
        input_layers,
        extent,
        clip,
        data_format,
        output_name,
        context)


def merge_layers(
        input_layer,
        merge_layer,
        merging_attributes=[],
        output_name=None,
        context=None,
        gis=None):
    """
    Combines two inputs of the same feature data type into a new output.

    Parameters
    ----------
    input_layer : Required layer (see Feature Input in documentation)
         The point, line, or polygon  features to merge with the mergeLayer.
    merge_layer : Required layer (see Feature Input in documentation)
        The point, line or polygon features to merge with inputLayer.  mergeLayer must contain the same feature type
        point, line, or polygon) as the inputLayer.
    merging_attributes : Optional list of strings
        An array of values that describe how fields from the mergeLayer are to be modified.  By default all fields from
        both inputs will be carried across to the output.
    output_name : Optional string
        Additional properties such as output feature service name.
    context : Optional string
        Additional settings such as processing extent and output spatial reference.
    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

    Returns
    -------
    merged_layer : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.merge_layers(
        input_layer,
        merge_layer,
        merging_attributes,
        output_name,
        context)


def overlay_layers(
        input_layer,
        overlay_layer,
        overlay_type="Intersect",
        snap_to_input=False,
        output_type="Input",
        tolerance=None,
        output_name=None,
        context=None,
        gis=None):
    """
    Overlays the input layer with the overlay layer. Overlay operations supported are Intersect, Union, and Erase.

    Parameters
    ----------
    input_layer : Required layer (see Feature Input in documentation)
        The input analysis layer.
    overlay_layer : Required layer (see Feature Input in documentation)
        The layer to be overlaid with the analysis layer.
    overlay_type : Optional string
        The overlay type (INTERSECT, UNION, or ERASE) defines how the analysis layer and the overlay layer are combined.
    snap_to_input : Optional bool
        When the distance between features is less than the tolerance, the features in the overlay layer will snap to
        the features in the input layer.
    output_type : Optional string
        The type of intersection (INPUT, LINE, POINT).
    tolerance : Optional float
        The minimum distance separating all feature coordinates (nodes and vertices) as well as the distance a
        coordinate can move in X or Y (or both).
    output_name : Optional string
        Additional properties such as output feature service name.
    context : Optional string
        Additional settings such as processing extent and output spatial reference.
    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

    Returns
    -------
    output_layer : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.overlay_layers(
        input_layer,
        overlay_layer,
        overlay_type,
        snap_to_input,
        output_type,
        tolerance,
        output_name,
        context)

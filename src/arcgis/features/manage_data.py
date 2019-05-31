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
        gis=None,
        estimate=False,
        multi_part_features=True):
    """
    .. image:: _static/images/dissolve_boundaries/dissolve_boundaries.png 

    The dissolve_boundaries method finds polygons that overlap or share a common boundary and merges them together to form a single polygon.

    You can control which boundaries are merged by specifying a field. For example, if you have a layer of counties, and each county 
    has a State_Name attribute, you can dissolve boundaries using the State_Name attribute. Adjacent counties will be merged together 
    if they have the same value for State_Name. The end result is a layer of state boundaries.
 
    ====================================     ====================================================================
    **Parameter**                            **Description**
    ------------------------------------     --------------------------------------------------------------------
    input_layer                              Required layer. The layer containing polygon features that will be dissolved. See :ref:`Feature Input<FeatureInput>`.
    ------------------------------------     --------------------------------------------------------------------
    dissolve_fields                          Optional list of strings. One or more fields on the input_layer that control which polygons 
                                             are merged. If you don't supply dissolve_fields , or you supply an empty list of fields, polygons 
                                             that share a common border (that is, they are adjacent) or polygon areas that overlap will be dissolved into one polygon.

                                             If you do supply values for the dissolve_fields parameter, polygons that share a common border 
                                             and contain the same value in one or more fields will be dissolved. For example, if you have a layer of counties, 
                                             and each county has a State_Name attribute, you can dissolve boundaries using the State_Name attribute. 
                                             Adjacent counties will be merged together if they have the same value for State_Name. The end result is a layer of 
                                             state boundaries.If two or more fields are specified, the values in these fields must be the same for the boundary to be dissolved.
    ------------------------------------     --------------------------------------------------------------------
    summary_fields                           Optional list of strings. A list of field names and statistical summary type that you wish to calculate from the polygons 
                                             that are dissolved together. For example, if you are dissolving counties based on State_Name, and each county had a Population field, you can sum Population. 
                                             The result would be a layer of state boundaries with total population.
                                             
                                             fieldName is the name of one of the numeric fields found in the input_layer.
                                             summary type is one of the following:

                                             * Sum—Adds the total value of all the points in each polygon
                                             * Mean—Calculates the average of all the points in each polygon.
                                             * Min—Finds the smallest value of all the points in each polygon.
                                             * Max—Finds the largest value of all the points in each polygon.
                                             * Stddev—Finds the standard deviation of all the points in each polygon.
                                             Example [fieldName1 summaryType1,fieldName2 summaryType2].
    ------------------------------------     --------------------------------------------------------------------                       
    output_name                              Optional string. If provided, the task will create a feature service of the results. 
                                             You define the name of the service. If output_name is not supplied, the task will return a feature collection.
    ------------------------------------     --------------------------------------------------------------------
    context                                  Optional string. Context contains additional settings that affect task execution. For dissolve_boundaries Points, there are two settings.
                                             
                                             #. Extent (extent)-a bounding box that defines the analysis area. Only those features in the input_layer that intersect the bounding box will be analyzed.
                                             #. Output Spatial Reference (outSR)—the output features will be projected into the output spatial reference.
    ------------------------------------     --------------------------------------------------------------------
    gis                                      Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    ------------------------------------     --------------------------------------------------------------------
    estimate                                 Optional Boolean. If True, the number of credits to run the operation will be returned.
    ------------------------------------     --------------------------------------------------------------------                       
    multi_part_features                      Optional boolean. Specifies whether multipart features (i.e. features which share a common 
                                             attribute table but are not visibly connected) are allowed in the output feature class.    

                                             Choice list: ['True', 'False'].

                                             True: Specifies multipart features are allowed.

                                             False: Specifies multipart features are not allowed. Instead of creating multipart features, individual features will be created for each part.

                                             The default value is True.    
    ====================================     ====================================================================

    :returns: result_layer : feature layer Item if output_name is specified, else Feature Collection.


    .. code-block:: python

        USAGE EXAMPLE: To dissolve boundaries of polygons with same state name. The dissolved polygons are summarized using population as summary field and standard deviation as summary type.
        diss_counties = dissolve_boundaries(input_layer=usa_counties,
                                            dissolve_fields=["STATE_NAME"],
                                            summary_fields=["POPULATION STDDEV"],
                                            output_name="DissolveBoundaries")    
    """                           
  
    gis = _arcgis.env.active_gis if gis is None else gis

    return gis._tools.featureanalysis.dissolve_boundaries(
        input_layer,
        dissolve_fields,
        summary_fields,
        output_name,
        context,
        estimate=estimate,
        multi_part_features=multi_part_features)


def extract_data(
        input_layers,
        extent=None,
        clip=False,
        data_format=None,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    .. image:: _static/images/extract_data/extract_data.png 

    The ``extract_data`` method is used to extract data from one or more layers within a given extent. 
    The extracted data format can be a file geodatabase, shapefiles, csv, or kml. 
    File geodatabases and shapefiles are added to a zip file that can be downloaded.

    ===================================    =========================================================
    **Argument**                           **Description**
    -----------------------------------    ---------------------------------------------------------
    input_layers                           Required list of strings. A list of input layers to be extracted. See :ref:`Feature Input<FeatureInput>`.
    -----------------------------------    ---------------------------------------------------------
    extent                                 Optional layer. The extent is the area of interest used to extract the input features. If not specified, all features from each input layer are extracted. See :ref:`Feature Input<FeatureInput>`.
    -----------------------------------    ---------------------------------------------------------
    clip                                   Optional boolean. A Boolean value that specifies whether the features within the input layer are clipped 
                                           within the extent. By default, features are not clipped and all features intersecting the extent are returned. 

                                           The default is false.     
    -----------------------------------    ---------------------------------------------------------
    data_format                            Optional string. A keyword defining the output data format for your extracted data.
                                           
                                           Choice list: ['FileGeodatabase', 'ShapeFile', 'KML', 'CSV']
                                           
                                           The default is 'CSV'.

                                           If FILEGEODATABASE is specified, and the input layer has `attachments <https://enterprise.arcgis.com/en/portal/latest/use/manage-hosted-layers.htm#ESRI_SECTION2_EF4F7A72F7B74E47B5CBCC1F343445E2>`_ , the attachments will be extracted 
                                           to the output file geodatabase if clip is false. If clip is true, attachments will not be extracted.
    -----------------------------------    ---------------------------------------------------------
    output_name                            Optional string or dict. ``output_name`` is used to name the item in your My contents page. For more information on these item properties, see the Item resource page in the `ArcGIS REST API <https://developers.arcgis.com/rest/users-groups-and-items/item.htm>`_
                                           Syntax when ``output_name`` is dict: {
                                                                                "title": "<title>",
                                                                                "tag": "<tags>",
                                                                                "snippet": "<snippet>",
                                                                                "description": "<description>"
                                                                                }
    -----------------------------------    ---------------------------------------------------------   
    context                                Optional string. Context contains additional settings that affect method execution. For ``extract_data``, there is one setting.

                                           #. Output Spatial Reference (outSR)—the extracted features will be projected into the output spatial reference.
    -----------------------------------    ---------------------------------------------------------   
    gis                                    Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    ===================================    =========================================================    

    .. code-block:: python

        # USAGE EXAMPLE: To extract data from highways layer with the extent of a state boundary. 
        
        ext_state_highway = extract_data(input_layers=[highways.layers[0]],
                                 extent=state_area_boundary.layers[0],
                                 clip=True,
                                 data_format='shapefile',
                                 output_name='state highway extracted')	    
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.extract_data(
        input_layers,
        extent,
        clip,
        data_format,
        output_name,
        context,
        estimate=estimate)


def merge_layers(
        input_layer,
        merge_layer,
        merging_attributes=[],
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
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
        context,
        estimate=estimate)


def overlay_layers(
        input_layer,
        overlay_layer,
        overlay_type="Intersect",
        snap_to_input=False,
        output_type="Input",
        tolerance=None,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
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
        context,
        estimate=estimate)

def create_route_layers(route_data_item,
                        delete_route_data_item=False,
                        tags=None,
                        summary=None,
                        route_name_prefix=None,
                        folder_name=None,
                        gis=None,
                        estimate=False):
    
    """
    The ``create_route_layers`` method creates route layer items on the portal from the input route data.

    A route layer includes all the information for a particular route such as the stops assigned to 
    the route as well as the travel directions. Creating route layers is useful if you want to share 
    individual routes with other members in your organization.


    =========================    =========================================================
    **Parameter**                **Description**
    -------------------------    ---------------------------------------------------------
    route_data                   Required item. The item id for the route data item that is used to create route layer items. 
                                 Before running this task, the route data must be added to your portal as an item.
    -------------------------    ---------------------------------------------------------
    delete_route_data_item       Required boolean. Indicates if the input route data item should be deleted. You may want to 
                                 delete the route data in case it is no longer required after the route layers have been created from it.

                                 When ``delete_route_data_item`` is set to true and the task fails to delete the route data item, 
                                 it will return a warning message but still continue execution.

                                 The default value is False.
    -------------------------    ---------------------------------------------------------
    tags                         Optional string. Tags used to describe and identify the route layer items. 
                                 Individual tags are separated using a comma. The route name is always
                                 added as a tag even when a value for this argument is not specified.
    -------------------------    ---------------------------------------------------------
    summary                      Optional string. The summary displayed as part of the item information for the route layer item. 
                                 If a value for this argument is not specified, a default summary text "Route and directions for <Route Name>" is used.
    -------------------------    ---------------------------------------------------------
    route_name_prefix            Optional string. A qualifier added to the title of every route layer item. This can be used to designate all routes that are shared for a
                                 specific purpose to have the same prefix in the title. The name of the route is always appended after this qualifier.
                                 If a value for the route_name_prefix is not specified, the title for the route layer item is created using only the route name.
    -------------------------    ---------------------------------------------------------
    folder_name                  Optional string. The folder within your personal online workspace (My Content in your ArcGIS Online or Portal for ArcGIS organization) where the
                                 route layer items will be created. If a folder with the specified name does not exist, a new folder will be created.
                                 If a folder with the specified name exists, the items will be created in the existing folder.
                                 If a value for folder_name is not specified, the route layer items are created in the root folder of your online workspace.
    -------------------------    ---------------------------------------------------------
    gis                          Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------    ---------------------------------------------------------
    estimate                     Optional boolean. If True, the estimated number of credits required to run the operation will be returned.
    =========================    =========================================================

    :returns: result_layer : list (items)

    .. code-block:: python

        USAGE EXAMPLE: To create route layers from geodatabase item.
        route = create_route_layers(route_data_item=route_item,
                            delete_route_data_item=False,
                            tags="datascience",
                            summary="example of create route layers method",
                            route_name_prefix="santa_ana",
                            folder_name="create route layers")        
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    output_name = {}
    output_item_properties = {}
    if route_name_prefix:
        output_item_properties["title"] = route_name_prefix
    if tags:
        output_item_properties["tags"] = tags
    if summary:
        output_item_properties["snippet"] = summary
    if folder_name:
        folder_id = ""
        # Get a dict of folder names for the current user
        folders = {fld["title"]: fld for fld in gis.users.me.folders}
        # if the folder already exists, just get its folder id
        if folder_name in folders:
            folder_id = folders[folder_name].get("id", "")
        else:
            # Create a new folder and get its folder id
            new_folder = gis.content.create_folder(folder_name)
            folder_id = new_folder.get("id", "")
        if folder_id:
            output_item_properties["folderId"] = folder_id
    if output_item_properties:
        output_name["itemProperties"] = output_item_properties

    return gis._tools.featureanalysis.create_route_layers(
        route_data_item,
        delete_route_data_item,
        output_name, estimate=estimate)

"""
These functions calculate total counts, lengths, areas, and basic descriptive statistics of features and their attributes
within areas or near other features.

aggregate_points calculates statistics about points that fall within specified areas.
summarize_nearby calculates statistics for features and their attributes that are within a specified distance.
summarize_within calculates statistics for area features and attributes that overlap each other.
"""
import arcgis as _arcgis
from arcgis._impl.common._utils import _date_handler

def aggregate_points(
                     point_layer,
                     polygon_layer,
                     keep_boundaries_with_no_points=True,
                     summary_fields=[],
                     group_by_field=None,
                     minority_majority=False,
                     percent_points=False,
                     output_name=None,
                     context=None,
                     gis=None,
                     estimate=False):
    """
    The Aggregate Points task works with a layer of point features and a layer of polygon features. It first figures out which points fall within each polygon's area.
    After determining this point-in-polygon spatial relationship, statistics about all points in the polygon are calculated and assigned to the area. The most basic statistic is the count of the number of points within the polygon, but you can get other statistics as well.
    For example, if your points represented coffee shops and each point has a TOTAL_SALES attribute, you can get statistics like the sum of all TOTAL_SALES within the polygon, or the minimum or maximum TOTAL_SALES value, or the standard deviation of all sales within the polygon.

    ====================================     ====================================================================
    **Parameter**                            **Description**
    ------------------------------------     --------------------------------------------------------------------
    point_layer                              Required point layer. The point features that will be aggregated into the polygons in the polygon_layer. See :ref:`Feature Input<FeatureInput>`.
    ------------------------------------     --------------------------------------------------------------------
    polygon_layer                            Required polygon layer. The polygon features (areas) into which the input points will be aggregated. See :ref:`Feature Input<FeatureInput>`.
    ------------------------------------     --------------------------------------------------------------------
    keep_boundaries_with_no_points           Optional boolean. A Boolean value that specifies whether the polygons that have no points within them should be returned in the output. The default is true.
    ------------------------------------     --------------------------------------------------------------------
    summary_fields                           Optional list of strings. A list of field names and statistical summary type that you wish to calculate for all points within each polygon.
                                             Note that the count of points within each polygon is always returned.
                                             summary type is one of the following:

                                             * Sum—Adds the total value of all the points in each polygon
                                             * Mean—Calculates the average of all the points in each polygon.
                                             * Min—Finds the smallest value of all the points in each polygon.
                                             * Max—Finds the largest value of all the points in each polygon.
                                             * Stddev—Finds the standard deviation of all the points in each polygon.
                                             Example [fieldName1 summaryType1,fieldName2 summaryType2].
    ------------------------------------     --------------------------------------------------------------------
    group_by_field                           Optional string. A field name in the point_layer. Points that have the same value for the group by field will have their own counts and summary field statistics. You can create statistical groups using an attribute in the analysis layer. For example, if you are aggregating crimes to neighborhood boundaries, you may have an attribute Crime_type with five different crime types. Each unique crime type forms a group, and the statistics you choose will be calculated for each unique value of Crime_type. When you choose a grouping attribute, two results are created: the result layer and a related table containing the statistics.
    ------------------------------------     --------------------------------------------------------------------
    minority_majority                        Optional boolean. This boolean parameter is applicable only when a group_by_field is specified. If true, the minority (least dominant) or the majority (most dominant) attribute values for each group field within each boundary are calculated. Two new fields are added to the aggregated_layer prefixed with Majority_ and Minority_.
                                             The default is false.
    ------------------------------------     -------------------------------------------------------------------- 
    percent_points                           Optional boolean. This boolean parameter is applicable only when a group_by_field is specified. If set to true, the percentage count of points for each unique group_by_field value is calculated. A new field is added to the group summary output table containing the percentages of each attribute value within each group. If minority_majority is true, two additional fields are added to the aggregated_layer containing the percentages of the minority and majority attribute values within each group.
    ------------------------------------     --------------------------------------------------------------------                       
    output_name                              Optional string. Output Features Name (str). Optional parameter.
    ------------------------------------     --------------------------------------------------------------------
    context                                  Optional string. Context contains additional settings that affect task execution. For Aggregate Points, there are two settings.
                                             
                                             #. Extent (extent)-a bounding box that defines the analysis area. Only those points in the input pointLayer that intersect the bounding box will be analyzed.
                                             #. Output Spatial Reference (outSR)—the output features will be projected into the output spatial reference.
    ------------------------------------     --------------------------------------------------------------------
    gis                                      Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    ------------------------------------     --------------------------------------------------------------------
    estimate                                 Optional Boolean. If True, the number of credits to run the operation will be returned.
    ====================================     ====================================================================

    :returns: result_layer : feature layer Item if output_name is specified, else Feature Collection.


    .. code-block:: python

        USAGE EXAMPLE: To find number of permits issued in each zip code of US.
        
        agg_result = aggregate_points(point_layer=permits,
                                polygon_layer=zip_codes,
                                keep_boundaries_with_no_points=False,
                                summary_fields=["DeclValNu mean","DeclValNu2 mean"],
                                group_by_field='Declared_V',
                                minority_majority=True,
                                percent_points=True,
                                output_name="aggregated_permits",
                                context='{"extent":{"xmin":-8609738.077325115,"ymin":4743483.445485223,"xmax":-8594030.268012533,"ymax":4752206.821338257,"spatialReference":{"wkid":102100,"latestWkid":3857}}}') 

    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.aggregate_points(
                     point_layer,
                     polygon_layer,
                     keep_boundaries_with_no_points,
                     summary_fields,
                     group_by_field,
                     minority_majority,
                     percent_points,
                     output_name,
                     context,
                     estimate=estimate)



def summarize_nearby(sum_nearby_layer,
                     summary_layer,
                     near_type="StraightLine",
                     distances=[],
                     units="Meters",
                     time_of_day=None,
                     time_zone_for_time_of_day="GeoLocal",
                     return_boundaries=True,
                     sum_shape=True,
                     shape_units=None,
                     summary_fields=[],
                     group_by_field=None,
                     minority_majority=False,
                     percent_shape=False,
                     output_name=None,
                     context=None,
                     gis=None,
                     estimate=False):
    """
    The SummarizeNearby task finds features that are within a specified distance of features in the input layer.
    Distance can be measured as a straight-line distance, a drive-time distance (for example, within 10 minutes), or a
    drive distance (within 5 kilometers). Statistics are then calculated for the nearby features. For example:Calculate
    the total population within five minutes of driving time of a proposed new store location.Calculate the number of
    freeway access ramps within a one-mile driving distance of a proposed new store location to use as a measure of
    store accessibility.

    Parameters
    ----------
    sum_nearby_layer : Required layer (see Feature Input in documentation)
        Point, line, or polygon features from which distances will be measured to features in the summarizeLayer.
    summary_layer : Required layer (see Feature Input in documentation)
        Point, line, or polygon features. Features in this layer that are within the specified distance to features in
        the sumNearbyLayer will be summarized.
    near_type : Optional string
        Defines what kind of distance measurement you want to use to create areas around the nearbyLayer features.
    distances : Required list of floats
        An array of double values that defines the search distance for creating areas mentioned above
    units : Optional string
        The linear unit for distances parameter above. Eg. Miles, Kilometers, Minutes Seconds etc
    time_of_day : Optional datetime.datetime
        For timeOfDay, set the time and day according to the number of milliseconds elapsed since the Unix epoc
        (January 1, 1970 UTC). When specified and if relevant for the nearType parameter, the traffic conditions during
        the time of the day will be considered.
    time_zone_for_time_of_day : Optional string
        Determines if the value specified for timeOfDay is specified in UTC or in a time zone that is local to the
        location of the origins.
    return_boundaries : Optional bool
        If true, will return a result layer of areas that contain the requested summary information.  The resulting
        areas are defined by the specified nearType.  For example, if using a StraightLine of 5 miles, your result will
        contain areas with a 5 mile radius around the input features and specified summary information.If false, the
        resulting layer will return the same features as the input analysis layer with requested summary information.
    sum_shape : Optional bool
        A boolean value that instructs the task to calculate count of points, length of lines or areas of polygons of
        the summaryLayer within each polygon in sumWithinLayer.
    shape_units : Optional string
        Specify units to summarize the length or areas when sumShape is set to true. Units is not required to summarize
        points.
    summary_fields : Optional list of strings
        A list of field names and statistical summary type that you wish to calculate for all features in the
        summaryLayer that are within each polygon in the sumWithinLayer . Eg: ["fieldname1 summary",
        "fieldname2 summary"]
    group_by_field : Optional string
        Specify a field from the summaryLayer features to calculate statistics separately for each unique value of the
        field.
    minority_majority : Optional bool
        This boolean parameter is applicable only when a groupByField is specified. If true, the minority
        (least dominant) or the majority (most dominant) attribute values within each group, within each boundary will
        be calculated.
    percent_shape : Optional bool
        This boolean parameter is applicable only when a groupByField is specified. If set to true, the percentage of
        shape (eg. length for lines) for each unique groupByField value is calculated.
    output_name : Optional string
        Additional properties such as output feature service name.
    context : Optional string
        Additional settings such as processing extent and output spatial reference.
    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    estimate :
        Optional Boolean. If True, the number of credits to run the operation will be returned.

    Returns
    -------
    dict with the following keys:
       "result_layer" : layer (FeatureCollection)
       "group_by_summary" : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.summarize_nearby(
                     sum_nearby_layer,
                     summary_layer,
                     near_type,
                     distances,
                     units,
                     _date_handler(time_of_day),
                     time_zone_for_time_of_day,
                     return_boundaries,
                     sum_shape,
                     shape_units,
                     summary_fields,
                     group_by_field,
                     minority_majority,
                     percent_shape,
                     output_name,
                     context,
                     estimate=estimate)


def summarize_center_and_dispersion(
        analysis_layer,
        summarize_type=["CentralFeature"],
        ellipse_size=None,
        weight_field=None,
        group_field=None,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):

    """
    .. image:: _static/images/summarize_center_and_dispersion/summarize_center_and_dispersion.png 

    The ``summarize_center_and_dispersion`` method finds central features and directional distributions. It can be used to answer questions such as:

    * Where is the center?
    * Which feature is the most accessible from all other features?
    * How dispersed, compact, or integrated are the features?
    * Are there directional trends?s

    ====================    =========================================================
    **Argument**            **Description**
    --------------------    ---------------------------------------------------------
    analysis_layer          Required frature layer. The point, line, or polygon features to be analyzed. See :ref:`Feature Input<FeatureInput>`.
    --------------------    ---------------------------------------------------------
    summarize_type          Required list of strings. The method with which to summarize the ``analysis_layer``.

                            Choice list: ["CentralFeature", "MeanCenter", "MedianCenter", "Ellipse"]
    --------------------    ---------------------------------------------------------
    ellipse_size            Optional string. The size of the output ellipse in standard deviations.
                            
                            Choice list: ['1 standard deviations', '2 standard deviations', '3 standard deviations']

                            The default ellipse size is '1 standard deviations'.
    --------------------    ---------------------------------------------------------
    weight_field            Optional field. A numeric field in the ``analysis_layer`` to be used to
                            weight locations according to their relative importance.
    --------------------    ---------------------------------------------------------
    group_field             Optional field. The field used to group features for separate directional
                            distribution calculations. The ``group_field`` can be of
                            integer, date, or string type.
    --------------------    ---------------------------------------------------------
    output_name             Optional string. If provided, the method will create a feature service of the results. 
                            You define the name of the service. If ``output_name`` is not supplied, the method will return a feature collection.
    --------------------    ---------------------------------------------------------
    context                 Optional string. Context contains additional settings that affect task execution. For ``summarize_center_and_dispersion``, there are two settings.

                            #. Extent (``extent``)—a bounding box that defines the analysis area. Only those features in the input layer that intersect the bounding box will be buffered.
                            #. Output Spatial Reference (``outSR``)—the output features will be projected into the output spatial reference.
    --------------------    ---------------------------------------------------------
    estimate                Optional boolean. If True, the number of credits to run the operation will be returned.
    ====================    =========================================================

    :returns: list of items if ``output_name`` is supplied else, a Python dictionary with the following keys:
        "central_feature_result_layer" : layer (FeatureCollection)
        "mean_feature_result_layer" : layer (FeatureCollection)
        "median_feature_result_layer" : layer (FeatureCollection)
        "ellipse_feature_result_layer" : layer (FeatureCollection)

    .. code-block:: python

        # USAGE EXAMPLE: To find central features and mean center of earthquake over past months.
        central_features = summarize_center_and_dispersion(analysis_layer=earthquakes,
                                                           summarize_type=["CentralFeature","MeanCenter"],
                                                           ellipse_size='2 standard deviations',
                                                           weight_field='mag',
                                                           group_field='magType',
                                                           output_name='find central features and mean center of earthquake over past months')

    """

    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.summarize_center_and_dispersion(
        analysis_layer,
        summarize_type,
        ellipse_size,
        weight_field,
        group_field,
        output_name,
        context,
        estimate=estimate)


def summarize_within(sum_within_layer,
                     summary_layer,
                     sum_shape=True,
                     shape_units=None,
                     summary_fields=[],
                     group_by_field=None,
                     minority_majority=False,
                     percent_shape=False,
                     output_name=None,
                     context=None,
                     gis=None,
                     estimate=False):
    """
    .. image:: _static/images/summarize_within/summarize_within.png 

    The ``summarize_within`` method finds the point, line, or polygon features (or portions of these features) 
    that are within the boundaries of polygons in another layer. For example:

        * Given a layer of watershed boundaries and a layer of land-use boundaries by land-use type, calculate total acreage of land-use type for each watershed.
        * Given a layer of parcels in a county and a layer of city boundaries, summarize the average value of vacant parcels within each city boundary.
        * Given a layer of counties and a layer of roads, summarize the total mileage of roads by road type within each county.

    You can think of ``summarize_within`` as taking two layers and stacking them on top of each other. 
    One of the layers, the ``sum_within_layer`` must be a polygon layer, and imagine that these polygon 
    boundaries are all colored red. The other layer, the ``summary_layer``, can be any feature type—point, 
    line, or polygon. After stacking these layers on top of each other, you peer down through the stack 
    and count the number of features in the ``summary_layer`` that fall within the polygons with the red 
    boundaries (the ``sum_within_layer``). Not only can you count the number of features, you can calculate 
    simple statistics about the attributes of the features in the ``summary_layer``, such as sum, mean, minimum, maximum, and so on.

    =====================================    =========================================================
    **Argument**                             **Description**
    -------------------------------------    ---------------------------------------------------------
    sum_within_layer                         Required feature layer. The polygon features. Features, or 
                                             portions of features, in the ``summary_layer`` (below) that fall within 
                                             the boundaries of these polygons will be summarized. See :ref:`Feature Input<FeatureInput>`.
    -------------------------------------    ---------------------------------------------------------
    summary_layer                            Required feature layer. Point, line, or polygon features that will be summarized for each polygon in the ``sum_within_layer``.
                                             See :ref:`Feature Input<FeatureInput>`.
    -------------------------------------    ---------------------------------------------------------       
    sum_shape                                Optional boolean. A boolean value that instructs the task to calculate statistics 
                                             based on shape type of the ``summary_layer``, such as the length of lines or areas of 
                                             polygons of the ``summary_layer`` within each polygon in ``sum_within_layer``. 
                                             
                                             The default is True.
    -------------------------------------    ---------------------------------------------------------
    shape_units                              Optional string. Specify units to summarize the length or areas when ``sum_shape`` is set to true. Units is not required to summarize
                                             points.

                                             When ``summary_layer`` contains polygons: ['Acres', 'Hectares', 'SquareMeters', 'SquareKilometers', 'SquareMiles', 'SquareYards', 'SquareFeet']
                                             
                                             When ``summary_layer`` contains lines: ['Meters', 'Kilometers', 'Feet', 'Yards', 'Miles']
    -------------------------------------    ---------------------------------------------------------
    summary_fields                           Optional list of strings. A list of field names and statistical summary type that you wish 
                                             to calculate for all features in the ``summary_layer`` that are within each polygon in the ``sum_within_layer`` .

                                             Example: ["fieldname1 summary", "fieldname2 summary"]
    -------------------------------------    ---------------------------------------------------------
    group_by_field                           Optional string. This is a field of the ``summary_layer`` features that you can use to calculate statistics separately 
                                             for each unique attribute value. For example, suppose the ``sum_within_layer`` contains city boundaries and 
                                             the ``summary_layer`` features are parcels. One of the fields of the parcels is Status which contains 
                                             two values: VACANT and OCCUPIED. To calculate the total area of vacant and occupied parcels within the 
                                             boundaries of cities, use Status as the ``group_by_field`` field.
    -------------------------------------    ---------------------------------------------------------
    minority_majority                        Optional boolean. This boolean parameter is applicable only when a ``group_by_field`` is specified. 
                                             If true, the minority (least dominant) or the majority (most dominant) attribute values for each group 
                                             field are calculated. Two new fields are added to the ``result_layer`` prefixed with Majority_ and Minority_.

                                             The default is False.
    -------------------------------------    ---------------------------------------------------------
    percent_shape                            Optional boolean. This Boolean parameter is applicable only when a ``group_by_field`` is specified.
                                             If set to true, the percentage of each unique ``group_by_field`` value is calculated for 
                                             each ``sum_within_layer`` polygon. 
                                             
                                             The default is False.
    -------------------------------------    ---------------------------------------------------------
    output_name                              Optional string. If provided, the method will create a feature service of the results. 
                                             You define the name of the service. If ``output_name`` is not supplied, the method will return a feature collection.
    -------------------------------------    ---------------------------------------------------------
    context                                  Optional string. Context contains additional settings that affect task execution. For ``summarize_within``, there are two settings.

                                             #. Extent (``extent``)—a bounding box that defines the analysis area. Only those features in the ``sum_within_layer`` and the ``Summary_layer`` that intersect the bounding box will be summarized.
                                             #. Output Spatial Reference (``outSR``)—the output features will be projected into the output spatial reference.
    -------------------------------------    ---------------------------------------------------------
    estimate                                 Optional boolean. If True, the number of credits to run the operation will be returned.
    =====================================    =========================================================

    :returns: Item if ``output_name`` is set. else results in a Python dict with the following keys:

        dict with the following keys:

            "result_layer" : layer (FeatureCollection)

            "group_by_summary" : layer (FeatureCollection)

    .. code-block:: python

        # USAGE EXAMPLE: To summarize traffic accidents within each county and group them by the day of accident. 
        acc_within_county = summarize_within(sum_within_layer=boundaries,
                                             summary_layer=collision_lyr,
                                             sum_shape=True,
                                             group_by_field='Day',
                                             minority_majority=True,
                                             percent_shape=True,
                                             output_name='summarize accidents within each county',
                                             context={"extent":{"xmin":-13160690.837046918,"ymin":4041586.5461609075,"xmax":-13132466.464352652,"ymax":4058001.397985127,"spatialReference":{"wkid":102100,"latestWkid":3857}}})           
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.summarize_within(
                     sum_within_layer,
                     summary_layer,
                     sum_shape,
                     shape_units,
                     summary_fields,
                     group_by_field,
                     minority_majority,
                     percent_shape,
                     output_name,
                     context,
                     estimate=estimate)


def join_features(target_layer,
                  join_layer,
                  spatial_relationship=None,
                  spatial_relationship_distance=None,
                  spatial_relationship_distance_units=None,
                  attribute_relationship=None,
                  join_operation="""JoinOneToOne""",
                  summary_fields=None,
                  output_name=None,
                  context=None,
                  gis=None,
                  estimate=False):
    """
    .. image:: _static/images/join_features/join_features.png 

    The ``join_features`` method works with two layers and joins the attributes 
    from one feature to another based on spatial and attribute relationships.

    ============================================================================================     =================================================================================================================================
    **Parameter**                                                                                    **Description**
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    target_layer                                                                                     Required layer. The point, line, polygon or table layer that will have attributes from 
                                                                                                     the ``join_layer`` appended to its table. See :ref:`Feature Input<FeatureInput>`.
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    join_layer                                                                                       Required layer. The point, line, polygon or table layer that will be joined to the ``target_layer``. See :ref:`Feature Input<FeatureInput>`.
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    spatial_relationship                                                                             Required string. Defines the spatial relationship used to spatially join features.

                                                                                                     Choice list: ['identicalto', 'intersects', 'completelycontains', 'completelywithin', 'withindistance']
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    spatial_relationship_distance (Required if ``spatial_relationship`` is withindistance)           Optional float. A float value used for the search distance to determine if the target features are near or within a 
                                                                                                     specified distance of the join features. 
                                                                                                     This is only applied if Within a distance of is the selected ``spatial_relationship``. 
                                                                                                     You can only enter a single distance value. The units of the distance values are supplied by the 
                                                                                                     ``spatial_relationship_distance_units`` parameter.
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    spatial_relationship_distance_units (Required if ``spatial_relationship`` is withindistance)     Optional string. The linear unit to be used with the distance value specified in ``spatial_relationship_distance``.

                                                                                                     Choice list: ['Miles', 'Yards', 'Feet', 'NauticalMiles', 'Meters', 'Kilometers']

                                                                                                     The default is 'Miles'.
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    attribute_relationship                                                                           Optional list of dicts. Defines an attribute relationship used to join features. Features are matched when the field 
                                                                                                     values in the join layer are equal to field values in the target layer.
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    join_operation                                                                                   Optional string. A string representing the type of join that will be applied.
                                                                                                     
                                                                                                     Choice list: ['JoinOneToOne', 'JoinOneToMany']

                                                                                                        * ``JoinOneToOne``—If multiple join features are found that have the same relationships with a 
                                                                                                          single target feature, the attributes from the multiple join features will be aggregated using 
                                                                                                          the specified summary statistics. For example, if a point target feature is found within two 
                                                                                                          separate polygon join features, the attributes from the two polygons will be aggregated before 
                                                                                                          being transferred to the output point feature class. If one polygon has an attribute value of 
                                                                                                          3 and the other has a value of 7, and a SummaryField of sum is selected, the aggregated value 
                                                                                                          in the output feature class will be 10. There will always be a Count field calculated, with a 
                                                                                                          value of 2, for the number of features specified. This is the default.
                                                                                                        
                                                                                                        * ``JoinOneToMany``—If multiple join features are found that have the same relationship with 
                                                                                                          a single target feature, the output feature class will contain multiple copies (records) of 
                                                                                                          the target feature. For example, if a single point target feature is found within two separate 
                                                                                                          polygon join features, the output feature class will contain two copies of the target feature: 
                                                                                                          one record with the attributes of the first polygon, and another record with the attributes of 
                                                                                                          the second polygon. There are no summary statistics calculated with this method.
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    summary_fields                                                                                   Optional list of dicts. A list of field names and statistical summary types that you want to calculate. 
                                                                                                     Note that the count is always returned by default.

                                                                                                     fieldName is the name of one of the numeric fields found in the input join layer.

                                                                                                     statisticType is one of the following:

                                                                                                        * ``SUM``—Adds the total value of all the points in each polygon
                                                                                                        * ``MEAN``—Calculates the average of all the points in each polygon
                                                                                                        * ``MIN``—Finds the smallest value of all the points in each polygon
                                                                                                        * ``MAX``—Finds the largest value of all the points in each polygon
                                                                                                        * ``STDDEV``—Finds the standard deviation of all the points in each polygon
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    output_name                                                                                      Optional string. If provided, the method will create a feature service of the results. You define the name of the service. 
                                                                                                     If ``output_name`` is not supplied, the task will return a feature collection.
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    context                                                                                          Optional string. Context contains additional settings that affect method execution. For ``join_features``, there are the following two settings:

                                                                                                     #. Extent (``extent``)—A bounding box that defines the analysis area. Only those features in the input layer that intersect the bounding box will be analyzed.

                                                                                                     #. Output Spatial Reference (``outSR``)—The output features will be projected into the output spatial reference.
    --------------------------------------------------------------------------------------------     ---------------------------------------------------------------------------------------------------------------------------------
    estimate                                                                                         Optional boolean. If True, the number of credits to run the operation will be returned.
    ============================================================================================     =================================================================================================================================
    
    :returns: result_layer : feature layer Item if ``output_name`` is specified, else feature collection.

    .. code-block:: python

        USAGE EXAMPLE: To summarize traffic accidents within each parcel using spatial relationship.
        accident_count_in_each_parcel = join_features(target_layer=parcel_lyr,
                                                      join_layer=traffic_accidents_lyr,
                                                      spatial_relationship='intersects',
                                                      output_name='join features',
                                                      context={"extent":{"xmin":-9375809.87305117,"ymin":4031882.3806860778,"xmax":-9370182.196843527,"ymax":4034872.9794178144,"spatialReference":{"wkid":102100,"latestWkid":3857}}}, )
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.join_features(
        target_layer,
        join_layer,
        spatial_relationship,
        spatial_relationship_distance,
        spatial_relationship_distance_units,
        attribute_relationship,
        join_operation,
        summary_fields,
        output_name,
        context,
        estimate=estimate)

"""
These functions help you identify, quantify, and visualize spatial patterns in your data.

calculate_density takes known quantities of some phenomenon and spreads these quantities across the map.
find_hot_spots identifies statistically significant clustering in the spatial pattern of your data.
interpolate_points predicts values at new locations based on measurements found in a collection of points.
"""

import arcgis as _arcgis

def calculate_density(
        input_layer,
        field=None,
        cell_size=None,
        cell_size_units="Meters",
        radius=None,
        radius_units=None,
        bounding_polygon_layer=None,
        area_units=None,
        classification_type="EqualInterval",
        num_classes=10,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    The calculate_density function creates a density map from point or line features by spreading known quantities of
    some phenomenon (represented as attributes of the points or lines) across the map. The result is a layer of areas
    classified from least dense to most dense.

    For point input, each point should represent the location of some event	or incident, and the result layer represents
    a count of the incident per unit area. A higher density value in a new location means that there are more points near
    that location. In many cases, the result layer can be interpreted as a risk surface for future events. For example,
    if the input points represent locations of lightning strikes, the result layer can be interpreted as a risk surface
    for future lightning strikes.	
            
    For line input, the line density surface represents the total amount of line that is near each location. The units of	
    the calculated density values are the length of line per unit area. For example, if the lines represent rivers, the	
    result layer will represent the total length of rivers that are within the search radius. This result can be used to	
    identify areas that are hospitable to grazing animals.
    
    =========================    =========================================================
    **Argument**                 **Description**
    -------------------------    ---------------------------------------------------------
    input_layer                  Required layer. The point or line features from which to calculate density. See :ref:`Feature Input<FeatureInput>`.
    -------------------------    ---------------------------------------------------------
    field                        Optional string. A numeric field name specifying the number of incidents at each location.  For example, if you have points that represent cities, you can use a field representing the population of the city as the count field, and the resulting population density layer will calculate larger population densities near cities with larger populations. If not specified, each location will be assumed to represent a single count.
    -------------------------    ---------------------------------------------------------
    cell_size                    Optional float. This value is used to create a mesh of points where density values are calculated. The default is approximately 1/1000th of the smaller of the width and height of the analysis extent as defined in the context parameter. The smaller the value, the smoother the polygon boundaries will be. Conversely, with larger values, the polygon boundaries will be more coarse and jagged.
    -------------------------    ---------------------------------------------------------
    cell_size_units              Optional string. The units of the cell_size value.
                                 Choice list: ['Miles', 'Feet', 'Kilometers',  'Meters']
    -------------------------    ---------------------------------------------------------
    radius                       Optional float. A distance specifying how far to search to find point or line features when calculating density values.
    -------------------------    ---------------------------------------------------------
    radius_units                 Optional string. The units of the radius parameter. If no distance is provided, a default will be calculated that is based on the locations of the input features and the values in the count field (if a count field is provided).
                                 Choice list: ['Miles', 'Feet', 'Kilometers',  'Meters']
    -------------------------    ---------------------------------------------------------
    bounding_polygon_layer       Optional layer. A layer specifying the polygon(s) where you want densities to be calculated. For example, if you are interpolating densities of fish within a lake, you can use the boundary of the lake in this parameter and the output will only draw within the boundary of the lake. See :ref:`Feature Input<FeatureInput>`.
    -------------------------    ---------------------------------------------------------
    area_units                   Optional string. The units of the calculated density values.
                                 Choice list: ['areaUnits', 'SquareMiles']
    -------------------------    ---------------------------------------------------------	
    classification_type          Optional string. Determines how density values will be classified into polygons.
                                 Choice list: ['EqualInterval', 'GeometricInterval', 'NaturalBreaks', 'EqualArea', 'StandardDeviation']	
                                    * EqualInterval—Polygons are created such that the range of density values is equal for each area.	
                                    * GeometricInterval—Polygons are based on class intervals that have a geometric series. This method ensures that each class range has approximately the same number of values within each class and that the change between intervals is consistent.	
                                    * NaturalBreaks—Class intervals for polygons are based on natural groupings of the data. Class break values are identified that best group similar values and that maximize the differences between classes.	
                                    * EqualArea—Polygons are created such that the size of each area is equal. For example, if the result has more high density values than low density values, more polygons will be created for high densities.	
                                    * StandardDeviation—Polygons are created based upon the standard deviation of the predicted density values.
    -------------------------    ---------------------------------------------------------
    num_classes                  Optional int. This value is used to divide the range of predicted values into distinct classes. The range of values in each class is determined by the classification_type parameter.
    -------------------------    ---------------------------------------------------------
    output_name                  Optional string. Additional properties such as output feature service name.	
    -------------------------    ---------------------------------------------------------
    context                      Optional string. Additional settings such as processing extent and output spatial reference. For calculate_density, there are two settings.

                                 #. Extent (extent)-a bounding box that defines the analysis area. Only those points in the input_layer that intersect the bounding box will be analyzed.	
                                 #. Output Spatial Reference (outSR)—the output features will be projected into the output spatial reference.
    -------------------------    ---------------------------------------------------------
    gis                          Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------    ---------------------------------------------------------
    estimate                     Optional Boolean. Is true, the number of credits needed to run the operation will be returned as a float.
    =========================    =========================================================


    :returns: result_layer : feature layer Item if output_name is specified, else Feature Collection.

    .. code-block:: python

        USAGE EXAMPLE: To create a layer that shows density of collisions within 2 miles.	
                       The density is classified based upon the standard deviation.
                       The range of density values is divided into 5 classes.	
        	
        collision_density = calculate_density(input_layer=collisions,	
                                        radius=2,	
                                        radius_units='Miles',	
                                        bounding_polygon_layer=zoning_lyr,	
                                        area_units='SquareMiles',	
                                        classification_type='StandardDeviation',	
                                        num_classes=5,	
                                        output_name='density_of_incidents')

    """

    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.calculate_density(
        input_layer,
        field,
        cell_size,
        cell_size_units,
        radius,
        radius_units,
        bounding_polygon_layer,
        area_units,
        classification_type,
        num_classes,
        output_name,
        context,
        estimate=estimate)

def summarize_center_and_dispersion(
        analysis_layer,
        summarize_type,
        ellipse_size=None,
        weight_field=None,
        group_field=None,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):

    """
    The Summarize Center and Dispersion task finds central features and directional distributions.

    ====================    =========================================================
    **Argument**            **Description**
    --------------------    ---------------------------------------------------------
    analysis_layer          The point, line, or polygon features to be analyzed. This
                            parameter can be a URL to a feature service layer with an
                            optional filter to select specific feaures, or a feature
                            collection
    --------------------    ---------------------------------------------------------
    summarize_type          The method with which to summarize the analysis_layer.
                            Choice List:
                            ["CentralFeature", "MeanCenter", "MedianCenter",
                            "Ellipse"]
                            Example: "CentralFeature"
    --------------------    ---------------------------------------------------------
    ellipse_size            The size of the output ellipse in standard deviations.
                            The default ellipse size is 1. Valid choices are 1, 2, or
                            3 standard deviations.
                            Choice List: [1, 2, 3]
                            Examples:
                            "1"
                            [1, 2, 3]
    --------------------    ---------------------------------------------------------
    weight_field            A numeric field in the analysis_layer to be used to
                            weight locations according to their relative importance.
    --------------------    ---------------------------------------------------------
    group_field             The field used to group features for separate directional
                            distribution calculations. The group_field can be of
                            integer, date, or string type.
    --------------------    ---------------------------------------------------------
    output_name             Optional string. Additional properties such as output
                            feature service name.
    --------------------    ---------------------------------------------------------
    context                 Optional string. Additional settings such as processing
                            extent and output spatial reference.
    --------------------    ---------------------------------------------------------
    gis                     Optional, the GIS on which this tool runs. If not
                            specified, the active GIS is used.
    --------------------    ---------------------------------------------------------
    estimate                Optional Boolean. If True, the number of credits to run the operation will be returned.
    ====================    =========================================================

    :returns: Python dictionary with the following keys:
        "central_feature_result_layer" : layer (FeatureCollection)
        "mean_feature_result_layer" : layer (FeatureCollection)
        "median_feature_result_layer" : layer (FeatureCollection)
        "ellipse_feature_result_layer" : layer (FeatureCollection)
        "process_info" : list of messages
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

def find_point_clusters(
        analysis_layer,
        min_features_cluster,
        search_distance=None,
        search_distance_unit=None,
        output_name=None,
        context=None,
        gis=None, estimate=False):

    """
    The Find Point Clusters function finds clusters of point features in surrounding
    noise based on their spatial distribution. Output is a layer containing records
    assigned to a cluster or noise.

    ====================    =========================================================
    **Argument**            **Description**
    --------------------    ---------------------------------------------------------
    analysis_layer          Required layer. The point feature layer for which
                            density-based clustering will be calculated.
    --------------------    ---------------------------------------------------------
    min_features_cluster    Required integer. The minimum number of features to be
                            considered a cluster. Any cluster with fewer features
                            than the number provided will be considered noise.
    --------------------    ---------------------------------------------------------
    search_distance         Optional double. The maximum distance to consider. The
                            Minimum Features per Cluster specified must be found
                            within this distance for cluster membership. Individual
                            clusters will be separated by at least this distance. If
                            a feature is located further than this distance from the
                            next closest feature in the cluster, it will not be
                            included in the cluster.
    --------------------    ---------------------------------------------------------
    search_distance_unit    Optional string. The linear unit to be used for the
                            search distance parameter.
    --------------------    ---------------------------------------------------------
    output_name             Optional string. Additional properties such as output
                            feature service name.
    --------------------    ---------------------------------------------------------
    context                 Optional string. Additional settings such as processing
                            extent and output spatial reference.
    --------------------    ---------------------------------------------------------
    gis                     Optional, the GIS on which this tool runs. If not
                            specified, the active GIS is used.
    --------------------    ---------------------------------------------------------
    estimate                Optional Boolean. If True, the number of credits to run the operation will be returned.
    ====================    =========================================================

    :returns: Python dictionary with the following keys:
        "point_clusters_result_layer" : layer (FeatureCollection)
        "process_info" : list of messages
    """

    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.find_point_clusters(
        analysis_layer,
        min_features_cluster,
        search_distance,
        search_distance_unit,
        output_name,
        context,
        estimate=estimate)

def find_hot_spots(
        analysis_layer,
        analysis_field=None,
        divided_by_field=None,
        bounding_polygon_layer=None,
        aggregation_polygon_layer=None,
        output_name=None,
        context=None,
        gis=None,
        estimate=False,
        shape_type=None):
    """
    The Find Hot Spots function finds statistically significant clusters of incident points, weighted points, or
    weighted polygons. For incident data, the analysis field (weight) is obtained by aggregation.
    Output is a hot spot map.

    =========================    =========================================================
    **Argument**                 **Description**
    -------------------------    ---------------------------------------------------------
    analysis_layer               Required layer (see Feature Input in documentation). The point or polygon feature layer for which hot spots will be calculated.
    -------------------------    ---------------------------------------------------------
    analysis_field               Optional string. The numeric field in the AnalysisLayer that will be analyzed.
    -------------------------    ---------------------------------------------------------
    divided_by_field             Optional string. The field that will segment the locations.
    -------------------------    ---------------------------------------------------------
    bounding_polygon_layer       Optional layer (see Feature Input in documentation). When the analysis layer is points and no AnalysisField is specified, you can provide polygons features that define where incidents could have occurred.
    -------------------------    ---------------------------------------------------------
    aggregation_polygon_layer    Optional layer (see Feature Input in documentation). When the AnalysisLayer contains points and no AnalysisField is specified, you can provide polygon features into which the points will be aggregated and analyzed, such as administrative units.
    -------------------------    ---------------------------------------------------------
    output_name                  Optional string. Additional properties such as output feature service name.
    -------------------------    ---------------------------------------------------------
    context                      Optional string. Additional settings such as processing extent and output spatial reference.
    -------------------------    ---------------------------------------------------------
    gis                          Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------    ---------------------------------------------------------
    estimate                     Optional Boolean. Is true, the number of credits needed to run the operation will be returned as a float.
    -------------------------    ---------------------------------------------------------
    shape_type                   Optional string. The shape of the polygon mesh the input features will be aggregated into.
    =========================    =========================================================

    :Returns: dict with the following keys:
       "hot_spots_result_layer" : layer (FeatureCollection)
       "process_info" : list of messages

    """

    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.find_hot_spots(
        analysis_layer,
        analysis_field,
        divided_by_field,
        bounding_polygon_layer,
        aggregation_polygon_layer,
        output_name,
        context,
        estimate=estimate,
        shape_type=shape_type)


def find_outliers(analysis_layer,
                  analysis_field,
                  divided_by_field=None,
                  bounding_polygon_layer=None,
                  aggregation_polygon_layer=None,
                  permutations=None,
                  shape_type=None,
                  cell_size=None,
                  cell_units=None,
                  distance_band=None,
                  band_units=None,
                  output_name=None,
                  context=None,
                  gis=None,
                  estimate=False):
    """

    The Find Outliers task analyzes point data (such as crime incidents, traffic accidents, or trees) or field values associated with points or area features (such as the number of people in each census tract or the total sales for retail stores). It finds statistically significant spatial clusters of high values and low values and statistically significant high or low spatial outliers within those clusters.

    The result map layer shows high outliers in red and low outliers in dark blue. Clusters of high values appear pink and clusters of low values appear light blue. Features that are beige are not a statistically significant outlier and not part of a statistically significant cluster; the spatial pattern associated with these features could very likely be the result of random processes and random chance.

    Parameters
    ----------
    analysis_layer : Required layer (see Feature Input in documentation)
        The point or polygon feature layer for which outliers will be calculated.
    analysis_field : Optional string
        The numeric field that will be analyzed.
    divided_by_field : Optional string, The numeric field in the analysis_layer that will be used to normalize your data.
    bounding_polygon_layer : Optional layer (see Feature Input in documentation)
        When the analysis layer is points and no analysisField is specified, you can provide polygon features that define where incidents could have occurred.
    aggregation_polygon_layer : Optional layer (see Feature Input in documentation)
        When the AnalysisLayer contains points and no AnalysisField is specified, you can provide polygon features into which the points will be aggregated and analyzed, such as administrative units.
    permutations : Permutations are used to determine how likely it would be to find the actual spatial distribution of the values you are analyzing. Choosing the number of permutations is a balance between precision and increased processing time. A lower number of permutations can be used when first exploring a problem, but it is best practice to increase the permutations to the highest number feasible for final results.

       - Speed implements 199 permutations and results in p-values with a precision of 0.01.
       - Balance implements 499 permutations and results in p-values with a precision of 0.002.
       - Precision implements 999 permutations and results in p-values with a precision of 0.001.
       Values: Speed | Balance | Precision
    shape_type : optional string, The shape of the polygon mesh the input features will be aggregated into.

      - Fishnet - The input features will be aggregated into a grid of square (fishnet) cells.
      - Hexagon - The input features will be aggregated into a grid of hexagonal cells.
    cell_size : The size of the grid cells used to aggregate your features. When aggregating into a hexagon grid, this distance is used as the height to construct the hexagon polygons.
    cell_units : The units of the cellSize value. You must provide a value if cellSize has been set.
      Values: Miles | Feet | Kilometers | Meters
    distance_band : The spatial extent of the analysis neighborhood. This value determines which features are analyzed together in order to assess local clustering.
    band_units : The units of the distanceBand value. You must provide a value if distanceBand has been set.
      Values: Miles | Feet | Kilometers | Meters
    output_name : Optional string
        Additional properties such as output feature service name.
    context : Optional string
        Additional settings such as processing extent and output spatial reference.
    gis : The GIS used for running this analysis
    estimate : Optional Boolean. If True, the number of credits to run the operation will be returned.

    Returns
    -------
    Item it output_name is set.
    dict with the following keys:
       "find_outliers_result_layer" : layer (FeatureCollection)
       "process_info" : list of messages

        """

    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.find_outliers(analysis_layer,
                                                    analysis_field,
                                                    divided_by_field,
                                                    bounding_polygon_layer,
                                                    aggregation_polygon_layer,
                                                    permutations,
                                                    shape_type,
                                                    cell_size,
                                                    cell_units,
                                                    distance_band,
                                                    band_units,
                                                    output_name,
                                                    context,
                                                    estimate=estimate)


def interpolate_points(
        input_layer,
        field,
        interpolate_option="5",
        output_prediction_error=False,
        classification_type="GeometricInterval",
        num_classes=10,
        class_breaks=[],
        bounding_polygon_layer=None,
        predict_at_point_layer=None,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    The Interpolate Points function allows you to predict values at new locations based on measurements from a
    collection of points. The function takes point data with values at each point and returns areas classified by
    predicted values.

    Parameters
    ----------
    input_layer : Required layer (see Feature Input in documentation)
        The point layer whose features will be interpolated.
    field : Required string
        Name of the numeric field containing the values you wish to interpolate.
    interpolate_option : Optional string
        Integer value declaring your preference for speed versus accuracy, from 1 (fastest) to 9 (most accurate). More
        accurate predictions take longer to calculate.
    output_prediction_error : Optional bool
        If True, a polygon layer of standard errors for the interpolation predictions will be returned in the
        predictionError output parameter.
    classification_type : Optional string
        Determines how predicted values will be classified into areas.
    num_classes : Optional int
        This value is used to divide the range of interpolated values into distinct classes. The range of values in each
        class is determined by the classificationType parameter. Each class defines the boundaries of the result
        polygons.
    class_breaks : Optional list of floats
        If classificationType is Manual, supply desired class break values separated by spaces. These values define the
        upper limit of each class, so the number of classes will equal the number of entered values. Areas will not be
        created for any locations with predicted values above the largest entered break value. You must enter at least
        two values and no more than 32.
    bounding_polygon_layer : Optional layer (see Feature Input in documentation)
        A layer specifying the polygon(s) where you want values to be interpolated.
    predict_at_point_layer : Optional layer (see Feature Input in documentation)
        An optional layer specifying point locations to calculate prediction values. This allows you to make predictions
        at specific locations of interest.
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
       "prediction_error" : layer (FeatureCollection)
       "predicted_point_layer" : layer (FeatureCollection)
    """

    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.interpolate_points(
        input_layer,
        field,
        interpolate_option,
        output_prediction_error,
        classification_type,
        num_classes,
        class_breaks,
        bounding_polygon_layer,
        predict_at_point_layer,
        output_name,
        context,
        estimate=estimate)

"""
These functions are used to identify areas that meet a number of different criteria you specify. These criteria can be based
upon attribute queries (for example, parcels that are vacant) and spatial queries (for example, within 1 kilometer of a
river). The areas that are found can be selected from existing features (such as existing land parcels) or new features
can be created where all the requirements are met.

find_existing_locations searches for existing areas in a layer that meet a series of criteria.
derive_new_locations creates new areas from locations in your study area that meet a series of criteria.
find_similar_locations finds locations most similar to one or more reference locations based on criteria you specify.
find_centroids finds and generates points from the representative center (centroid) of each input multipoint, line, or area feature.
choose_best_facilities choose the best locations for facilities by allocating locations that have demand for these
facilities in a way that satisfies a given goal.
create_viewshed creates areas that are visible based on locations you specify.
create_watersheds creates catchment areas based on locations you specify.
trace_downstream determines the flow paths in a downstream direction from the locations you specify
"""
import arcgis as _arcgis

from arcgis.features._analysis import choose_best_facilities

def find_existing_locations(
        input_layers=None,
        expressions=None,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    The Find Existing Locations task selects features in the input layer that meet a query you specify.
    A query is made up of one or more expressions. There are two types of expressions: attribute and spatial.
    An example of an attribute expression is that a parcel must be vacant, which is an attribute of the Parcels layer
    (where STATUS = 'VACANT'). An example of a spatial expression is that the parcel must also be within a certain
    distance of a river (Parcels within a distance of 0.75 Miles from Rivers).

    Parameters
    ----------
    input_layers : Required list of strings
        A list of layers that will be used in the expressions parameter.
    expressions : Required string
        Specify a list of expressions. Please refer documentation at http://developers.arcgis.com for more information
        on creating expressions.
    output_name : Optional string
        Additional properties such as output feature service name.
    context : Optional string
        Additional settings such as processing extent and output spatial reference.
    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

    Returns
    -------
    result_layer : layer (FeatureCollection)
    """
    if input_layers is None:
        input_layers = []
    if expressions is None:
        expressions = []
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.find_existing_locations(
        input_layers,
        expressions,
        output_name,
        context,
        estimate=estimate)


def derive_new_locations(
        input_layers=[],
        expressions=[],
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    .. image:: _static/images/derive_new_locations/derive_new_locations.png 

    .. |intersect| image:: _static/images/derive_new_locations/intersect.png
    .. |distance| image:: _static/images/derive_new_locations/distance.png
    .. |within| image:: _static/images/derive_new_locations/within.png    
    .. |nearest| image:: _static/images/derive_new_locations/nearest.png  
    .. |contains| image:: _static/images/derive_new_locations/contains.png          

    The ``derive_new_locations`` method derives new features from the input layers that meet a query you specify. A query is
    made up of one or more expressions. There are two types of expressions: attribute and spatial. An example of an
    attribute expression is that a parcel must be vacant, which is an attribute of the Parcels layer
    (STATUS = 'VACANT'). An example of a spatial expression is that the parcel must also be within a certain
    distance of a river (Parcels within a distance of 0.75 Miles from Rivers).
    
    The ``derive_new_locations`` method is very similar to the ``find_existing_locations`` method, the main difference is that 
    the result of ``derive_new_locations`` can contain partial features.
    
    * In both methods, the attribute expression  ``where`` and the spatial relationships within and contains return the same result. 
      This is because these relationships return entire features.
    * When ``intersects`` or ``within_distance`` is used, ``derive_new_locations`` creates new features 
      in the result. For example, when intersecting a parcel feature and a flood zone area that partially overlap each other, 
      ``find_existing_locations`` will return the entire parcel whereas ``derive_new_locations`` will return just the portion of 
      the parcel that is within the flood zone.

    =====================================    ======================================================================================================
    **Argument**                             **Description**
    -------------------------------------    ------------------------------------------------------------------------------------------------------
    input_layers                             Required list of feature layers. A list of layers that will be used in the expressions parameter.
                                             Each layer in the list can be:

                                             * a feature service layer with an optional filter to select specific features, or
                                             * a feature collection
    -------------------------------------    ------------------------------------------------------------------------------------------------------
    expressions                              Required dict. There are two types of expressions, attribute and spatial. 
                                             
                                             Example attribute expression:
                                             
                                             {
                                                "operator": "and",
                                                "layer": 0,
                                                "where": "STATUS = 'VACANT'"
                                             }   

                                             **Note**
                                             * operator can be either ``and`` or ``or``
                                             * layer is the index of the layer in the ``input_layers`` parameter.
                                             * The where clause must be surrounded by double quotes.
                                             * When dealing with text fields, values must be single-quoted ('VACANT').
                                             * Date fields support all queries except LIKE. Dates are strings in YYYY:MM:DD hh:mm:ss format. Here's an example using the date field ObsDate:
                                               "where": "ObsDate >= '1998-04-30 13:30:00' "

                                             +----------+------------------------------------------------------------------+
                                             | =        | Equal                                                            |
                                             +----------+------------------------------------------------------------------+
                                             | >        | Greater than                                                     |
                                             +----------+------------------------------------------------------------------+
                                             | <        | Less than                                                        |
                                             +----------+------------------------------------------------------------------+
                                             | >=       | Greater than or equal to                                         |
                                             +----------+------------------------------------------------------------------+
                                             | <=       | Less than or equal to                                            |
                                             +----------+------------------------------------------------------------------+
                                             | <>       | Not equal                                                        |
                                             +----------+------------------------------------------------------------------+
                                             | LIKE '%  | A percent symbol (%) signifies a wildcard, meaning that          |
                                             | <string>'| anything is acceptable in its place—one character, a             |
                                             |          | hundred characters, or no character. This expression             |
                                             |          | would select Mississippi and Missouri among USA                  |
                                             |          | state names: STATE_NAME LIKE 'Miss%'                             |
                                             +----------+------------------------------------------------------------------+
                                             | BETWEEN  | Selects a record if it has a value greater than or equal         |
                                             | <value1> | to <value1> and less than or equal to <value2>.                  |
                                             | AND      | For example, this expression selects all records with            | 
                                             | <value2> | an HHSIZE value greater than or equal to 3 and less              |
                                             |          | than or equal to 10:                                             |          
                                             |          |                                                                  |
                                             |          | HHSIZE BETWEEN 3 AND 10                                          |
                                             |          |                                                                  |
                                             |          | The above is equivalent to:                                      |
                                             |          |                                                                  |
                                             |          | HHSIZE >= 3 AND HHSIZE <= 10                                     | 
                                             |          | This operator applies to numeric or date fields.                 |
                                             |          | Here is an example of a date query on the field ObsDate:         |
                                             |          |                                                                  | 
                                             |          | ObsDate BETWEEN '1998-04-30 00:00:00' AND '1998-04-30 23:59:59'  |  
                                             |          |                                                                  |
                                             |          | Time is optional.                                                |
                                             +----------+------------------------------------------------------------------+ 
                                             | NOT      | Selects a record if it has a value outside the range between     |
                                             | BETWEEN  | <value1> and less than or equal to <value2>.                     |
                                             | <value1> | For example, this expression selects all records whose           | 
                                             | AND      | HHSIZE value is less than 5 and greater than 7.                  |
                                             | <value2> |                                                                  |                       
                                             |          | HHSIZE NOT BETWEEN 5 AND 7                                       |
                                             |          |                                                                  |
                                             |          | The above is equivalent to:                                      |
                                             |          |                                                                  |
                                             |          | HHSIZE < 5 OR HHSIZE > 7                                         | 
                                             |          | This operator applies to numeric or date fields.                 |
                                             |          |                                                                  |
                                             |          | **Note**                                                         |
                                             |          |                                                                  |
                                             |          | You can use the contains relationship with points and lines.     |
                                             |          | For example, you have a layer of street centerlines (lines) and  |
                                             |          | a layer of manhole covers (points), and you want to find streets |
                                             |          | that contain a manhole cover. You could use contains to find     |
                                             |          | streets that contain manhole covers, but in order for a line to  |
                                             |          | contain a point, the point must be exactly on the line (that is, | 
                                             |          | in GIS terms, they are snapped to each other). If there is any   |
                                             |          | doubt about this, use the withinDistance relationship with a     |
                                             |          | suitable distance value.                                         |
                                             +----------+------------------------------------------------------------------+                                         
             
                                             Example spatial expression:
                                             {
                                                "operator": "and",
                                                "layer": 0,
                                                "spatialRel": "withinDistance",
                                                "selectingLayer": 1,
                                                "distance": 10,
                                                "units": "miles"
                                             }

                                             * operator can be either ``and`` or ``or``
                                             * layer is the index of the layer in ``the input_layers`` parameter. The result of the expression is features in this layer.
                                             * spatialRel is the spatial relationship. There are nine spatial relationships.
                                             * distance is the distance to use for the withinDistance and notWithinDistance spatial relationship.
                                             * units is the units for distance. 

                                             +-------------------+----------------------------------------------------------------------------------------+
                                             | spatialRel        | Description                                                                            |
                                             +-------------------+----------------------------------------------------------------------------------------+
                                             | intersects        | |intersect|                                                                            |
                                             |                   |                                                                                        |       
                                             |                   | A feature in layer passes the intersect test if it overlaps                            |
                                             | notIntersects     | any part of a feature in selectingLayer, including touches                             |
                                             |                   | (where features share a common point).                                                 |
                                             |                   |                                                                                        |
                                             |                   | * intersects—If a feature in layer intersects a feature in                             |
                                             |                   |   selectingLayer, the portion of the feature in layer that                             |
                                             |                   |   intersects the feature in selectingLayer is included in                              |
                                             |                   |   the output.                                                                          |
                                             |                   | * notIntersects—If a feature in layer intersects a feature in                          |
                                             |                   |   selectingLayer, the portion of the feature in layer that                             |
                                             |                   |   intersects the feature in selectingLayer is excluded from                            |
                                             |                   |   the output.                                                                          |
                                             +-------------------+----------------------------------------------------------------------------------------+
                                             | withinDistance    | |distance|                                                                             |
                                             |                   |                                                                                        |
                                             |                   | The within a distance relationship uses the straight-line                              |
                                             | notWithinDistance | distance between features in layer to those in selectingLayer.                         |
                                             |                   | withinDistance—The portion of the feature in layer that is                             |
                                             |                   | within the specified distance of a feature in selectingLayer                           |
                                             |                   | is included in the output.                                                             |
                                             |                   | notWithinDistance—The portion of the feature in layer that is                          |
                                             |                   | within the specified distance of a feature in selectingLayer is                        | 
                                             |                   | excluded from output. You can think of this relationship as                            |
                                             |                   | "is farther away than".                                                                |
                                             +-------------------+----------------------------------------------------------------------------------------+
                                             | contains          | |intersect|                                                                            |
                                             |                   |                                                                                        |
                                             |                   | A feature in layer passes this test if it completely                                   |
                                             | notContains       | surrounds a feature in selectingLayer. No portion of the                               |
                                             |                   | containing feature; however, the contained feature is allowed                          | 
                                             |                   | to touch the containing feature (that is, share a common                               |
                                             |                   | point along its boundary).                                                             |     
                                             |                   |                                                                                        |
                                             |                   | contains—If a feature in layer contains a feature in                                   |
                                             |                   | selectingLayer, the feature in layer is included in the output.                        |
                                             |                   | notContains—If a feature in layer contains a feature in                                |
                                             |                   | selectingLayer, the feature in the first layer is excluded                             |
                                             +-------------------+----------------------------------------------------------------------------------------+ 
                                             | within            | |within|                                                                               |
                                             |                   |                                                                                        |
                                             |                   | A feature in layer passes this test if it is completely                                |
                                             | notWithin         | surrounded by a feature in selectingLayer. The entire feature                          |
                                             |                   | layer must be within the containing feature; however, the two                          |
                                             |                   | features are allowed to touch (that is, share a common point                           |
                                             |                   | along its boundary).                                                                   |
                                             |                   |                                                                                        |
                                             |                   | * within—If a feature in layer is completely within a feature in                       | 
                                             |                   |   selectingLayer, the feature in layer is included in the output.                      |
                                             |                   | * notWithin—If a feature in layer is completely within a feature                       | 
                                             |                   |   in selectingLayer, the feature in layer is excluded from the                         |
                                             |                   |   output.                                                                              |
                                             |                   |                                                                                        |
                                             |                   | **Note:**                                                                              |
                                             |                   |                                                                                        |
                                             |                   | can use the within relationship for points and lines, just as                          |
                                             |                   | you can with the contains relationship. For example, your first                        |
                                             |                   | layer contains points representing manhole covers and you want                         |
                                             |                   | to find the manholes that are on street centerlines (as opposed                        |
                                             |                   | to parking lots or other non-street features). You could use                           |
                                             |                   | within to find manhole points within street centerlines, but                           |
                                             |                   | in order for a point to contain a line, the point must be exactly                      | 
                                             |                   | on the line (that is, in GIS terms, they are snapped to each                           |
                                             |                   | other). If there is any doubt about this, use the withinDistance                       |
                                             |                   | relationship with a suitable distance value.                                           |    
                                             +-------------------+----------------------------------------------------------------------------------------+ 
                                             | nearest           | |nearest|                                                                              |
                                             |                   |                                                                                        |
                                             |                   | feature in the first layer passes this test if it is nearest                           |
                                             |                   | to a feature in the second layer.                                                      |
                                             |                   |                                                                                        |
                                             |                   | * nearest—If a feature in the first layer is nearest to a                              |
                                             |                   |   feature in the second layer, the feature in the first layer                          |
                                             |                   |   is included in the output.                                                           |
                                             +-------------------+----------------------------------------------------------------------------------------+
                                         
    -------------------------------------    ------------------------------------------------------------------------------------------------------
    output_name                              Optional string. If provided, the task will create a feature layer of the results. You define the name of the layer.                                           If output_name is not supplied, the task will return a feature collection.
    -------------------------------------    ------------------------------------------------------------------------------------------------------
    context                                  Optional string. Additional settings such as processing extent and output spatial reference. For                                                               ``derive_new_locations``, there are two settings.

                                             #. Extent (extent)-a bounding box that defines the analysis area. Only those points in the input_layers that intersect the bounding box will be analyzed.	
                                             #. Output Spatial Reference (outSR)
    -------------------------------------    ------------------------------------------------------------------------------------------------------
    gis                                      Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------------------    ------------------------------------------------------------------------------------------------------
    estimate                                 Optional boolean. Is true, the number of credits needed to run the operation will be returned as a float.        
    =====================================    ======================================================================================================
 
.. code-block:: python

        USAGE EXAMPLE: To Identify areas that are suitable cougar habitat using the criteria defined by experts. 
         
        new_loaction = derive_new_locations(input_layers=[slope, vegetation, streams, highways],
                                    expressions=[{"operator":"","layer":0,"selectingLayer":1,"spatialRel":"intersects"},
                                                 {"operator":"and","layer":0,"selectingLayer":2,"spatialRel":"withinDistance","distance":500,"units":"Feet"},
                                                 {"operator":"and","layer":0,"selectingLayer":3,"spatialRel":"notWithinDistance","distance":1500,"units":"Feet"},
                                                 {"operator":"and","layer":0,"where":"GRIDCODE = 1"}],
                                    output_name='derive_new_loactions') 



    """

    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.derive_new_locations(
        input_layers,
        expressions,
        output_name,
        context,
        estimate=estimate)



def find_similar_locations(
        input_layer,
        search_layer,
        analysis_fields=[],
        input_query=None,
        number_of_results=0,
        output_name=None,
        context=None,
        gis=None, estimate=False):
    """
    Finds the locations that are most similar to one or more reference locations based on criteria that you specify.

    Parameters
    ----------
    input_layer : Required layer (see Feature Input in documentation)

    search_layer : Required layer (see Feature Input in documentation)

    analysis_fields : Required list of strings

    input_query : Optional string

    number_of_results : Optional int

    output_name : Optional string

    context : Optional string


    Returns
    -------
    dict with the following keys:
       "similar_result_layer" : layer (FeatureCollection)
       "process_info" : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.find_similar_locations(
        input_layer,
        search_layer,
        analysis_fields,
        input_query,
        number_of_results,
        output_name,
        context,
        estimate=estimate)

def find_centroids(input_layer,
                   point_location=False,
                   output_name=None,
                   context=None,
                   gis=None, 
                   estimate=False):
    """
    .. image:: _static/images/find_centroids/find_centroids.png 

    The ``find_centroids`` method that finds and generates points from the representative center (centroid) of 
    each input multipoint, line, or area feature. Finding the centroid of a feature is very common for many analytical 
    workflows where the resulting points can then be used in other analytic workflows.

    For example, polygon features that contain demographic data can be converted to centroids that can be used in network analysis.

    ================  ===============================================================
    **Argument**      **Description**
    ----------------  ---------------------------------------------------------------
    input_layer       Required feature layer. The multipoint, line, or polygon features that will be used to generate centroid point features. See :ref:`Feature Input<FeatureInput>`.
    ----------------  ---------------------------------------------------------------
    point_location    Optional boolean. A Boolean value that determines the output location of the points.

                        + True - Output points will be the nearest point to the actual centroid, but located inside or contained by the bounds of the input feature.
                        + False - Output point locations will be determined by the calculated geometric center of each input feature. This is the default.
    ----------------  ---------------------------------------------------------------
    output_name       Optional string. If provided, the method will create a feature service of the results. You define the name of the service. If ``output_name`` is not supplied, the method will return a feature collection.
    ----------------  ---------------------------------------------------------------
    context           Optional string. Context contains additional settings that affect method execution. For ``find_centroids``, there are two settings.
                       
                      #. Extent (``extent``)—a bounding box that defines the analysis area. Only those features in the ``input_layer`` that intersect the bounding box will be buffered.
                      #. Output Spatial Reference (``outSR``)—the output features will be projected into the output spatial reference. 
    ----------------  ---------------------------------------------------------------
    estimate          Optional boolean. If True, the number of credits to run the operation will be returned.
    ================  ===============================================================

    :returns: result_layer : feature layer Item if ``output_name`` is specified, else Feature Collection.

    .. code-block:: python

        # USAGE EXAMPLE: To find centroids of madison fields nearest to the actual centroids.
        
        centroid = find_centroids(madison_fields,
                                  point_location=True,
                                  output_name='find centroids')              
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    if gis._portal.is_arcgisonline == False:
        raise Exception("find_centroids is only available on ArcGIS Online.")
    return gis._tools.featureanalysis.find_centroids(input_layer,
                                                     point_location,
                                                     output_name,
                                                     context,
                                                     estimate=estimate)



"""
def choose_best_facilities():
    '
    Choose the best locations for facilities by allocating locations that have demand for these facilities in a way that
    satisfies a given goal.
    '
    pass #TODO
"""

def create_viewshed(
        input_layer,
        dem_resolution="Finest",
        maximum_distance=None,
        max_distance_units="Meters",
        observer_height=None,
        observer_height_units="Meters",
        target_height=None,
        target_height_units="Meters",
        generalize=True,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    .. image:: _static/images/create_viewshed/create_viewshed.png 

    The create_viewshed method identifies visible areas based on the observer locations you provide. 
    The results are areas where the observers can see the observed objects (and the observed objects can see the observers).

    =========================    =========================================================
    **Parameter**                **Description**
    -------------------------    ---------------------------------------------------------
    input_layer                  Required point feature layer. The features to use as the observer locations. See :ref:`Feature Input<FeatureInput>`.
    -------------------------    ---------------------------------------------------------
    dem_resolution               Optional string. The approximate spatial resolution (cell size) of the source elevation data used for the calculation.

                                 The resolution values are an approximation of the spatial resolution of the digital elevation model. 
                                 While many elevation sources are distributed in units of arc seconds, the keyword is an approximation 
                                 of those resolutions in meters for easier understanding.

                                 Choice list: ['FINEST', '10m', '24m', '30m', '90m']

                                 The default is the finest resolution available.
    -------------------------    ---------------------------------------------------------
    maximum_distance             Optional float. This is a cutoff distance where the computation of visible areas stops. Beyond this distance, it is unknown whether the analysis points and the other objects can see each other.

                                 It is useful for modeling current weather conditions or a given time of day, such as dusk. Large values increase computation time.

                                 Unless specified, a default maximum distance will be computed based on the resolution and extent of the source DEM. The allowed maximum value is 50 kilometers.
                                 Use max_distance_units to set the units for maximum_distance.
    -------------------------    ---------------------------------------------------------
    max_distance_units           Optional string. The units for the maximum_distance parameter.
                                             
                                 Choice list: ['Meters', 'Kilometers', 'Feet', 'Miles', 'Yards']
                                             
                                 The default is 'Meters'.
    -------------------------    ---------------------------------------------------------
    observer_height              Optional float. This is the height above the ground of the observer locations.

                                 The default is 1.75 meters, which is approximately the average height of a person. If you are looking from an elevated location, such as an observation tower or a tall building, use that height instead.

                                 Use observer_height_units to set the units for observer_height.

    -------------------------    ---------------------------------------------------------
    observer_height_units        Optional string. The units for the observer_height parameter.
                                 
                                 Choice list: ['Meters', 'Kilometers', 'Feet', 'Miles', 'Yards']

                                 The default is 'Meters'.
    -------------------------    ---------------------------------------------------------
    target_height                Optional float. This is the height of structures or people on the ground used to 
                                 establish visibility. The result viewshed are those areas where an input point can see these other objects. 
                                 The converse is also true; the other objects can see an input point.

                                 * If your input points represent wind turbines and you want to determine where people standing on the 
                                   ground can see the turbines, enter the average height of a person (approximately 6 feet). 
                                   The result is those areas where a person standing on the ground can see the wind turbines.
                                 * If your input points represent fire lookout towers and you want to determine which lookout 
                                   towers can see a smoke plume 20 feet high or higher, enter 20 feet for the height. The result 
                                   is those areas where a fire lookout tower can see a smoke plume at least 20 feet high.
                                 * If your input points represent scenic overlooks along roads and trails and you want to determine 
                                   where wind turbines 400 feet high or higher can be seen, enter 400 feet for the height. The result 
                                   is those areas where a person standing at a scenic overlook can see a wind turbine at least 400 feet high.
                                 * If your input points represent scenic overlooks and you want to determine how much area on the ground 
                                   people standing at the overlook can see, enter zero. The result is those areas that can be seen from the scenic overlook.
                                 
                                 Use target_height_units to set the units for target_height.                                                                

    -------------------------    ---------------------------------------------------------
    target_height_units          Optional string. The units for the target_height parameter.

                                 Choice list: ['Meters', 'Kilometers', 'Feet', 'Miles', 'Yards']
                                             
                                 The default is 'Meters'.
    -------------------------    ---------------------------------------------------------
    generalize                   Optional boolean. Determines whether or not the viewshed polygons are to be generalized.

                                 The viewshed calculation is based on a raster elevation model that creates a result with stair-stepped edges. 
                                 To create a more pleasing appearance and improve performance, the default behavior is to generalize the polygons. 
                                 The generalization process smooths the boundary of the visible areas and may remove some single-cell visible areas.  

                                 The default value is True.          
    -------------------------    ---------------------------------------------------------
    output_name                  Optional string. Output feature service name. If not provided, a feature collection is returned.
    -------------------------    ---------------------------------------------------------
    context                      Optional dict. Context contains additional settings that affect task execution. For ``create_viewshed``, there are two settings.
                                             
                                 #. Extent (``extent``)-a bounding box that defines the analysis area. Only those points in the ``input_layer`` 
                                    that intersect the bounding box will be analyzed.

                                 #. Output Spatial Reference (``outSR``)—the output features will be projected into the output spatial reference.
    -------------------------    ---------------------------------------------------------
    gis                          Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------    ---------------------------------------------------------
    estimate                     Optional boolean. If True, the estimated number of credits required to run the operation will be returned.
    =========================    =========================================================
    
    :returns result_layer : feature layer Item if output_name is specified, else Feature Collection.

    .. code-block:: python

        USAGE EXAMPLE: To create viewshed around esri headquarter office.
        
        viewshed3 = create_viewshed(hq_lyr,
                            maximum_distance=9,
                            max_distance_units='Miles',
                            target_height=6,
                            target_height_units='Feet',
                            output_name="create Viewshed")
    
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.create_viewshed(
        input_layer,
        dem_resolution,
        maximum_distance,
        max_distance_units,
        observer_height,
        observer_height_units,
        target_height,
        target_height_units,
        generalize,
        output_name,
        context,
        estimate=estimate)


def create_watersheds(
        input_layer,
        search_distance=None,
        search_units="Meters",
        source_database="FINEST",
        generalize=True,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    .. image:: _static/images/create_watersheds/create_watersheds.png 

    The ``create_watersheds`` method determines the watershed, or upstream contributing area, for each point 
    in your analysis layer. For example, suppose you have point features representing locations 
    of waterborne contamination, and you want to find the likely sources of the contamination. 
    Since the source of the contamination must be somewhere within the watershed upstream of the 
    point, you would use this tool to define the watersheds containing the sources of the contaminant.
 

    =========================    =========================================================
    **Parameter**                **Description**
    -------------------------    ---------------------------------------------------------
    input_layer                  Required point feature layer. The point features used for calculating watersheds. 
                                 These are referred to as pour points, because it is the location at which water pours out of the watershed. 
                                 See :ref:`Feature Input<FeatureInput>`.
    -------------------------    ---------------------------------------------------------
    search_distance              Optional float. The maximum distance to move the location of an input point.
                                 Use search_units to set the units for search_distance.

                                 If your input points are located away from a drainage line, the resulting watersheds 
                                 are likely to be very small and not of much use in determining the upstream source of 
                                 contamination. In most cases, you want your input points to snap to the nearest drainage 
                                 line in order to find the watersheds that flows to a point located on the drainage line. 
                                 To find the closest drainage line, specify a search distance. If you do not specify a 
                                 search distance, the tool will compute and use a conservative search distance.

                                 To use the exact location of your input point, specify a search distance of zero.

                                 For analysis purposes, drainage lines have been precomputed by Esri using standard 
                                 hydrologic models. If there is no drainage line within the search distance, the location 
                                 containing the highest flow accumulation within the search distance is used.
    -------------------------    ---------------------------------------------------------
    search_units                 Optional string. The linear units specified for the search distance.

                                 Choice list: ['Meters', 'Kilometers', 'Feet', 'Miles', 'Yards']
    -------------------------    ---------------------------------------------------------
    source_database              Optional string. Keyword indicating the data source resolution that will be used in the analysis.
                                             
                                 Choice list: ['Finest', '30m', '90m']

                                 * Finest (Default): Finest resolution available at each location from all possible data sources.
                                 * 30m: The hydrologic source was built from 1 arc second - approximately 30 meter resolution, elevation data.
                                 * 90m: The hydrologic source was built from 3 arc second - approximately 90 meter resolution, elevation data.
    -------------------------    ---------------------------------------------------------
    generalize                   Optional boolean. Determines if the output watersheds will be smoothed into simpler shapes or conform 
                                 to the cell edges of the original DEM.

                                 * True: The polygons will be smoothed into simpler shapes. This is the default.
                                 * False: The edge of the polygons will conform to the edges of the original DEM.

                                 The default value is True.          
    -------------------------    ---------------------------------------------------------
    output_name                  Optional string. Output feature service name. If not provided, a feature collection is returned.
    -------------------------    ---------------------------------------------------------
    context                      Optional dict. Context contains additional settings that affect task execution. For ``create_watersheds``, there are two settings.
                                             
                                 #. Extent (``extent``)-a bounding box that defines the analysis area. Only those points in the ``input_layer`` 
                                    that intersect the bounding box will be analyzed.

                                 #. Output Spatial Reference (``outSR``)—the output features will be projected into the output spatial reference.
    -------------------------    ---------------------------------------------------------
    gis                          Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------    ---------------------------------------------------------
    estimate                     Optional boolean. If True, the estimated number of credits required to run the operation will be returned.
    =========================    =========================================================

    :returns result_layer : feature layer Item if output_name is specified, else Feature Collection.

    .. code-block:: python

        USAGE EXAMPLE: To create watersheds for Chennai lakes.    

        lakes_watershed = create_watersheds(lakes_lyr,
                                            search_distance=3,
                                            search_units='Kilometers',
                                            source_database='90m',
                                            output_name='create watersheds')
    
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.create_watersheds(
        input_layer,
        search_distance,
        search_units,
        source_database,
        generalize,
        output_name,
        context,
        estimate=estimate)


def trace_downstream(
        input_layer,
        split_distance=None,
        split_units="Kilometers",
        max_distance=None,
        max_distance_units="Kilometers",
        bounding_polygon_layer=None,
        source_database=None,
        generalize=True,
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    Determine the flow paths in a downstream direction from the locations you specify.

    Parameters
    ----------
    input_layer : Required layer (see Feature Input in documentation)

    split_distance : Optional float

    split_units : Optional string

    max_distance : Optional float

    max_distance_units : Optional string

    bounding_polygon_layer : Optional layer (see Feature Input in documentation)

    source_database : Optional string

    generalize : Optional bool

    output_name : Optional string

    context : Optional string

    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

    estimate :
        Optional Boolean. If True, the number of credits to run the operation will be returned.

    Returns
    -------
    trace_layer : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.trace_downstream(
        input_layer,
        split_distance,
        split_units,
        max_distance,
        max_distance_units,
        bounding_polygon_layer,
        source_database,
        generalize,
        output_name,
        context,
        estimate=estimate)

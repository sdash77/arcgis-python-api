"""
These functions help you answer one of the most common questions posed in spatial analysis: "What is near what?"

connect_origins_to_destinations measures the travel time or distance between pairs of points.
create_buffers create areas of equal distance from features.
create_drive_time_areas finds areas around locations that can be reached within a time period.
find_nearest identifies those places that are the closest to known locations.
plan_routes determines the best way to route a fleet of vehicles to visit many stops.
"""
import arcgis as _arcgis
from arcgis._impl.common._utils import _date_handler

def connect_origins_to_destinations(origins_layer,
                                    destinations_layer,
                                    measurement_type="DrivingTime",
                                    origins_layer_route_id_field=None,
                                    destinations_layer_route_id_field=None,
                                    time_of_day=None,
                                    time_zone_for_time_of_day="GeoLocal",
                                    output_name=None,
                                    context=None,
                                    gis=None,
                                    estimate=False,
                                    point_barrier_layer=None,
                                    line_barrier_layer=None,
                                    polygon_barrier_layer=None):
    """
    The Connect Origins to Destinations task measures the travel time or distance between pairs of points. Using this tool, you can

    * Calculate the total distance or time commuters travel on their home-to-work trips.
    * Measure how far customers are traveling to shop at your stores. Use this information to define your market reach, especially when targeting advertising campaigns or choosing new store locations.
    * Calculate the expected trip mileage for your fleet of vehicles. Afterward, run the Summarize Within tool to report mileage by state or other region.

    You provide starting and ending points, and the tool returns a layer containing route lines, including measurements, between the
    paired origins and destinations.

    ===================================    =========================================================
    **Argument**                           **Description**
    -----------------------------------    ---------------------------------------------------------
    origins_layer                          Required layer. The starting point or points of the routes to be generated. See :ref:`Feature Input<FeatureInput>`.
    -----------------------------------    ---------------------------------------------------------
    destinations_layer                     Required layer. The routes end at points in the destinations layer. See :ref:`Feature Input<FeatureInput>`.
    -----------------------------------    ---------------------------------------------------------
    measurement_type                       Required string. The origins and destinations can be connected by measuring straight-line distance,
                                           or by measuring travel time or travel distance along a street network using various modes of transportation
                                           known as travel modes.

                                           Valid values are a string, StraightLine, which indicates Euclidean distance to be used as distance measure or
                                           a Python dictionary representing settings for a travel mode.

                                           When using a travel mode for the measurement_type, you need to specify a dictionary
                                           containing the settings for a travel mode supported by your organization. The code in the example section below generates
                                           a valid Python dictionary and then passes it as the value for the measurement_type parameter.

                                           Supported travel modes: ['Driving Distance', 'Driving Time', 'Rural Driving Distance', 'Rural Driving Time',
                                           'Trucking Distance', 'Trucking Time', 'Walking Distance', 'Walking Time']

    -----------------------------------    ---------------------------------------------------------
    origins_layer_route_id_field           Optional string. Specify the field in the origins layer containing the IDs that pair origins with destinations.

                                           * The ID values must uniquely identify points in the origins layer.

                                           * Each ID value must also correspond with exactly one route ID value in the destinations layer. Route IDs that match
                                             across the layers create origin-destination pairs, which the tool connects together.

                                           *  Specifying origins_layer_route_id_field is optional when there is exactly one point feature in the origins or
                                              destinations layer. The tool will connect all origins to the one destination or the one origin to all destinations,
                                              depending on which layer contains one point.
    -----------------------------------    ---------------------------------------------------------
    destinations_layer_route_id_field      Optional string. Specify the field in the destinations layer containing the IDs that pair origins with destinations.

                                           * The ID values must uniquely identify points in the destinations layer.

                                           * Each ID value must also correspond with exactly one route ID value in the origins layer. Route IDs that match across the
                                             layers create origin-destination pairs, which the tool connects together.

                                           * Specifying destinations_layer_route_id_field is optional when there is exactly one point feature in the origins or
                                             destinations layer. The tool will connect all origins to the one destination or the one origin to all destinations,
                                             depending on which layer contains one point.
    -----------------------------------    ---------------------------------------------------------
    time_of_day                            Optional datetime.datetime. Specify whether travel times should consider traffic conditions. To use traffic in the analysis,
                                           set measurement_type to a travel mode object whose impedance_attribute_name property is set to travel_time and assign a value
                                           to time_of_day. (A travel mode with other impedance_attribute_name values don't support traffic.) The time_of_day value represents
                                           the time at which travel begins, or departs, from the origin points. The time is specified as datetime.datetime.

                                           The service supports two kinds of traffic: typical and live. Typical traffic references travel speeds that are made up of historical
                                           averages for each five-minute interval spanning a week. Live traffic retrieves speeds from a traffic feed that processes phone probe
                                           records, sensors, and other data sources to record actual travel speeds and predict speeds for the near future.

                                           The `data coverage <http://www.arcgis.com/home/webmap/viewer.html?webmap=b7a893e8e1e04311bd925ea25cb8d7c7>`_ page shows the countries
                                           Esri currently provides traffic data for.

                                           Typical Traffic:

                                           To ensure the task uses typical traffic in locations where it is available, choose a time and day of the week, and then convert the day
                                           of the week to one of the following dates from 1990:

                                           * Monday—1/1/1990
                                           * Tuesday—1/2/1990
                                           * Wednesday—1/3/1990
                                           * Thursday—1/4/1990
                                           * Friday—1/5/1990
                                           * Saturday—1/6/1990
                                           * Sunday—1/7/1990
                                           Set the time and date as datetime.datetime.

                                           For example, to solve for 1:03 p.m. on Thursdays, set the time and date to 1:03 p.m., 4 January 1990; and convert to
                                           datetime eg. datetime.datetime(1990, 1, 4, 1, 3).

                                           Live Traffic:

                                           To use live traffic when and where it is available, choose a time and date and convert to datetime.

                                           Esri saves live traffic data for 12 hours and references predictive data extending 12 hours into the future. If the time and date you
                                           specify for this parameter is outside the 24-hour time window, or the travel time in the analysis continues past the predictive data window, the task falls back to typical traffic speeds.

                                           Examples:
                                           from datetime import datetime

                                           * "time_of_day": datetime(1990, 1, 4, 1, 3) # 13:03, 4 January 1990. Typical traffic on Thursdays at 1:03 p.m.
                                           * "time_of_day": datetime(1990, 1, 7, 17, 0) # 17:00, 7 January 1990. Typical traffic on Sundays at 5:00 p.m.
                                           * "time_of_day": datetime(2014, 10, 22, 8, 0) # 8:00, 22 October 2014. If the current time is between 8:00 p.m., 21 Oct. 2014 and 8:00 p.m., 22 Oct. 2014,
                                             live traffic speeds are referenced in the analysis; otherwise, typical traffic speeds are referenced.
                                           * "time_of_day": datetime(2015, 3, 18, 10, 20) # 10:20, 18 March 2015. If the current time is between 10:20 p.m., 17 Mar. 2015 and 10:20 p.m., 18 Mar. 2015,
                                             live traffic speeds are referenced in the analysis; otherwise, typical traffic speeds are referenced.

    -----------------------------------    ---------------------------------------------------------
    time_zone_for_time_of_day              Optional string. Specify the time zone or zones of the timeOfDay parameter.
                                           Choice list: ['GeoLocal', 'UTC']

                                           GeoLocal-refers to the time zone in which the originsLayer points are located.

                                           UTC-refers to Coordinated Universal Time.
    -----------------------------------    ---------------------------------------------------------
    include_route_layers                   Optional Boolean. When include_route_layers is set to true, each route from the result is also saved as a route layer item. A route layer includes all the
                                           information for a particular route such as the stops assigned to the route as well as the travel directions. Creating route layers is useful if you want
                                           to share individual routes with other members in your organization. The route layers use the output feature service name provided in the outputName
                                           parameter as a prefix and the route name generated as part of the analysis is added to create a unique name for each route layer.

                                           Caution: Route layers cannot be created when the output is a feature collection. The task will raise an error if output_name is not specified
                                           (which indicates feature collection output) and include_route_layers is true.

                                           The maximum number of route layers that can be created is 1,000. If the result contains more than 1,000 routes and include_route_layers is true,
                                           the task will only create the output feature service.
    -----------------------------------    ---------------------------------------------------------
    output_name                            Optional string. If provided, the task will create a feature layer of the results. You define the name of the layer. If output_name is not supplied,
                                           the task will return a feature collection.
    -----------------------------------    ---------------------------------------------------------
    context                                Optional string. Additional settings such as processing extent and output spatial reference. For calculate_density, there are two settings.

                                           #. Extent (extent)-a bounding box that defines the analysis area. Only those points in the origins_layer and destinations_layer that intersect the
                                              bounding box will be analyzed.
                                           #. Output Spatial Reference (outSR)

                                           * If the output is a feature service, the spatial reference will be the same as originsLayer. Setting outSR for feature services has no effect.

                                           * If the output is a feature collection, the features will be in the spatial reference of the outSRvalue or the spatial reference of originsLayer
                                             when outSR is not specified.
    -----------------------------------    ---------------------------------------------------------
    gis                                    Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -----------------------------------    ---------------------------------------------------------
    estimate                               Optional Boolean. Is true, the number of credits needed to run the operation will be returned as a float.
    -----------------------------------    ---------------------------------------------------------
    point_barrier_layer                    Optional layer. Specify one or more point features that act as temporary restrictions (in other words, barriers) when traveling on the underlying streets.

                                           A point barrier can model a fallen tree, an accident, a downed electrical line, or anything that completely blocks traffic at a specific position along
                                           the street. Travel is permitted on the street but not through the barrier. See :ref:`Feature Input<FeatureInput>`.
    -----------------------------------    ---------------------------------------------------------
    line_barrier_layer                     Optional layer. Specify one or more line features that prohibit travel anywhere the lines intersect the streets.

                                           A line barrier prohibits travel anywhere the barrier intersects the streets. For example, a parade or protest that blocks traffic across several street
                                           segments can be modeled with a line barrier. See :ref:`Feature Input<FeatureInput>`.
    -----------------------------------    ---------------------------------------------------------
    polygon_barrier_layer                  Optional string. Specify one or more polygon features that completely restrict travel on the streets intersected by the polygons.

                                           One use of this type of barrier is to model floods covering areas of the street network and making road travel there impossible. See :ref:`Feature Input<FeatureInput>`.
    ===================================    =========================================================


    :returns: dict with the following keys:

        "routes_layer" : layer (FeatureCollection)

        "unassigned_origins_layer" : layer (FeatureCollection)

        "unassigned_destinations_layer" : layer (FeatureCollection)
    .. code-block:: python

        USAGE EXAMPLE: To retrieve trvel modes and run connect_origins_to_destinations tool.

        This example creates route between esri regional offices to esri headquarter.

        import arcgis.network as network
        route_service = network.RouteLayer(gis.properties.helperServices.route.url, gis=gis)
        travel_mode = [i for i in route_service.retrieve_travel_modes()['supportedTravelModes']
            if i['name'] == 'Rural Driving Distance'][0]
        routes =  connect_origins_to_destinations(origins_layer=esri_regional,
                                         destinations_layer=dest_layer,
                                         measurement_type=travel_mode,
                                         time_of_day=datetime(1990, 1, 4, 1, 3),
                                         output_name="routes_from_offices_to_hq")
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.connect_origins_to_destinations(
        origins_layer,
        destinations_layer,
        measurement_type,
        origins_layer_route_id_field,
        destinations_layer_route_id_field,
        _date_handler(time_of_day),
        time_zone_for_time_of_day,
        output_name,
        context,
        estimate=estimate)


def create_buffers(
        input_layer,
        distances=[],
        field=None,
        units="Meters",
        dissolve_type="None",
        ring_type="Disks",
        side_type="Full",
        end_type="Round",
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    .. image:: _static/images/create_buffers/create_buffers.png 
    
    .. |Disks| image:: _static/images/create_buffers/Disks.png
    .. |Dissolve| image:: _static/images/create_buffers/Dissolve.png
    .. |Flat| image:: _static/images/create_buffers/Flat.png
    .. |Full| image:: _static/images/create_buffers/Full.png
    .. |Left| image:: _static/images/create_buffers/Left.png
    .. |None| image:: _static/images/create_buffers/None.png
    .. |Outside| image:: _static/images/create_buffers/Outside.png
    .. |Right| image:: _static/images/create_buffers/Right.png
    .. |Rings| image:: _static/images/create_buffers/Rings.png
    .. |Round| image:: _static/images/create_buffers/Round.png
    .. |Unspecified| image:: _static/images/create_buffers/Unspecified.png

    The ``create_buffers`` task creates polygons that cover a given distance from a point,
    line, or polygon feature. Buffers are typically used to create areas that can be 
    further analyzed using a tool such as ``overlay_layers``. For example, if the question 
    is "What buildings are within one mile of the school?", the answer can be found by 
    creating a one-mile buffer around the school and overlaying the buffer with the layer 
    containing building footprints. The end result is a layer of those buildings within 
    one mile of the school.

    =========================    =========================================================
    **Parameter**                **Description**
    -------------------------    ---------------------------------------------------------
    input_layer                  Required point, line or polygon feature layer. The input features to be buffered. See :ref:`Feature Input<FeatureInput>`.
    -------------------------    ---------------------------------------------------------
    distances                    Optional list of floats to buffer the input features. The distance(s) that will be buffered. You must supply values 
                                 for either the ``distances`` or ``field`` parameter. You can enter a single distance value or multiple values. 
                                 The units of the distance values is suppied by the units parameter.
    -------------------------    ---------------------------------------------------------
    field                        Optional string. A field on the ``input_layer`` containing a buffer distance. Buffers will be created using field values. 
                                 Unlike the ``distances`` parameter, multiple distances are not supported on field input.
    -------------------------    ---------------------------------------------------------
    units                        Optional string. The linear unit to be used with the distance value(s) specified in distances or contained in the field value.
                                             
                                 Choice list: ['Meters', 'Kilometers', 'Feet', 'Miles', 'NauticalMiles', 'Yards']
                                             
                                 The default is 'Meters'.
    -------------------------    ---------------------------------------------------------
    dissolve_type                Optional string. Determines how overlapping buffers are processed.

                                 Choice list: ['None', 'Dissolve']   

                                 +------------+---------------------------------------------------------------------------------+
                                 | |None|     | ``None``—Overlapping areas are kept. This is the default.                       |
                                 +------------+---------------------------------------------------------------------------------+
                                 | |Dissolve| | ``Dissolve``—Overlapping areas are combined.                                    |
                                 +------------+---------------------------------------------------------------------------------+

    -------------------------    ---------------------------------------------------------
    ring_type                    Optional string. Determines how multiple-distance buffers are processed.
    
                                 Choice list: ['Disks', 'Rings']

                                 +-----------+--------------------------------------------------------------------------------------------------+
                                 | |Disks|   | ``Disks``—buffers are concentric and will overlap. For example, if your distances are 10 and 14, | 
                                 |           | the result will be two buffers, one from 0 to 10 and one from 0 to 14. This is the default.      |
                                 +-----------+--------------------------------------------------------------------------------------------------+
                                 | |Rings|   | ``Rings``—buffers will not overlap. For example, if your distances are 10 and 14, the result will|
                                 |           | be two buffers, one from 0 to 10 and one from 10 to 14.                                          |
                                 +-----------+--------------------------------------------------------------------------------------------------+
                                 
    -------------------------    ---------------------------------------------------------
    side_type                    Optional string. When buffering line features, you can choose which side of the line to buffer.

                                 Typically, you choose both sides (Full, which is the default). Left and right are determined as 
                                 if you were walking from the first x,y coordinate of the line (the start coordinate) to the last 
                                 x,y coordinate of the line (the end coordinate). Choosing left or right usually means you know 
                                 that your line features were created and stored in a particular direction (for example, upstream 
                                 or downstream in a river network).

                                 When buffering polygon features, you can choose whether the buffer includes or excludes the polygon 
                                 being buffered.

                                 Choice list: ['Full', 'Left', 'Right', 'Outside']

                                 +---------------+----------------------------------------------------------------------------------------------------+
                                 | |Full|        | ``Full``—both sides of the line will be buffered. This is the default for line featuress.          |
                                 |               |                                                                                                    |           
                                 +---------------+----------------------------------------------------------------------------------------------------+
                                 | |Left|        | ``Left``—only the right side of the line will be buffered.                                         |
                                 +---------------+----------------------------------------------------------------------------------------------------+
                                 | |Right|       | ``Right``—only the right side of the line will be buffered.                                        |
                                 +---------------+----------------------------------------------------------------------------------------------------+
                                 | |Outside|     | ``Outside``—when buffering a polygon, the polygon being buffered is excluded in the result buffer. |
                                 +---------------+----------------------------------------------------------------------------------------------------+
                                 | |Unspecified| | If ``side_type`` not supplied, the polygon being buffered is included in the result buffer.        | 
                                 |               | This is the  default for polygon features.                                                         |
                                 +---------------+----------------------------------------------------------------------------------------------------+                                                                  

    -------------------------    ---------------------------------------------------------
    end_type                     Optional string. The shape of the buffer at the end of line input features. This parameter is not 
                                 valid for polygon input features. At the ends of lines the buffer can be rounded (Round) or be 
                                 straight across (Flat).

                                 Choice list: ['Round', 'Flat']

                                 +---------+-------------------------------------------------------------------------------+
                                 | |Round| | ``Round``—buffers will be rounded at the ends of lines. This is the default.  |
                                 +---------+-------------------------------------------------------------------------------+
                                 | |Flat|  | ``Flat``—buffers will be flat at the ends of lines.                           |
                                 +---------+-------------------------------------------------------------------------------+
                                   
    -------------------------    ---------------------------------------------------------
    output_name                  Optional string. Output feature service name. If not provided, a feature collection is returned.
    -------------------------    ---------------------------------------------------------
    context                      Optional dict. Context contains additional settings that affect task execution. For ``create_buffers``, there are two settings.
                                             
                                 #. Extent (``extent``)-a bounding box that defines the analysis area. Only those points in the ``input_layer`` 
                                    that intersect the bounding box will be analyzed.

                                 #. Output Spatial Reference (``outSR``)—the output features will be projected into the output spatial reference.
    -------------------------    ---------------------------------------------------------
    gis                          Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------    ---------------------------------------------------------
    estimate                     Optional boolean. If True, the estimated number of credits required to run the operation will be returned.
    =========================    =========================================================

    :returns: result_layer : feature layer Item if output_name is specified, else Feature Collection.


    .. code-block:: python

        USAGE EXAMPLE: To create 5 mile buffer around US parks, within the specified extent.
        
        polygon_lyr_buffer = create_buffers(input_layer=parks_lyr,
                                 distances=[5],
                                 units='Miles',
                                 ring_type='Rings',
                                 end_type='Flat',
                                 output_name='create_buffers',
                                 context={"extent":{"xmin":-12555831.656684224,"ymin":5698027.566358956,"xmax":-11835489.102124758,"ymax":6104672.556836072,"spatialReference":{"wkid":102100,"latestWkid":3857}}})
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.create_buffers(input_layer,
                                                     distances,
                                                     field,
                                                     units,
                                                     dissolve_type,
                                                     ring_type,
                                                     side_type,
                                                     end_type,
                                                     output_name,
                                                     context,
                                                     estimate=estimate)


def create_drive_time_areas(input_layer,
                            break_values=[5, 10, 15],
                            break_units="Minutes",
                            travel_mode="Driving Time",
                            overlap_policy="Overlap",
                            time_of_day=None,
                            time_zone_for_time_of_day="GeoLocal",
                            output_name=None,
                            context=None,
                            gis=None,
                            estimate=False,
                            point_barrier_layer=None,
                            line_barrier_layer=None,
                            polygon_barrier_layer=None):
    """
    .. image:: _static/images/create_drive_time_areas/create_drive_time_areas.png 

    .. |Overlap| image:: _static/images/create_drive_time_areas/Overlap.png    
    .. |Dissolve| image:: _static/images/create_drive_time_areas/Dissolve.png    
    .. |Split| image:: _static/images/create_drive_time_areas/Split.png            

    The ``create_drive_time_areas`` method creates areas that can be reached within a 
    given drive time or drive distance. It can help you answer questions such as:

    * How far can I drive from here in five minutes?
    * What areas are covered within a three-mile drive distance of my stores?
    * What areas are within four minutes of our fire stations?

    =========================    =========================================================
    **Parameter**                **Description**
    -------------------------    ---------------------------------------------------------
    input_layer                  Required point feature layer. The points around which travel areas 
                                 based on a mode of transportation will be drawn. 
                                 See :ref:`Feature Input<FeatureInput>`.
    -------------------------    ---------------------------------------------------------
    travel_mode                  Optional string or dict. Specify the mode of transportation for the analysis.
                                 
                                 Choice list: ['Driving Distance', 'Driving Time', 'Rural Driving Distance', 'Rural Driving Time', 'Trucking Distance', 'Trucking Time', 'Walking Distance', 'Walking Time']
 
                                 The default is 'Driving Time'.
    -------------------------    ---------------------------------------------------------
    break_values                 Optional list of floats. The size of the polygons to create. 
                                 The units for break_values is specified with the break_units parameter.

                                 By setting many unique values in the list, polygons of different sizes are generated around each input location.

                                 The default is [5, 10, 15].
    -------------------------    ---------------------------------------------------------
    break_units                  Optional string. The units of the break_values parameter.

                                 To create areas showing how far you can go along roads or walkways within a given time, specify a time unit. 
                                 Alternatively, specify a distance unit to generate areas bounded by a maximum travel distance.  

                                 When the travel_mode is time based, a time unit should be specified for the break_units. When the 
                                 travel_mode is distance based, a distance unit should be specified for the break_units.          
                                
                                 Choice list: ['Seconds', 'Minutes', Hours', 'Feet', 'Meters', 'Kilometers', 'Feet', 'Miles', 'Yards']
                                             
                                 The default is 'Minutes'.
    -------------------------    ---------------------------------------------------------
    overlap_policy               Optional string. Determines how overlapping areas are processed.

                                 Choice list: ['Overlap', 'Dissolve', 'Split']   

                                 +---------------+-----------------------------------------------------------------------------------------------------+
                                 | |Overlap|     | ``Overlap``-Overlapping areas are kept. This is the default.                                        |
                                 +---------------+-----------------------------------------------------------------------------------------------------+
                                 | |Dissolve|    | ``Dissolve``-Overlapping areas are combined by break value. Because the areas are dissolved,        |
                                 |               | use this option when you need to know the areas that can be reached within a                        |
                                 |               | given time or distance, but you don't need to know which input points are nearest.                  |      
                                 +---------------+-----------------------------------------------------------------------------------------------------+
                                 | |Split|       | ``Split``-Overlapping areas are split in the middle. Use this option when you need to know          |
                                 |               | the one nearest input location to the covered area.                                                 |
                                 +---------------+-----------------------------------------------------------------------------------------------------+

                                 The default is 'Overlap'

    -------------------------    ---------------------------------------------------------
    time_of_day                  Optional datetime.datetime. Specify whether travel times should consider traffic conditions. To use traffic in the analysis, 
                                 set measurement_type to a travel mode object whose impedance_attribute_name property is set to travel_time and assign a value 
                                 to time_of_day. (A travel mode with other impedance_attribute_name values don't support traffic.) The time_of_day value represents 
                                 the time at which travel begins, or departs, from the origin points. The time is specified as datetime.datetime.

                                 The service supports two kinds of traffic: typical and live. Typical traffic references travel speeds that are made up of historical 
                                 averages for each five-minute interval spanning a week. Live traffic retrieves speeds from a traffic feed that processes phone probe 
                                 records, sensors, and other data sources to record actual travel speeds and predict speeds for the near future.
                                
                                 The `data coverage <http://www.arcgis.com/home/webmap/viewer.html?webmap=b7a893e8e1e04311bd925ea25cb8d7c7>`_ page shows the countries 
                                 Esri currently provides traffic data for.
                                
                                 Typical Traffic:

                                 To ensure the task uses typical traffic in locations where it is available, choose a time and day of the week, and then convert the day 
                                 of the week to one of the following dates from 1990:

                                 * Monday—1/1/1990
                                 * Tuesday—1/2/1990
                                 * Wednesday—1/3/1990
                                 * Thursday—1/4/1990
                                 * Friday—1/5/1990
                                 * Saturday—1/6/1990
                                 * Sunday—1/7/1990
                                 Set the time and date as datetime.datetime.

                                 For example, to solve for 1:03 p.m. on Thursdays, set the time and date to 1:03 p.m., 4 January 1990; and convert to 
                                 datetime eg. datetime.datetime(1990, 1, 4, 1, 3).
                                
                                 Live Traffic:

                                 To use live traffic when and where it is available, choose a time and date and convert to datetime.

                                 Esri saves live traffic data for 12 hours and references predictive data extending 12 hours into the future. If the time and date you 
                                 specify for this parameter is outside the 24-hour time window, or the travel time in the analysis continues past the predictive data window, the task falls back to typical traffic speeds.
                                 
                                 Examples:
                                 from datetime import datetime

                                 * "time_of_day": datetime(1990, 1, 4, 1, 3) # 13:03, 4 January 1990. Typical traffic on Thursdays at 1:03 p.m.
                                 * "time_of_day": datetime(1990, 1, 7, 17, 0) # 17:00, 7 January 1990. Typical traffic on Sundays at 5:00 p.m.
                                 * "time_of_day": datetime(2014, 10, 22, 8, 0) # 8:00, 22 October 2014. If the current time is between 8:00 p.m., 21 Oct. 2014 and 8:00 p.m., 22 Oct. 2014, 
                                   live traffic speeds are referenced in the analysis; otherwise, typical traffic speeds are referenced.
                                 * "time_of_day": datetime(2015, 3, 18, 10, 20) # 10:20, 18 March 2015. If the current time is between 10:20 p.m., 17 Mar. 2015 and 10:20 p.m., 18 Mar. 2015, 
                                   live traffic speeds are referenced in the analysis; otherwise, typical traffic speeds are referenced.                      
    -------------------------    ---------------------------------------------------------
    time_zone_for_time_of_day    Optional string. Specify the time zone or zones of the time_of_day parameter. 
                                
                                 Choice list: ['GeoLocal', 'UTC']
                                           
                                 GeoLocal-refers to the time zone in which the originsLayer points are located.
                                           
                                 UTC-refers to Coordinated Universal Time.    
                                 
                                 The default is 'GeoLocal'.                                                                                        
    -------------------------    ---------------------------------------------------------
    output_name                  Optional string. Output feature service name. If not provided, a feature collection is returned.
    -------------------------    ---------------------------------------------------------
    context                      Optional dict. Context contains additional settings that affect task execution. For ``create_drive_time_areas``, there are two settings.
                                             
                                 #. Extent (``extent``)-a bounding box that defines the analysis area. Only those points in the ``input_layer`` 
                                    that intersect the bounding box will be analyzed.

                                 #. Output Spatial Reference (``outSR``)—the output features will be projected into the output spatial reference.
    -------------------------    ---------------------------------------------------------
    gis                          Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    -------------------------    ---------------------------------------------------------
    estimate                     Optional boolean. If True, the estimated number of credits required to run the operation will be returned.
    -------------------------    ---------------------------------------------------------
    point_barrier_layer          Optional layer. Specify one or more point features that act as temporary restrictions (in other words, barriers) 
                                 when traveling on the underlying streets.

                                 A point barrier can model a fallen tree, an accident, a downed electrical line, or anything that completely blocks 
                                 traffic at a specific position along the street. Travel is permitted on the street but not through the barrier. See :ref:`Feature Input<FeatureInput>`.
    -------------------------    ---------------------------------------------------------
    line_barrier_layer           Optional layer. Specify one or more line features that prohibit travel anywhere the lines intersect the streets.

                                 A line barrier prohibits travel anywhere the barrier intersects the streets. For example, a parade or protest that blocks traffic across several street 
                                 segments can be modeled with a line barrier. See :ref:`Feature Input<FeatureInput>`.
    -------------------------    ---------------------------------------------------------
    polygon_barrier_layer        Optional string. Specify one or more polygon features that completely restrict travel on the streets intersected by the polygons.

                                 One use of this type of barrier is to model floods covering areas of the street network and making road travel there impossible. See :ref:`Feature Input<FeatureInput>`.     
    =========================    =========================================================

    :returns: result_layer : feature layer Item if output_name is specified, else Feature Collection.


    .. code-block:: python

        USAGE EXAMPLE: To create drive time areas around USA airports, within the specified extent.
        
        target_area4 = create_drive_time_areas(airport_lyr,
                                       break_values=[2, 4],
                                       break_units='Hours',
                                       travel_mode='Trucking Time',
                                       overlap_policy='Split',  
                                       time_of_day=datetime(2019, 5, 13, 7, 52),
                                       output_name='create_drive_time_areas',
                                       context={"extent":{"xmin":-11134400.655784884,"ymin":3368261.7800108367,"xmax":-10682810.692676282,"ymax":3630899.409198575,"spatialReference":{"wkid":102100,"latestWkid":3857}}}) """

    gis = _arcgis.env.active_gis if gis is None else gis
    if isinstance(travel_mode, str):
        route_service = network.RouteLayer(gis.properties.helperServices.route.url, gis=gis)
        travel_mode = [i for i in route_service.retrieve_travel_modes()['supportedTravelModes'] if i['name'] == travel_mode][0] 
    return gis._tools.featureanalysis.create_drive_time_areas(
        input_layer,
        break_values,
        break_units,
        travel_mode,
        overlap_policy,
        _date_handler(time_of_day),
        time_zone_for_time_of_day,
        output_name,
        context,
        estimate=estimate,
        point_barrier_layer=point_barrier_layer,
        line_barrier_layer=line_barrier_layer,
        polygon_barrier_layer=polygon_barrier_layer)


def find_nearest(
        analysis_layer,
        near_layer,
        measurement_type="StraightLine",
        max_count=100,
        search_cutoff=2147483647,
        search_cutoff_units=None,
        time_of_day=None,
        time_zone_for_time_of_day="GeoLocal",
        output_name=None,
        context=None,
        gis=None,
        estimate=False):
    """
    Measures the straight-line distance, driving distance, or driving time from features in the analysis layer to
    features in the near layer, and copies the nearest features in the near layer to a new layer. Returns a layer
    containing the nearest features and a line layer that links the start locations to their nearest locations.

    Parameters
    ----------
    analysis_layer : Required layer (see Feature Input in documentation)
        For each feature in this layer, the task finds the nearest features from the nearLayer.
    near_layer : Required layer (see Feature Input in documentation)
        The features from which the nearest locations are found.
    measurement_type : Required string
        The nearest locations can be determined by measuring straight-line distance, driving distance, or driving time
    max_count : Optional int
        The maximum number of near locations to find for each feature in analysisLayer.
    search_cutoff : Optional float
        Limits the search range to this value
    search_cutoff_units : Optional string
        The units for the value specified as searchCutoff
    time_of_day : Optional datetime.datetime
        When measurementType is DrivingTime, this value specifies the time of day to be used for driving time
        calculations based on traffic.
    time_zone_for_time_of_day : Optional string

    output_name : Optional string
        Additional properties such as output feature service name
    context : Optional string
        Additional settings such as processing extent and output spatial reference
    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.
    estimate :
        Optional Boolean. If True, the number of credits to run the operation will be returned.

    Returns
    -------
    dict with the following keys:
       "nearest_layer" : layer (FeatureCollection)
       "connecting_lines_layer" : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.find_nearest(
        analysis_layer,
        near_layer,
        measurement_type,
        max_count,
        search_cutoff,
        search_cutoff_units,
        _date_handler(time_of_day),
        time_zone_for_time_of_day,
        output_name,
        context,
        estimate=estimate)


def plan_routes(
        stops_layer,
        route_count,
        max_stops_per_route,
        route_start_time,
        start_layer,
        start_layer_route_id_field=None,
        return_to_start=True,
        end_layer=None,
        end_layer_route_id_field=None,
        travel_mode="Driving",
        stop_service_time=0,
        max_route_time=525600,
        include_route_layers=False,
        output_name=None,
        context=None,
        gis=None,
        estimate=False,
        point_barrier_layer=None,
        line_barrier_layer=None,
        polygon_barrier_layer=None):
    """
    You provide a set of stops and the number of vehicles available to visit the stops, and Plan Routes determines how
    to efficiently assign the stops to the vehicles and route the vehicles to the stops.

    Use this tool to plan work for a mobile team of inspectors, appraisers, in-home support service providers, and
    others; deliver or pick up items from remote locations; or offer transportation services to people.

    Parameters
    ----------

    stops_layer : Required layer (see Feature Input in documentation)

    route_count : Required int

    max_stops_per_route : Required int

    route_start_time : Required datetime.datetime

    start_layer : Required layer (see Feature Input in documentation)

    start_layer_route_id_field : Optional string

    return_to_start : Optional bool

    end_layer : Optional layer (see Feature Input in documentation)

    end_layer_route_id_field : Optional string

    travel_mode : Optional string

    stop_service_time : Optional float

    max_route_time : Optional float

    include_route_layers : Optional bool

    output_name : Optional string

    context : Optional string

    gis :
        Optional, the GIS on which this tool runs. If not specified, the active GIS is used.

    estimate :
        Optional Boolean. If True, the number of credits to run the operation will be returned.

    point_barrier_layer: Optional FeatureSet/FeatureLayer

    line_barrier_layer: Optional FeatureSet/FeatureLayer

    polygon_barrier_layer: Optional FeatureSet/FeatureLayer

    Returns
    -------
    dict with the following keys:
       "routes_layer" : layer (FeatureCollection)
       "assigned_stops_layer" : layer (FeatureCollection)
       "unassigned_stops_layer" : layer (FeatureCollection)
    """
    gis = _arcgis.env.active_gis if gis is None else gis
    return gis._tools.featureanalysis.plan_routes(
        stops_layer,
        route_count,
        max_stops_per_route,
        _date_handler(route_start_time),
        start_layer,
        start_layer_route_id_field,
        return_to_start,
        end_layer,
        end_layer_route_id_field,
        travel_mode,
        stop_service_time,
        max_route_time,
        include_route_layers,
        output_name,
        context,
        estimate=estimate,
        point_barrier_layer=point_barrier_layer,
        line_barrier_layer=line_barrier_layer,
        polygon_barrier_layer=polygon_barrier_layer)

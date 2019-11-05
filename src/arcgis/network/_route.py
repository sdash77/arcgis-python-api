import logging as _logging
import arcgis
from datetime import datetime
from arcgis. geoprocessing import import_toolbox
from arcgis.features import FeatureSet
from arcgis.mapping import MapImageLayer
from arcgis.geoprocessing import DataFile, LinearUnit, RasterData
from arcgis.geoprocessing._support import _execute_gp_tool

_log = _logging.getLogger(__name__)

_use_async = True

default_stops = {'fields': [{'alias': 'OBJECTID', 'name': 'OBJECTID', 'type': 'esriFieldTypeOID'},
                                                {'alias': 'Name', 'name': 'Name', 'type': 'esriFieldTypeString',
                                                 'length': 128}, {'alias': 'Route Name', 'name': 'RouteName',
                                                                  'type': 'esriFieldTypeString', 'length': 128},
                                                {'alias': 'Sequence', 'name': 'Sequence',
                                                 'type': 'esriFieldTypeInteger'},
                                                {'alias': 'Additional Time', 'name': 'AdditionalTime',
                                                 'type': 'esriFieldTypeDouble'},
                                                {'alias': 'Additional Distance', 'name': 'AdditionalDistance',
                                                 'type': 'esriFieldTypeDouble'},
                                                {'alias': 'Time Window Start', 'name': 'TimeWindowStart',
                                                 'type': 'esriFieldTypeDate', 'length': 8},
                                                {'alias': 'Time Window End', 'name': 'TimeWindowEnd',
                                                 'type': 'esriFieldTypeDate', 'length': 8},
                                                {'alias': 'Curb Approach', 'name': 'CurbApproach',
                                                 'type': 'esriFieldTypeSmallInteger'}],
                                     'geometryType': 'esriGeometryPoint', 'displayFieldName': '',
                                     'exceededTransferLimit': False,
                                     'spatialReference': {'latestWkid': 4326, 'wkid': 4326}, 'features': []}

default_point_barriers = {
                    'fields': [{'alias': 'OBJECTID', 'name': 'OBJECTID', 'type': 'esriFieldTypeOID'},
                               {'alias': 'Name', 'name': 'Name', 'type': 'esriFieldTypeString', 'length': 128},
                               {'alias': 'Barrier Type', 'name': 'BarrierType', 'type': 'esriFieldTypeInteger'},
                               {'alias': 'Additional Time', 'name': 'Additional_Time', 'type': 'esriFieldTypeDouble'},
                               {'alias': 'Additional Distance', 'name': 'Additional_Distance',
                                'type': 'esriFieldTypeDouble'},
                               {'alias': 'CurbApproach', 'name': 'CurbApproach', 'type': 'esriFieldTypeSmallInteger'}],
                    'geometryType': 'esriGeometryPoint', 'displayFieldName': '', 'exceededTransferLimit': False,
                    'spatialReference': {'latestWkid': 4326, 'wkid': 4326}, 'features': []}

default_line_barriers = {
                    'fields': [{'alias': 'OBJECTID', 'name': 'OBJECTID', 'type': 'esriFieldTypeOID'},
                               {'alias': 'Name', 'name': 'Name', 'type': 'esriFieldTypeString', 'length': 128},
                               {'alias': 'SHAPE_Length', 'name': 'SHAPE_Length', 'type': 'esriFieldTypeDouble'}],
                    'geometryType': 'esriGeometryPolyline', 'displayFieldName': '', 'exceededTransferLimit': False,
                    'spatialReference': {'latestWkid': 4326, 'wkid': 4326}, 'features': []}

default_polygon_barriers = {
                    'fields': [{'alias': 'OBJECTID', 'name': 'OBJECTID', 'type': 'esriFieldTypeOID'},
                               {'alias': 'Name', 'name': 'Name', 'type': 'esriFieldTypeString', 'length': 128},
                               {'alias': 'Barrier Type', 'name': 'BarrierType', 'type': 'esriFieldTypeInteger'},
                               {'alias': 'Scaled Time Factor', 'name': 'ScaledTimeFactor',
                                'type': 'esriFieldTypeDouble'},
                               {'alias': 'Scaled Distance Factor', 'name': 'ScaledDistanceFactor',
                                'type': 'esriFieldTypeDouble'},
                               {'alias': 'SHAPE_Length', 'name': 'SHAPE_Length', 'type': 'esriFieldTypeDouble'},
                               {'alias': 'SHAPE_Area', 'name': 'SHAPE_Area', 'type': 'esriFieldTypeDouble'}],
                    'geometryType': 'esriGeometryPolygon', 'displayFieldName': '', 'exceededTransferLimit': False,
                    'spatialReference': {'latestWkid': 4326, 'wkid': 4326}, 'features': []}

default_restrictions = """['Avoid Unpaved Roads', 'Avoid Private Roads', 'Driving an Automobile', 'Through Traffic Prohibited', 'Roads Under Construction Prohibited', 'Avoid Gates', 'Avoid Express Lanes', 'Avoid Carpool Roads']"""

default_attributes = {
                    'fields': [{'alias': 'ObjectID', 'name': 'OBJECTID', 'type': 'esriFieldTypeOID'},
                               {'alias': 'AttributeName', 'name': 'AttributeName', 'type': 'esriFieldTypeString',
                                'length': 255},
                               {'alias': 'ParameterName', 'name': 'ParameterName', 'type': 'esriFieldTypeString',
                                'length': 255},
                               {'alias': 'ParameterValue', 'name': 'ParameterValue', 'type': 'esriFieldTypeString',
                                'length': 25}], 'features': [{'attributes': {'OBJECTID': 1,
                                                                             'AttributeName': 'Any Hazmat Prohibited',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 2,
                                                                                'AttributeName': 'Avoid Carpool Roads',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 3,
                                                                             'AttributeName': 'Avoid Express Lanes',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 4,
                                                                                'AttributeName': 'Avoid Ferries',
                                                                                'ParameterValue': 'AVOID_MEDIUM',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 5,
                                                                             'AttributeName': 'Avoid Gates',
                                                                             'ParameterValue': 'AVOID_MEDIUM',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 6,
                                                                                'AttributeName': 'Avoid Limited Access Roads',
                                                                                'ParameterValue': 'AVOID_MEDIUM',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 7,
                                                                             'AttributeName': 'Avoid Private Roads',
                                                                             'ParameterValue': 'AVOID_MEDIUM',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 8,
                                                                                'AttributeName': 'Avoid Roads Unsuitable for Pedestrians',
                                                                                'ParameterValue': 'AVOID_HIGH',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 9,
                                                                             'AttributeName': 'Avoid Stairways',
                                                                             'ParameterValue': 'AVOID_HIGH',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 10,
                                                                                'AttributeName': 'Avoid Toll Roads',
                                                                                'ParameterValue': 'AVOID_MEDIUM',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 11,
                                                                             'AttributeName': 'Avoid Toll Roads for Trucks',
                                                                             'ParameterValue': 'AVOID_MEDIUM',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 12,
                                                                                'AttributeName': 'Avoid Truck Restricted Roads',
                                                                                'ParameterValue': 'AVOID_HIGH',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 13,
                                                                             'AttributeName': 'Avoid Unpaved Roads',
                                                                             'ParameterValue': 'AVOID_HIGH',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 14,
                                                                                'AttributeName': 'Axle Count Restriction',
                                                                                'ParameterValue': '0',
                                                                                'ParameterName': 'Number of Axles'}}, {
                                                                 'attributes': {'OBJECTID': 15,
                                                                                'AttributeName': 'Axle Count Restriction',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 16,
                                                                             'AttributeName': 'Driving a Bus',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 17,
                                                                                'AttributeName': 'Driving a Delivery Vehicle',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 18,
                                                                             'AttributeName': 'Driving a Taxi',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 19,
                                                                                'AttributeName': 'Driving a Truck',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 20,
                                                                             'AttributeName': 'Driving an Automobile',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 21,
                                                                                'AttributeName': 'Driving an Emergency Vehicle',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 22,
                                                                             'AttributeName': 'Height Restriction',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 23,
                                                                                'AttributeName': 'Height Restriction',
                                                                                'ParameterValue': '0',
                                                                                'ParameterName': 'Vehicle Height (meters)'}},
                                                             {'attributes': {'OBJECTID': 24,
                                                                             'AttributeName': 'Kingpin to Rear Axle Length Restriction',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 25,
                                                                                'AttributeName': 'Kingpin to Rear Axle Length Restriction',
                                                                                'ParameterValue': '0',
                                                                                'ParameterName': 'Vehicle Kingpin to Rear Axle Length (meters)'}},
                                                             {'attributes': {'OBJECTID': 26,
                                                                             'AttributeName': 'Length Restriction',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 27,
                                                                                'AttributeName': 'Length Restriction',
                                                                                'ParameterValue': '0',
                                                                                'ParameterName': 'Vehicle Length (meters)'}},
                                                             {'attributes': {'OBJECTID': 28,
                                                                             'AttributeName': 'Preferred for Pedestrians',
                                                                             'ParameterValue': 'PREFER_LOW',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 29,
                                                                                'AttributeName': 'Riding a Motorcycle',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 30,
                                                                             'AttributeName': 'Roads Under Construction Prohibited',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 31,
                                                                                'AttributeName': 'Semi or Tractor with One or More Trailers Prohibited',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 32,
                                                                             'AttributeName': 'Single Axle Vehicles Prohibited',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 33,
                                                                                'AttributeName': 'Tandem Axle Vehicles Prohibited',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 34,
                                                                             'AttributeName': 'Through Traffic Prohibited',
                                                                             'ParameterValue': 'AVOID_HIGH',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 35,
                                                                                'AttributeName': 'Truck with Trailers Restriction',
                                                                                'ParameterValue': '0',
                                                                                'ParameterName': 'Number of Trailers on Truck'}},
                                                             {'attributes': {'OBJECTID': 36,
                                                                             'AttributeName': 'Truck with Trailers Restriction',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 37,
                                                                                'AttributeName': 'Use Preferred Hazmat Routes',
                                                                                'ParameterValue': 'PREFER_MEDIUM',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 38,
                                                                             'AttributeName': 'Use Preferred Truck Routes',
                                                                             'ParameterValue': 'PREFER_MEDIUM',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 39,
                                                                                'AttributeName': 'WalkTime',
                                                                                'ParameterValue': '5',
                                                                                'ParameterName': 'Walking Speed (km/h)'}},
                                                             {'attributes': {'OBJECTID': 40, 'AttributeName': 'Walking',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 41,
                                                                                'AttributeName': 'Weight Restriction',
                                                                                'ParameterValue': 'PROHIBITED',
                                                                                'ParameterName': 'Restriction Usage'}},
                                                             {'attributes': {'OBJECTID': 42,
                                                                             'AttributeName': 'Weight Restriction',
                                                                             'ParameterValue': '0',
                                                                             'ParameterName': 'Vehicle Weight (kilograms)'}},
                                                             {'attributes': {'OBJECTID': 43,
                                                                             'AttributeName': 'Weight per Axle Restriction',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 44,
                                                                                'AttributeName': 'Weight per Axle Restriction',
                                                                                'ParameterValue': '0',
                                                                                'ParameterName': 'Vehicle Weight per Axle (kilograms)'}},
                                                             {'attributes': {'OBJECTID': 45,
                                                                             'AttributeName': 'Width Restriction',
                                                                             'ParameterValue': 'PROHIBITED',
                                                                             'ParameterName': 'Restriction Usage'}}, {
                                                                 'attributes': {'OBJECTID': 46,
                                                                                'AttributeName': 'Width Restriction',
                                                                                'ParameterValue': '0',
                                                                                'ParameterName': 'Vehicle Width (meters)'}}],
                    'displayFieldName': '', 'exceededTransferLimit': False}

default_tolerance = {'distance': 10, 'units': 'esriMeters'}





def find_routes(stops,
                measurement_units='Minutes',
                analysis_region=None,
                reorder_stops_to_find_optimal_routes=False,
                preserve_terminal_stops='Preserve First',
                return_to_start=False,
                use_time_windows=False,
                time_of_day=None,
                time_zone_for_time_of_day='Geographically Local',
                uturn_at_junctions='Allowed Only at Intersections and Dead Ends',
                point_barriers=None,
                line_barriers=None,
                polygon_barriers=None,
                use_hierarchy=True,
                restrictions=None,
                attribute_parameter_values=None,
                route_shape='True Shape',
                route_line_simplification_tolerance=None,
                populate_route_edges=False,
                populate_directions=True,
                directions_language='en',
                directions_distance_units='Miles',
                directions_style_name='NA Desktop',
                travel_mode='Custom',
                impedance='Drive Time',
                overrides=None,
                time_impedance='TravelTime',
                save_route_data=False,
                distance_impedance='Kilometers',
                output_format='Feature Set',
                save_output_na_layer=False,
                time_zone_for_time_windows='Geographically Local',
                gis=None,
                future=False):
    """
    Find Routes determines the shortest paths to visit the input stops and
    returns the driving directions, information about the visited stops,
    and the route paths, including travel time and distance., The tool is
    capable of finding routes that visit several input stops in a sequence
    you predetermine or in the  sequence that minimizes overall travel. You
    can group the input stops into different routes using the RouteName
    field, and the tool will output one route for each group of stops,
    allowing you to generate routes for many vehicles in a single solve
    operation.

    Parameters:

    stops: Stops (FeatureSet). Required parameter.  Specify the locations you want the output route
           or routes to visit. You can add up to 10,000 stops and assign up to 150 stops to a single
           route. (Assign stops to routes using the RouteName attribute.)When specifying the stops,
           you can set properties for each one, such as its name or service time, by using
           attributes. The stops can be specified with the following attributes:NameThe name of the
           stop. The name is used in the driving directions. If the name is not specified, a unique
           name prefixed with Location is automatically generated in the output stops, routes, and
           directions.RouteNameThe name of the route to which the stop is assigned. Assigning the
           same route name to different stops causes those stops to be grouped together and visited
           by the same route. You can generate many routes in a single solve by assigning unique
           route names to different groups of stops. You can group up to 150 stops into one route.
           SequenceThe output routes will visit the stops in the order you specify with this
           attribute. Within a group of stops that have the same RouteName value, the sequence
           number should be greater than 0 but not greater than the total number of stops. Also, the
           sequence number should not be duplicated. If Reorder Stops To Find Optimal Routes is
           checked (True), all but possibly the first and last sequence values for each route name
           are ignored so the tool can find the sequence that minimizes overall travel for each
           route. (The settings for Preserve Ordering of Stops and Return to Start determine whether
           the first or last sequence values for each route are ignored.)AdditionalTime The amount
           of time spent at the stop, which is added to the total time of the route. The default value
           is 0. The units for this attribute value are specified by the Measurement Units parameter.
           The attribute value is included in the analysis only when the measurement units are time
           based.  You can account for the extra time it takes at the stop to complete a task, such
           as to repair an appliance, deliver a package, or inspect the premises.
           AdditionalDistance, The extra distance traveled at the stops, which is added to the total
           distance of the route. The default value is 0.The units for this attribute value are
           specified by the Measurement Units parameter. The attribute value is included in the
           analysis only when the measurement units are distance based. Generally, the location of a
           stop, such as a home, isn't exactly on the street; it is set back somewhat from the road.
           This attribute value can be used to model the distance between the actual stop location
           and its location on the street if it is important to include that distance in the total
           travel distance.AdditionalCostThe extra cost spent at the stop, which is added to the
           total cost of the route. The default value is 0. This attribute value should be used when
           the travel mode for the analysis uses an impedance attribute that is neither time-based
           or distance-based The units for the attribute values are interpreted to be in unknown
           units. TimeWindowStartThe earliest time the stop can be visited. By specifying a start
           and end time for a stop's time window, you are defining when a route should visit the
           stop. When the travel mode for the analysis uses an impedance attribute that is
           time-based, by specifying time-window values the analysis will find a solution that
           minimizes overall travel and reaches the stop within the prescribed time window.  Make
           sure you specify the value as a date and time value, such as 8/12/2015 12:15 PM.  When
           solving a problem that spans multiple time zones, time-window values refer to the time
           zone in which the stop is located.This field can contain a null value; a null value
           indicates a route can arrive at any time before the time indicated in the TimeWindowEnd
           attribute. If a null value is also present in TimeWindowEnd, a route can visit the stop
           at any time.TimeWindowEndThe latest time the stop can be visited. By specifying a start
           and end time for a stop's time window, you are defining when a route should visit the
           stop. When the travel mode for the analysis uses an impedance attribute that is
           time-based, specifying time-window values will cause the analysis to find a solution
           that minimizes overall travel and reaches the stop within the prescribed time window.
           Make sure you specify the value as a date and time value, such as 8/12/2015 12:15 PM.
           When solving a problem that spans multiple time zones, time-window values refer to the
           time zone in which the stop is located.This field can contain a null value; a null value
           indicates a route can arrive at any time after the time indicated in the TimeWindowStart
           attribute. If a null value is also present in TimeWindowStart, a route can visit the
           stop at any time.CurbApproachSpecifies the direction a vehicle may arrive at and depart
           from the stop. The field value is specified as one of the
           following integers (use the numeric code, not the name in parentheses):  0 (Either side of vehicle) - The vehicle can approach and depart the stop in either direction, so a U-turn is allowed at the stop. This setting can be chosen if it is possible and practical for a vehicle to turn around at the stop. This decision may depend on the width of the road and the amount of traffic or whether the stop has a parking lot where vehicles can enter and turn around. 1 (Right side of vehicle)-When the vehicle approaches and departs the stop, the curb must be on the right side of the vehicle. A U-turn is prohibited. This is typically used for vehicles such as buses that must arrive with the bus stop on the right-hand side. 2 (Left side of vehicle)-When the vehicle approaches and departs
           the stop, the curb must be on the left side of the vehicle. A
           U-turn is prohibited. This is typically used for vehicles such as buses that must arrive with the bus stop on the left-hand side.  3 (No U-Turn)-When
           the vehicle approaches the stop, the curb can be on either side
           of the vehicle; however, the vehicle must depart without turning
           around. The CurbApproach property is designed to work with both kinds of national driving standards: right-hand traffic (United States) and left-hand traffic (United Kingdom). First, consider a stop on the left side of a vehicle. It is always on the left side regardless of whether the vehicle travels on the left or right half of the road. What may change with national driving standards is your decision to approach a stop from one of two directions, that is, so it ends up on the right or left side of the vehicle. For example, if you want to arrive at a stop and not have a lane of traffic between the vehicle and the stop, you would choose Right side of vehicle (1) in the United States but Left side of vehicle (2) in the United Kingdom.LocationType Specifies the stop type. The field value is specified as one of the following integers (use the numeric code, not the name in the parentheses): 0 (Stop)-A location that the route should visit. This is the default.1 (Waypoint)- A location that the route should travel through without making a stop. Waypoints can be used to force the route to take a specific path (to go through the waypoint) without being considered an actual stop. Waypoints do not appear in directions.BearingThe direction in which a point is moving. The units are degrees and are measured clockwise from true north. This field is used in conjunction with the BearingTol field. Bearing data is usually sent automatically from a mobile device equipped with a GPS receiver. Try to include bearing data if you are loading an input location that is moving, such as a pedestrian or a vehicle. Using this field tends to prevent adding locations to the wrong edges, which can occur when a vehicle is near an intersection or an overpass for example. Bearing also helps the tool determine on which side of the street the point is. For more information, see Bearing and BearingTol in the ArcGIS help system. BearingTolThe bearing tolerance value creates a range of acceptable bearing values when locating moving points on an edge using the Bearing field. If the value from the Bearing field is within the range of acceptable values that are generated from the bearing tolerance on an edge, the point can be added as a network location there; otherwise, the closest point on the next-nearest edge is evaluated. The units are in degrees and the default value is 30. Values must be greater than zero and less than 180. A value of 30 means that when ArcGIS Network Analyst extension  attempts to add a network location on an edge, a range of acceptable bearing values is generated 15 degrees to either side of the edge (left and right) and in both digitized directions of the edge. For more information, see Bearing and BearingTol in the ArcGIS help system. NavLatencyThis field is only used in the solve process if Bearing and BearingTol also have values; however, entering a NavLatency value is optional, even when values are present in Bearing and BearingTol. NavLatency indicates how much time is expected to elapse from the moment GPS information is sent from a moving vehicle to a server and the moment the processed route is received by the vehicle's navigation device. The time units of NavLatency are the same as the units specified by the timeUnits property of the analysis object.

           measurement_units: Measurement Units (str). Required parameter.  Specify the units that should be used to measure and report the total travel time or travel distance for the output routes. The units you choose for this parameter determine whether the tool will measure distance or time to find the best routes. Choose a time unit to minimize travel time for your chosen travel mode (driving or walking time, for instance). To minimize travel distance for the given travel mode, choose a distance unit. Your choice also determines in which units the tool will report total time or distance in the results. The choices include the following:MetersKilometersFeetYardsMilesNauticalMilesSecondsMinutesHoursDays
                              Choice list:['Meters', 'Kilometers', 'Feet', 'Yards', 'Miles', 'NauticalMiles', 'Seconds', 'Minutes', 'Hours', 'Days']

           analysis_region: Analysis Region (str). Optional parameter.  Specify the region in which to perform the analysis. If a value is not specified for this parameter, the tool
                            will automatically calculate the region name based on the location of the input points. Setting the name of the region is required only if the
                            auto-detection of the region name is not accurate for your inputs. To specify a region, use one of the following values:  Europe,Japan,Korea,MiddleEast,
                            and Africa.  NorthAmerica, SouthAmerica, SouthAsia,Thailand; The following region names are no longer supported and will be removed in future releases.
                            If you specify one of the deprecated region names, the tool automatically assigns a supported region name for your region. Greece redirects to Europe.
                            India redirects to South Asia. Oceania redirects to South Asia. South East Asia redirects to South Asia. Taiwan redirects to South Asia.

                            Choice list:['Europe', 'Japan', 'Korea', 'MiddleEastAndAfrica', 'NorthAmerica', 'SouthAmerica', 'SouthAsia', 'Thailand']

           reorder_stops_to_find_optimal_routes: Reorder Stops to Find Optimal Routes (bool). Optional parameter.  Specify whether to visit the stops in the order you define or the order the tool determines will minimize overall travel. Checked (True)-The tool determines the sequence that will minimize overall travel distance or time. It can reorder stops and account for time windows at stops. Additional parameters allow you to preserve the first or last stops while allowing the tool to reorder the intermediary stops.Unchecked (False)-The stops are visited in the order you define. This is the default option. You can set the order of stops using a Sequence attribute in the input stops features or let the sequence be determined by the Object ID of the stops. Finding the optimal stop order and the best routes is commonly known as solving the traveling salesman problem (TSP).

           preserve_terminal_stops: Preserve Terminal Stops (str). Optional parameter.  When Reorder Stops to Find Optimal Routes is checked (or True), you have options to preserve the starting or ending stops and the tool can reorder the rest. The first and last stops are determined by their Sequence attribute values or, if the Sequence values are null, by their Object ID values.Preserve First-The tool won't reorder the first stop. Choose this option if you are starting from a known location, such as your home, headquarters, or current location.Preserve Last-The tool won't reorder the last stop. The output routes may start from any stop feature but must end at the predetermined last stop. Preserve First and Last-The tool won't reorder the first and last stops.Preserve None-The tool may reorder any stop, including the first and last stops. The route may start or end at any of the stop features.Preserve Terminal Stops is ignored when Reorder Stops to Find Optimal Routes is unchecked (or False).
                  Choice list:['Preserve First', 'Preserve Last', 'Preserve First and Last', 'Preserve None']

           return_to_start: Return to Start (bool). Optional parameter.  Choose whether routes should start and end at the same location. With this option you can avoid duplicating the first stop feature and sequencing the duplicate stop at the end.The starting location of the route is the stop feature with the lowest value in the Sequence attribute. If the Sequence values are null, it is the stop feature with the lowest Object ID value.Checked (True)-The route should start and end at the first stop feature. This is the default value. When Reorder Stops to Find Optimal Routes and Return to Start are both checked (or True), Preserve Terminal Stops must be set to Preserve First.Unchecked (False)-The route won't start and end at the first stop feature.

           use_time_windows: Use Time Windows (bool). Optional parameter.  Check this option (or set it to True) if any input stops have time windows that specify when the route should reach the stop. You can add time windows to input stops by entering time values in the TimeWindowStart and TimeWindowEnd attributes.Checked (True)-The input stops have time windows and you want the tool to try to honor them.Unchecked (False)-The input stops don't have time windows, or if they do, you don't want the tool to try to honor them. This is the default value.The tool will take slightly longer to run when Use Time Windows is checked (or True), even when none of the input stops have time windows, so it is recommended to uncheck this option (set to False) if possible.

           time_of_day: Time of Day (datetime). Optional parameter.  Specifies the time and date at which the routes should
            begin. If you are modeling the driving travel mode and specify the current date and time as the value
            for this parameter, the tool will use live traffic conditions to
            find the best routes and the total travel time will be based
            on traffic conditions. Specifying a time of day results in more accurate
            routes and estimations of travel times because the
            travel times account for the traffic conditions that are applicable
            for that date and time.The Time Zone for Time of Day parameter specifies whether this time and date refer to UTC or the time zone in which the stop is located.The tool ignores this parameter when Measurement Units isn't set to a time-based unit.

           time_zone_for_time_of_day: Time Zone for Time of Day (str). Optional parameter.  Specifies the time zone of the Time of Day parameter.Geographically Local-The Time of Day parameter refers to the time zone in which the first stop of a route is located. If you are generating many routes that start in multiple times zones, the start times are staggered in Coordinated Universal Time (UTC). For example, a Time of Day value of 10:00 a.m., 2 January, would mean a start time of 10:00 a.m. Eastern Standard Time (UTC-3:00) for routes beginning in the Eastern Time Zone and 10:00 a.m. Central Standard Time (UTC-4:00) for routes beginning in the Central Time Zone. The start times are offset by one hour in UTC. The arrive and depart times and dates recorded in the output Stops feature class will refer to the local time zone of the first stop for each route.UTC-The Time of Day parameter refers to Coordinated Universal Time (UTC). Choose this option if you want to generate a route for a specific time, such as now, but aren't certain in which time zone the first stop will be located. If you are generating many routes spanning multiple times zones, the start times in UTC are simultaneous. For example, a Time of Day value of 10:00 a.m., 2 January, would mean a start time of 5:00 a.m. Eastern Standard Time (UTC-5:00) for routes beginning in the Eastern Time Zone and 4:00 a.m. Central Standard Time (UTC-6:00) for routes beginning in the Central Time Zone. Both routes would start at 10:00 a.m. UTC. The arrive and depart times and dates recorded in the output Stops feature class will refer to UTC.
                  Choice list:['Geographically Local', 'UTC']

           uturn_at_junctions: UTurn at Junctions (str). Optional parameter.  The U-Turn policy at junctions. Allowing U-turns implies the solver can turn around at a junction and double back on the same street.

           Given that junctions represent street intersections and dead ends, different vehicles  may be able to turn around at some junctions but not at others-it depends on whether the junction represents an intersection or dead end. To accommodate, the U-turn policy parameter is implicitly specified by how many edges connect to the junction, which is known as junction valency. The acceptable values for this parameter are listed below; each is followed by a description of its meaning in terms of junction valency.
            Allowed- U-turns are permitted at junctions with any number of connected edges. This is the default value.Not Allowed- U-turns are prohibited at all junctions, regardless of junction valency. Note, however, that U-turns are still permitted at network locations even when this setting is chosen; however, you can set the individual network locations' CurbApproach property to prohibit U-turns there as well.Allowed only at Dead Ends- U-turns are prohibited at all junctions, except those that have only one adjacent edge (a dead end).Allowed only at Intersections and Dead Ends- U-turns are prohibited at junctions where exactly two adjacent edges meet but are permitted at intersections (junctions with three or more adjacent edges) and dead ends (junctions with exactly one adjacent edge).  Often, networks have extraneous junctions in the middle of road segments. This option prevents vehicles from making U-turns at these locations.
                  Choice list:['Allowed', 'Not Allowed', 'Allowed Only at Dead Ends', 'Allowed Only at Intersections and Dead Ends']

           point_barriers: Point Barriers (FeatureSet). Optional parameter.  Specify one or more points to act as temporary
            restrictions or represent additional time or distance that may be
            required to travel on the underlying streets. For example, a point
            barrier can be used to represent a fallen tree along a street or
            time delay spent at a railroad crossing. The tool imposes a limit of 250 points that can be added
            as barriers.When specifying the point barriers, you can set properties for each one, such as its name or barrier type, by using attributes. The point barriers can be specified with the following attributes:
                                                                    Name The name of the barrier. BarrierType Specifies whether the point barrier restricts travel
            completely or adds time or distance when it is crossed. The value
            for this attribute is specified as one of the following
            integers (use the numeric code, not the name in parentheses):  0 (Restriction)-Prohibits travel through the barrier. The barrier
            is referred to as a restriction point barrier since it acts as a
            restriction.  2 (Added Cost)-Traveling through the barrier increases the travel
            time or distance by the amount specified in the
            Additional_Time, Additional_Distance, or Additional_Cost field. This barrier type is
            referred to as an added-cost point barrier.  Additional_Time Indicates how much travel time is added when the
            barrier is traversed. This field is applicable only for added-cost
            barriers and only if the travel mode used for the analysis uses an impedance attribute that is time-based. This field
            value must be greater than or equal to zero, and its units are the same as those specified in the
            Measurement Units parameter. Additional_DistanceIndicates how much distance is added when the
            barrier is traversed. This field is applicable only for added-cost
            barriers and only if the travel mode used for the analysis uses an impedance attribute that is distance-based. The field value
            must be greater than or equal to zero, and its units are the same as those specified in the
            Measurement Units parameter.Additional_CostIndicates how much cost is added when the
            barrier is traversed. This field is applicable only for added-cost
            barriers and only if the travel mode used for the analysis uses an impedance attribute that is neither time-based or distance-based. FullEdgeSpecify how the restriction point barriers are applied to the edge elements during the analysis. The field value is specified as one of the following integers (use the numeric code, not the name in parentheses):  0 (False):  Permits travel on the edge up to the barrier, but not through it. This is the default value.1 (True): Restricts travel anywhere on the associated edge. CurbApproachSpecifies the direction of traffic that is affected by the barrier. The field value is specified as one of the following integers (use the numeric code, not the name in parentheses): 0 (Either side of vehicle): The barrier affects travel over the edge in both directions.1 (Right side of vehicle): Vehicles are only affected if the barrier is on their right side during the approach. Vehicles that traverse the same edge but approach the barrier on their left side are not affected by the barrier. 2 (Left side of vehicle): Vehicles are only affected if the barrier is on their left side during the approach. Vehicles that traverse the same edge but approach the barrier on their right side are not affected by the barrier. Since junctions are points and don't have a side, barriers on junctions affect all vehicles regardless of the curb approach. The CurbApproach property was designed to work with both kinds of national driving standards: right-hand traffic (United States) and left-hand traffic (United Kingdom). First, consider a facility on the left side of a vehicle. It is always on the left side regardless of whether the vehicle travels on the left or right half of the road. What may change with national driving standards is your decision to approach a facility from one of two directions, that is, so it ends up on the right or left side of the vehicle. For example, if you want to arrive at a facility and not have a lane of traffic between the vehicle and the facility, you would choose Right side of vehicle (1) in the United States but Left side of vehicle (2) in the United Kingdom.BearingThe direction in which a point is moving. The units are degrees and are measured clockwise from true north. This field is used in conjunction with the BearingTol field. Bearing data is usually sent automatically from a mobile device equipped with a GPS receiver. Try to include bearing data if you are loading an input location that is moving, such as a pedestrian or a vehicle. Using this field tends to prevent adding locations to the wrong edges, which can occur when a vehicle is near an intersection or an overpass for example. Bearing also helps the tool determine on which side of the street the point is. For more information, see Bearing and BearingTol in the ArcGIS help system. BearingTolThe bearing tolerance value creates a range of acceptable bearing values when locating moving points on an edge using the Bearing field. If the value from the Bearing field is within the range of acceptable values that are generated from the bearing tolerance on an edge, the point can be added as a network location there; otherwise, the closest point on the next-nearest edge is evaluated. The units are in degrees and the default value is 30. Values must be greater than zero and less than 180. A value of 30 means that when ArcGIS Network Analyst extension  attempts to add a network location on an edge, a range of acceptable bearing values is generated 15 degrees to either side of the edge (left and right) and in both digitized directions of the edge. For more information, see Bearing and BearingTol in the ArcGIS help system. NavLatencyThis field is only used in the solve process if Bearing and BearingTol also have values; however, entering a NavLatency value is optional, even when values are present in Bearing and BearingTol. NavLatency indicates how much time is expected to elapse from the moment GPS information is sent from a moving vehicle to a server and the moment the processed route is received by the vehicle's navigation device. The time units of NavLatency are the same as the units specified by the timeUnits property of the analysis object.

           line_barriers: Line Barriers (FeatureSet). Optional parameter.  Specify one or more lines that prohibit travel anywhere
            the lines intersect the streets. For example, a parade or protest
            that blocks traffic across several street segments can be modeled
            with a line barrier. A line barrier can also quickly fence off
            several roads from being traversed, thereby channeling possible
            routes away from undesirable parts of the street
            network. The tool imposes a limit on the number of streets you can
            restrict using the Line Barriers parameter. While there is no limit on
            the number of lines you can specify as line barriers, the combined
            number of streets intersected by all the lines cannot exceed
            500.When specifying the line barriers, you can set a name property for each one by using the following attribute:
                                                                    Name The name of the barrier.

           polygon_barriers: Polygon Barriers (FeatureSet). Optional parameter.  Specify polygons that either completely restrict travel or
            proportionately scale the time or distance required to travel on
            the streets intersected by the polygons. The service imposes a limit on the number of streets you
            can restrict using the Polygon Barriers parameter. While there is
            no limit on the number of polygons you can specify as the polygon
            barriers, the combined number of streets intersected by all the
            polygons should not exceed 2,000.When specifying the polygon barriers, you can set properties for each one, such as its name or barrier type, by using attributes. The polygon barriers can be specified with the following attributes:
            Name The name of the barrier. BarrierType Specifies whether the barrier restricts travel completely
            or scales the time or distance for traveling through it. The field
            value is specified as one of the following integers (use the numeric code, not the name in parentheses):  0 (Restriction)-Prohibits traveling through any part of the barrier.
            The barrier is referred to as a restriction polygon barrier since it
            prohibits traveling on streets intersected by the barrier. One use
            of this type of barrier is to model floods covering areas of the
            street that make traveling on those streets impossible.  1 (Scaled Cost)-Scales the time or distance required to travel the
            underlying streets by a factor specified using the ScaledTimeFactor
            or ScaledDistanceFactor field. If the streets are partially
            covered by the barrier, the travel time or distance is apportioned
            and then scaled. For example, a factor 0.25 would mean that travel
            on underlying streets is expected to be four times faster than
            normal. A factor of 3.0 would mean it is expected to take three
            times longer than normal to travel on underlying streets. This
            barrier type is referred to as a scaled-cost polygon barrier. It
            might be used to model storms that reduce travel speeds in specific
            regions. ScaledTimeFactor This is the factor by which the travel time of the streets
            intersected by the barrier is multiplied. The field value must be greater than zero. This field is applicable only for scaled-cost
            barriers and only if the travel mode used for the analysis uses an impedance attribute that is time based. ScaledDistanceFactor This is the factor by which the distance of the streets
            intersected by the barrier is multiplied. The field value must be greater than zero.This field is applicable only for scaled-cost
            barriers and only if the travel mode used for the analysis uses an impedance attribute that is distance based.  ScaledCostFactor This is the factor by which the cost of the streets
            intersected by the barrier is multiplied. The field value must be greater than zero. This field is applicable only for scaled-cost
            barriers and only if the travel mode used for the analysis uses an impedance attribute that is neither time based nor distance based.

           use_hierarchy: Use Hierarchy (bool). Optional parameter.  Specify whether hierarchy should be used when finding the shortest paths between stops. Checked (True)-Use hierarchy when finding routes. When
            hierarchy is used, the tool prefers higher-order streets (such as
            freeways) to lower-order streets (such as local roads), and can be used
            to simulate the driver preference of traveling on freeways instead
            of local roads even if that means a longer trip. This is especially
            true when finding routes to faraway locations, because drivers on long-distance trips tend to prefer traveling on freeways where stops, intersections, and turns can be avoided. Using hierarchy is computationally faster,
            especially for long-distance routes, since the tool can determine the
            best route from a relatively smaller subset of streets.   Unchecked (False)-Do not use hierarchy when finding routes. If
            hierarchy is not used, the tool considers all the streets and doesn't
            prefer higher-order streets when finding the route. This is often
            used when finding short routes within a city.  The tool automatically reverts to using hierarchy if the
            straight-line distance between facilities and demand points is
            greater than 50 miles (80.46
            kilometers), even if you have set this parameter to not use hierarchy.This parameter is ignored unless Travel Mode is set to Custom. When modeling a custom walking mode, it is recommended to turn off hierarchy since the hierarchy is designed for motorized vehicles.

           restrictions: Restrictions (str). Optional parameter.  Specify which restrictions should be honored by the tool when finding the best routes.A restriction represents a driving
            preference or requirement. In most cases, restrictions cause roads
            to be prohibited. For instance, using an Avoid Toll Roads restriction will result in a route that will include toll roads only when it is absolutely required to travel on toll roads in order to visit an incident or a facility. Height Restriction makes it possible to route around any clearances that are lower than the height of your vehicle. If you are carrying corrosive materials on your vehicle, using the Any Hazmat Prohibited restriction prevents hauling the materials along roads where it is marked as illegal to do so. The values you provide for this parameter are ignored unless Travel Mode is set to Custom.Some restrictions require an additional value to be
            specified for their desired use. This value needs to be associated
            with the restriction name and a specific parameter intended to work
            with the restriction. You can identify such restrictions if their
            names appear under the AttributeName column in the Attribute
            Parameter Values parameter. The ParameterValue field should be
            specified in the Attribute Parameter Values parameter for the
            restriction to be correctly used when finding traversable roads.Some restrictions are supported only in certain countries; their availability is stated by region in the list below. Of the restrictions that have limited availability within a region, you can check whether the restriction is available in a particular country by looking at the table in the Country List section of the Data coverage for network analysis services web page. If a country has a value of  Yes in the Logistics Attribute column, the restriction with select availability in the region is supported in that country. If you specify restriction names that are not available in the country where your incidents are located, the service ignores the invalid restrictions. The service also ignores restrictions whose Restriction Usage parameter value is between 0 and 1 (see the Attribute Parameter Value parameter). It prohibits all restrictions whose Restriction Usage parameter value is greater than 0.The tool supports the following restrictions: Any Hazmat Prohibited-The results will not include roads
            where transporting any kind of hazardous material is
            prohibited. Availability: Select countries in North America and Europe Avoid Carpool Roads-The results will avoid roads that are
            designated exclusively for carpool (high-occupancy)
            vehicles. Availability: All countries Avoid Express Lanes-The results will avoid roads designated
            as express lanes. Availability: All countries Avoid Ferries-The results will avoid ferries. Availability: All countries Avoid Gates-The results will avoid roads where there are
            gates such as keyed access or guard-controlled
            entryways.Availability: All countries Avoid Limited Access Roads-The results will avoid roads
            that are limited access highways. Availability: All countries Avoid Private Roads-The results will avoid roads that are
            not publicly owned and maintained. Availability: All countries Avoid Roads Unsuitable for Pedestrians-The results will avoid roads that are
            unsuitable for pedestrians. Availability: All countries Avoid Stairways-The results will avoid all stairways on a pedestrian suitable route. Availability: All countries Avoid Toll Roads-The results will avoid all toll
            roads for automobiles.Availability: All countries Avoid Toll Roads for Trucks-The results will avoid all toll
            roads for trucks.Availability: All countries Avoid Truck Restricted Roads-The results will avoid roads where trucks are not allowed, except when making deliveries.Availability: All countries Avoid Unpaved Roads-The results will avoid roads that are
            not paved (for example, dirt, gravel, and so on). Availability: All countries Axle Count Restriction-The results will not include roads
            where trucks with the specified number of axles are prohibited. The
            number of axles can be specified using the Number of Axles
            restriction parameter.Availability: Select countries in North America and Europe Driving a Bus-The results will not include roads where
            buses are prohibited. Using this restriction will also ensure that
            the results will honor one-way streets. Availability: All countries Driving a Delivery Vehicle-The results will not include
            roads where delivery vehicles are prohibited. Using this restriction
            will also ensure that the results will honor one-way
            streets. Availability: All countries Driving a Taxi-The results will not include roads where
            taxis are prohibited. Using this restriction will also ensure that
            the results will honor one-way streets. Availability: All countries Driving a Truck-The results will not include roads where
            trucks are prohibited. Using this restriction will also ensure that
            the results will honor one-way streets. Availability: All countries Driving an Automobile-The results will not include roads
            where automobiles are prohibited. Using this restriction will also
            ensure that the results will honor one-way streets. Availability: All countries Driving an Emergency Vehicle-The results will not include
            roads where emergency vehicles are prohibited. Using this
            restriction will also ensure that the results will honor one-way
            streets. Availability: All countries Height Restriction-The results will not include roads
            where the vehicle height exceeds the maximum allowed height for the
            road. The vehicle height can be specified using the Vehicle Height
            (meters) restriction parameter. Availability: Select countries in North America and Europe Kingpin to Rear Axle Length Restriction-The results will
            not include roads where the vehicle length exceeds the maximum
            allowed kingpin to rear axle for all trucks on the road. The length
            between the vehicle kingpin and the rear axle can be specified
            using the Vehicle Kingpin to Rear Axle Length (meters) restriction
            parameter. Availability: Select countries in North America and Europe Length Restriction-The results will not include roads
            where the vehicle length exceeds the maximum allowed length for the
            road. The vehicle length can be specified using the Vehicle Length
            (meters) restriction parameter. Availability: Select countries in North America and Europe Preferred for Pedestrians-The results will use preferred routes suitable for pedestrian navigation. Availability: Select countries in North America and Europe Riding a Motorcycle-The results will not include roads
            where motorcycles are prohibited. Using this restriction will also
            ensure that the results will honor one-way streets. Availability: All countries Roads Under Construction Prohibited-The results will not
            include roads that are under construction.Availability: All countries Semi or Tractor with One or More Trailers Prohibited-The
            results will not include roads where semis or tractors with one or
            more trailers are prohibited. Availability: Select countries in North America and Europe Single Axle Vehicles Prohibited-The results will not
            include roads where vehicles with single axles are
            prohibited.Availability: Select countries in North America and Europe Tandem Axle Vehicles Prohibited-The results will not
            include roads where vehicles with tandem axles are
            prohibited.Availability: Select countries in North America and Europe Through Traffic Prohibited-The results will not include
            roads where through traffic (non local) is prohibited.Availability: All countries Truck with Trailers Restriction-The results will not
            include roads where trucks with the specified number of trailers on
            the truck are prohibited. The number of trailers on the truck can
            be specified using the Number of Trailers on Truck restriction
            parameter.Availability: Select countries in North America and Europe Use Preferred Hazmat Routes-The results will prefer roads
            that are designated for transporting any kind of hazardous
            materials. Availability: Select countries in North America and Europe Use Preferred Truck Routes-The results will prefer roads
            that are designated as truck routes, such as the roads that are
            part of the national network as specified by the National Surface
            Transportation Assistance Act in the United States, or roads that
            are designated as truck routes by the state or province, or roads
            that are preferred by the trucks when driving in an
            area.Availability: Select countries in North America and Europe Walking-The results will not include roads where
            pedestrians are prohibited.Availability: All countries Weight Restriction-The results will not include roads
            where the vehicle weight exceeds the maximum allowed weight for the
            road. The vehicle weight can be specified using the Vehicle Weight
            (kilograms) restriction parameter.Availability: Select countries in North America and Europe Weight per Axle Restriction-The results will not include
            roads where the vehicle weight per axle exceeds the maximum allowed
            weight per axle for the road. The vehicle weight per axle can be
            specified using the Vehicle Weight per Axle (kilograms) restriction
            parameter.Availability: Select countries in North America and Europe Width Restriction-The results will not include roads where
            the vehicle width exceeds the maximum allowed width for the road.
            The vehicle width can be specified using the Vehicle Width (meters)
            restriction parameter.Availability: Select countries in North America and Europe The Driving a Delivery Vehicle restriction attribute is no longer available. The service will ignore this restriction since it is invalid. To achieve similar results, use the Driving a Truck restriction attribute along with the Avoid Truck Restricted Roads restriction attribute.
                  Choice list:['Any Hazmat Prohibited', 'Avoid Carpool Roads', 'Avoid Express Lanes', 'Avoid Ferries', 'Avoid Gates', 'Avoid Limited Access Roads', 'Avoid Private Roads', 'Avoid Roads Unsuitable for Pedestrians', 'Avoid Stairways', 'Avoid Toll Roads', 'Avoid Toll Roads for Trucks', 'Avoid Truck Restricted Roads', 'Avoid Unpaved Roads', 'Axle Count Restriction', 'Driving a Bus', 'Driving a Taxi', 'Driving a Truck', 'Driving an Automobile', 'Driving an Emergency Vehicle', 'Height Restriction', 'Kingpin to Rear Axle Length Restriction', 'Length Restriction', 'Preferred for Pedestrians', 'Riding a Motorcycle', 'Roads Under Construction Prohibited', 'Semi or Tractor with One or More Trailers Prohibited', 'Single Axle Vehicles Prohibited', 'Tandem Axle Vehicles Prohibited', 'Through Traffic Prohibited', 'Truck with Trailers Restriction', 'Use Preferred Hazmat Routes', 'Use Preferred Truck Routes', 'Walking', 'Weight Restriction', 'Weight per Axle Restriction', 'Width Restriction']

           attribute_parameter_values: Attribute Parameter Values (FeatureSet). Optional parameter.  Specify additional values required by some restrictions, such as the weight of a vehicle for Weight Restriction. You can also use the attribute parameter to specify whether any restriction prohibits, avoids, or prefers
            travel on roads that use the restriction. If the restriction is
            meant to avoid or prefer roads, you can further specify the degree
            to which they are avoided or preferred using this
            parameter. For example, you can choose to never use toll roads, avoid them as much as possible, or even highly prefer them.The values you provide for this parameter are ignored unless Travel Mode is set to Custom. If you specify the Attribute Parameter Values parameter from a
            feature class, the field names on the feature class must match the fields as described below:AttributeName- Lists the name of the restriction.ParameterName- Lists the name of the parameter associated with the
            restriction. A restriction can have one or more ParameterName field
            values based on its intended use.ParameterValue- The value for ParameterName used by the tool
            when evaluating the restriction. Attribute Parameter Values is dependent on the
            Restrictions parameter. The ParameterValue field is applicable only
            if the restriction name is specified as the value for the
            Restrictions parameter. In Attribute Parameter Values, each
            restriction (listed as AttributeName) has a ParameterName field
            value, Restriction Usage, that specifies whether the restriction
            prohibits, avoids, or prefers travel on the roads associated with
            the restriction and the degree to which the roads are avoided or
            preferred. The Restriction Usage ParameterName can be assigned any of
            the following string values or their equivalent numeric values
            listed within the parentheses:  PROHIBITED (-1)-Travel on the roads using the restriction is completely
            prohibited.  AVOID_HIGH (5)-It
            is highly unlikely for the tool to include in the route the roads
            that are associated with the restriction.  AVOID_MEDIUM (2)-It
            is unlikely for the tool to include in the route the roads that are
            associated with the restriction.  AVOID_LOW (1.3)-It
            is somewhat unlikely for the tool to include in the route the roads
            that are associated with the restriction.  PREFER_LOW (0.8)-It
            is somewhat likely for the tool to include in the route the roads
            that are associated with the restriction.  PREFER_MEDIUM (0.5)-It is likely for the tool to include in the route the roads that
            are associated with the restriction.  PREFER_HIGH (0.2)-It is highly likely for the tool to include in the route the roads
            that are associated with the restriction.  In most cases, you can use the default value, PROHIBITED,
            for the Restriction Usage if the restriction is dependent on a
            vehicle-characteristic such as vehicle height. However, in some
            cases, the value for Restriction Usage depends on your routing
            preferences. For example, the Avoid Toll Roads restriction has the
            default value of AVOID_MEDIUM for the Restriction Usage parameter.
            This means that when the restriction is used, the tool will try to
            route around toll roads when it can. AVOID_MEDIUM also indicates
            how important it is to avoid toll roads when finding the best
            route; it has a medium priority. Choosing AVOID_LOW would put lower
            importance on avoiding tolls; choosing AVOID_HIGH instead would
            give it a higher importance and thus make it more acceptable for
            the service to generate longer routes to avoid tolls. Choosing
            PROHIBITED would entirely disallow travel on toll roads, making it
            impossible for a route to travel on any portion of a toll road.
            Keep in mind that avoiding or prohibiting toll roads, and thus
            avoiding toll payments, is the objective for some; in contrast,
            others prefer to drive on toll roads because avoiding traffic is
            more valuable to them than the money spent on tolls. In the latter
            case, you would choose PREFER_LOW, PREFER_MEDIUM, or PREFER_HIGH as
            the value for Restriction Usage. The higher the preference, the
            farther the tool will go out of its way to travel on the roads
            associated with the restriction.

           route_shape: Route Shape (str). Optional parameter.  Specify the type of route features that are output by the
            tool. The parameter can be specified using one of the following
            values:  True Shape-Return the exact shape of the resulting route
            that is based on the underlying streets.  True Shape with Measures-Return the exact shape of the resulting route that is based on the underlying streets. Additionally, construct measures so the shape may be used in linear referencing. The measurements increase from the first stop and record the cumulative travel time or travel distance in the units specified by the Measurement Units parameter. Straight Line-Return a straight line between two stops.   None-Do not return any shapes for the routes. This value
            can be useful, and return results quickly, in cases where you are only interested in determining
            the total travel time or travel distance of a route.  When the Route Shape parameter is set to True Shape or True Shape with Measures, the
            generalization of the route shape can be further controlled using
            the appropriate value for the Route Line Simplification Tolerance
            parameter. No matter which value you choose for the Route Shape
            parameter, the best route is always determined by minimizing the
            travel time or the travel distance, never using the straight-line
            distance between stops. This means that only the route shapes are different,
            not the underlying streets that are searched when finding the
            route.
                  Choice list:['True Shape', 'True Shape with Measures', 'Straight Line', 'None']

           route_line_simplification_tolerance: Route Line Simplification Tolerance (LinearUnit). Optional parameter.  Specify by how much you want to simplify the geometry of the output lines for routes, directions, and route edges.The tool ignores this parameter if the Route Shape parameter isn't set to True Shape. Simplification maintains critical
            points on a route, such as turns at intersections, to define the
            essential shape of the route and removes other points. The
            simplification distance you specify is the maximum allowable offset
            that the simplified line can deviate from the original line.
            Simplifying a line reduces the number of vertices that are part of
            the route geometry. This improves the tool execution
            time.

           populate_route_edges: Populate Route Edges (bool). Optional parameter.  Specify whether the tool should generate edges for each route. Route edges represent the individual street features or other similar features that are traversed by a route. The output Route Edges layer is commonly used to see which streets or paths are traveled on the most or least by the resultant routes. Checked (True)-Generate route edges. The output Route Edges layer is populated with line features.   Unchecked (False)-Don't generate route edges. The output Route Edges layer is returned, but it is empty.

           populate_directions: Populate Directions (bool). Optional parameter.  Specify whether the tool should generate driving directions for
            each route.  Checked (True)-Indicates that the directions will be generated
            and configured based on the values for the Directions Language,
            Directions Style Name, and Directions Distance Units
            parameters.  Unchecked (False)-Directions are not generated, and the tool
            returns an empty Directions layer.

           directions_language: Directions Language (str). Optional parameter.  Specify the language that should be used when generating
            travel directions. This parameter is used only when the Populate
            Directions parameter is checked, or set to True. The parameter value can be
            specified using one of the following two- or five-character language codes:  ar-Arabic  bs-Bosnian ca-Catalancs-Czech da-Danish de-German  el-Greek en-English  es-Spanish et-Estonian fi-Finnish fr-French  he-Hebrew  hi-Hindi hr-Croatian hu-Hungarian id-Indonesian it-Italian  ja-Japanese  ko-Korean  lt-Lithuanian lv-Latvian nb-Norwegian nl-Dutch  pl-Polish  pt-BR-Brazilian
            Portuguese  pt-PT-European
            Portuguese  ro-Romanian ru-Russian  sl-Slovenian sr-Serbian sv-Swedish  th-Thaitr-Turkish vi-Vietnamese zh-CN-Simplified
            Chinese  zh-HK-Traditional Chinese (Hong Kong)
             zh-TW-Traditional Chinese (Taiwan)
            The tool first tries to find an exact match for the specified language including any language localization. If an exact match is not found, it tries to match the language family. If a match is still not found, the tool returns the directions using the default language, English. For example, if the directions language is specified as  es-MX (Mexican Spanish), the tool will return the directions in Spanish as it supports es language code and not es-MX.If a language supports localization, such as Brazilian Portuguese (pt-BR) and European Portuguese (pt-PT), you should specify the language family and   the localization. If you only specify the language family, the tool will not match the language family and instead return directions in the default language, English. For example, if the directions language is specified as pt, the tool will return the directions in English since it cannot decide if the directions should be returned in pt-BR or pt-PT.

           directions_distance_units: Directions Distance Units (str). Optional parameter.  Specify the units for displaying travel distance in the
            driving directions. This parameter is used only when the Populate
            Directions parameter is checked, or set to True.MilesKilometersMetersFeetYardsNauticalMiles
                  Choice list:['Meters', 'Kilometers', 'Feet', 'Yards', 'Miles', 'NauticalMiles']

               directions_style_name: Directions Style Name (str). Optional parameter.  Specify the name of the formatting style for the
            directions. This parameter is used only when the Populate Directions parameter is checked, or set to True. The parameter can be specified
            using the following values:  NA Desktop-Generates turn-by-turn directions suitable
            for printing.  NA Navigation-Generates turn-by-turn directions designed
            for an in-vehicle navigation device.
                  Choice list:['NA Desktop', 'NA Navigation']

           travel_mode: Travel Mode (str). Optional parameter.  Specify the mode of transportation to model in the analysis. Travel modes are managed in ArcGIS Online and can be configured by the administrator of your organization to better reflect your organization's workflows. You need to specify the name of a travel mode supported by your organization. To get a list of supported travel mode names, use the same GIS server connection you used to access this tool, and from the Utilities toolbox, run GetTravelModes. The GetTravelModes tool adds a table, Supported Travel Modes, to the application. Any value in the Travel Mode Name field from the Supported Travel Modes table can be specified as input. You can also specify the value from the Travel Mode Settings field as input. This speeds up the tool execution because the tool does not have to look up the settings based on the travel mode name. The default value, Custom, allows you to configure your own travel mode using the custom travel mode parameters (UTurn at Junctions, Use Hierarchy, Restrictions, Attribute Parameter Values,  and Impedance). The default values of the custom travel mode parameters model traveling by car. You may want to choose Custom and set the custom travel mode parameters listed above to model a pedestrian with a fast walking speed or a truck with a given height, weight, and cargo of certain hazardous materials. You may choose to do this to try out different settings to get the analysis results you want. Once you have identified the analysis settings, you should work with your organization's administrator and save these settings as part of a new or existing travel mode so that everyone in your organization can rerun the analysis with the same settings. By choosing Custom, the values you set for the custom travel mode parameters are included in the analysis. Specifying  another travel mode, as defined by your organization, causes any values you set for the custom travel mode parameters to be ignored; the tool overrides them with values from your specified travel mode.

           impedance: Impedance (str). Optional parameter.  Specify the
            impedance, which is a value that represents the effort or cost of traveling along road segments or on other parts of the transportation network. Travel time is an impedance; a car may take one minute to travel a mile along an empty road. Travel times can vary by travel mode-a pedestrian may take more than 20  minutes to walk the same mile, so it is important to choose the right impedance for the travel mode you are modeling. Travel distance can also be an impedance; the length of a road in kilometers can be thought of as impedance. Travel distance in this sense is the same for all modes-a kilometer for a pedestrian is also a kilometer for a car. (What may change is the pathways on which the different modes are allowed to travel, which affects distance between points, and this is modeled by travel mode settings.)The value you provide for this parameter is ignored unless Travel Mode is set to Custom, which is the default value.Choose from the following impedance values:TravelTime-takes advantage of historical and live traffic data and is good for modeling the time it takes automobiles to travel along roads at a specific time of the day using live traffic speed data where available. When using TravelTime, you can optionally specify the TravelTime::Vehicle Maximum Speed (km/h) attribute parameter to specify the physical limitation of the speed the vehicle is capable of traveling.Minutes-does not use live traffic data but uses the historical average speeds for automobiles.TruckTravelTime-takes advantage of historical and live traffic data, but caps the speed to the posted truck speed limit. This is good for modeling the time it takes for the trucks to travel along roads at a specific time. When using TruckTravelTime, you can optionally specify the TruckTravelTime::Vehicle Maximum Speed (km/h) attribute parameter to specify the physical limitation of the speed the truck is capable of traveling.TruckMinutes-does not use live traffic data but uses the smaller of the historical average speeds for automobiles and the posted speed limits for trucks.WalkTime-defaults to a speed of 5 km/hr on all roads and paths, but this can be configured through the WalkTime::Walking Speed (km/h) attribute parameter.Miles-Stores  length measurements along roads in miles and can be used for performing analysis based on shortest distance.Kilometers-Stores  length measurements along roads in kilometers and can be used for performing analysis based on shortest distance.TimeAt1KPH-defaults to a speed of 1 km/hr on all roads and paths. The speed cannot be changed using any attribute parameters.If you choose a time-based impedance, such as TravelTime, TruckTravelTime, Minutes, TruckMinutes, or WalkTime, the Measurement Units parameter must be set to a time-based value; if you choose a distance-based impedance such as  Miles, Kilometers, Measurement Units must be distance-based.Drive Time, Truck Time, Walk Time, and Travel Distance impedance values are no longer supported and will be removed in a future release.   If you use one of these values, the tool uses the value of the  Time Impedance parameter for time-based values or Distance Impedance parameter for distance-based values.
                  Choice list:['Drive Time', 'Truck Time', 'Walk Time', 'Travel Distance', 'Minutes', 'TravelTime', 'TimeAt1KPH', 'WalkTime', 'TruckMinutes', 'TruckTravelTime', 'Miles', 'Kilometers']

           time_zone_for_time_windows: Time Zone for Time Windows (str). Optional parameter.  Specifies the time zone for the time window values on stops. The time windows are specified as part of TimeWindowStart and TimeWindowEnd fields on stops. This parameter is applicable only when the Use Time Windows parameter is checked (or set to True).
             The parameter can be specified using one of the following values:Geographically Local-The time window values associated with the stops are in the time zone in which the stops are located. For example, if the stop is located in an area that follows Eastern Standard Time and has time window values of 8 AM and 10 AM, the time window values will be treated as 8 AM and 10 AM in Eastern Standard Time. This is the default value.UTC-The time window values associated with the stops are in the Coordinated Universal Time (UTC). For example, if the stop is located in an area that follows Eastern Standard Time and has time window values of 8 AM and 10 AM, the time window values will be treated as 12 PM and 2 PM Eastern Standard Time assuming the Eastern Standard Time is obeying the Daylight Saving Time. Specifying the time window values in UTC is useful if you do not know the time zone in which the stops are located or when you have stops in multiple time zones and you want all the time windows to start simultaneously.
                  Choice list:['Geographically Local', 'UTC']

           save_output_network_analysis_layer: Save Output Network Analysis Layer (bool). Optional parameter.  Specify if the tool should save the analysis settings as a network analysis layer file. You cannot directly work with this file even when you open the file in an ArcGIS Desktop application like ArcMap. It is meant to be sent to Esri Technical Support to diagnose the quality of results returned from the tool.
            Checked (True)-Save the network analysis layer file. The file is downloaded in a temporary directory on your machine. In ArcGIS Pro, the location of the downloaded file can be determined  by viewing the value for the Output Network Analysis Layer parameter in the entry corresponding to the tool execution in the Geoprocessing history of your Project. In ArcMap, the location of the file can be determined by accessing the Copy Location option in the shortcut menu on the Output Network Analysis Layer parameter in the entry corresponding to the tool execution in the Geoprocessing Results window.   Unchecked (False)-Do not save the network analysis layer file. This is the default.

           overrides: Overrides (str). Optional parameter.  Specify additional settings that can influence the behavior of the solver when finding solutions for the network analysis problems.
             The value for this parameter needs to be specified in JavaScript Object Notation (JSON). For example, a valid value is of the following form {"overrideSetting1" : "value1", "overrideSetting2" : "value2"}. The override setting name is always enclosed in double quotation marks. The values can be a number, Boolean, or a string. The default value for this parameter is no
            value, which indicates not to override any solver
            settings. Overrides are advanced settings that should be
            used only after careful analysis of the results obtained before and
            after applying the settings. A list of supported override settings
            for each solver and their acceptable values can be obtained by
            contacting Esri Technical Support.

           save_route_data: Save Route Data (bool). Optional parameter.  Choose whether the output includes a zip file
            that contains a file geodatabase holding the inputs and outputs of
            the analysis in a format that can be used to share route layers
            with ArcGIS Online or Portal for ArcGIS.Checked (True)-Save the route data as a zip file. The file is downloaded in a temporary directory on your machine. In ArcGIS Pro, the location of the downloaded file can be determined by viewing the value for the Output Route Data parameter in the entry corresponding to the tool execution in the Geoprocessing history of your Project. In ArcMap, the location of the file can be determined by accessing the Copy Location option in the shortcut menu on the Output Route Data  parameter in the entry corresponding to the tool execution in the Geoprocessing Results window.   Unchecked (False)-Do not save the route data. This is the default.

           time_impedance: Time Impedance (str). Optional parameter.  Specify the time-based impedance, which is a value that represents the travel time along road segments or on other parts of the transportation network.If the impedance for the travel mode, as specified using the impedance parameter, is time-based, the value for time_impedance and impedance parameters should be identical. Otherwise the service will return an error.
                  Choice list:['Minutes', 'TravelTime', 'TimeAt1KPH', 'WalkTime', 'TruckMinutes', 'TruckTravelTime']

           distance_impedance: Distance Impedance (str). Optional parameter.  Specify the distance-based impedance, which is a value that represents the travel distance along road segments or on other parts of the transportation network.If the impedance for the travel mode, as specified using the impedance parameter, is distance-based, the value for distance_impedance and impedance parameters should be identical. Otherwise the service will return an error.
                  Choice list:['Miles', 'Kilometers']

           output_format: Output Format (str). Optional parameter.  Specify the format in which the output features are created.
            Choose from the following formats:Feature Set: The output features are returned as feature classes and tables. This is the default. JSON File: The output features are returned as a compressed file containing the JSON representation of the outputs. When this option is specified, the output is a single file (with a .zip extension) that contains one or more JSON files (with a .json extension) for each of the outputs created by the service. GeoJSON File: The output features are returned as a compressed file containing the GeoJSON representation of the outputs. When this option is specified, the output is a single file (with a .zip extension) that contains one or more GeoJSON files (with a .geojson extension) for each of the outputs created by the service.When a file based output format, such as JSON File or GeoJSON File, is specified,  no outputs are added to the display since the applications like ArcMap or ArcGIS Pro  do not know how to draw the contents of the result file. Instead, the result file is downloaded in a temporary directory on your machine. In ArcGIS Pro, the location of the downloaded file can be determined by viewing the value for the Output Result File parameter in the entry corresponding to the tool execution in the Geoprocessing history of your Project. In ArcMap, the location of the file can be determined by accessing the Copy Location option in the shortcut menu on the Output Result File  parameter in the entry corresponding to the tool execution in the Geoprocessing Results window.
                  Choice list:['Feature Set', 'JSON File']

           gis: Optional, the GIS on which this tool runs. If not specified, the active GIS is used.


           future: Optional, If True, a future object will be returns and the process will not wait for the task to complete. The default is False, which means wait for results.


           Returns the following as a named tuple:
               solve_succeeded - Solve Succeeded as a bool
               output_routes - Output Routes as a FeatureSet
               output_route_edges - Output Route Edges as a FeatureSet
               output_directions - Output Directions as a FeatureSet
               output_stops - Output Stops as a FeatureSet
               output_network_analysis_layer - Output Network Analysis Layer as a DataFile
               output_route_data - Output Route Data as a DataFile
               output_result_file - Output Result File as a DataFile
    """



    if gis is None:
        gis = arcgis.env.active_gis
    url = gis.properties.helperServices.asyncRoute.url
    tbx = import_toolbox(url, gis=gis)
    defaults = dict(zip(tbx.find_routes.__annotations__.keys(),
                        tbx.find_routes.__defaults__))
    if stops is None:
        stops = default_stops

    if point_barriers is None:
        point_barriers = defaults['point_barriers']

    if line_barriers is None:
        line_barriers = defaults['line_barriers']

    if polygon_barriers is None:
        polygon_barriers = defaults['polygon_barriers']

    if restrictions is None:
        restrictions = defaults['restrictions']

    if attribute_parameter_values is None:
        attribute_parameter_values = defaults['attribute_parameter_values']

    if route_line_simplification_tolerance is None:
        route_line_simplification_tolerance = defaults['route_line_simplification_tolerance']


    job = tbx.find_routes(stops=stops,
                          measurement_units=measurement_units,
                          analysis_region=analysis_region,
                          reorder_stops_to_find_optimal_routes=reorder_stops_to_find_optimal_routes,
                          preserve_terminal_stops=preserve_terminal_stops,
                          return_to_start=return_to_start,
                          use_time_windows=use_time_windows,
                          time_of_day=time_of_day,
                          time_zone_for_time_of_day=time_zone_for_time_of_day,
                          uturn_at_junctions=uturn_at_junctions,
                          point_barriers=point_barriers,
                          line_barriers=line_barriers,
                          polygon_barriers=polygon_barriers,
                          use_hierarchy=use_hierarchy,
                          restrictions=restrictions,
                          attribute_parameter_values=attribute_parameter_values,
                          route_shape=route_shape,
                          route_line_simplification_tolerance=route_line_simplification_tolerance,
                          populate_route_edges=populate_route_edges,
                          populate_directions=populate_directions,
                          directions_language=directions_language,
                          directions_distance_units=directions_distance_units,
                          directions_style_name=directions_style_name,
                          travel_mode=travel_mode,
                          impedance=impedance,
                          time_zone_for_time_windows=time_zone_for_time_windows,
                          save_output_network_analysis_layer=save_output_na_layer,
                          overrides=overrides,
                          save_route_data=save_route_data,
                          time_impedance=time_impedance,
                          distance_impedance=distance_impedance,
                          output_format=output_format,
                          gis=gis,
                          future=True)
    if future:
        return job
    res = job.result()
    return res

find_routes.__annotations__ = {
    'stops': FeatureSet,
    'measurement_units': str,
    'analysis_region': str,
    'reorder_stops_to_find_optimal_routes': bool,
    'preserve_terminal_stops': str,
    'return_to_start': bool,
    'use_time_windows': bool,
    'time_of_day': datetime,
    'time_zone_for_time_of_day': str,
    'uturn_at_junctions': str,
    'point_barriers': FeatureSet,
    'line_barriers': FeatureSet,
    'polygon_barriers': FeatureSet,
    'use_hierarchy': bool,
    'restrictions': str,
    'attribute_parameter_values': FeatureSet,
    'route_shape': str,
    'route_line_simplification_tolerance': LinearUnit,
    'populate_route_edges': bool,
    'populate_directions': bool,
    'directions_language': str,
    'directions_distance_units': str,
    'directions_style_name': str,
    'travel_mode': str,
    'impedance': str,
    'return': tuple}
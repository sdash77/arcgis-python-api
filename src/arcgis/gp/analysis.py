import os
import sys
import uuid
import arcpy
from arcgis.features import SpatialDataFrame
import pandas as pd

from arcgis.arctools._base import _process_kwargs, _process_results


#--------------------------------------------------------------------------
def buffer(features=None, output_name=None, buffer_distance_or_field=None, line_side=None, line_end_type=None, dissolve_option=None, dissolve_field=None, method=None):
    '''Buffer_analysis(features, output_name, buffer_distance_or_field, {line_side}, {line_end_type}, {dissolve_option}, {dissolve_field;dissolve_field...}, {method})

        Creates buffer polygons around input features to a specified distance.

     INPUTS:
      features (Feature Layer):
          The input point, line, or polygon features to be buffered.
      buffer_distance_or_field (Linear Unit / Field):
          The distance around the input features that will be buffered.
          Distances can be provided as either a value representing a linear
          distance or as a field from the input features that contains the
          distance to buffer each feature.If linear units are not specified or
          are entered as Unknown, the
          linear unit of the input features' spatial reference is used.When
          specifying a distance, if the desired linear unit has two words,
          such as Decimal Degrees, combine the two words into one (for example,
          20 DecimalDegrees).
      line_side {String}:
          The sides of the input features that will be buffered.

          * FULL-For line input features, buffers will be generated on both
          sides of the line. For polygon input features, buffers will be
          generated around the polygon and will contain and overlap the area of
          the input features. For point input features, buffers will be
          generated around the point. This is the default.

          * LEFT-For line input features, buffers will be generated on the
          topological left of the line. This option is not valid for polygon
          input features.

          * RIGHT-For line input features, buffers will be generated on the
          topological right of the line. This option is not valid for polygon
          input features.

          * OUTSIDE_ONLY-For polygon input features, buffers will be generated
          only outside the input polygon (the area inside the input polygon will
          be erased from the output buffer). This option is not valid for line
          input features.
          This optional parameter is not available with a Desktop Basic or
          Desktop Standard license.
      line_end_type {String}:
          The shape of the buffer at the end of line input features. This
          parameter is not valid for polygon input features.

          * ROUND-The ends of the buffer will be round, in the shape of a half
          circle. This is the default.

          * FLAT-The ends of the buffer will be flat, or squared, and will end
          at the endpoint of the input line feature.
          This optional parameter is not available with a Desktop Basic or
          Desktop Standard license.
      dissolve_option {String}:
          Specifies the dissolve to be performed to remove buffer overlap.

          * NONE-An individual buffer for each feature is maintained, regardless
          of overlap. This is the default.

          * ALL-All buffers are dissolved together into a single feature,
          removing any overlap.

          * LIST-Any buffers sharing attribute values in the listed fields
          (carried over from the input features) are dissolved.
      dissolve_field {Field}:
          The list of fields from the input features on which to dissolve the
          output buffers. Any buffers sharing attribute values in the listed
          fields (carried over from the input features) are dissolved.
      method {String}:
          Specifies what method to use, planar or geodesic, to create the
          buffer.

          * PLANAR-If the input features are in a projected coordinate system,
          Euclidean buffers are created. If the input features are in a
          geographic coordinate system and the buffer distance is in linear
          units (meters, feet, and so forth, as opposed to angular units such as
          degrees), geodesic buffers are created. This is the default. You can
          use the Output Coordinate System environment setting to specify the
          coordinate system to use. For example, if your input features are in a
          projected coordinate system, you can set the environment to a
          geographic coordinate system in order to create geodesic buffers.

          * GEODESIC-All buffers are created using a shape-preserving geodesic
          buffer method, regardless of input coordinate system.

     OUTPUTS:
      output_name (Feature Class):
          The feature class containing the output buffers.'''
    kwargs = locals()
    argdb = {'buffer_distance_or_field': 'buffer_distance_or_field',
             'out_feature_class': 'output_name', 'dissolve_field': 'dissolve_field',
             'method': 'method', 'dissolve_option': 'dissolve_option',
             'in_features': 'features', 'line_end_type': 'line_end_type',
             'line_side': 'line_side'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Buffer(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def clip(features=None, clip_features=None, output_name=None, cluster_tolerance=None):
    '''Clip_analysis(features, clip_features, output_name, {cluster_tolerance})

        Extracts input features that overlay the clip features.Use this tool
        to cut out a piece of one feature class using one or
        more of the features in another feature class as a cookie cutter. This
        is particularly useful for creating a new feature class-also referred
        to as study area or area of interest (AOI)-that contains a geographic
        subset of the features in another, larger feature class.

     INPUTS:
      features (Feature Layer):
          The features to be clipped.
      clip_features (Feature Layer):
          The features used to clip the input features.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates as well as the
          distance a coordinate can move in X or Y (or both). Set the value to
          be higher for data with less coordinate accuracy and lower for data
          with extremely high accuracy.

     OUTPUTS:
      output_name (Feature Class):
          The feature class to be created.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'out_feature_class': 'output_name', 'cluster_tolerance': 'cluster_tolerance', 'clip_features': 'clip_features'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Clip(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def create_thiessen_polygons(features=None, output_name=None, fields_to_copy=None):
    '''CreateThiessenPolygons_analysis(features, output_name, {fields_to_copy})

        Creates Thiessen polygons from point features.Each Thiessen polygon
        contains only a single point input feature. Any
        location within a Thiessen polygon is closer to its associated point
        than to any other point input feature.

     INPUTS:
      features (Feature Layer):
          The point input features from which Thiessen polygons will be
          generated.
      fields_to_copy {String}:
          Determines which fields from the input features will be transferred to
          the output feature class.

          * ONLY_FID-Only the FID field from the input features will be
          transferred to the output feature class. This is the default.

          * ALL-All fields from the input features will be transferred to the
          output feature class.

     OUTPUTS:
      output_name (Feature Class):
          The output feature class containing the Thiessen polygons that are
          generated from the point input features.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'out_feature_class': 'output_name', 'fields_to_copy': 'fields_to_copy'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.CreateThiessenPolygons(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def enrich_layer(features=None, output_name=None, country=None, data_collection=None, variables=None, buffer_type=None, distance=None, unit=None):
    '''EnrichLayer_analysis(features, output_name, country, data_collection, {variables;variables...}, {buffer_type}, {distance}, {unit})

        Enriches your data by adding demographic and landscape facts about
        the people and places that surround or are inside your data locations.
        The output is a duplicate of your input with new attribute fields
        added to the table. This tool requires an ArcGIS Online organizational
        account and consumes credits.

     INPUTS:
      features (Feature Layer):
          The features to enrich with new data.
      country (String):
          The country whose data collections and variables are used to enrich
          the input. You can use the Global country code to obtain enriched data
          from anywhere in the world. Global can also be used when you have
          input features that are in more than one country.You can specify the
          value that is used in the tool dialog box, such as
          Canada (CA), or you can use the two-character country code, such as
          CA.
      data_collection (String):
          The collection of data used to enrich the input. You can specify a
          data collection without selecting any variables to enrich your data
          with all variables included in that collection. The Global country
          code only includes one data collection, KeyGlobalFacts.You can use a
          value such as Health & Personal Care
          (HealthPersonalCare), or you can use the collection name
          HealthPersonalCare. See the Esri Demographics site for more
          information on data collections and their variables.
      variables {String}:
          The specific variables used to enrich the input. Variables can be
          from one or multiple data collections.Variables should be entered in a
          Python list. You can use a value such
          as 2013 Total$: Health care (HealthPersonalCare.THS148), or you can
          use the collection name and variable name HealthPersonalCare.THS148.
          See the Esri Demographics site for more information on data
          collections and their variables.
      buffer_type {String}:
          If the input features are points, you must define an area around them
          to enrich from one of the following seven types. If the input features
          are lines, Straight line (Euclidean distance) is the only valid
          option.

          * STRAIGHT_LINE-Straight-line or Euclidean distance is used as the
          distance measure.

          * DRIVE_TIME-Driving time is used as the distance measure. Current
          posted speed limits, one-way streets, and turn restrictions affect
          driving time.

          * DRIVING_DISTANCE-Driving distance is used as the distance measure.
          One-way streets and turn restrictions affect driving distance.

          * TRUCKING_TIME-Trucking time is used as the distance measure. Current
          posted speed limits, one-way streets, and turn restrictions affect
          trucking time. This option is similar to Driving time, but travel can
          only occur on roads that are suitable for trucks.

          * TRUCKING_DISTANCE-Trucking distance is used as the distance measure.
          One-way streets and turn restrictions affect trucking distance. This
          option is similar to Driving distance, but travel can only occur on
          roads that are suitable for trucks.

          * WALKING_TIME-Walking time is used as the distance measure.
          Measurements are made using a walking speed of 5 KPH (3.1 MPH). Travel
          is allowed where pedestrians are allowed, such as trails, but not on
          limited-access highways.

          * WALKING_DISTANCE-Walking distance is used as the distance measure.
          Travel is allowed where pedestrians are allowed, such as trails, but
          not on limited-access highways.
      distance {Double}:
          The value that determines the straight-line distance or drive time
          around the input features for areas to enrich. The unit of the
          distance or time should be supplied in the unit parameter.
      unit {String}:
          The unit for Distance or time.

          * MILES

          * YARDS

          * FEET

          * KILOMETERS

          * METERS

          * HOURS

          * MINUTES

          * SECONDS

     OUTPUTS:
      output_name (Feature Class):
          The output feature class, which is a copy of the input features with
          new attribute fields added.'''
    kwargs = locals()
    argdb = {'variables': 'variables', 'out_feature_class': 'output_name', 'country': 'country', 'data_collection': 'data_collection', 'unit': 'unit', 'in_features': 'features', 'buffer_type': 'buffer_type', 'distance': 'distance'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.EnrichLayer(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def erase(features=None, erase_features=None, output_name=None, cluster_tolerance=None):
    '''Erase_analysis(features, erase_features, output_name, {cluster_tolerance})

        Creates a feature class by overlaying the input features with the
        polygons of the erase features. Only those portions of the input
        features falling outside the erase features outside boundaries are
        copied to the output feature class.

     INPUTS:
      features (Feature Layer):
          The input feature class or layer.
      erase_features (Feature Layer):
          The features to be used to erase coincident features in the input.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates (nodes and
          vertices) as well as the distance a coordinate can move in X or Y (or
          both).

     OUTPUTS:
      output_name (Feature Class):
          The feature class that will contain only those Input Features that are
          not coincident with the Erase Features.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'erase_features': 'erase_features', 'cluster_tolerance': 'cluster_tolerance', 'out_feature_class': 'output_name'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Erase(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def frequency(table=None, out_table=None, frequency_fields=None, summary_fields=None):
    '''Frequency_analysis(table, out_table, frequency_fields;frequency_fields..., {summary_fields;summary_fields...})

        Reads a table and a set of fields and creates a new table containing
        unique field values and the number of occurrences of each unique field
        value.

     INPUTS:
      table (Table View / Raster Layer):
          The table containing the field(s) that will be used to calculate
          frequency statistics. This table can be an INFO or OLE DB table, a
          dBASE or a VPF table, or a             feature class table.
      frequency_fields (Field):
          The attribute field or fields that will be used to calculate frequency
          statistics.
      summary_fields {Field}:
          The attribute field or fields to sum and add to the output table. Null
          values are excluded from this calculation.

     OUTPUTS:
      out_table (Table):
          The table that will store the calculated frequency statistics.'''
    kwargs = locals()
    argdb = {'in_table': 'table', 'out_table': 'out_table', 'frequency_fields': 'frequency_fields', 'summary_fields': 'summary_fields'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Frequency(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def generate_near_table(features=None, near_features=None, out_table=None, search_radius=None, location=None, angle=None, closest=None, closest_count=None, method=None):
    '''GenerateNearTable_analysis(features, near_features;near_features..., out_table, {search_radius}, {location}, {angle}, {closest}, {closest_count}, {method})

        Calculates distances and other proximity information between features
        in one or more feature class or layer. Unlike the Near tool, which
        modifies the input, Generate Near Table writes results to a new stand-
        alone table and supports finding more than one near feature.

     INPUTS:
      features (Feature Layer):
          The input features that can be point, polyline, polygon, or multipoint
          type.
      near_features (Feature Layer):
          One or more layer of feature class containing near feature candidates.
          The near features can be of point, polyline, polygon, or multipoint.
          If multiple layers or feature classes is specified, a field named
          NEAR_FC is added to the input table and will store the paths of the
          source feature class containing the nearest feature found. The same
          feature class or layer may be used as both input and near features.
      search_radius {Linear Unit}:
          The radius used to search for near features. If no value is specified,
          all near features will be candidates. If a distance is entered, but
          the unit is left blank or set to Unknown, the units of the coordinate
          system of the input features are used. If the Geodesic option is used
          in the Method parameter, a linear unit such as Kilometers or Miles
          should be used.
      location {Boolean}:
          Specifies whether x- and y-coordinates of the input feature's location
          and nearest location of the near feature will be written to the
          FROM_X, FROM_Y, NEAR_X, and NEAR_Y fields.

          * NO_LOCATION-Locations will not be written to the output table. This
          is the default.

          * LOCATION-Locations will be written to the output table.
      angle {Boolean}:
          Specifies whether the near angle will be calculated and written to a
          NEAR_ANGLE field in the output table. A near angle measures direction
          of the line connecting an input feature to its nearest feature at
          their closest locations. When the PLANAR method is used in the method
          parameter, the angle is within the range of -180° to 180°, with 0° to
          the east, 90° to the north, 180° (or -180°) to the west, and -90° to
          the south. When the GEODESIC method is used, the angle is within the
          range of -180° to 180°, with 0° to the north, 90° to the east, 180°
          (or -180°) to the south, and -90° to the west.

          * NO_ANGLE-NEAR_ANGLE will not be added to the output table. This is
          the default.

          * ANGLE-NEAR_ANGLE will be added to the output table.
      closest {Boolean}:
          Specifies whether to return only the closest features or multiple
          features.

          * CLOSEST-Only the closest near feature will be written to the output
          table. This is the default.

          * ALL-Multiple near features will be written to the output table (a
          limit can be specified in the closest_count parameter).
      closest_count {Long}:
          Limit the number of near features reported for each input feature.
          This parameter is ignored if the closest parameter is set to CLOSEST.
      method {String}:
          Determines whether to use a shortest path on a spheroid (geodesic) or
          a flat earth (planar). It is strongly suggested to use Geodesic method
          with data stored in a coordinate system which is not appropriate for
          distance measurements (for example, Web Mercator and any geographic
          coordinate system), or any dataset which spans a large geographic
          area.

          * PLANAR-Uses planar distances between the features. This is the
          default.

          * GEODESIC-Uses geodesic distances between features. This method takes
          into account the curvature of the spheroid and correctly deals with
          data near the dateline and poles.

     OUTPUTS:
      out_table (Table):
          The output table containing the result of the analysis.'''
    kwargs = locals()
    argdb = {'near_features': 'near_features', 'closest': 'closest', 'location': 'location', 'out_table': 'out_table', 'in_features': 'features', 'search_radius': 'search_radius', 'closest_count': 'closest_count', 'angle': 'angle', 'method': 'method'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.GenerateNearTable(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def graphic_buffer(features=None, output_name=None, buffer_distance_or_field=None, line_caps=None, line_joins=None, miter_limit=None, max_deviation=None):
    '''GraphicBuffer_analysis(features, output_name, buffer_distance_or_field, {line_caps}, {line_joins}, {miter_limit}, {max_deviation})

        Creates buffer polygons around input features to a specified distance.
        A number of cartographic shapes are available for buffer ends (caps)
        and corners (joins) when the buffer is generated around the feature.

     INPUTS:
      features (Feature Layer):
          The input point, line, or polygon features to be buffered.
      buffer_distance_or_field (Linear Unit / Field):
          The distance around the input features that will be buffered.
          Distances can be provided as either a value representing a linear
          distance or as a field from the input features that contains the
          distance to buffer each feature.If linear units are not specified or
          are entered as Unknown, the
          linear unit of the input features' spatial reference is used.When
          specifying a distance, if the desired linear unit has two words,
          such as Decimal Degrees, combine the two words into one (for example,
          20 DecimalDegrees).
      line_caps {String}:
          The caps (ends) of the input features that will be buffered. This
          parameter is only supported for point and polygon features.

          * SQUARE-A square end around the end of a segment. This is the
          default.

          * BUTT-End of the buffer of a segment would be perpendicular to the
          segment.

          * ROUND-End of the buffer is round around the end of the segment.
      line_joins {String}:
          The shape of the buffer at corners where two segments join. This
          parameter is only supported for line and polygon features.

          * MITER-Square or sharp shape around corners. For example, a square
          input polygon feature will have a square buffer feature. This is the
          default.

          * BEVEL-Inner corners will be squared while the outer corner will be
          chopped off perpendicular to the furthest point of the corner.

          * ROUND-Inner corners will be squared while the outer corner will be
          round.
      miter_limit {Double}:
          Where line segments meet at a sharp angle and a line_joins of MITER
          has been specified, this parameter can be used to control how sharp
          corners in buffer output come to a point. In some cases, the outer
          angle where two lines join is quite large when using the MITER
          line_joins. This could cause the point of the corner to extend further
          than you want.
      max_deviation {Linear Unit}:
          The maximum distance the output buffer polygon boundary will deviate
          from the true ideal buffer boundary. The true buffer boundary is a
          curve and the output polygon boundary is a densified polyline. With
          this parameter you can control how well the output polygon boundary
          approximates the true buffer boundary.If the parameter is not set, or
          is set to 0, the tool will determine
          the maximum deviation for you. The default is strongly recommended.
          Severe performance degradation, in the tool itself or in subsequent
          analysis, could result from using a maximum offset deviation that is
          too small.See the max_deviation parameter information contained in the
          Densify
          tool documentation for more details.

     OUTPUTS:
      output_name (Feature Class):
          The feature class containing the output buffers.'''
    kwargs = locals()
    argdb = {'buffer_distance_or_field': 'buffer_distance_or_field', 'line_caps': 'line_caps', 'out_feature_class': 'output_name', 'max_deviation': 'max_deviation', 'line_joins': 'line_joins', 'miter_limit': 'miter_limit', 'in_features': 'features'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.GraphicBuffer(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def identity(features=None, identity_features=None, output_name=None, joattributes=None, cluster_tolerance=None, relationship=None):
    '''Identity_analysis(features, identity_features, output_name, {joattributes}, {cluster_tolerance}, {relationship})

        Computes a geometric intersection of the input features and identity
        features. The input features or portions thereof that overlap identity
        features will get the attributes of those identity features.

     INPUTS:
      features (Feature Layer):
          The input feature class or layer.
      identity_features (Feature Layer):
          The identity feature class or layer. Must be polygons or the same
          geometry type as the input features.
      joattributes {String}:
          Determines what attributes will be transferred to the output feature
          class.

          * ALL-All the attributes (including FIDs) from the input features, as
          well as the identity features, will be transferred to the output
          features. If no intersection is found the identity feature values will
          not be transferred to the output (their values will be set to empty
          strings or 0) and the identity feature FID will be -1. This is the
          default.

          * NO_FID-All the attributes except the FID from the input features and
          identity features will be transferred to the output features. If no
          intersection is found the identity feature values will not be
          transferred to the output (their values will be set to empty strings
          or 0).

          * ONLY_FID-All the attributes from the input features but only the FID
          from the identity features will be transferred to the output features.
          The identity features FID attribute value in the output will be -1 if
          no intersection is found.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates (nodes and
          vertices) as well as the distance a coordinate can move in X or Y (or
          both).
      relationship {Boolean}:
          Determines if additional spatial relationships between the features
          and the identity_features are to be written to the output. This only
          applies when the features are lines and the identity_features are
          polygons.

          * NO_RELATIONSHIPS-No additional spatial relationship will be
          determined.

          * KEEP_RELATIONSHIPS-The output line features will contain two
          additional fields, LEFT_poly and RIGHT_poly. These fields contain the
          feature ID of the identity_features on the left and right side of the
          line feature.

     OUTPUTS:
      output_name (Feature Class):
          The feature class that will be created and to which the results will
          be written.'''
    kwargs = locals()
    argdb = {'out_feature_class': 'output_name', 'identity_features': 'identity_features', 'relationship': 'relationship', 'in_features': 'features', 'cluster_tolerance': 'cluster_tolerance', 'join_attributes': 'joattributes'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Identity(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def intersect(features=None, output_name=None, joattributes=None, cluster_tolerance=None, output_type=None):
    '''Intersect_analysis(features;features..., output_name, {joattributes}, {cluster_tolerance}, {output_type})

        Computes a geometric intersection of the input features. Features or
        portions of features which overlap in all layers and/or feature
        classes will be written to the output feature class.

     INPUTS:
      features (Value Table):
          A list of the input feature classes or layers. When the distance
          between features is less than the cluster tolerance, the features with
          the lower rank will snap to the feature with the higher rank. The
          highest rank is one. For more information, see Priority ranks and
          geoprocessing tools.
      joattributes {String}:
          Determines which attributes from the input features will be
          transferred to the output feature class.

          * ALL-All the attributes from the input features will be transferred
          to the output feature class. This is the default.

          * NO_FID-All the attributes except the FID from the input features
          will be transferred to the output feature class.

          * ONLY_FID-Only the FID field from the input features will be
          transferred to the output feature class.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates (nodes and
          vertices) as well as the distance a coordinate can move in X or Y (or
          both).
      output_type {String}:
          Choose what type of intersection you want to find.

          * INPUT-The intersections returned will be the same geometry type as
          the input features with the lowest dimension geometry. If all inputs
          are polygons, the output feature class will contain polygons. If one
          or more of the inputs are lines and none of the inputs are points, the
          output will be line. If one or more of the inputs are points, the
          output feature class will contain points. This is the default.

          * LINE-Line intersections will be returned. This is only valid if none
          of the inputs are points.

          * POINT-Point intersections will be returned. If the inputs are line
          or polygon, the output will be a multipoint feature class.

     OUTPUTS:
      output_name (Feature Class):
          The output feature class.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'out_feature_class': 'output_name', 'output_type': 'output_type', 'cluster_tolerance': 'cluster_tolerance', 'join_attributes': 'joattributes'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Intersect(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def multiple_ring_buffer(Input_Features=None, Output_Feature_class=None, Distances=None, Buffer_Unit=None, Field_Name=None, Dissolve_Option=None, Outside_Polygons_Only=None):
    '''MultipleRingBuffer_analysis(Input_Features, Output_Feature_class, Distances;Distances..., {Buffer_Unit}, {Field_Name}, {Dissolve_Option}, {Outside_Polygons_Only})

        Creates multiple buffers at specified distances around the input
        features. These buffers can optionally be merged and dissolved using
        the buffer distance values to create non-overlapping buffers.

     INPUTS:
      Input_Features (Feature Layer):
          The input point, line, or polygon features to be buffered.
      Distances (Double):
          The list of buffer distances.
      Buffer_Unit {String}:
          The linear unit to be used with the distance values. If the units are
          not specified, or Default is used, the linear unit of the input
          features' spatial reference is used. If Default is used and the Output
          Coordinate System geoprocessing environment has been set, the linear
          unit of the environment will be used.

          * Default

          * Inches

          * Feet

          * Yards

          * Miles

          * NauticalMiles

          * Millimeters

          * Centimeters

          * Decimeters

          * Meters

          * Kilometers

          * DecimalDegrees

          * Points
      Field_Name {String}:
          The name of the field in the output feature class that stores the
          buffer distance used to create each buffer feature. If no name is
          specified, the default field name is 'distance'. This field will be of
          type Double.
      Dissolve_Option {String}:
          Determines if buffers will be dissolved to resemble rings around the
          input features.

          * ALL-Buffers will be rings around the input features that do not
          overlap (think of these as rings or donuts around the input features).
          The smallest buffer will cover the area of its input feature plus the
          buffer distance, and subsequent buffers will be rings around the
          smallest buffer which do not cover the area of the input feature or
          smaller buffers. All buffers of the same distance will be dissolved
          into a single feature. This is the default.

          * NONE-All buffer areas will be maintained regardless of overlap. Each
          buffer will cover its input feature plus the area of any smaller
          buffers.
      Outside_Polygons_Only {Boolean}:
          Valid only for polygon input features.

          * FULL-Buffers will overlap or cover the input features. This is the
          default.

          * OUTSIDE_ONLY-Buffers will be rings around the input features, and
          will not overlap or cover the input features (the area inside the
          input polygon will be erased from the buffer).

     OUTPUTS:
      Output_Feature_class (Feature Class):
          The output feature class that will contain multiple buffers.'''
    kwargs = locals()
    argdb = {'Distances': 'Distances', 'Buffer_Unit': 'Buffer_Unit', 'Dissolve_Option': 'Dissolve_Option', 'Output_Feature_class': 'Output_Feature_class', 'Outside_Polygons_Only': 'Outside_Polygons_Only', 'Input_Features': 'Input_Features', 'Field_Name': 'Field_Name'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.MultipleRingBuffer(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def near(features=None, near_features=None, search_radius=None, location=None, angle=None, method=None):
    '''Near_analysis(features, near_features;near_features..., {search_radius}, {location}, {angle}, {method})

        Calculates distance and additional proximity information between the
        input features and the closest feature in another layer or feature
        class.

     INPUTS:
      features (Feature Layer):
          The input features that can be point, polyline, polygon, or multipoint
          type.
      near_features (Feature Layer):
          One or more feature layers or feature classes containing near feature
          candidates. The near features can be of point, polyline, polygon, or
          multipoint. If multiple layers or feature classes are specified, a
          field named NEAR_FC is added to the input table and will store the
          paths of the source feature class containing the nearest feature
          found. The same feature class or layer may be used as both input and
          near features.
      search_radius {Linear Unit}:
          The radius used to search for near features. If no value is specified,
          all near features are considered. If a distance but no unit or unknown
          is specified, the units of the coordinate system of the input features
          are used. If the Geodesic option is used, a linear unit such as
          Kilometers or Miles should be used.
      location {Boolean}:
          Specifies whether x- and y-coordinates of the closest location of the
          near feature will be written to the NEAR_X and NEAR_Y fields.

          * NO_LOCATION-Location information will not be written to the output
          table. This is the default.

          * LOCATION-Location information will be written to the output table.
      angle {Boolean}:
          Specifies whether the near angle will be calculated and written to a
          NEAR_ANGLE field in the output table. A near angle measures direction
          of the line connecting an input feature to its nearest feature at
          their closest locations. When the PLANAR method is used in the method
          parameter, the angle is within the range of -180° to 180°, with 0° to
          the east, 90° to the north, 180° (or -180°) to the west, and -90° to
          the south. When the GEODESIC method is used, the angle is within the
          range of -180° to 180°, with 0° to the north, 90° to the east, 180°
          (or -180°) to the south, and -90° to the west.

          * NO_ANGLE-The near angle values will not be written. This is the
          default.

          * ANGLE-The near angle values will be written to the NEAR_ANGLE field.
      method {String}:
          Determines whether to use a shortest path on a spheroid (geodesic) or
          a flat earth (planar) method. It is strongly suggested to use the
          Geodesic method with data stored in a coordinate system that is not
          appropriate for distance measurements (for example, Web Mercator or
          any geographic coordinate system) and any analysis that spans a large
          geographic area.

          * PLANAR-Uses planar distances between the features. This is the
          default.

          * GEODESIC-Uses geodesic distances between features. This method takes
          into account the curvature of the spheroid and correctly deals with
          data near the dateline and poles.'''
    kwargs = locals()
    argdb = {'near_features': 'near_features', 'location': 'location', 'search_radius': 'search_radius', 'in_features': 'features', 'method': 'method', 'angle': 'angle'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Near(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def pairwise_buffer(features=None, output_name=None, buffer_distance_or_field=None, dissolve_option=None, dissolve_field=None, method=None, max_deviation=None):
    '''PairwiseBuffer_analysis(features, output_name, buffer_distance_or_field, {dissolve_option}, {dissolve_field;dissolve_field...}, {method}, {max_deviation})

        Creates buffer polygons around input features to a specified distance
        using a parallel processing approach.The Pairwise Buffer tool is very
        similar to the Buffer tool. The
        Pairwise Buffer tool has the ability to process the buffer features in
        parallel.

     INPUTS:
      features (Feature Layer):
          The input point, line, or polygon features to be buffered.
      buffer_distance_or_field (Linear Unit / Field):
          The distance around the input features that will be buffered.
          Distances can be provided as either a value representing a linear
          distance or as a field from the input features that contains the
          distance to buffer each feature.If linear units are not specified or
          are entered as Unknown, the
          linear unit of the input features' spatial reference is used.When
          specifying a distance, if the desired linear unit has two words,
          such as Decimal Degrees, combine the two words into one (for example,
          20 DecimalDegrees).
      dissolve_option {String}:
          The type of dissolve operation to be performed to remove buffer
          overlap.

          * NONE-An individual buffer for each feature is maintained, regardless
          of overlap. This is the default.

          * ALL-All buffers are dissolved together into a single feature,
          removing any overlap.

          * LIST-Any buffers sharing attribute values in the listed fields
          (carried over from the input features) are dissolved.
      dissolve_field {Field}:
          The list of fields from the input features on which to dissolve the
          output buffers. Any buffers sharing attribute values in the listed
          fields (carried over from the input features) are dissolved.
      method {String}:
          Specifies what method to use, planar or geodesic, to create the
          buffer.

          * PLANAR-If the input features are in a projected coordinate system,
          Euclidean buffers are created. If the input features are in a
          geographic coordinate system and the buffer distance is in linear
          units (meters, feet, and so forth, as opposed to angular units such as
          degrees), geodesic buffers are created. This is the default. You can
          use the Output Coordinate System environment setting to specify the
          coordinate system to use. For example, if your input features are in a
          projected coordinate system, you can set the environment to a
          geographic coordinate system in order to create geodesic buffers.

          * GEODESIC-All buffers are created using a shape-preserving geodesic
          buffer method, regardless of input coordinate system.
      max_deviation {Linear Unit}:
          The maximum distance the resulting output buffer polygon boundary will
          deviate from the true buffer boundary.The true buffer boundary is a
          curve. However, the result polygon
          boundary is a densified polyline. With this parameter you can choose
          to control how well the output polygon boundary approximates the true
          buffer boundary.If the parameter is not set, or is set to 0, the tool
          will determine
          the maximum deviation for you. We highly recommend you use the
          default. Severe performance degradation (in the tool itself or in
          subsequent analysis) could result from using a maximum offset
          deviation that is too small.See the max_deviation parameter
          information contained in the Densify
          tool documentation for more details.

     OUTPUTS:
      output_name (Feature Class):
          The feature class containing the output buffers.'''
    kwargs = locals()
    argdb = {'buffer_distance_or_field': 'buffer_distance_or_field', 'out_feature_class': 'output_name', 'method': 'method', 'in_features': 'features', 'max_deviation': 'max_deviation', 'dissolve_field': 'dissolve_field', 'dissolve_option': 'dissolve_option'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.PairwiseBuffer(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def pairwise_dissolve(features=None, output_name=None, dissolve_field=None, statistics_fields=None, multi_part=None):
    '''PairwiseDissolve_analysis(features, output_name, {dissolve_field;dissolve_field...}, {statistics_fields;statistics_fields...}, {multi_part})

        Aggregates features based on specified attributes using a parallel
        processing approach.

     INPUTS:
      features (Feature Layer):
          The features to be aggregated.
      dissolve_field {Field}:
          The field or fields on which to aggregate features.The Add Field
          button, which is used only in ModelBuilder, allows you
          to add expected fields so you can complete the dialog box and continue
          to build your model.
      statistics_fields {Value Table}:
          The fields and statistics with which to summarize attributes. Text
          attribute fields may be summarized using the statistics FIRST or LAST.
          Numeric attribute fields may be summarized using any statistic. Nulls
          are excluded from all statistical calculations.

          * FIRST-Finds the first record in the Input Features and uses its
          specified field value.

          * LAST-Finds the last record in the Input Features and uses its
          specified field value.

          * SUM-Adds the total value for the specified field.

          * MEAN-Calculates the average for the specified field.

          * MIN-Finds the smallest value for all records of the specified field.

          * MAX-Finds the largest value for all records of the specified field.

          * RANGE-Finds the range of values (MAX-MIN) for the specified field.

          * STD-Finds the standard deviation on values in the specified field.

          * COUNT-Finds the number of values included in statistical
          calculations. This counts each value except null values. To determine
          the number of null values in a field, use the COUNT statistic on the
          field in question and a COUNT statistic on a different field that does
          not contain nulls (for example, the OID if present), and subtract the
          two values.
      multi_part {Boolean}:
          Specifies whether multipart features are allowed in the output feature
          class.

          * MULTI_PART-Specifies multipart features are allowed. This is the
          default.

          * SINGLE_PART-Specifies multipart features are not allowed. Instead of
          creating multipart features, individual features will be created for
          each part.

     OUTPUTS:
      output_name (Feature Class):
          The feature class to be created that will contain the aggregated
          features.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'multi_part': 'multi_part', 'out_feature_class': 'output_name', 'dissolve_field': 'dissolve_field', 'statistics_fields': 'statistics_fields'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.PairwiseDissolve(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def pairwise_intersect(features=None, output_name=None, joattributes=None, cluster_tolerance=None, output_type=None):
    '''PairwiseIntersect_analysis(features;features..., output_name, {joattributes}, {cluster_tolerance}, {output_type})

        Computes a pairwise intersection of the input features. Features or
        portions of features that overlap between the input feature layers
        and/or feature classes are written to the output feature class.
        Pairwise intersection refers to selecting one feature from the first
        input and intersecting it with all those features in the second input
        that it overlaps.The Pairwise Intersect tool is similar to the
        Intersect tool in that
        geometric intersections are computed, but it is significantly
        different in that intersections are computed on pairs of features
        rather than all combinations of features.  You may find this tool
        useful in situations where the Intersect tool results in an output
        with many more features than were input (for example, the inputs
        contained tens of thousands of features and the result is tens or
        hundreds of million features).

     INPUTS:
      features (Value Table):
          The input feature classes or layers to intersect. Only two inputs are
          allowed.
      joattributes {String}:
          Determines which attributes from the input features will be
          transferred to the output feature class.

          * ALL-All the attributes from the input features will be transferred
          to the output feature class. This is the default.

          * NO_FID-All the attributes except the FID from the input features
          will be transferred to the output feature class.

          * ONLY_FID-Only the FID field from the input features will be
          transferred to the output feature class.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates (nodes and
          vertices) as well as the distance a coordinate can move in X or Y (or
          both).
      output_type {String}:
          Choose what type of intersection you want to find.

          * INPUT-The intersections returned will be the same geometry type as
          the input features with the lowest dimension geometry. If all inputs
          are polygons, the output feature class will contain polygons. If one
          or more of the inputs are lines and none of the inputs are points, the
          output will be lines. If one or more of the inputs are points, the
          output feature class will contain points. This is the default.

          * LINE-Line intersections will be returned. This is only valid if none
          of the inputs are points.

          * POINT-Point intersections will be returned. If the inputs are line
          or polygon, the output will be a multipoint feature class.

     OUTPUTS:
      output_name (Feature Class):
          The output feature class.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'out_feature_class': 'output_name', 'output_type': 'output_type', 'cluster_tolerance': 'cluster_tolerance', 'join_attributes': 'joattributes'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.PairwiseIntersect(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def point_distance(features=None, near_features=None, out_table=None, search_radius=None):
    '''PointDistance_analysis(features, near_features, out_table, {search_radius})

        Determines the distances from input point features to all points in
        the near features within a specified search radius.This is a
        deprecated tool. This functionality has been replaced by
        Near and Generate Near Table tools that now calculate distances
        between point, polyline and polygon features.

     INPUTS:
      features (Feature Layer):
          The point features from which distances to the near features will be
          calculated.
      near_features (Feature Layer):
          The points to which distances from the input features will be
          calculated. Distances between points within the same feature class or
          layer can be determined by specifying the same feature class or layer
          for the input and near features.
      search_radius {Linear Unit}:
          Specifies the radius used to search for candidate near features. The
          near features within this radius are considered for calculating the
          nearest feature. If no value is specified (that is, the default
          (empty) radius is used) all near features are considered for
          calculation. The unit of search radius defaults to units of the input
          features. The units can be changed to any other unit. However, this
          has no impact on the units of the output DISTANCE field which is based
          on the units of the coordinate system of the input features.

     OUTPUTS:
      out_table (Table):
          The table containing the list of input features and information about
          all near features within the search radius. If a search radius is not
          specified, distances from all input features to all near features are
          calculated.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'near_features': 'near_features', 'out_table': 'out_table', 'search_radius': 'search_radius'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.PointDistance(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def polygon_neighbors(features=None, out_table=None, fields=None, area_overlap=None, both_sides=None, cluster_tolerance=None, out_linear_units=None, out_area_units=None):
    '''PolygonNeighbors_analysis(features, out_table, {fields;fields...}, {area_overlap}, {both_sides}, {cluster_tolerance}, {out_linear_units}, {out_area_units})

        Creates a table with statistics based on polygon contiguity
        (overlaps, coincident edges, or nodes).

     INPUTS:
      features (Feature Layer):
          The input polygon features.
      fields {Field}:
          Input attribute field or fields used to identify unique polygons or
          polygon groups and represent them in the output.
      area_overlap {Boolean}:
          Determines if overlapping polygons will be analyzed and reported in
          the output.

          * NO_AREA_OVERLAP-Overlapping relationships will not be analyzed and
          included in the output. This is the default.

          * AREA_OVERLAP-Overlapping relationships will be analyzed and included
          in the output.
      both_sides {Boolean}:
          Determines if both sides of neighbor relationships will be included in
          the output.

          * BOTH_SIDES-For a pair of neighboring polygons, report both
          neighboring information of one polygon being the source and the other
          being the neighbor and vice versa. This is the default.

          * NO_BOTH_SIDES-For a pair of neighboring polygons, only report
          neighboring information of one polygon being the source and the other
          being the neighbor. Do not include the reciprocal relationship.
      cluster_tolerance {Linear Unit}:
          The minimum distance between coordinates before they are considered
          equal. By default, this is the XY Tolerance of the input features.
      out_linear_units {String}:
          Units used to report the total length of the coincident edge between
          neighboring polygons. The default is the input feature units.

          * UNKNOWN

          * INCHES

          * FEET

          * YARDS

          * MILES

          * NAUTICAL_MILES

          * MILLIMETERS

          * CENTIMETERS

          * DECIMETERS

          * METERS

          * KILOMETERS

          * DECIMAL_DEGREES

          * POINTS
      out_area_units {String}:
          Units used to report the area overlap of neighboring polygons. The
          default is the input feature units. This parameter is only enabled
          when area_overlap = "AREA_OVERLAP".

          * UNKNOWN

          * ARES

          * ACRES

          * HECTARES

          * SQUARE_INCHES

          * SQUARE_FEET

          * SQUARE_YARDS

          * SQUARE_MILES

          * SQUARE_MILLIMETERS

          * SQUARE_CENTIMETERS

          * SQUARE_DECIMETERS

          * SQUARE_METERS

          * SQUARE_KILOMETERS

     OUTPUTS:
      out_table (Table):
          The output table.'''
    kwargs = locals()
    argdb = {'out_linear_units': 'out_linear_units', 'area_overlap': 'area_overlap', 'cluster_tolerance': 'cluster_tolerance', 'out_area_units': 'out_area_units', 'in_fields': 'fields', 'in_features': 'features', 'out_table': 'out_table', 'both_sides': 'both_sides'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.PolygonNeighbors(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def select(features=None, output_name=None, where_clause=None):
    '''Select_analysis(features, output_name, {where_clause})

        Extracts features from an input feature class or input feature layer,
        typically using a select or Structured Query Language (SQL) expression
        and stores them in an output feature class.

     INPUTS:
      features (Feature Layer):
          The input feature class or layer from which features are selected.
      where_clause {SQL Expression}:
          An SQL expression used to select a subset of features. For more
          information on SQL syntax see the help topic SQL reference for
          elements used in query expressions.

     OUTPUTS:
      output_name (Feature Class):
          The output feature class to be created. If no expression is used, it
          contains all input features.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'out_feature_class': 'output_name', 'where_clause': 'where_clause'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Select(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def spatial_join(target_features=None, jofeatures=None, output_name=None, jooperation=None, jotype=None, field_mapping=None, match_option=None, search_radius=None, distance_field_name=None):
    '''SpatialJoanalysis(target_features, jofeatures, output_name, {jooperation}, {jotype}, {field_mapping}, {match_option}, {search_radius}, {distance_field_name})

        Joins attributes from one feature to another based on the spatial
        relationship. The target features and the joined attributes from the
        join features are written to the output feature class.

     INPUTS:
      target_features (Feature Layer):
          Attributes of the target features and the attributes from the joined
          features are transferred to the output feature class. However, a
          subset of attributes can be defined in the field map parameter.
      jofeatures (Feature Layer):
          The attributes from the join features are joined to the attributes of
          the target features. See the explanation of the jooperation
          parameter for details on how the aggregation of joined attributes are
          affected by the type of join operation.
      jooperation {String}:
          Determines how joins between the target features and join features
          will be handled in the output feature class if multiple join features
          are found that have the same spatial relationship with a single target
          feature.

          * JOIN_ONE_TO_ONE-If multiple join features are found that have the
          same spatial relationship with a single target feature, the attributes
          from the multiple join features will be aggregated using a field map
          merge rule. For example, if a point target feature is found within two
          separate polygon join features, the attributes from the two polygons
          will be aggregated before being transferred to the output point
          feature class. If one polygon has an attribute value of 3 and the
          other has a value of 7, and a Sum merge rule is specified, the
          aggregated value in the output feature class will be 10. This is the
          default.

          * JOIN_ONE_TO_MANY-If multiple join features are found that have the
          same spatial relationship with a single target feature, the output
          feature class will contain multiple copies (records) of the target
          feature. For example, if a single point target feature is found within
          two separate polygon join features, the output feature class will
          contain two copies of the target feature: one record with the
          attributes of one polygon, and another record with the attributes of
          the other polygon.
      jotype {Boolean}:
          Determines if all target features will be maintained in the output
          feature class (known as outer join), or only those that have the
          specified spatial relationship with the join features (inner join).

          * KEEP_ALL-All target features will be maintained in the output (outer
          join). This is the default.

          * KEEP_COMMON-Only those target features that have the specified
          spatial relationship with the join features will be maintained in the
          output feature class (inner join). For example, if a point feature
          class is specified for the target features, and a polygon feature
          class is specified for the join features, with match_option =
          "WITHIN", the output feature class will only contain those target
          features that are within a polygon join feature; any target features
          not within a join feature will be excluded from the output.
      field_mapping {Field Mappings}:
          Controls what attribute fields will be in the output feature class.
          The initial list contains all the fields from both the target features
          and the join features. Fields can be added, deleted, renamed, or have
          their properties changed. The selected fields from the target features
          are transferred as is, but selected fields from the join features can
          be aggregated by a merge rule. For details on field mapping, see Using
          the field mapping control and Mapping input fields to output fields.
          Multiple fields and statistic combination may be specified.
      match_option {String}:
          Defines the criteria used to match rows. The match options are:

          * INTERSECT-The features in the join features will be matched if they
          intersect a target feature. This is the default. Specify a distance in
          the search_radius parameter.

          * INTERSECT_3D-The features in the join features will be matched if
          they intersect a target feature in three-dimensional space (x, y, and
          z). Specify a distance in the search_radius parameter.

          * WITHIN_A_DISTANCE-The features in the join features will be matched
          if they are within a specified distance of a target feature. Specify a
          distance in the search_radius parameter.

          * WITHIN_A_DISTANCE_GEODESIC-Same as WITHIN_A_DISTANCE except that
          geodesic distance is used rather than planar distance. Choose this if
          your data covers a large geographic extent or the coordinate system of
          the inputs is unsuitable for distance calculations.

          * WITHIN_A_DISTANCE_3D-The features in the join features will be
          matched if they are within a specified distance of a target feature in
          three-dimensional space. Specify a distance in the search_radius
          parameter.

          * CONTAINS-The features in the join features will be matched if a
          target feature contains them. The target features must be polygons or
          polylines. For this option, the target features cannot be points, and
          the join features can only be polygons when the target features are
          also polygons.

          * COMPLETELY_CONTAINS-The features in the join features will be
          matched if a target feature completely contains them. Polygon can
          completely contain any feature. Point cannot completely contain any
          feature, not even a point. Polyline can completely contain only
          polyline and point.

          * CONTAINS_CLEMENTINI-This spatial relationship yields the same
          results as COMPLETELY_CONTAINS with the exception that if the join
          feature is entirely on the boundary of the target feature (no part is
          properly inside or outside) the feature will not be matched.
          Clementini defines the boundary polygon as the line separating inside
          and outside, the boundary of a line is defined as its end points, and
          the boundary of a point is always empty.

          * WITHIN-The features in the join features will be matched if a target
          feature is within them. It is opposite to CONTAINS. For this option,
          the target features can only be polygons when the join features are
          also polygons. Point can be join feature only if point is target.

          * COMPLETELY_WITHIN-The features in the join features will be matched
          if a target feature is completely within them. This is opposite to
          COMPLETELY_CONTAINS.

          * WITHIN_CLEMENTINI-The result will be identical to WITHIN except if
          the entirety of the feature in the join features is on the boundary of
          the target feature, the feature will not be matched. Clementini
          defines the boundary polygon as the line separating inside and
          outside, the boundary of a line is defined as its end points, and the
          boundary of a point is always empty.

          * ARE_IDENTICAL_TO-The features in the join features will be matched
          if they are identical to a target feature. Both join and target
          feature must be of same shape type-point-to-point, line-to-line, and
          polygon-to-polygon.

          * BOUNDARY_TOUCHES-The features in the join features will be matched
          if they have a boundary that touches a target feature. When the target
          and join features are lines or polygons, the boundary of the join
          feature can only touch the boundary of the target feature and no part
          of the join feature can cross the boundary of the target feature.

          * SHARE_A_LINE_SEGMENT_WITH-The features in the join features will be
          matched if they share a line segment with a target feature. The join
          and target features must be lines or polygons.

          * CROSSED_BY_THE_OUTLINE_OF-The features in the join features will be
          matched if a target feature is crossed by their outline. The join and
          target features must be lines or polygons. If polygons are used for
          the join or target features, the polygon's boundary (line) will be
          used. Lines that cross at a point will be matched, not lines that
          share a line segment.

          * HAVE_THEIR_CENTER_IN-The features in the join features will be
          matched if a target feature's center falls within them. The center of
          the feature is calculated as follows: for polygon and multipoint the
          geometry's centroid is used, and for line input the geometry's
          midpoint is used. Specify a distance in the search_radius parameter.

          * CLOSEST-The feature in the join features that is closest to a target
          feature is matched. See the usage tip for more information. Specify a
          distance in the search_radius parameter.

          * CLOSEST_GEODESIC-Same as CLOSEST except that geodesic distance is
          used rather than planar distance. Choose this if your data covers a
          large geographic extent or the coordinate system of the inputs is
          unsuitable for distance calculations
      search_radius {Linear Unit}:
          Join features within this distance of a target feature will be
          considered for the spatial join. A search radius is only valid when
          the spatial relationship (match_option) INTERSECT, WITHIN_A_DISTANCE,
          WITHIN_A_DISTANCE_GEODESIC, HAVE_THEIR_CENTER_IN, CLOSEST or
          CLOSEST_GEODESIC is specified. Using a search radius of 100 meters
          with the spatial relationship WITHIN_A_DISTANCE will join feature
          within 100 meters of a target feature. For the three WITHIN_A_DISTANCE
          relationships, if no value is specified for search radius then a
          distance of 0 is used.
      distance_field_name {String}:
          The name of a field to be added to the output feature class, which
          contains the distance between the target feature and the closest join
          feature. This option is only valid when the spatial relationship
          (match_option) CLOSEST or CLOSEST_GEODESIC is specified. The value of
          this field is -1 if no feature is matched within a search radius. If
          no field name is specified, the field will not be added to the output
          feature class.

     OUTPUTS:
      output_name (Feature Class):
          A new feature class containing the attributes of the target and join
          features. By default, all attributes of target features and the
          attributes of the joined features are written to the output. However,
          the set of attributes to be transferred can be controlled by the field
          map parameter.'''
    kwargs = locals()
    argdb = {'field_mapping': 'field_mapping', 'match_option': 'match_option', 'out_feature_class': 'output_name', 'target_features': 'target_features', 'distance_field_name': 'distance_field_name', 'join_features': 'jofeatures', 'search_radius': 'search_radius', 'join_type': 'jotype', 'join_operation': 'jooperation'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.SpatialJoin(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def split(features=None, split_features=None, split_field=None, out_workspace=None, cluster_tolerance=None):
    '''Split_analysis(features, split_features, split_field, out_workspace, {cluster_tolerance})

        Splitting the Input Features creates a subset of multiple output
        feature classes.The Split Field's unique values form the names of the
        output feature
        classes. These are saved in the target workspace.

     INPUTS:
      features (Feature Layer):
          The features to be split.
      split_features (Feature Layer):
          Polygon features containing a tabular field whose unique values are
          used to split the input features and provide the output feature
          classes' names.
      split_field (Field):
          The character field used to split the input features. This field's
          values identify the split features used to create each output feature
          class. The split field's unique values provide the output feature
          classes' names.
      out_workspace (Workspace / Feature Dataset):
          The existing workspace where the output feature classes are stored.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates (nodes and
          vertices) as well as the distance a coordinate can move in X or Y (or
          both). Set the value to be higher for data that has less coordinate
          accuracy and lower for datasets with extremely high accuracy.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'split_field': 'split_field', 'cluster_tolerance': 'cluster_tolerance', 'split_features': 'split_features', 'out_workspace': 'out_workspace'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Split(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def split_by_attributes(Input_Table=None, Target_Workspace=None, Split_Fields=None):
    '''SplitByAttributes_analysis(Input_Table, Target_Workspace, Split_Fields;Split_Fields...)

        Splits an input dataset by unique attributes.

     INPUTS:
      Input_Table (Table View):
          The input feature class or table whose data will be split into the
          target workspace.
      Target_Workspace (Workspace):
          The existing workspace where the output feature classes or tables are
          written.
      Split_Fields (Field):
          The fields on which the input will be split into new feature classes
          or tables.'''
    kwargs = locals()
    argdb = {'Input_Table': 'Input_Table', 'Target_Workspace': 'Target_Workspace', 'Split_Fields': 'Split_Fields'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.SplitByAttributes(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def statistics(table=None, out_table=None, statistics_fields=None, case_field=None):
    '''Statistics_analysis(table, out_table, statistics_fields;statistics_fields..., {case_field;case_field...})

        Calculates summary statistics for field(s) in a table.

     INPUTS:
      table (Table View / Raster Layer):
          The input table containing the field(s) that will be used to calculate
          statistics. The input can be an INFO table, a dBASE table, an OLE DB
          table, a VPF table, or a feature class.
      statistics_fields (Value Table):
          The numeric field containing attribute values used to calculate the
          specified statistic. Multiple statistic and field combinations may be
          specified. Null values are excluded from all statistical
          calculations.The Add Field button, which is used only in ModelBuilder,
          allows you
          to add expected field(s) so you can complete the dialog box and
          continue to build your model.Available statistics types are:

          * SUM-Adds the total value for the specified field.

          * MEAN-Calculates the average for the specified field.

          * MIN-Finds the smallest value for all records of the specified field.

          * MAX-Finds the largest value for all records of the specified field.

          * RANGE-Finds the range of values (MAX minus MIN) for the specified
          field.

          * STD-Finds the standard deviation on values in the specified field.

          * COUNT-Finds the number of values included in statistical
          calculations. This counts each value except null values. To determine
          the number of null values in a field, use the COUNT statistic on the
          field in question, and a COUNT statistic on a different field which
          does not contain nulls (for example, the OID if present), then
          subtract the two values.

          * FIRST-Finds the first record in the Input Table and uses its
          specified field value.

          * LAST-Finds the last record in the Input Table and uses its specified
          field value.
      case_field {Field}:
          The fields in the Input Table used to calculate statistics separately
          for each unique attribute value (or combination of attribute values
          when multiple fields are specified).

     OUTPUTS:
      out_table (Table):
          The output dBASE or geodatabase table that will store the calculated
          statistics.'''
    kwargs = locals()
    argdb = {'in_table': 'table', 'case_field': 'case_field', 'out_table': 'out_table', 'statistics_fields': 'statistics_fields'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Statistics(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def summarize_nearby(features=None, sum_features=None, output_name=None, distance_type=None, distances=None, distance_units=None, time_of_day=None, time_zone=None, keep_all_polygons=None, sum_fields=None, sum_shape=None, shape_unit=None, group_field=None, add_mmaj=None, add_group_percent=None, Output_Grouped_Table=None):
    '''SummarizeNearby_analysis(features, sum_features, output_name, distance_type, distances;distances..., distance_units, {time_of_day}, {time_zone}, {keep_all_polygons}, {sum_fields;sum_fields...}, {sum_shape}, {shape_unit}, {group_field}, {add_mmaj}, {add_group_percent}, {Output_Grouped_Table})

        Finds features that are within a specified distance of features in
        the input layer and calculates statistics for the nearby features.
        Distance can be measured as a straight-line distance, a drive-time
        distance (for example, within 10 minutes), or a drive distance (within
        5 kilometers). Drive-time and drive distance measurements require that
        you are logged in to an ArcGIS Online organizational account with
        Network Analysis privileges, and they consume credits.Example
        scenarios using Summarize Nearby:

        * Calculate the total population within 5 minutes of driving time of a
        proposed new store location.

        * Calculate the number of freeway access ramps within a 1-mile driving
        distance of a proposed new store location to use as a measure of store
        accessibility.

     INPUTS:
      features (Feature Layer):
          The point, line, or polygon features that will be buffered and those
          buffers used to summarize the input summary features.
      sum_features (Feature Layer):
          The point, line, or polygon features that will be summarized.
      distance_type (String):
          Defines what kind of distance measurement to use in generating buffer
          areas around the input features. Both driving distance and driving
          time use the road network and honor such restrictions as one-way
          streets. Driving time honors the current posted speed limits.To use
          the drive-time and drive distance measurement options you must
          be logged in to an ArcGIS Online organizational account with Network
          Analysis privileges. Each time the tool runs successfully, service
          credits are debited from your subscription based on the service used
          and the results returned from the service. The ArcGIS Online service
          credits page provides details about service credits.All distance types
          except straight-line distance use ArcGIS Online
          routing and network services.

          * DRIVING_DISTANCE-The distance covered in a car or other similar
          small automobiles, such as pickup trucks. Travel follows all rules
          that are specific to cars.

          * DRIVING_TIME-The distance covered within a specified time in a car
          or other similar small automobiles, such as pickup trucks. Dynamic
          travel speeds based on traffic are used where it is available when you
          specify a time of day. Travel follows all rules that are specific to
          cars.

          * STRAIGHT_LINE-Euclidean or straight-line distance.

          * TRUCKING_DISTANCE-The distance covered along designated truck
          routes. Travel follows all rules for cars as well as rules specific to
          trucking.

          * TRUCKING_TIME-The distance covered within a specified time when
          traveling along designated truck routes. Dynamic travel speeds based
          on traffic are used where it is available when you specify a time of
          day. Travel follows all rules for cars as well as rules specific to
          trucking.

          * WALKING_DISTANCE-The distance covered along paths and roads that
          allow pedestrian traffic.

          * WALKING_TIME-The distance covered within a specified time when
          walking along paths and roads that allow pedestrian traffic.
      distances (Double):
          Distance values define a search distance (for straight-line, driving,
          trucking, or walking distance) or travel time (for driving, trucking,
          or walking time). Features that are within (or equal to) the distances
          you enter will be summarized.Multiple values can be specified. One
          area around each input feature
          will be generated for each distance.
      distance_units (String):
          The units of the distance values.

          * MILES

          * KILOMETERS

          * FEET

          * YARDS

          * METERS

          * HOURS

          * MINUTES

          * SECONDS
      time_of_day {Date}:
          Specify whether travel times should consider traffic conditions.
          Traffic conditions, especially in urbanized areas, can significantly
          impact the area covered within a specified travel time. If no date or
          time is specified, the distance covered during a specified travel time
          will not be impacted by traffic.Traffic conditions may be live or
          typical (historical) based on the
          date and time specified for this parameter. Esri saves live traffic
          data for 12 hours and references predictive data extending 12 hours
          into the future. If the time and date you specify is within the
          24-hour time window, live traffic is used. If it is outside the time
          window, typical or historic traffic is used.
      time_zone {String}:
          The time zone for the specified time of day. Time zones can be
          specified in local time or Coordinated Universal Time (UTC).

          * GEOLOCAL-The time of day refers to the local time zone or zones in
          which the input features are located. This option can cause the
          analysis to have rolling start times across time zones. This is the
          default.For example, setting a geolocal time of day to 9:00 a.m.
          causes the drive times for points in the Eastern Time Zone to start at
          9:00 a.m. Eastern Time, and 9:00 a.m. Central Time for points in the
          Central Time Zone. (The start times are offset by an hour in real or
          UTC time.)

          * UTC-The time of day refers to Coordinated Universal Time (UTC). The
          start times for all points are simultaneous, regardless of time
          zones.For example, setting a UTC time of day to 9:00 a.m. causes the
          drive times for points in the Eastern Time Zone to start at 4:00 a.m.
          Eastern Time, and 3:00 a.m. Central Time for points in the Central
          Time Zone. (The start times are simultaneous.)
      keep_all_polygons {Boolean}:
          Determines if all buffers of the input features or only those
          intersecting or containing at least one input summary feature will be
          copied to the output feature class.

          * KEEP_ALL-All buffers will be copied to the output feature class.
          This is the default.

          * ONLY_INTERSECTING-Only buffers that intersect or contain at least
          one input summary feature will be copied to the output feature class.
      sum_fields {Value Table}:
          A list of attribute field names from the input summary features and
          statistical summary types you want to calculate for those attribute
          fields for all points within each input feature buffer.Summary fields
          must be numeric. Text and other attribute field types
          are not supported.Statistic types include the following:

          * Sum-Adds the total value of all the points in each buffer.

          * Mean-Calculates the average of all the points in each buffer.

          * Min-Finds the smallest value of all the points in each buffer.

          * Max-Finds the largest value of all the points in each buffer.

          * Stddev-Finds the standard deviation of all the points in each
          buffer.
      sum_shape {Boolean}:
          Determines if the output feature class will contain attributes for the
          number of points, length of lines, and area of polygon features
          summarized in each input feature buffer.

          * ADD_SHAPE_SUM-Add shape summary attributes to the output feature
          class. This is the default.

          * NO_SHAPE_SUM-Do not add shape summary attributes to the output
          feature class.
      shape_unit {String}:
          The unit in which to calculate shape summary attributes. If the input
          summary features are points, no shape unit is used, since only the
          count of points within each input feature buffer is added.If the input
          summary features are lines, specify a linear unit. If the
          input summary features are polygons, specify an areal unit.

          * METERS

          * KILOMETERS

          * FEET

          * YARDS

          * MILES

          * ACRES

          * HECTARES

          * SQUAREMETERS

          * SQUAREKILOMETERS

          * SQUAREFEET

          * SQUAREYARDS

          * SQUAREMILES
      group_field {Field}:
          Attribute field from the input summary features used for grouping.
          Features that have the same group field value will be combined and
          summarized with other features with the same group field value.When
          you choose a group field, an additional output grouped table will
          be created and its location must be specified in the out_grouped_table
          parameter.
      add_mmaj {Boolean}:
          This option is only enabled if you have selected a group field. It
          allows you to determine which group field value is the minority (least
          dominant) and the majority (most dominant) within each input feature
          buffer.

          * NO_MIN_MAJ-Do not add minority and majority fields to the output.
          This is the default.

          * ADD_MIN_MAJ-Add minority and majority fields to the output.
      add_group_percent {Boolean}:
          This option is only enabled if you have selected a group field. It
          allows you to determine the percentage of each attribute value within
          each group.

          * NO_PERCENT-Do not add a percentage attribute field to the output.
          This is the default.

          * ADD_PERCENT-Add a percentage attribute field to the output.

     OUTPUTS:
      output_name (Feature Class):
          The output polygon feature class containing the buffered input
          features, the attributes of the input features, and new attributes
          about the number points, length of lines, and area of polygons inside
          each buffer and statistics about those features.
      Output_Grouped_Table {Table}:
          If a group field is specified, the output grouped table is
          required.An output table that includes summary fields for each group
          of summary
          features for each input feature buffer. The table will have the
          following attribute fields:

          * JoID-An ID corresponding to an ID field added to the output
          feature class.

          * The group field.

          * A shape summary field such as count of points or length of lines.

          * One field for each of the summary fields.

          * Percentage field.'''
    kwargs = locals()
    argdb = {'time_of_day': 'time_of_day', 'add_group_percent': 'add_group_percent', 'keep_all_polygons': 'keep_all_polygons', 'Output_Grouped_Table': 'Output_Grouped_Table', 'in_features': 'features', 'sum_fields': 'sum_fields', 'sum_shape': 'sum_shape', 'distance_type': 'distance_type', 'in_sum_features': 'sum_features', 'group_field': 'group_field', 'out_feature_class': 'output_name', 'shape_unit': 'shape_unit', 'add_min_maj': 'add_mmaj', 'distance_units': 'distance_units', 'distances': 'distances', 'time_zone': 'time_zone'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.SummarizeNearby(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def summarize_within(polygons=None, sum_features=None, output_name=None, keep_all_polygons=None, sum_fields=None, sum_shape=None, shape_unit=None, group_field=None, add_mmaj=None, add_group_percent=None, out_group_table=None):
    '''SummarizeWithanalysis(polygons, sum_features, output_name, {keep_all_polygons}, {sum_fields;sum_fields...}, {sum_shape}, {shape_unit}, {group_field}, {add_mmaj}, {add_group_percent}, {out_group_table})

        Overlays a polygon layer with another layer to summarize the number of
        points, length of the lines, or area of the polygons within each
        polygon, and calculate attribute field statistics about those features
        within the polygons.Example scenarios using Summarize Within:

        * Given a layer of watershed boundaries and a layer of land-use
        boundaries by land-use type, calculate total acreage of land-use type
        for each watershed.

        * Given a layer of parcels in a county and a layer of city boundaries,
        summarize the average value of vacant parcels within each city
        boundary.

        * Given a layer of counties and a layer of roads, summarize the total
        mileage of roads by road type within each county.

     INPUTS:
      polygons (Feature Layer):
          The polygons used to summarize the features, or portions of features,
          in the input summary layer.
      sum_features (Feature Layer):
          The point, line, or polygon features that will be summarized for each
          polygon in the input polygons.
      keep_all_polygons {Boolean}:
          Determines if all input polygons or only those containing at least
          one input point will be copied to the output feature class.

          * KEEP_ALL-All input polygons will be copied to the output feature
          class. This is the default.

          * ONLY_INTERSECTING-Only input polygons that intersect or contain at
          least one input summary feature will be copied to the output feature
          class.
      sum_fields {Value Table}:
          A list of attribute field names from the input summary features, and
          statistical summary types that you wish to calculate for those
          attribute fields for all points within each polygon.Summary fields
          must be numeric. Text and other attribute field types
          are not supported.Statistic types include:

          * Sum-Adds the total value of all the points in each polygon.

          * Mean-Calculates the average of all the points in each polygon.

          * Min-Finds the smallest value of all the points in each polygon.

          * Max-Finds the largest value of all the points in each polygon.

          * Stddev-Finds the standard deviation of all the points in each
          polygon.
      sum_shape {Boolean}:
          Determines if the output feature class will contain attributes for the
          number of points, length or lines, and area of polygon features
          summarized in each input polygon.

          * ADD_SHAPE_SUM-Add shape summary attributes to the output feature
          class. This is the default.

          * NO_SHAPE_SUM-Do not add shape summary attributes to the output
          feature class.
      shape_unit {String}:
          The unit in which to calculate shape summary attributes. If the input
          summary features are points no shape unit is necessary, since only the
          count of points within each input polygon is added.If the input
          summary features are lines, specify a linear unit. If the
          input summary features are polygons, specify an areal unit.

          * METERS

          * KILOMETERS

          * FEET

          * YARDS

          * MILES

          * ACRES

          * HECTARES

          * SQUAREMETERS

          * SQUAREKILOMETERS

          * SQUAREFEET

          * SQUAREYARDS

          * SQUAREMILES
      group_field {Field}:
          Attribute field from the input summary features that is used for
          grouping. Features that have the same group field value will be
          combined and summarized with other features with the same group field
          value.When you chose a group field, an additional output grouped table
          will
          be created and its location must be specified in the out_grouped_table
          parameter.
      add_mmaj {Boolean}:
          This option is only enabled if you have selected a group field. It
          allows you to determine which group field value is the minority (least
          dominant) and the majority (most dominant) within each input polygon.

          * NO_MIN_MAJ-Do not add minority and majority fields to the output.
          This is the default.

          * ADD_MIN_MAJ-Add minority and majority fields to the output.
      add_group_percent {Boolean}:
          This option is only enabled if you have selected a group field. It
          allows you to determine the percentage of each attribute value within
          each group.

          * NO_PERCENT-Do not add a percentage attribute field to the output.
          This is the default.

          * ADD_PERCENT-Add a percentage attribute field to the output.

     OUTPUTS:
      output_name (Feature Class):
          The output polygon feature class containing the same geometries and
          attributes as the input polygons with additional new attributes about
          the number points, length of lines, and area of polygons inside each
          input polygon and statistics about those features.
      out_group_table {Table}:
          If a group field is specified, the output grouped table is
          required.An output table that includes summary fields for each group
          of summary
          features for each input polygon. The table will have the following
          attribute fields:

          * JoID-an ID corresponding to an ID field added to the output
          feature class.

          * The group field.

          * A shape summary field.

          * One field for each of the summary fields.

          * Percentage field.'''
    kwargs = locals()
    argdb = {'group_field': 'group_field', 'in_polygons': 'polygons', 'out_feature_class': 'output_name', 'keep_all_polygons': 'keep_all_polygons', 'shape_unit': 'shape_unit', 'add_min_maj': 'add_mmaj', 'out_group_table': 'out_group_table', 'sum_fields': 'sum_fields', 'add_group_percent': 'add_group_percent', 'sum_shape': 'sum_shape', 'in_sum_features': 'sum_features'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.SummarizeWithin(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def sym_diff(features=None, update_features=None, output_name=None, joattributes=None, cluster_tolerance=None):
    '''SymDiff_analysis(features, update_features, output_name, {joattributes}, {cluster_tolerance})

        Features or portions of features in the input and update features
        that do not overlap will be written to the output feature class.

     INPUTS:
      features (Feature Layer):
          The input feature class or layer.
      update_features (Feature Layer):
          The update feature class or layer. Geometry type must be the same
          geometry type as the input feature class or layer.
      joattributes {String}:
          Determines which attributes will be transferred to the output feature
          class.

          * ALL-All the attributes from the input features will be transferred
          to the output feature class. This is the default.

          * NO_FID-All the attributes except the FID from the input features
          will be transferred to the output feature class.

          * ONLY_FID-Only the FID field from the input features will be
          transferred to the output feature class.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates (nodes and
          vertices) as well as the distance a coordinate can move in x or y (or
          both).

     OUTPUTS:
      output_name (Feature Class):
          The feature class to which the results will be written.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'update_features': 'update_features', 'out_feature_class': 'output_name', 'cluster_tolerance': 'cluster_tolerance', 'join_attributes': 'joattributes'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.SymDiff(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def table_select(table=None, out_table=None, where_clause=None):
    '''TableSelect_analysis(table, out_table, {where_clause})

        Selects table records matching a Structured Query Language (SQL)
        expression and writes them to an output table.

     INPUTS:
      table (Table View / Raster Layer):
          The table whose records matching the specified expression will be
          written to the output table.
      where_clause {SQL Expression}:
          An SQL expression used to select a subset of records. For more
          information on SQL syntax see the help topic SQL reference for
          elements used in query expressions.

     OUTPUTS:
      out_table (Table):
          The output table containing records from the input table that match
          the specified expression.'''
    kwargs = locals()
    argdb = {'in_table': 'table', 'out_table': 'out_table', 'where_clause': 'where_clause'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.TableSelect(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def tabulate_intersection(zone_features=None, zone_fields=None, class_features=None, out_table=None, class_fields=None, sum_fields=None, xy_tolerance=None, out_units=None):
    '''TabulateIntersection_analysis(zone_features, zone_fields;zone_fields..., class_features, out_table, {class_fields;class_fields...}, {sum_fields;sum_fields...}, {xy_tolerance}, {out_units})

        Computes the intersection between two feature classes and cross-
        tabulates the area, length, or count of the intersecting features.

     INPUTS:
      zone_features (Feature Layer):
          The features used to identify zones.
      zone_fields (Field):
          The attribute field or fields that will be used to define zones.
      class_features (Feature Layer):
          The features used to identify classes.
      class_fields {Field}:
          The attribute field or fields used to define classes.
      sum_fields {Field}:
          The fields to sum from the Input Class Features.
      xy_tolerance {Linear Unit}:
          The distance that determines the range in which features or their
          vertices are considered equal. By default, this is the XY Tolerance of
          the Input Zone Features.
      out_units {String}:
          Units to be used to calculate area or length measurements. Setting
          output units when the input class features are points is not
          supported.

          * UNKNOWN

          * INCHES

          * FEET

          * YARDS

          * MILES

          * NAUTICAL_MILES

          * MILLIMETERS

          * CENTIMETERS

          * DECIMETERS

          * METERS

          * KILOMETERS

          * DECIMAL_DEGREES

          * POINTS

          * ARES

          * ACRES

          * HECTARES

          * SQUARE_INCHES

          * SQUARE_FEET

          * SQUARE_YARDS

          * SQUARE_MILES

          * SQUARE_MILLIMETERS

          * SQUARE_CENTIMETERS

          * SQUARE_DECIMETERS

          * SQUARE_METERS

          * SQUARE_KILOMETERS

     OUTPUTS:
      out_table (Table):
          The table that will contain the cross-tabulation of intersections
          between zones and classes.'''
    kwargs = locals()
    argdb = {'xy_tolerance': 'xy_tolerance', 'out_units': 'out_units', 'in_class_features': 'class_features', 'out_table': 'out_table', 'in_zone_features': 'zone_features', 'zone_fields': 'zone_fields', 'sum_fields': 'sum_fields', 'class_fields': 'class_fields'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.TabulateIntersection(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def union(features=None, output_name=None, joattributes=None, cluster_tolerance=None, gaps=None):
    '''Union_analysis(features;features..., output_name, {joattributes}, {cluster_tolerance}, {gaps})

        Computes a geometric union of the input features. All features and
        their attributes will be written to the output feature class.

     INPUTS:
      features (Value Table):
          A list of the input feature classes or layers. When the distance
          between features is less than the cluster tolerance, the features with
          the lower rank will snap to the feature with the higher rank. The
          highest rank is one. All of the input features must be polygons.
      joattributes {String}:
          Determines which attributes from the input features will be
          transferred to the output feature class.

          * ALL-All the attributes from the input features will be transferred
          to the output feature class. This is the default.

          * NO_FID-All the attributes except the FID from the input features
          will be transferred to the output feature class.

          * ONLY_FID-Only the FID field from the input features will be
          transferred to the output feature class.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates (nodes and
          vertices) as well as the distance a coordinate can move in X or Y (or
          both).
      gaps {Boolean}:
          Gaps are areas in the output feature class that are completely
          enclosed by other polygons. This is not invalid, but it may be
          desirable to identify these for analysis. To find the gaps in the
          output, set this option to NO_GAPS, and a feature will be created in
          these areas. To select these features, query the output feature class
          based on all the input feature's FID values being equal to -1.

          * GAPS-No feature will be created for areas in the output that are
          completely enclosed by polygons. This is the default.

          * NO_GAPS-A feature will be created for the areas in the output that
          are completely enclosed by polygons. This feature will have blank
          attributes and its FID values will be -1.

     OUTPUTS:
      output_name (Feature Class):
          The feature class that will contain the results.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'out_feature_class': 'output_name', 'cluster_tolerance': 'cluster_tolerance', 'join_attributes': 'joattributes', 'gaps': 'gaps'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Union(**kwargs)
    return _process_results(result)



#--------------------------------------------------------------------------
def update(features=None, update_features=None, output_name=None, keep_borders=None, cluster_tolerance=None):
    '''Update_analysis(features, update_features, output_name, {keep_borders}, {cluster_tolerance})

        Computes the geometric intersection of the Input Features and Update
        Features. The attributes and geometry of the input features are
        updated by the update features in the output feature class.

     INPUTS:
      features (Feature Layer):
          The input feature class or layer. Geometry type must be polygon.
      update_features (Feature Layer):
          The features that will be used to update the input features. Geometry
          type must be polygon.
      keep_borders {Boolean}:
          Specifies whether the boundary of the update polygon features will be
          kept.

          * BORDERS-The outside border of the update_features will be kept in
          the output_name. This is the default option.

          * NO_BORDERS-The outside border of the update_features are dropped
          after they are inserted into the features. Item values of the
          update_features take precedence over features attributes.
      cluster_tolerance {Linear Unit}:
          The minimum distance separating all feature coordinates (nodes and
          vertices) as well as the distance a coordinate can move in X or Y (or
          both).

     OUTPUTS:
      output_name (Feature Class):
          The feature class to contain the results.'''
    kwargs = locals()
    argdb = {'in_features': 'features', 'update_features': 'update_features', 'out_feature_class': 'output_name', 'cluster_tolerance': 'cluster_tolerance', 'keep_borders': 'keep_borders'}
    kwargs = _process_kwargs(argdb, **kwargs)

    result = arcpy.analysis.Update(**kwargs)
    return _process_results(result)


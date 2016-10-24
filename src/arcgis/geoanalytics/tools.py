

def aggregate_points(gis,
                     point_layer,
                     output_name,
                     distance_interval=None,
                     distance_interval_unit=None,
                     bin_type="SQUARE",
                     polygon_layer=None,
                     time_interval=None,
                     time_interval_unit=None,
                     time_repeat=None,
                     time_repeat_unit=None,
                     time_reference=None,
                     summary_fields=None,
                     out_sr=None,
                     process_sr=None,
                     out_extent=None,
                     datastore="GDB"):
    """


    Parameters
    ----------
    point_layer : Required FeatureSet

    distance_interval : Optional float

    distance_interval_unit : Optional string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    bin_type : Optional string
        One of the following: ['SQUARE', 'HEXAGON']
    polygon_layer : Optional FeatureSet

    time_interval : Optional int

    time_interval_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_repeat : Optional int

    time_repeat_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_reference : Optional datetime.date

    summary_fields : Optional string

    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass


def describe_dataset(gis,
                     in_dataset,
                     out_sr=None,
                     out_extent=None,
                     datastore="GDB",
                     context=None):
    """


    Parameters
    ----------
    in_dataset : Required FeatureSet

    out_sr : Optional string

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']
    context : Optional string


    Returns
    -------
    output_json : layer (Feature Service item)
    """
    pass


def join_features(gis,
                  target_layer,
                  join_layer,
                  output_name,
                  join_operation="Join one to one",
                  join_fields=None,
                  summary_fields=None,
                  spatial_relationship=None,
                  spatial_near_distance=None,
                  spatial_near_distance_unit=None,
                  temporal_relationship=None,
                  temporal_near_distance=None,
                  temporal_near_distance_unit=None,
                  attribute_relationship=None,
                  join_condition=None,
                  out_sr=None,
                  process_sr=None,
                  out_extent=None,
                  datastore="GDB"):
    """


    Parameters
    ----------
    target_layer : Required FeatureSet

    join_layer : Required FeatureSet

    join_operation : Required string
        One of the following: ['Join one to one', 'Join one to many']
    join_fields : Optional string

    summary_fields : Optional string

    spatial_relationship : Optional string
        One of the following: ['Equals', 'Intersects', 'Contains', 'Within', 'Crosses', 'Touches', 'Overlaps', 'Near']
    spatial_near_distance : Optional float

    spatial_near_distance_unit : Optional string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    temporal_relationship : Optional string
        One of the following: ['Equals', 'Intersects', 'During', 'Contains', 'Finishes', 'FinishedBy', 'Meets', 'MetBy', 'Overlaps', 'OverlappedBy', 'Starts', 'StartedBy', 'Near']
    temporal_near_distance : Optional int

    temporal_near_distance_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    attribute_relationship : Optional string

    join_condition : Optional string

    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass


def create_buffers(gis,
                   input_layer,
                   output_name,
                   distance=None,
                   distance_unit=None,
                   field=None,
                   method="PLANAR",
                   dissolve_option="NONE",
                   dissolve_fields=None,
                   summary_fields=None,
                   multipart=False,
                   out_sr=None,
                   process_sr=None,
                   out_extent=None,
                   datastore="GDB"):
    """


    Parameters
    ----------
    input_layer : Required FeatureSet

    distance : Optional float

    distance_unit : Optional string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    field : Optional string

    method : Required string
        One of the following: ['GEODESIC', 'PLANAR']
    dissolve_option : Optional string
        One of the following: ['ALL', 'LIST', 'NONE']
    dissolve_fields : Optional string

    summary_fields : Optional string

    multipart : Optional bool

    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass


def calculate_density(gis,
                      input_layer,
                      bin_size,
                      bin_size_unit,
                      radius,
                      radius_unit,
                      output_name,
                      fields=None,
                      weight="UNIFORM",
                      bin_type="SQUARE",
                      time_interval=None,
                      time_interval_unit=None,
                      time_repeat=None,
                      time_repeat_unit=None,
                      time_reference=None,
                      area_units=None,
                      out_sr=None,
                      process_sr=None,
                      out_extent=None,
                      datastore="GDB"):
    """


    Parameters
    ----------
    input_layer : Required FeatureSet

    fields : Optional string

    weight : Required string
        One of the following: ['UNIFORM', 'KERNEL']
    bin_size : Required float

    bin_size_unit : Required string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    bin_type : Required string
        One of the following: ['SQUARE', 'HEXAGON']
    time_interval : Optional int

    time_interval_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_repeat : Optional int

    time_repeat_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_reference : Optional datetime.date

    radius : Required float

    radius_unit : Required string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    area_units : Optional string
        One of the following: ['ACRES', 'SQUARE_KILOMETERS', 'SQUARE_INCHES', 'SQUARE_FEET', 'SQUARE_YARDS', 'SQUARE_MAP_UNITS', 'SQUARE_METERS', 'SQUARE_MILES', 'HECTARES']
    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional int

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass


def reconstruct_tracks(gis,
                       input_layer,
                       track_fields,
                       output_name,
                       method="PLANAR",
                       buffer_field=None,
                       summary_fields=None,
                       time_split=None,
                       time_split_unit=None,
                       out_sr=None,
                       process_sr=None,
                       out_extent=None,
                       datastore="GDB"):
    """


    Parameters
    ----------
    input_layer : Required FeatureSet

    track_fields : Required string

    method : Required string
        One of the following: ['GEODESIC', 'PLANAR']
    buffer_field : Optional string

    summary_fields : Optional string

    time_split : Optional int

    time_split_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass


def create_space_time_cube(gis,
                           point_layer,
                           distance_interval,
                           distance_interval_unit,
                           time_interval,
                           time_interval_unit,
                           output_name,
                           time_interval_alignment=None,
                           reference_time=None,
                           summary_fields=None,
                           out_sr=None,
                           process_sr=None,
                           out_extent=None,
                           datastore="GDB"):
    """


    Parameters
    ----------
    point_layer : Required FeatureSet

    distance_interval : Required float

    distance_interval_unit : Required string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    time_interval : Required int

    time_interval_unit : Required string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_interval_alignment : Optional string
        One of the following: ['END_TIME', 'START_TIME', 'REFERENCE_TIME']
    reference_time : Optional datetime.date

    summary_fields : Optional string

    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output_cube : layer (Feature Service item)
    """
    pass


def create_panel_data(gis,
                      in_target_features,
                      in_join_features,
                      time_interval,
                      time_interval_unit,
                      time_repeat,
                      time_repeat_unit,
                      time_reference,
                      out_features_name,
                      in_summary_stats=None,
                      in_spatial_relationship=None,
                      in_spatial_distance=None,
                      in_spatial_distance_unit=None,
                      in_attribute_relationship=None,
                      out_sr=None,
                      out_extent=None,
                      datastore="GDB",
                      context=None):
    """


    Parameters
    ----------
    in_target_features : Required FeatureSet

    in_join_features : Required FeatureSet

    in_summary_stats : Optional string

    in_spatial_relationship : Optional string
        One of the following: ['Intersect', 'Contains', 'Within', 'Crosses', 'Touches', 'Overlaps', 'Near']
    in_spatial_distance : Optional float

    in_spatial_distance_unit : Optional string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    in_attribute_relationship : Optional string

    time_interval : Required int

    time_interval_unit : Required string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_repeat : Required int

    time_repeat_unit : Required string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_reference : Required datetime.date

    out_features_name : Required string

    out_sr : Optional string

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']
    context : Optional string


    Returns
    -------
    out_features : layer (Feature Service item)
    """
    pass


def generate_manifest(gis,
                      data_store_item_id,
                      update_data_item=False,
                      out_sr=None,
                      out_extent=None,
                      datastore="GDB",
                      context=None):
    """


    Parameters
    ----------
    data_store_item_id : Required string

    update_data_item : Optional bool

    out_sr : Optional string

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']
    context : Optional string


    Returns
    -------
    manifest : layer (Feature Service item)
    """
    pass


def create_sample(gis,
                  input_layer,
                  output_layer_name,
                  out_sr=None,
                  out_extent=None,
                  datastore="GDB",
                  context=None):
    """


    Parameters
    ----------
    input_layer : Required FeatureSet

    output_layer_name : Required string

    out_sr : Optional string

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']
    context : Optional string


    Returns
    -------
    output_layer : layer (Feature Service item)
    """
    pass


def copy_to_data_store(gis,
                       input_layer,
                       output_name,
                       out_sr=None,
                       out_extent=None,
                       datastore="GDB",
                       context=None):
    """


    Parameters
    ----------
    input_layer : Required FeatureSet

    output_name : Required string

    out_sr : Optional string

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']
    context : Optional string


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass


def summarize_attributes(gis,
                         input_layer,
                         fields,
                         output_name,
                         summary_fields=None,
                         out_sr=None,
                         process_sr=None,
                         out_extent=None,
                         datastore="GDB"):
    """


    Parameters
    ----------
    input_layer : Required FeatureSet

    fields : Required string

    summary_fields : Optional string

    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass


def summarize_within(gis,
                     summary_layer,
                     output_name,
                     bin_size=None,
                     bin_size_unit=None,
                     bin_type="SQUARE",
                     sum_within_layer=None,
                     time_interval=None,
                     time_interval_unit=None,
                     time_repeat=None,
                     time_repeat_unit=None,
                     time_reference=None,
                     summary_fields=None,
                     proportional_weighting=False,
                     out_sr=None,
                     process_sr=None,
                     out_extent=None,
                     datastore="GDB"):
    """


    Parameters
    ----------
    summary_layer : Required FeatureSet

    bin_size : Optional float

    bin_size_unit : Optional string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    bin_type : Optional string
        One of the following: ['SQUARE', 'HEXAGON']
    sum_within_layer : Optional FeatureSet

    time_interval : Optional int

    time_interval_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_repeat : Optional int

    time_repeat_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_reference : Optional datetime.date

    summary_fields : Optional string

    proportional_weighting : Optional bool

    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass


def find_hot_spots(gis,
                   point_layer,
                   bin_size,
                   bin_size_unit,
                   output_name,
                   time_step_interval=None,
                   time_step_interval_unit=None,
                   time_step_alignment=None,
                   referencetime=None,
                   neighborhood_distance=None,
                   neighborhood_distance_unit=None,
                   out_sr=None,
                   process_sr=None,
                   out_extent=None,
                   datastore="GDB"):
    """


    Parameters
    ----------
    point_layer : Required FeatureSet

    bin_size : Required float

    bin_size_unit : Required string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    time_step_interval : Optional int

    time_step_interval_unit : Optional string
        One of the following: ['Years', 'Months', 'Weeks', 'Days', 'Hours', 'Minutes', 'Seconds', 'Milliseconds']
    time_step_alignment : Optional string
        One of the following: ['END_TIME', 'START_TIME', 'REFERENCE_TIME']
    referencetime : Optional datetime.date

    neighborhood_distance : Optional float

    neighborhood_distance_unit : Optional string
        One of the following: ['Feet', 'Yards', 'Miles', 'Meters', 'Kilometers', 'Nautical Miles']
    output_name : Required string

    out_sr : Optional int

    process_sr : Optional int

    out_extent : Optional string

    datastore : Optional string
        One of the following: ['BDS', 'GDB']


    Returns
    -------
    output : layer (Feature Service item)
    """
    pass

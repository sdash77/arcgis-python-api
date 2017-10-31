from ._ge import _GeoEnrichment
from arcgis import env

#----------------------------------------------------------------------
def list_countries(gis=None):
    """"
    returns a Pandas' DataFrame of available countries that have GeoEnrichment data.
    """
    if gis is None:
        gis = env.active_gis
    ge = _GeoEnrichment(gis=gis)
    return ge.countries
#----------------------------------------------------------------------
def create_report(study_areas,
                  report=None,
                  export_format='pdf',
                  report_fields=None,
                  options=None,
                  return_type=None,
                  use_data=None,
                  in_sr=4326,
                  f='bin',
                  out_name=None,
                  out_folder=None,
                  gis=None):
    """
    The Create Report method allows you to create many types of high quality reports for a
    variety of use cases describing the input area. If a point is used as a study area, the
    service will create a 1-mile ring buffer around the point to collect and append enrichment
    data. Optionally, you can create a buffer ring or drive-time service area around points of
    interest to generate PDF or Excel reports containing relevant information for the area on
    demographics, consumer spending, tapestry market, business or market potential.

    Report options are available and can be used to describe and gain a better understanding
    about the market, customers / clients and competition associated with an area of interest.


    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    study_areas            required list. Required parameter: Study areas may be defined by
                           input points, polygons, administrative boundaries or addresses.
    ------------------     --------------------------------------------------------------------
    report                 optional string. identify the id of the report. This may be one of
                           the many default reports available along with our demographic data
                           collections or a customized report. Custom report templates are
                           stored in an ArcGIS Online organization as a Report Template item.
                           The organization URL and a valid ArcGIS Online authentication token
                           is required for security purposes to access these templates. If no
                           report is specified, the default report is census profile for United
                           States and a general demographic summary report for most countries.
    ------------------     --------------------------------------------------------------------
    export_format          Optional parameter to specify the format of the generated report.
                           Supported formats include PDF and XLSX.
    ------------------     --------------------------------------------------------------------
    report_fields          Optional parameter specifies additional choices to customize
                           reports. Below is an example of the position on the report header
                           for each field.
    ------------------     --------------------------------------------------------------------
    options                Optional parameter to specify the properties for the study area
                           buffer. For a full list of valid buffer properties values and
                           further examples review the Input XY Locations' options parameter.

                           By default a 1 mile radius buffer will be applied to point(s) and
                           address locations to define a study area.
    ------------------     --------------------------------------------------------------------
    return_type            Optional parameter used for storing an output report item to Portal
                           for ArcGIS instead of returning a report to a customer via binary
                           stream. The attributes are used by Portal to determine where and how
                           an item is stored. Parameter attributes include: user, folder,
                           title, item_properties, URL, token, and referrer.
                           Example

                           Creating a new output in a Portal for ArcGIS Instance:

                           return_type = {'user' : 'testUser',
                                          'folder' : 'FolderName',
                                          'title' : 'Report Title',
                                          'item_properties' : '<properties>',
                                          'url' : 'https://hostname.domain.com/webadaptor',
                                          'token' : 'token', 'referrer' : 'referrer'}
    ------------------     --------------------------------------------------------------------
    use_data               Optional dictionary. This parameter explicitly specify the country
                           or dataset to query. When all input features specified in the
                           study_areas parameter describe locations or areas that lie in the
                           same country or dataset, this parameter can be specified to provide
                           an additional 'performance hint' to the service.

                           By default, the service will automatically determine the country or
                           dataset that is associated with each location or area submitted in
                           the study_areas parameter. Specifying a specific dataset or country
                           through this parameter will potentially improve response time.

                           By default, the data apportionment method is determined by the size
                           of the study area. Small study areas use block apportionment for
                           higher accuracy whereas large study areas (100 miles or more) will
                           use a cascading centroid apportionment method to maintain
                           performance. This default behavior can be overridden by using the
                           detailed_aggregation parameter.
    ------------------     --------------------------------------------------------------------
    in_sr                  Optional parameter to define the input geometries in the study_areas
                           parameter in a specified spatial reference system.
                           When input points are defined in the study_areas parameter, this
                           optional parameter can be specified to explicitly indicate the
                           spatial reference system of the point features. The parameter value
                           can be specified as the well-known ID describing the projected
                           coordinate system or geographic coordinate system.
                           The default is 4326
    ------------------     --------------------------------------------------------------------
    f                      Optional parameter to specify the output response format.
                           Values: f, bin
    ------------------     --------------------------------------------------------------------
    out_name               Optional string.  Name of the output file
    ------------------     --------------------------------------------------------------------
    out_folder             Optional string. Name of the save folder
    ==================     ====================================================================
    """
    if gis is None:
        gis = env.active_gis

    ge = _GeoEnrichment(gis=gis)
    return ge.create_report(study_areas=study_areas,
                             report=report,
                             export_format=export_format,
                            report_fields=report_fields,
                            options=options,
                            return_type=return_type,
                            use_data=use_data,
                            in_sr=in_sr,
                            out_folder=out_folder,
                            out_name=out_name,
                            f=f)
#----------------------------------------------------------------------
def data_collections(country=None,
                     dataset=None,
                     variables=None,
                     out_fields="*",
                     hide_nulls=True,
                     gis=None):
    """
    The GeoEnrichment class uses the concept of a data collection to define the data
    attributes returned by the enrichment service. Each data collection has a unique name
    that acts as an ID that is passed in the data_collections parameter of the GeoEnrichment
    service.

    Some data collections (such as default) can be used in all supported countries. Other data
    collections may only be available in one or a collection of countries. Data collections may
    only be available in a subset of countries because of differences in the demographic data
    that is available for each country. A list of data collections for all available countries
    can be generated with the data collection discover method seen below.
    Return a list of data collections that can be run for any country.

    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    country                optional string. lets the user supply and optional name of a country
                           in order to get information about the data collections in that given
                           country.
    ------------------     --------------------------------------------------------------------
    dataset                Optional string. Name of the data collection to examine.
    ------------------     --------------------------------------------------------------------
    variables              Optional string/list. This parameter to specifies a list of field
                           names that include variables for the derivative statistics.
    ------------------     --------------------------------------------------------------------
    out_fields             Optional string. This parameter is a string of comma seperate field
                           names.
    ------------------     --------------------------------------------------------------------
    hide_nulls             Optional boolean. parameter to return only values that are not NULL
                           in the output response. Adding the optional suppress_nulls parameter
                           to any data collections discovery method will reduce the size of the
                           output that is returned.
    ------------------     --------------------------------------------------------------------
    gis                    Optional GIS.  If None, the GIS object will be used from the
                           arcgis.env.active_gis.  This GIS object must be authenticated and
                           have the ability to consume credits
    ==================     ====================================================================

    :returns: dictionary, describing the requested return data.
    """
    if gis is None:
        gis = env.active_gis
    ge = _GeoEnrichment(gis=gis)

    return ge.data_collections(country=country,
                                dataset=dataset,
                                variables=variables,
                                out_fields=out_fields,
                                hide_nulls=hide_nulls)
#----------------------------------------------------------------------
def enrich(study_areas,
           data_collections=None,
           analysis_variables=None,
           add_derivative_variables="all",
           options=None,
           use_data=None,
           intersecting_geographies=None,
           return_geometry=True,
           in_sr=4326,
           out_sr=4326,
           suppress_nulls=False,
           for_storage=True,
           as_featureset=False,
           gis=None):
    """
    The GeoEnrichment class uses the concept of a study area to
    define the location of the point or area that you want to enrich
    with additional information. If one or many points are input as
    a study area, the service will create a 1-mile ring buffer around
    the point to collect and append enrichment data. You can optionally
    change the ring buffer size or create drive-time service areas
    around the point. The most common method to determine the center
    point for a study areas is a set of one or many point locations
    defined as XY locations. More specifically, one or many input
    points (latitude and longitude) can be provided to the service to
    set the study areas that you want to enrich with additional
    information. You can create a buffer ring or drive-time service
    area around the points to aggregate data for the study areas. You
    can also return enrichment data for buffers around input line
    features.

    =========================     ====================================================================
    **Argument**                  **Description**
    -------------------------     --------------------------------------------------------------------
    study_areas                   Required list/dictionary. This parameter is used to specify a list
                                  of input features to be enriched. Study areas can be input XY point
                                  locations.
    -------------------------     --------------------------------------------------------------------
    data_collections              Optional list. A Data Collection is a preassembled list of
                                  attributes that will be used to enrich the input features.
                                  Enrichment attributes can describe various types of information such
                                  as demographic characteristics and geographic context of the
                                  locations or areas submitted as input features in study_areas.
    -------------------------     --------------------------------------------------------------------
    analysis_variables            Optional list. A Data Collection is a preassembled list of
                                  attributes that will be used to enrich the input features. With the
                                  analysis_variables parameter you can return a subset of variables
                                  enrichment attributes can describe various types of information such
                                  as demographic characteristics and geographic context of the
                                  locations or areas submitted as input features in study_areas.
    -------------------------     --------------------------------------------------------------------
    add_derivative_variables      Optional list. This parameter is used to specify an array of string
                                  values that describe what derivative variables to include in the
                                  output.
    -------------------------     --------------------------------------------------------------------
    options                       Optional dictionary. This parameter is used to specify enrichment
                                  behavior. For points described as map coordinates, a 1-mile ring
                                  area centered on each site will be used by default. You can use this
                                  parameter to change these default settings.
                                  With this parameter, the caller can override the default behavior
                                  describing how the enrichment attributes are appended to the input
                                  features described in study_areas. For example, you can change the
                                  output ring buffer to 5 miles, change the number of output buffers
                                  created around each point, and also change the output buffer type to
                                  a drive-time service area rather than a simple ring buffer.
    -------------------------     --------------------------------------------------------------------
    use_data                      Optional dictionary. The parameter is used to explicitly specify the
                                  country or dataset to query.
    -------------------------     --------------------------------------------------------------------
    intersecting_geographies      Optional parameter to explicitly define the geographic layers used
                                  to provide geographic context during the enrichment process. For
                                  example, you can use this optional parameter to return the U.S.
                                  county and ZIP Code that each input study area intersects.
                                  You can intersect input features defined in the study_areas
                                  parameter with standard geography layers that are provided by the
                                  GeoEnrichment class for each country. You can also intersect
                                  features from a publicly available feature service.
    -------------------------     --------------------------------------------------------------------
    return_geometry               Optional boolean. A parameter to request the output geometries in
                                  the response.
    -------------------------     --------------------------------------------------------------------
    in_sr                         Optional integer. A parameter used to define the input geometries in
                                  the study_areas parameter in a specified spatial reference system.
    -------------------------     --------------------------------------------------------------------
    out_sr                        Optional integer. A parameter to request the output geometries in a
                                  specified spatial reference system.
    -------------------------     --------------------------------------------------------------------
    suppress_nulls                Optional boolean. A parameter to return only values that are not
                                  NULL in the output response. Adding the optional suppress_nulls
                                  parameter to any data collections discovery method will reduce the
                                  size of the output that is returned.
    -------------------------     --------------------------------------------------------------------
    for_storage                   Optional boolean. A parameter to define if GeoEnrichment output is
                                  being stored. The price for using the Enrich method varies according
                                  to whether the data returned is being persisted, i.e. being stored,
                                  or whether it is merely being used in an interactive context and is
                                  discarded after being viewed. If the data is being stored, the terms
                                  of use for the GeoEnrichment class require that you specify the
                                  for_storage parameter to true.
    -------------------------     --------------------------------------------------------------------
    as_featureset                 Optional boolean.  The default is True. If True, the result will be
                                  a arcgis.features.FeatureSet object instead of a SpatailDataFrame or
                                  Pandas' DataFrame.
    -------------------------     --------------------------------------------------------------------
    gis                           Optional GIS.  If None, the GIS object will be used from the
                                  arcgis.env.active_gis.  This GIS object must be authenticated and
                                  have the ability to consume credits
    =========================     ====================================================================

    :returns: Spatial DataFrame, Panda's DataFrame when as_featureset=False,
              list FeatureSet objects when as_featureset=True,
              or a dictionary on error
    """
    if gis is None:
        gis = env.active_gis
    ge = _GeoEnrichment(gis=gis)
    return ge.enrich(study_areas=study_areas,
                      data_collections=data_collections,
                     analysis_variables=analysis_variables,
                     add_derivative_variables=add_derivative_variables,
                     options=options,
                     use_data=use_data,
                     intersecting_geographies=intersecting_geographies,
                     return_geometry=return_geometry,
                     in_sr=in_sr,
                     out_sr=out_sr,
                     suppress_nulls=suppress_nulls,
                     for_storage=for_storage,
                     as_featureset=as_featureset)
#----------------------------------------------------------------------
def find_report(country, gis=None):
    """
    Returns a list of reports by a country code

    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    country                optional string. lets the user supply and optional name of a country
                           in order to get information about the data collections in that given
                           country. This should be a two country code name.
                           Example: United States as US
    ------------------     --------------------------------------------------------------------
    gis                    Optional GIS.  If None, the GIS object will be used from the
                           arcgis.env.active_gis.  This GIS object must be authenticated and
                           have the ability to consume credits
    ==================     ====================================================================

    :returns: Panda's DataFrame
    """
    if gis is None:
        gis = env.active_gis
    ge = _GeoEnrichment(gis=gis)
    return ge.find_report(country=country)
#----------------------------------------------------------------------
def get_variables(country,
                  dataset=None,
                  text=None,
                  gis=None):
    """
    The GeoEnrichment get_variables method allows you to search the data
    collections for variables that contain specific keywords.

    ======================     ====================================================================
    **Argument**               **Description**
    ----------------------     --------------------------------------------------------------------
    country                    Optional string. Specifies the source country for the search. Use
                               this parameter to limit the search and query of standard geographic
                               features to one country. This parameter supports both the
                               two-digit and three-digit country codes illustrated in the
                               coverage table.

                               Example 1 - Set source country to the United States:
                               country=US

                               Example 2 - Set source country to the Canada:
                               country=CA

                               Additional notes
                               Currently, the service is available for Canada, the United States
                               and a number of European countries. Other countries will be added
                               in the near future.
    ----------------------     --------------------------------------------------------------------
    dataset                    optional string/list. Optional parameter to specify a specific
                               dataset within a defined country. This parameter will not be used
                               in the Beta release. In the future, some countries may have two or
                               more datasets that may have different vintages and standard
                               geography areas. For example, in the United States, there may be
                               an optional dataset with historic census data from previous years.
                               Examples
                               dataset=USA_ESRI_2013
    ----------------------     --------------------------------------------------------------------
    text                       Optional string. Use this parameter to specify the text to query and
                               search the data collections for the country and datasets specified.
                               You can use this parameter to query and find specific keywords that
                               are contained in a data collection.
    ------------------         --------------------------------------------------------------------
    gis                        Optional GIS.  If None, the GIS object will be used from the
                               arcgis.env.active_gis.  This GIS object must be authenticated and
                               have the ability to consume credits
    ======================     ====================================================================

    returns: Pandas' DataFrame
    """
    if gis is None:
        gis = env.active_gis
    ge = _GeoEnrichment(gis=gis)
    return ge.get_variables(country=country,
                             dataset=dataset,
                             text=text)
#----------------------------------------------------------------------
def report_metadata(country, gis=None):
    """
    This method returns information about a given country's available reports and provides
    detailed metadata about each report.

    :Usage:
    >>> df = arcgis.geoenrichment.report_metadata("al", gis=gis)
    # returns basic report metadata for Albania

    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    country                Required string. lets the user supply and optional name of a country
                           in order to get information about the data collections in that given
                           country. This can be the two letter country code or the coutries
                           full name.
    ------------------     --------------------------------------------------------------------
    gis                    Optional GIS.  If None, the GIS object will be used from the
                           arcgis.env.active_gis.  This GIS object must be authenticated and
                           have the ability to consume credits
    ==================     ====================================================================

    :return: Pandas' DataFrame
    """
    if gis is None:
        gis = env.active_gis
    ge = _GeoEnrichment(gis=gis)
    return ge.report_metadata(country=country)
#----------------------------------------------------------------------
def select_businesses(type_filters=None,
                      feature_limit=1000,
                      feature_offset=0,
                      exact_match=False,
                      search_string=None,
                      spatial_filter=None,
                      simple_search=False,
                      dataset_id=None,
                      full_error_message=False,
                      out_sr=4326,
                      return_geometry=False,
                      as_featureset=False,
                      gis=None):
    """
    The select_businesses method returns business points matching a given search criteria.
    Business points can be selected using any combination of three search criteria: search
    string, spatial filter and business type. A business point will be selected if it matches
    all search criteria specified.

    ======================     ====================================================================
    **Argument**               **Description**
    ----------------------     --------------------------------------------------------------------
    type_filters               Optional list. List of business type filters restricting the search.
                               For USA, either the NAICS or SIC filter is useful as a business type
                               filter. If both filters are specified in the type_filters parameter
                               value, selected business points will match both of them.
    ----------------------     --------------------------------------------------------------------
    feature_limit              Optional integer. The limit of returned business points.
    ----------------------     --------------------------------------------------------------------
    feature_offset             Optional integer. Start the results on the number of the record
                               specified.
    ----------------------     --------------------------------------------------------------------
    exact_match                Optional boolean. True value of the parameter means the exact match
                               of the string to search.
    ----------------------     --------------------------------------------------------------------
    search_string              Optional string. A string of characters which is used in the search
                               query.
    ----------------------     --------------------------------------------------------------------
    spatial_filter             Optional SpatialFilter. A spatial filter restricting the search.
    ----------------------     --------------------------------------------------------------------
    simple_search              Optional boolean. A spatial filter restricting the search. True
                               value of the parameter means a simple search (e.g., in company
                               names only).
    ----------------------     --------------------------------------------------------------------
    dataset_id                 Optional string. ID of the active dataset.
    ----------------------     --------------------------------------------------------------------
    full_error_message         Optional boolean. Parameter for composing error message.
    ----------------------     --------------------------------------------------------------------
    out_sr                     Optional integer. Parameter specifying the spatial reference to
                               return the output dataframe.
    ----------------------     --------------------------------------------------------------------
    return_geometry            Optional boolean. When true, geometries are returned with the
                               response.
    ----------------------     --------------------------------------------------------------------
    as_featureset              Optional boolean.  The default is False. If True, the result will be
                               a arcgis.features.FeatureSet object instead of a SpatailDataFrame or
                               Pandas' DataFrame.
    ------------------         --------------------------------------------------------------------
    gis                        Optional GIS.  If None, the GIS object will be used from the
                               arcgis.env.active_gis.  This GIS object must be authenticated and
                               have the ability to consume credits
    ======================     ====================================================================

    returns: DataFrame (Spatial or Pandas), FeatureSet, or dictionary on error.
    """
    if gis is None:
        gis = env.active_gis
    ge = _GeoEnrichment(gis=gis)
    return ge.select_businesses(type_filters=type_filters,
                                 feature_limit=feature_limit,
                                feature_offset=feature_offset,
                                exact_match=exact_match,
                                search_string=search_string,
                                spatial_filter=spatial_filter,
                                simple_search=simple_search,
                                dataset_id=dataset_id,
                                full_error_message=full_error_message,
                                out_sr=out_sr,
                                return_geometry=return_geometry,
                                as_featureset=as_featureset)
#----------------------------------------------------------------------
def standard_geography_query(source_country=None,
                             country_dataset=None,
                             layers=None,
                             ids=None,
                             geoquery=None,
                             return_sub_geography=False,
                             sub_geography_layer=None,
                             sub_geography_query=None,
                             out_sr=4326,
                             return_geometry=False,
                             return_centroids=False,
                             generalization_level=0,
                             use_fuzzy_search=False,
                             feature_limit=1000,
                             as_featureset=False,
                             gis=None):
    """
    The GeoEnrichment class provides a helper method that returns standard geography IDs and
    features for the supported geographic levels in the United States and Canada.
    The GeoEnrichment class uses the concept of a study area to define the location of the point
    or area that you want to enrich with additional information. Locations can also be passed as
    one or many named statistical areas. This form of a study area lets you define an area by
    the ID of a standard geographic statistical feature, such as a census or postal area. For
    example, to obtain enrichment information for a U.S. state, county or ZIP Code or a Canadian
    province or postal code, the Standard Geography Query helper method allows you to search and
    query standard geography areas so that they can be used in the GeoEnrichment method to
    obtain facts about the location.
    The most common workflow for this service is to find a FIPS (standard geography ID) for a
    geographic name. For example, you can use this service to find the FIPS for the county of
    San Diego which is 06073. You can then use this FIPS ID within the GeoEnrichment class study
    area definition to get geometry and optional demographic data for the county. This study
    area definition is passed as a parameter to the GeoEnrichment class to return data defined
    in the enrichment pack and optionally return geometry for the feature.

    ======================     ====================================================================
    **Argument**               **Description**
    ----------------------     --------------------------------------------------------------------
    source_country             Optional string. to specify the source country for the search. Use
                               this parameter to limit the search and query of standard geographic
                               features to one country. This parameter supports both the two-digit
                               and three-digit country codes illustrated in the coverage table.
    ----------------------     --------------------------------------------------------------------
    country_dataset            Optional string. parameter to specify a specific dataset within a
                               defined country.
    ----------------------     --------------------------------------------------------------------
    layers                     Optional list/string. Parameter specifies which standard geography
                               layers are being queried or searched. If this parameter is not
                               provided, all layers within the defined country will be queried.
    ----------------------     --------------------------------------------------------------------
    ids                        Optional parameter to specify which IDs for the standard geography
                               layers are being queried or searched. You can use this parameter to
                               return attributes and/or geometry for standard geographic areas for
                               administrative areas where you already know the ID, for example, if
                               you know the Federal Information Processing Standard (FIPS) Codes for
                               a U.S. state or county; or, in Canada, to return the geometry and
                               attributes for a Forward Sortation Area (FSA).
                               Example:
                               Return the state of California where the layers parameter is set to
                               layers=['US.States']
                               then set ids=["06"]
    ----------------------     --------------------------------------------------------------------
    geoquery                   Optional string/list. This parameter specifies the text to query
                               and search the standard geography layers specified. You can use this
                               parameter to query and find standard geography features that meet an
                               input term, for example, for a list of all the U.S. counties that
                               contain the word "orange". The geoquery parameter can be a string
                               that contains one or more words.
    ----------------------     --------------------------------------------------------------------
    return_sub_geography       Optional boolean. Use this optional parameter to return all the
                               subgeographic areas that are within a parent geography.
                               For example, you could return all the U.S. counties for a given
                               U.S. state or you could return all the Canadian postal areas
                               (FSAs) within a Census Metropolitan Area (city).
                               When this parameter is set to true, the output features will be
                               defined in the sub_geography_layer. The output geometries will be
                               in the spatial reference system defined by out_sr.
    ----------------------     --------------------------------------------------------------------
    sub_geography_layer        Optional string/list. Use this optional parameter to return all the
                               subgeographic areas that are within a parent geography. For example,
                               you could return all the U.S. counties within a given U.S. state or
                               you could return all the Canadian postal areas (FSAs) within a
                               Census Metropolitan Areas (city).
                               When this parameter is set to true, the output features will be
                               defined in the sub_geography_layer. The output geometries will be
                               in the spatial reference system defined by out_sr.
    ----------------------     --------------------------------------------------------------------
    sub_geography_query        Optional string.User this parameter to filter the results of the
                               subgeography features that are returned by a search term.
                               You can use this parameter to query and find subgeography
                               features that meet an input term. This parameter is used to
                               filter the list of subgeography features that are within a
                               parent geography. For example, you may want a list of all the
                               ZIP Codes that are within "San Diego County" and filter the
                               results so that only ZIP Codes that start with "921" are
                               included in the output response. The subgeography query is a
                               string that contains one or more words.
    ----------------------     --------------------------------------------------------------------
    out_sr                     Optional integer Use this parameter to request the output geometries
                               in a specified spatial reference system.
    ----------------------     --------------------------------------------------------------------
    return_geometry            Optional boolean. Use this parameter to request the output
                               geometries in the response.  The return type will become a Spatial
                               DataFrame instead of a Panda's DataFrame.
    ----------------------     --------------------------------------------------------------------
    return_centroids           Optional Boolean.  Use this parameter to request the output geometry
                               to return the center point for each feature.
    ----------------------     --------------------------------------------------------------------
    generalization_level       Optional integer that specifies the level of generalization or
                               detail in the area representations of the administrative boundary or
                               standard geographic data layers.
                               Values must be whole integers from 0 through 6, where 0 is most
                               detailed and 6 is most generalized.
    ----------------------     --------------------------------------------------------------------
    use_fuzzy_search           Optional Boolean parameter to define if text provided in the
                               geoquery parameter should utilize fuzzy search logic. Fuzzy searches
                               are based on the Levenshtein Distance or Edit Distance algorithm.
    ----------------------     --------------------------------------------------------------------
    feature_limit              Optional integer value where you can limit the number of features
                               that are returned from the geoquery.
    ----------------------     --------------------------------------------------------------------
    as_featureset              Optional boolean.  The default is False. If True, the result will be
                               a arcgis.features.FeatureSet object instead of a SpatailDataFrame or
                               Pandas' DataFrame.
    ------------------         --------------------------------------------------------------------
    gis                        Optional GIS.  If None, the GIS object will be used from the
                               arcgis.env.active_gis.  This GIS object must be authenticated and
                               have the ability to consume credits
    ======================     ====================================================================

    :returns: Spatial or Pandas Dataframe on success, FeatureSet, or dictionary on failure.

    """
    if gis is None:
        gis = env.active_gis
    ge = _GeoEnrichment(gis=gis)

    return ge.standard_geography_query(source_country=source_country,
                                       country_dataset=country_dataset,
                                       layers=layers,
                                       ids=ids,
                                       geoquery=geoquery,
                                       return_sub_geography=return_sub_geography,
                                       sub_geography_layer=sub_geography_layer,
                                       sub_geography_query=sub_geography_query,
                                       out_sr=out_sr,
                                       return_geometry=return_geometry,
                                       return_centroids=return_centroids,
                                       generalization_level=generalization_level,
                                       use_fuzzy_search=use_fuzzy_search,
                                       feature_limit=feature_limit,
                                       as_featureset=as_featureset)
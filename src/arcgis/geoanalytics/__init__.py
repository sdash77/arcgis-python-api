"""
The arcgis.geoanalytics module provides types and functions for distributed analysis of large datasets.
These GeoAnalytics tools work with big data registered in the GISs datastores as well as with feature layers.

Use arcgis.geoanalytics.is_analysis_supported(gis) to check if geoanalytics is supported in your GIS.

Note: GeoAnalytics operations use the following context parameters defined in the `arcgis.env` module:

        =========================     ====================================================================
        **Context parameter**         **Description**
        -------------------------     --------------------------------------------------------------------
        out_spatial_reference         Used for setting the output spatial reference
        -------------------------     --------------------------------------------------------------------
        process_spatial_reference     Used for setting the processing spatial reference.
        -------------------------     --------------------------------------------------------------------
        analysis_extent               Used for setting the analysis extent.
        -------------------------     --------------------------------------------------------------------
        output_datastore              Used for setting the output datastore to be used.
        =========================     ====================================================================
"""

from . import summarize_data, analyze_patterns, use_proximity, manage_data, find_locations, data_enrichment

def get_datastores(gis=None):
    """
    Returns a helper object to manage geoanalytics datastores in the GIS.
    If a gis isn't specified, returns datastore manager of arcgis.env.active_gis
    """
    import arcgis
    gis = arcgis.env.active_gis if gis is None else gis

    for ds in gis._datastores:
        if 'GeoAnalytics' in ds._server['serverFunction']:
            return ds

    return None

def define_output_datastore(datastore=None, template=None):
    """
    Sets the `arcgis.env.output_datastore` by providing the datastore and template name
    to this method. If datastore is None, the `arcgis.env.output_datastore` will reset
    to default.

    ==========================   ===============================================================
    **Argument**                 **Description**
    --------------------------   ---------------------------------------------------------------
    datastore                    Optional Datastore. When provided, this tells the geoanalytical
                                 tools where to save the information to. If specified as None
                                 along with template, the `arcgis.env.output_datastore` will
                                 reset to default.
    --------------------------   ---------------------------------------------------------------
    template                     optional string.  If specified along with a datastore, the
                                 `arcgis.env.output_datastore` will be set.  The output will be
                                 written to that template.
    ==========================   ===============================================================

    :returns: Boolean

    """
    import arcgis

    if datastore and template:
        if isinstance(datastore, arcgis.gis.Datastore):
            arcgis.env.output_datastore = "{path}:{template}".format(path=datastore.path,
                                                                     template=template)
        elif isinstance(datastore, str):
            arcgis.env.output_datastore = "{path}:{template}".format(path=datastore,
                                                                     template=template)
        elif isinstance(datastore, arcgis.gis.server.Datastore):
            path = datastore.properties.path
            arcgis.env.output_datastore = "{path}:{template}".format(path=datastore,
                                                                     template=template)
        else:
            raise ValueError("Invalid Datastore")
        return True
    elif template and datastore is None:
        raise ValueError("datastore must be specified to set an output template.")
    elif datastore and template is None:
        raise ValueError("template must be specified to set the output_datastore.")
    else:
        arcgis.env.output_datastore = None
        return True
    return False

def is_supported(gis=None):
    """
    Returns True if the GIS supports geoanalytics. If a gis isn't specified,
    checks if arcgis.env.active_gis supports geoanalytics
    """
    import arcgis
    gis = arcgis.env.active_gis if gis is None else gis
    if 'geoanalytics' in gis.properties.helperServices:
        return True
    else:
        return False


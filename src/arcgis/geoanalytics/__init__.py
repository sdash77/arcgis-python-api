"""
The arcgis.geoanalytics module provides types and functions for distributed analysis of large datasets.
These GeoAnalytics tools work with big data registered in the GISs datastores as well as with feature layers.

Use arcgis.geoanalytics.is_analysis_supported(gis) to check if geoanalytics is supported in your GIS.
"""

from . import summarize_data, analyze_patterns, use_proximity, manage_data, find_locations

def get_datastores(gis=None):
    """
    Returns a helper object to manage geoanalytics datastores in the GIS. 
    If a gis isn't specified, returns datastore manager of arcgis.env.active_gis
    """
    import arcgis
    gis = arcgis.env.active_gis if gis is None else gis
    
    for ds in gis._datastores:
        if ds._server['serverFunction'] == 'GeoAnalytics':
            return ds
    
    return None
    
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


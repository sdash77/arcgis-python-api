from utils.imports.clear_import_cache import clear_arcgis_import_cache

def import_all_arcgis_submodules():
    clear_arcgis_import_cache()
    import arcgis
    import arcgis.gis
    import arcgis.gis.admin
    import arcgis.gis.server
    import arcgis.env
    import arcgis.features
    import arcgis.features.analysis
    import arcgis.features.analyze_patterns
    import arcgis.features.elevation
    import arcgis.features.enrich_data
    import arcgis.features.find_locations
    import arcgis.features.hydrology
    import arcgis.features.manage_data
    import arcgis.features.managers
    import arcgis.features.summarize_data
    import arcgis.features.use_proximity
    import arcgis.raster
    import arcgis.raster.analytics
    import arcgis.raster.functions
    import arcgis.raster.functions.gbl
    import arcgis.raster.orthomapping
    import arcgis.network
    import arcgis.network.analysis
    import arcgis.geoanalytics.analyze_patterns
    import arcgis.geoanalytics.data_enrichment
    import arcgis.geoanalytics.find_locations
    import arcgis.geoanalytics.manage_data
    import arcgis.geoanalytics.summarize_data
    import arcgis.geoanalytics.use_proximity
    import arcgis.geocoding
    import arcgis.geoenrichment
    import arcgis.geometry
    import arcgis.geometry.filters
    import arcgis.geoprocessing
    import arcgis.mapping
    import arcgis.realtime
    import arcgis.schematics
    import arcgis.widgets
    import arcgis.apps
    import arcgis.apps.hub
    import arcgis.learn
    clear_arcgis_import_cache()

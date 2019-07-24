# Test that the imported arcgis API is the one from ../../src

from utils._common import *

def test_arcgis_being_imported_is_dev():
    import arcgis
    expected = os.path.join(GEOSAURUS_SRC_ARCGIS_DIR, "__init__.py").lower()
    actual = arcgis.__file__.lower()
    assert actual == expected

# Test that each module can be imported without SyntaxError (basic sanity)
# This type of import syntax (from foo import *) must be run in module level

from arcgis import *
from arcgis.gis import *
from arcgis.gis.admin import *
from arcgis.gis.server import *
from arcgis.env import *
from arcgis.features import *
from arcgis.features.analysis import *
from arcgis.features.analyze_patterns import *
from arcgis.features.elevation import *
from arcgis.features.enrich_data import *
from arcgis.features.find_locations import *
from arcgis.features.hydrology import *
from arcgis.features.manage_data import *
from arcgis.features.managers import *
from arcgis.features.summarize_data import *
from arcgis.features.use_proximity import *
from arcgis.raster import *
from arcgis.raster.analytics import *
from arcgis.raster.functions import *
from arcgis.raster.functions.gbl import *
from arcgis.raster.orthomapping import *
from arcgis.network import *
from arcgis.network.analysis import *
from arcgis.geoanalytics.analyze_patterns import *
from arcgis.geoanalytics.data_enrichment import *
from arcgis.geoanalytics.find_locations import *
from arcgis.geoanalytics.manage_data import *
from arcgis.geoanalytics.summarize_data import *
from arcgis.geoanalytics.use_proximity import *
from arcgis.geocoding import *
from arcgis.geoenrichment import *
from arcgis.geometry import *
from arcgis.geometry.filters import *
from arcgis.geoprocessing import *
from arcgis.mapping import *
from arcgis.realtime import *
from arcgis.schematics import *
from arcgis.widgets import *
from arcgis.apps import *
from arcgis.apps.hub import *
from arcgis.learn import *

def test_all_arcgis_submodule_imports():
    """Test individual imports inside of test itself"""
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

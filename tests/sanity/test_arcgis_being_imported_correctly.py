# Test that the imported arcgis API is the one from ../../src

from utils._common import *
from utils.imports import *

def test_arcgis_being_imported_is_dev():
    clear_arcgis_import_cache()
    import arcgis
    expected = os.path.join(GEOSAURUS_SRC_ARCGIS_DIR, "__init__.py").lower()
    actual = arcgis.__file__.lower()
    assert actual == expected
    clear_arcgis_import_cache()

# Test that each module can be imported without SyntaxError (basic sanity)
# This type of import syntax (from foo import *) must be run in module level

clear_arcgis_import_cache()
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
clear_arcgis_import_cache()

def test_all_arcgis_submodule_imports():
    """Test individual imports inside of test itself"""
    import_all_arcgis_submodules()


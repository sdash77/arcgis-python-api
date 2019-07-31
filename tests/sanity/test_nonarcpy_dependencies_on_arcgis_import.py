import sys
import builtins
from utils._common import *
from utils.imports import __import__custom, configure_imports, \
                          clear_arcgis_import_cache

__import__real = builtins.__import__

def test_no_pandas():
    configure_imports(__import__real = __import__real,
                      modules_to_raise_importerrors = ['pandas'])
    builtins.__import__ = __import__custom
    clear_arcgis_import_cache()

    import arcgis
    from arcgis.gis import GIS

    builtins.__import__ = __import__real
    clear_arcgis_import_cache()

def test_no_fastai():
    configure_imports(__import__real = __import__real,
                      modules_to_raise_importerrors = ['fastai'])
    builtins.__import__ = __import__custom
    clear_arcgis_import_cache()


    import arcgis
    import arcgis.learn
    from arcgis.learn import export_training_data
    from arcgis.learn import prepare_data
    from arcgis.learn import Model
    from arcgis.learn import detect_objects
    from arcgis.learn import UnetClassifier

    builtins.__import__ = __import__real
    clear_arcgis_import_cache()

def test_minimal_install():
    """
    This test is not complete -- should go through all referenced third
    party libs in the source and make sure they are added to this test.
    In theory, the basic functionality of the Python API can be used with
    just `six` in the environment
    """
    configure_imports(__import__real = __import__real,
                      modules_to_raise_importerrors = ['pandas',
                                                       'fastai',
                                                       'numpy',
                                                       'shapely',
                                                       'arcpy',
                                                       'matplotlib',
                                                       'ipywidgets'
                                                       ])
    builtins.__import__ = __import__custom
    clear_arcgis_import_cache()

    import arcgis
    from arcgis.gis import GIS

    builtins.__import__ = __import__real
    clear_arcgis_import_cache()

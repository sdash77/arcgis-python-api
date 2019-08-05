import sys
import builtins
from utils._common import *
from utils.imports import __import__custom, configure_imports, \
                          clear_arcgis_import_cache

__import__real = builtins.__import__

def test_no_ipywidgets():
    try:
        configure_imports(__import__real = __import__real,
        modules_to_raise_importerrors = ['ipywidgets'])
        builtins.__import__ = __import__custom
        clear_arcgis_import_cache()

        import arcgis

        builtins.__import__ = __import__real
        clear_arcgis_import_cache()

    except ImportError as e:
        builtins.__import__ = __import__real
        clear_arcgis_import_cache()
        raise Exception(_assemble_err_msg('ipywidgets')) from e

def test_no_pandas():
    try:
        configure_imports(__import__real = __import__real,
        modules_to_raise_importerrors = ['pandas'])
        builtins.__import__ = __import__custom
        clear_arcgis_import_cache()

        import arcgis
        from arcgis.gis import GIS

        builtins.__import__ = __import__real
        clear_arcgis_import_cache()

    except ImportError as e:
        builtins.__import__ = __import__real
        clear_arcgis_import_cache()
        raise Exception(_assemble_err_msg('pandas')) from e

def test_no_fastai():
    try:
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

    except ImportError as e:
        builtins.__import__ = __import__real
        clear_arcgis_import_cache()
        raise Exception(_assemble_err_msg('fastai')) from e

def test_minimal_install():
    """
    This test is not complete -- should go through all referenced third
    party libs in the source and make sure they are added to this test.
    In theory, the basic functionality of the Python API can be used with
    just `six` in the environment
    """
    mods_import_errors = ['pandas', 'fastai', 'numpy', 'shapely', 
                          'arcpy', 'matplotlib', 'ipywidgets']
 
    try:
        configure_imports(__import__real = __import__real,
                          modules_to_raise_importerrors = mods_import_errors)

        builtins.__import__ = __import__custom
        clear_arcgis_import_cache()

        import arcgis
        from arcgis.gis import GIS

        builtins.__import__ = __import__real
        clear_arcgis_import_cache()
    except ImportError as e:
        builtins.__import__ = __import__real
        clear_arcgis_import_cache()
        raise Exception(_assemble_err_msg(mods_import_errors)) from e

def _assemble_err_msg(module_names):
    return f"`arcgis` could not be imported when `{module_names}` are not" \
           f"in the environment. Please move your `import` statements either "\
           f"inside of a function or in a try: except statement."

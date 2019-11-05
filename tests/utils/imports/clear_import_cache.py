import sys

def clear_arcgis_import_cache():
    """Clears any `arcgis` import cache from sys.modules, forcing future
    `import arcgis` calls to run fresh
    """
    for module_key in list(sys.modules.keys()):
        if ("arcgis" in module_key) and ("test" not in module_key):
            del sys.modules[module_key]

def clear_all_import_cache():
    """Probably clears a lot of necessary things, avoid calling this"""
    for module_key in list(sys.modules.keys()):
        del sys.modules[module_key]

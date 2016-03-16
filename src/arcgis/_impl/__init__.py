from .portalpy import *
from .io import *
try:
    import arcpy
    from .prj import *
    arcpyFound = True
except:
    arcpyFound = False

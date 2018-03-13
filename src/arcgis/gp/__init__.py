try:
    import arcpy
    HASARCPY = True
except:
    HASARCPY = False

if HASARCPY:
    from arcgis.gp.analysis import *

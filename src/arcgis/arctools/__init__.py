try:
    import arcpy
    HASARCPY = True
except:
    HASARCPY = False

if HASARCPY:
    from arcgis.arctools.analysis import *

from arcgis.raster import _util

def generate_direct_access_url(expiration=None, *, gis=None):
    """helper function to get the direct access url for user rasterStore on ArcGIS Online"""
    return _util._generate_direct_access_url(expiration=expiration, gis=gis)

def upload_imagery_to_agol_userstore(files, direct_access_url=None, *, gis=None):
    """uploads a file to the image layer to AGOL and returns the list of urls"""

    return _util._upload_imagery_agol(files=files, direct_access_url=direct_access_url, gis=gis)

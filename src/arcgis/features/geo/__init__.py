try:
    import uuid
    import tempfile, os, shutil
    import arcpy
    name = "a%sa.gdb" % uuid.uuid4().hex[:5]
    fgdb = arcpy.CreateFileGDB_management(tempfile.gettempdir(), name)[0]
    shutil.rmtree(fgdb)
except:
    pass

import pandas as pd
from ._accessor import GeoAccessor, GeoSeriesAccessor, _is_geoenabled
from ._io.fileops import from_featureclass
__all__ = ['GeoAccessor', 'GeoSeriesAccessor', 'from_featureclass']

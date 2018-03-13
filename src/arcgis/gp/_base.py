import os
import sys
import copy
import tempfile

import arcpy
import pandas as pd
from arcgis.features import SpatialDataFrame

arcpy.env.overwriteOutput = True
#--------------------------------------------------------------------------
def _process_kwargs_new(db, **kwargs):
    '''converts any SDF to arcpy.FeatureSet and pd.DataFrame to arcpy.RecordSet
    '''
    import copy
    import os
    params = {}
    kwargs = dict(zip(db.values(), kwargs.values()))
    if 'out_feature_class' in kwargs and kwargs['out_feature_class'] is None:
        import uuid
        kwargs['out_feature_class'] = os.path.join(arcpy.env.scratchGDB,
                                                   "a" + uuid.uuid4().hex[:6])

    for k,v in kwargs.items():
        if str(k).lower() == 'kwargs':
            continue
        if isinstance(v, SpatialDataFrame):
            params[k] = v._to_arcpy_featureset()
        elif isinstance(v, pd.DataFrame):
            import tempfile, os, uuid
            d = tempfile.gettempdir()
            file_path = os.path.join(d,
                                     "a%s.csv" % uuid.uuid4().hex[:8])
            v.to_csv(path_or_buf=file_path)
            params[k] = file_path
        else:
            params[k] = v
    return params
#--------------------------------------------------------------------------
def _process_kwargs(argdb=None, **kwargs):
    '''converts any SDF to arcpy.FeatureSet and pd.DataFrame to arcpy.RecordSet
    '''
    import os
    import uuid
    import copy
    import json

    params = {}
    if ('out_feature_class' in kwargs and kwargs['out_feature_class'] is None):
        kwargs['out_feature_class'] = os.path.join(arcpy.env.scratchGDB,
                                                   "a" + uuid.uuid4().hex[:6])
    elif ('output_name' in kwargs and kwargs['output_name'] is None):
        kwargs['output_name'] = os.path.join(arcpy.env.scratchGDB,
                                             "a" + uuid.uuid4().hex[:6])
    for k,v in kwargs.items():
        if str(k).lower() == 'kwargs':
            continue
        if isinstance(v, SpatialDataFrame):
            params[k] = v.to_featureclass(out_location=arcpy.env.scratchGDB,
                                          out_name="a%s" % uuid.uuid4().hex[:7])
        elif isinstance(v, pd.DataFrame):
            import tempfile, os, uuid
            d = tempfile.gettempdir()
            file_path = os.path.join(d,
                                     "a%s.csv" % uuid.uuid4().hex[:8])
            v.to_csv(path_or_buf=file_path)
            params[k] = file_path
        else:
            params[k] = v
    inputs = {}
    if 'argdb' in argdb:
        del argdb['argdb']
    for k,v in argdb.items():
        if v in params:
            inputs[k] = params[v]
    return inputs
#--------------------------------------------------------------------------
def _process_results(result):
    '''converts any and all feature classes to SDF and Tables to pd.DataFrames'''
    results = []
    for i in range(result.outputCount):
        desc = arcpy.Describe(result[i])
        if desc.datasetType == 'Table':
            if os.path.dirname(result[i]).lower().find(".gdb") > -1:
                import tempfile
                tmpcsv = os.path.join(tempfile.gettempdir(), "dummy.csv")
                if os.path.isfile(tmpcsv):
                    os.remove(tmpcsv)
                csv_file = arcpy.CopyRows_management(in_rows=result[i],
                                                     out_table=tmpcsv)[0]
                results.append(pd.read_csv(tmpcsv))
        elif desc.datasetType == 'FeatureClass':
            results.append( SpatialDataFrame.from_featureclass(result[i]))
        else:
            results.append(result[i])
    return results


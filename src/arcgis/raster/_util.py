import json as _json
from arcgis.raster._layer import ImageryLayer as _ImageryLayer
import arcgis as _arcgis
import string as _string
import random as _random
from arcgis._impl.common._utils import _date_handler
import datetime

import logging as _logging
_LOGGER = _logging.getLogger(__name__)

try:
    import numpy as _np
    import matplotlib.pyplot as _plt
    from matplotlib.pyplot import cm as _cm
except:
    pass


def _set_context(params, function_context = None):
    out_sr = _arcgis.env.out_spatial_reference
    process_sr = _arcgis.env.process_spatial_reference
    out_extent = _arcgis.env.analysis_extent
    mask = _arcgis.env.mask
    snap_raster = _arcgis.env.snap_raster
    cell_size = _arcgis.env.cell_size
    parallel_processing_factor = _arcgis.env.parallel_processing_factor

    context = {}

    if out_sr is not None:
        context['outSR'] = {'wkid': int(out_sr)}

    if out_extent is not None:
        context['extent'] = out_extent

    if process_sr is not None:
        context['processSR'] = {'wkid': int(process_sr)}


    if mask is not None:
        if isinstance(mask, _ImageryLayer):
            context['mask'] = {"url":mask._url}
        elif isinstance(mask,str):
            context['mask'] = {"url":mask}
    
    if cell_size is not None:
        if isinstance(cell_size, _ImageryLayer):
            context['cellSize'] = {"url":cell_size._url}
        elif isinstance(cell_size,str):
            if 'http:' in cell_size or 'https:' in cell_size:
                context['cellSize'] = {"url":cell_size}
            else:
                context['cellSize'] = cell_size
        else:
            context['cellSize'] = cell_size

    if snap_raster is not None:
        if isinstance(snap_raster, _ImageryLayer):
            context['snapRaster'] = {"url":snap_raster._url}
        elif isinstance(mask,str):
            context['snapRaster'] = {"url":snap_raster}


    if parallel_processing_factor is not None:
        context['parallelProcessingFactor'] = parallel_processing_factor


    if function_context is not None:
        if context is not None:
            context.update({k: function_context[k] for k in function_context.keys()})

        else:
            context = function_context

    if context:
        params["context"] = _json.dumps(context)

def _id_generator(size=6, chars=_string.ascii_uppercase + _string.digits):
    return ''.join(_random.choice(chars) for _ in range(size))

def _set_time_param(time):
    time_val = time
    if time is not None:
        if type(time) is list:
            if isinstance(time[0], datetime.datetime) or isinstance(time[0], datetime.date):
                if time[0].tzname() is None or time[0].tzname() != "UTC":
                    time[0] = time[0].astimezone(datetime.timezone.utc)
            if isinstance(time[1], datetime.datetime) or isinstance(time[1], datetime.date):
                if time[1].tzname() is None or time[1].tzname() != "UTC":
                    time[1] = time[1].astimezone(datetime.timezone.utc)
            starttime = _date_handler(time[0])
            endtime = _date_handler(time[1])
            if starttime is None:
                starttime = 'null'
            if endtime is None:
                endtime = 'null'
            time_val = "%s,%s" % (starttime, endtime)
        else:
            time_val = _date_handler(time)

    return time_val

def _to_datetime(dt):
    import datetime
    return  datetime.datetime.utcfromtimestamp(dt/1000)

def _datetime2ole(date):
    #date = datetime.strptime(date, '%d-%b-%Y')
    import datetime
    OLE_TIME_ZERO = datetime.datetime(1899, 12, 30)
    delta = date - OLE_TIME_ZERO
    return float(delta.days) + (float(delta.seconds) / 86400)

def _ole2datetime(oledt):
    import datetime
    OLE_TIME_ZERO = datetime.datetime(1899, 12, 30, 0, 0, 0)
    try:
        return OLE_TIME_ZERO + datetime.timedelta(days=float(oledt))
    except:
        return datetime.datetime.utcfromtimestamp(oledt/1000)

def _iso_to_datetime(timestamp):
    format_string = '%Y-%m-%dT%H:%M:%S%z'
    try:
        colon = timestamp[-3]
        colonless_timestamp = timestamp
        if colon == ':':
            colonless_timestamp = timestamp[:-3] + timestamp[-2:]
        dt_ob = datetime.datetime.strptime(colonless_timestamp, format_string)
        return dt_ob.replace(tzinfo=None)
    except:
        try:
            format_string = '%Y-%m-%dT%H:%M:%S'
            dt_ob = datetime.datetime.strptime(timestamp, format_string)
            return dt_ob
        except:
            return timestamp

def _check_if_iso_format(timestamp):
    format_string = '%Y-%m-%dT%H:%M:%S%z'
    try:
        colon = timestamp[-3]
        colonless_timestamp = timestamp
        if colon == ':':
            colonless_timestamp = timestamp[:-3] + timestamp[-2:]
        dt_ob = datetime.datetime.strptime(colonless_timestamp, format_string)
        return True
    except:
        try:
            format_string = '%Y-%m-%dT%H:%M:%S'
            dt_ob = datetime.datetime.strptime(timestamp, format_string)
            return dt_ob
        except:
            return False

def _time_filter(time_extent,ele):
    if time_extent is not None:
        if isinstance(time_extent, datetime.datetime):
            if(ele<time_extent):
                return True
            else:
                return False
        elif isinstance(time_extent, list):
            if isinstance(time_extent[0], datetime.datetime) and isinstance(time_extent[1], datetime.datetime):                                                
                if(time_extent[0] < ele and ele < time_extent[1]):
                    return True
                else:
                    return False

        else:                            
            return True
    else:
        return True


def _linear_regression(sample_size, date_list, x, y):
    ncoefficient = 2
    if sample_size < ncoefficient:
        _LOGGER.warning("Trend line cannot be drawn. Insufficient points to plot Linear Trend Line")
        return [],[]

    AA = _np.empty([sample_size,ncoefficient], dtype=float, order='C')
    BB = _np.empty([sample_size,1], dtype=float, order='C')
    XX = _np.empty([ncoefficient,1], dtype=float, order='C')
    for i in range(sample_size):
        n=0
        AA[i][n] = date_list[i] 
        AA[i][n+1] = 1
        BB[i] = y[i]

    x1 = _np.linalg.lstsq(AA, BB, rcond=None)[0]

    YY=[]
    for i in range(sample_size):
        y_temp=x1[0][0]*date_list[i] + x1[1][0]
        YY.append(y_temp)
    return x,YY


def _harmonic_regression(sample_size, date_list, x, y, trend_order):
    PI2_Year = 3.14159265*2/365.25

    ncoefficient = 2 * (trend_order + 1)
    if sample_size < ncoefficient:
        _LOGGER.warning("Trend line cannot be drawn. Insufficient points to plot Harmonic Trend Line for trend order "+str(trend_order)+". Please try specifying a lower trend order.")
        return [],[]

    AA = _np.empty([sample_size,ncoefficient], dtype=float, order='C')
    BB = _np.empty([sample_size,1], dtype=float, order='C')
    XX = _np.empty([ncoefficient,1], dtype=float, order='C')

    for i in range(sample_size):
        n=0
        AA[i][n] = date_list[i] 
        AA[i][n+1] = 1

        for j in range(1,trend_order+1):
            AA[i][n + 2 * j] = _np.sin(PI2_Year * j * date_list[i])
            AA[i][n + 2 * j + 1] = _np.cos(PI2_Year * j * date_list[i])

        BB[i] = y[i]

    x1 = _np.linalg.lstsq(AA, BB, rcond=None)[0]
    YY=[]
    for i in range(sample_size):
        y_temp=x1[0][0]*date_list[i] + x1[1][0]
        for q in range(2,len(x1),2):
            y_temp=y_temp + x1[q][0] * _np.sin(2 * 3.14159265358979323846 * (q / 2) * date_list[i] / 365.25)
            y_temp=y_temp + x1[q+1][0] * _np.cos(2 * 3.14159265358979323846 * (q / 2) * date_list[i] / 365.25)
        YY.append(y_temp)
    return x, YY
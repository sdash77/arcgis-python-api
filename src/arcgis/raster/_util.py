import json as _json
from arcgis.raster._layer import ImageryLayer as _ImageryLayer
import arcgis as _arcgis
import string as _string
import random as _random
from arcgis._impl.common._utils import _date_handler
import datetime


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
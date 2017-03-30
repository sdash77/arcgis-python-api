from ._layer import ImageryLayer

def arg_statistics(layer, stat_type=None, min_value=None, max_value=None, undefined_class=None, out_pixel_type=None):
    """
    The arg_statistics function produces an output with a pixel value that represents a statistical metric from all
    bands of input rasters. The statistics can be the band index of the maximum, minimum, or median value, or the
    duration (number of bands) between a minimum and maximum value

    See http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/argstatistics-function.htm

    :param layer: the imagery layers filtered by where clause, spatial and temporal filters
    :param stat_type: one of "max", "min", "median", "duration"
    :param min_value: double, required if the type is duration
    :param max_value: double, required if the type is duration
    :param undefined_class: int, required if the type is maximum or minimum
    :return: the output raster with this function applied to it
    """
    # find oids given spatial and temporal filter and where clause

    if isinstance(layer, ImageryLayer):
        target_rasters = layer.filtered_rasters()
    else:
        raise RuntimeError('Pass in an ImageryLayer (which could be filtered by where clause, spatial and temporal filters) as the input layer.')

    stat_types = {
        'max': 0,
        'min': 1,
        'median': 2,
        'duration': 3
    }

    in_stat_type = stat_types[stat_type.lower()]

    template_dict = {
        "rasterFunction": "ArgStatistics",
        "rasterFunctionArguments": {
            "ArgStatisticsType": in_stat_type,
            "Rasters": target_rasters
        },
        "variableName": "Rasters"
    }

    if min_value is not None:
        template_dict["rasterFunctionArguments"]['MinValue'] = min_value
    if max_value is not None:
        template_dict["rasterFunctionArguments"]['MaxValue'] = max_value
    if undefined_class is not None:
        template_dict["rasterFunctionArguments"]['UndefinedClass'] = undefined_class

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }

def aspect(raster):
    """
    aspect identifies the downslope direction of the maximum rate of change in value from each cell to its neighbors.
    Aspect can be thought of as the slope direction. The values of the output raster will be the compass direction of
    the aspect. For more information, see
    <a href="http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/aspect-function.htm">Aspect function</a>
    and <a href="http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/how-aspect-works.htm">How Aspect works</a>.
    :param raster: the input raster / imagery layer
    :return: aspect applied to the input raster
    """
    if isinstance(raster, ImageryLayer):
        target_raster = raster.filtered_rasters()
    elif isinstance(raster, dict):
        layer = raster['layer']
        fn = raster['function_chain']
        target_raster =  '$$' if fn is None else fn
    else:
        raise RuntimeError('Pass in an ImageryLayer or an arcgis.raster.function applied to an ImageryLayer')

    # target_raster = '$$' if raster._fn is None else raster._fn

    template_dict = {
        "rasterFunction": "Aspect",
        "rasterFunctionArguments": {
            "Raster" : target_raster,
        }
    }

    return {
        'layer' : raster,
        'function_chain' : template_dict
    }

def band_arithmetic(raster="$$", method=None, band_indexes=None, out_pixel_type=None, variable_name='Raster'):
    template_dict = {
        "rasterFunction": "BandArithmetic",
        "rasterFunctionArguments": {
            "Raster": raster
        },

        "variableName": "Raster"
    }

    if method is not None:
        template_dict['rasterFunctionArguments']['Method'] = method

    if band_indexes is not None:
        template_dict["rasterFunctionArguments"]['BandIndexes'] = band_indexes

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return template_dict
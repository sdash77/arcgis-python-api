"""
Raster functions allow you to define processing operations that will be applied to one or more rasters.
These functions are applied to the raster data on the fly as the data is accessed and viewed; therefore,
they can be applied quickly without having to endure the time it would otherwise take to create a
processed product on disk, for which raster analytics tools like arcgis.raster.analytics.generate_raster can be used.

Functions can be applied to various rasters (or images), including the following:

Raster dataset layers
Mosaic datasets
Rasters within mosaic datasets
Imagery layers
Rasters within imagery layers
"""
from ._layer import ImageryLayer


def _raster_input(raster):

    if isinstance(raster, ImageryLayer):
        layer = raster
        raster = raster.filtered_rasters()
    elif isinstance(raster, dict) and 'function_chain' in raster:
        layer = raster['layer']
        raster = raster['function_chain']
    elif isinstance(raster, list):
        r0 = raster[0]
        if 'function_chain' in r0:
            layer = r0['layer']
            raster = [r['function_chain'] for r in raster]
    else:
        layer = None

    return layer, raster


def arg_statistics(rasters, stat_type=None, min_value=None, max_value=None, undefined_class=None, out_pixel_type=None):
    """
    The arg_statistics function produces an output with a pixel value that represents a statistical metric from all
    bands of input rasters. The statistics can be the band index of the maximum, minimum, or median value, or the
    duration (number of bands) between a minimum and maximum value

    See http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/argstatistics-function.htm

    :param rasters: the imagery layers filtered by where clause, spatial and temporal filters
    :param stat_type: one of "max", "min", "median", "duration"
    :param min_value: double, required if the type is duration
    :param max_value: double, required if the type is duration
    :param undefined_class: int, required if the type is maximum or minimum
    :return: the output raster with this function applied to it
    """
    # find oids given spatial and temporal filter and where clause

    layer, target_rasters = _raster_input(rasters)

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
        'layer' : rasters,
        'function_chain' : template_dict
    }

def arg_max(rasters, undefined_class=None, out_pixel_type=None):
    """
     In the ArgMax method, all raster bands from every input raster are assigned a 0-based incremental band index,
     which is first ordered by the input raster index, as shown in the table below, and then by the relative band order
     within each input raster.

    See http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/argstatistics-function.htm

    :param rasters: the imagery layers filtered by where clause, spatial and temporal filters
    :param undefined_class: int, required
    :return: the output raster with this function applied to it
    """
    return arg_statistics(rasters, "max", undefined_class=undefined_class, out_pixel_type=out_pixel_type)

def arg_min(rasters, undefined_class=None, out_pixel_type=None):
    """
    ArgMin is the argument of the minimum, which returns the Band index for which the given pixel attains
    its minimum value.

    See http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/argstatistics-function.htm

    :param rasters: the imagery layers filtered by where clause, spatial and temporal filters
    :param undefined_class: int, required
    :return: the output raster with this function applied to it
    """
    return arg_statistics(rasters, "min", undefined_class=undefined_class, out_pixel_type=out_pixel_type)

def arg_median(rasters, undefined_class=None, out_pixel_type=None):
    """
    The ArgMedian method returns the Band index for which the given pixel attains the median value of values
    from all bands.

    Consider values from all bands as an array. After sorting the array in ascending order, the median is the
    one value separating the lower half of the array from the higher half. More specifically, if the ascend-sorted
    array has n values, the median is the ith (0-based) value, where:

    See http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/argstatistics-function.htm

    :param rasters: the imagery layers filtered by where clause, spatial and temporal filters
    :param undefined_class: int, required
    :return: the output raster with this function applied to it
    """
    return arg_statistics(rasters, "median", undefined_class=undefined_class, out_pixel_type=out_pixel_type)

def duration(rasters, min_value=None, max_value=None, undefined_class=None, out_pixel_type=None):
    """
    Returns the duration (number of bands) between a minimum and maximum value.
    The Duration method finds the longest consecutive elements in the array, where each element has a value greater
    than or equal to min_value and less than or equal to max_value, and then returns its length.

    See http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/argstatistics-function.htm

    :param rasters: the imagery layers filtered by where clause, spatial and temporal filters
    :param undefined_class: int, required
    :return: the output raster with this function applied to it
    """
    return arg_statistics(rasters, "max",  min_value=min_value, max_value=max_value,
                          undefined_class=undefined_class, out_pixel_type=out_pixel_type)


def arithmetic(raster1, raster2, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None, operation_type=1):
    """
    The Arithmetic function performs an arithmetic operation between two rasters or a raster and a scalar, and vice versa.

    :param raster1: the first raster- imagery layers filtered by where clause, spatial and temporal filters
    :param raster2: the 2nd raster - imagery layers filtered by where clause, spatial and temporal filters
    :param extent_type: one of "FirstOf", "IntersectionOf" "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf "MeanOf", "LastOf"
    :param operation_type: int 1 = Plus, 2 = Minus, 3 = Multiply, 4=Divide, 5=Power, 6=Mode
    :return: the output raster with this function applied to it
    """

    layer1, raster1 = _raster_input(raster1)
    layer2, raster2 = _raster_input(raster2)

    layer = layer1 if layer1 is not None else layer2

    extent_types = {
        "FirstOf" : 0,
        "IntersectionOf" : 1,
        "UnionOf" : 2,
        "LastOf" : 3
    }

    cellsize_types = {
        "FirstOf" : 0,
        "MinOf" : 1,
        "MaxOf" : 2,
        "MeanOf" : 3,
        "LastOf" : 4
    }

    in_extent_type = extent_types[extent_type]
    in_cellsize_type = cellsize_types[cellsize_type]

    template_dict = {
        "rasterFunction": "Arithmetic",
        "rasterFunctionArguments": {
            "OperationType": operation_type,
            "Raster": raster1,
            "Raster2": raster2
        }
    }

    if in_extent_type is not None:
        template_dict["rasterFunctionArguments"]['ExtentType'] = in_extent_type
    if in_cellsize_type is not None:
        template_dict["rasterFunctionArguments"]['CellsizeType'] = in_cellsize_type

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }



def plus(raster1, raster2, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    Adds two rasters or a raster and a scalar, and vice versa

    :param raster1: the first raster- imagery layers filtered by where clause, spatial and temporal filters
    :param raster2: the 2nd raster - imagery layers filtered by where clause, spatial and temporal filters
    :param extent_type: one of "FirstOf", "IntersectionOf" "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf "MeanOf", "LastOf"
    :return: the output raster with this function applied to it
    """

    return arithmetic(raster1, raster2, extent_type, cellsize_type, out_pixel_type, 1)

def minus(raster1, raster2, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    Subtracts a raster or a scalar from another raster or a scaler

    :param raster1: the first raster- imagery layers filtered by where clause, spatial and temporal filters
    :param raster2: the 2nd raster - imagery layers filtered by where clause, spatial and temporal filters
    :param extent_type: one of "FirstOf", "IntersectionOf" "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf "MeanOf", "LastOf"
    :return: the output raster with this function applied to it
    """

    return arithmetic(raster1, raster2, extent_type, cellsize_type, out_pixel_type, 2)

def multiply(raster1, raster2, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    Multiplies two rasters or a raster and a scalar, and vice versa

    :param raster1: the first raster- imagery layers filtered by where clause, spatial and temporal filters
    :param raster2: the 2nd raster - imagery layers filtered by where clause, spatial and temporal filters
    :param extent_type: one of "FirstOf", "IntersectionOf" "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf "MeanOf", "LastOf"
    :return: the output raster with this function applied to it
    """

    return arithmetic(raster1, raster2, extent_type, cellsize_type, out_pixel_type, 3)

def divide(raster1, raster2, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    Divides two rasters or a raster and a scalar, and vice versa

    :param raster1: the first raster- imagery layers filtered by where clause, spatial and temporal filters
    :param raster2: the 2nd raster - imagery layers filtered by where clause, spatial and temporal filters
    :param extent_type: one of "FirstOf", "IntersectionOf" "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf "MeanOf", "LastOf"
    :return: the output raster with this function applied to it
    """

    return arithmetic(raster1, raster2, extent_type, cellsize_type, out_pixel_type, 4)

def power(raster1, raster2, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    Adds two rasters or a raster and a scalar, and vice versa

    :param raster1: the first raster- imagery layers filtered by where clause, spatial and temporal filters
    :param raster2: the 2nd raster - imagery layers filtered by where clause, spatial and temporal filters
    :param extent_type: one of "FirstOf", "IntersectionOf" "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf "MeanOf", "LastOf"
    :return: the output raster with this function applied to it
    """

    return arithmetic(raster1, raster2, extent_type, cellsize_type, out_pixel_type, 5)

def mode(raster1, raster2, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    Adds two rasters or a raster and a scalar, and vice versa

    :param raster1: the first raster- imagery layers filtered by where clause, spatial and temporal filters
    :param raster2: the 2nd raster - imagery layers filtered by where clause, spatial and temporal filters
    :param extent_type: one of "FirstOf", "IntersectionOf" "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf "MeanOf", "LastOf"
    :return: the output raster with this function applied to it
    """

    return arithmetic(raster1, raster2, extent_type, cellsize_type, out_pixel_type, 6)


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

    layer, target_raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Aspect",
        "rasterFunctionArguments": {
            "Raster" : target_raster,
        }
    }

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }


def band_arithmetic(raster, band_indexes=None, out_pixel_type=None, method=0):

    layer, target_raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "BandArithmetic",
        "rasterFunctionArguments": {
            "Method": method,
            "BandIndexes": band_indexes,
            "Raster": target_raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }

def ndvi(raster, band_indexes="4 3", out_pixel_type=None):
    return band_arithmetic(raster, band_indexes, out_pixel_type, 1)

def savi(raster, band_indexes="4 3 0.33", out_pixel_type=None):
    return band_arithmetic(raster, band_indexes, out_pixel_type, 2)

def tsavi(raster, band_indexes= "4 3 0.33 0.50 1.50", out_pixel_type=None):
    return band_arithmetic(raster, band_indexes, out_pixel_type, 3)

def msavi(raster, band_indexes="4 3", out_pixel_type=None):
    return band_arithmetic(raster, band_indexes, out_pixel_type, 4)

def gemi(raster, band_indexes="4 3", out_pixel_type=None):
    return band_arithmetic(raster, band_indexes, out_pixel_type, 5)

def pvi(raster, band_indexes="4 3 0.3 0.5", out_pixel_type=None):
    return band_arithmetic(raster, band_indexes, out_pixel_type, 6)

def gvitm(raster, band_indexes= "1 2 3 4 5 6", out_pixel_type=None):
    return band_arithmetic(raster, band_indexes, out_pixel_type, 7)

def sultan(raster, band_indexes="1 2 3 4 5 6", out_pixel_type=None):
    return band_arithmetic(raster, band_indexes, out_pixel_type, 8)

def expression(raster, expression="(B3 - B1 / B3 + B1)", out_pixel_type=None):
    return band_arithmetic(raster, expression, out_pixel_type, 0)

def classify(raster1, raster2, classifier_definition, out_pixel_type=None):
    """
    classifies a segmented raster to a categorical raster.

    :param raster1: the first raster - imagery layers filtered by where clause, spatial and temporal filters
    :param raster2: the 2nd raster - imagery layers filtered by where clause, spatial and temporal filters
    :param classifier_definition: the classifier parameters as a Python dictionary / json format

    :return: the output raster with this function applied to it
    """

    layer1, raster1 = _raster_input(raster1)
    layer2, raster2 = _raster_input(raster2)

    layer = layer1 if layer1 is not None else layer2

    template_dict = {
        "rasterFunction": "Classify",
        "rasterFunctionArguments": {
            "ClassifierDefinition": classifier_definition,
            "Raster": raster1,
            "Raster2": raster2
        }
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }

def clip(raster, geometry=None, clip_outside=True, out_pixel_type=None):
    """
    Clips a raster using a rectangular shape according to the extents defined or will clip a raster to the shape of an
    input polygon. The shape defining the clip can clip the extent of the raster or clip out an area within the raster.

    :param raster: input raster
    :param geometry: clipping geometry
    :param clip_outside: boolean, If True, the imagery outside the extents will be removed, else the imagery within the
            clipping_geometry will be removed.
    :param out_pixel_type: output pixel type
    :return: the clipped raster
    """
    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Clip",
        "rasterFunctionArguments": {
            "ClippingGeometry": geometry,
            "ClipType": 1 if clip_outside else 2,
            "Raster": raster
        }
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }


def colormap(raster, colormap_name=None, colormap=None, out_pixel_type=None):
    """
    Transforms the pixel values to display the raster data as a color (RGB) image, based on specific colors in
    a color map. For more information, see Colormap function at
    http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/colormap-function.htm

    :param raster: input raster
    :param colormap_name: colormap name, if one of Random | NDVI | Elevation | Gray
    :param colormap: [
      [<value1>, <red1>, <green1>, <blue1>], //[int, int, int, int]
      [<value2>, <red2>, <green2>, <blue2>]
    ],
    :param out_pixel_type: output pixel type
    :return: the clipped raster
    """
    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Colormap",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Rasters"

    }

    if colormap_name is not None:
        template_dict["rasterFunctionArguments"]['ColormapName'] = colormap_name
    if colormap is not None:
        template_dict["rasterFunctionArguments"]['Colormap'] = colormap

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }


def composite_band(rasters, out_pixel_type=None):
    """
    Combines multiple images to form a multiband image.

    :param rasters: input rasters
    :param out_pixel_type: output pixel type
    :return: the multiband image
    """
    layer, rasters = _raster_input(rasters)

    template_dict = {
        "rasterFunction": "CompositeBand",
        "rasterFunctionArguments": {
            "Raster": rasters
        }
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }


"""
Raster functions allow you to define processing operations that will be applied to one or more rasters.
These functions are applied to the raster data on the fly as the data is accessed and viewed; therefore,
they can be applied quickly without having to endure the time it would otherwise take to create a
processed product on disk, for which raster analytics tools like arcgis.raster.analytics.generate_raster can be used.

Functions can be applied to various rasters (or images), including the following:

Imagery layers
Rasters within imagery layers
"""
# Raster dataset layers
# Mosaic datasets
# Rasters within mosaic datasets
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
    """
    The band_arithmetic function performs an arithmetic operation on the bands of a raster. For more information,
    see Band Arithmetic function at http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/band-arithmetic-function.htm

    :param raster: the input raster / imagery layer
    :param band_indexes: band indexes or expression
    :param out_pixel_type: output pixel type
    :param method: int (0 = UserDefined, 1 = NDVI, 2 = SAVI, 3 = TSAVI, 4 = MSAVI, 5 = GEMI, 6 = PVI, 7 = GVITM, 8 = Sultan)
    :return: band_arithmetic applied to the input raster
    """

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
    """
    Normalized Difference Vegetation Index
    NDVI = ((NIR - Red)/(NIR + Red))

    :param raster: the input raster / imagery layer
    :param band_indexes: Band Indexes "NIR Red", e.g., "4 3"
    :param out_pixel_type: output pixel type
    :return: Normalized Difference Vegetation Index raster
    """
    return band_arithmetic(raster, band_indexes, out_pixel_type, 1)

def savi(raster, band_indexes="4 3 0.33", out_pixel_type=None):
    """
    Soil-Adjusted Vegetation Index
    SAVI = ((NIR - Red) / (NIR + Red + L)) x (1 + L)
    where L represents amount of green vegetative cover, e.g., 0.5

    :param raster: the input raster / imagery layer
    :param band_indexes: "BandIndexes": "NIR Red L", for example, "4 3 0.33"
    :param out_pixel_type: output pixel type
    :return: output raster
    """
    return band_arithmetic(raster, band_indexes, out_pixel_type, 2)

def tsavi(raster, band_indexes= "4 3 0.33 0.50 1.50", out_pixel_type=None):
    """
    Transformed Soil Adjusted Vegetation Index
    TSAVI = (s(NIR-s*Red-a))/(a*NIR+Red-a*s+X*(1+s^2))
    :param raster: the input raster / imagery layer
    :param band_indexes: "NIR Red s a X", e.g., "4 3 0.33 0.50 1.50" where a = the soil line intercept, s = the soil line slope, X = an adjustment factor that is set to minimize soil noise
    :param out_pixel_type: output pixel type
    :return: output raster
    """
    return band_arithmetic(raster, band_indexes, out_pixel_type, 3)

def msavi(raster, band_indexes="4 3", out_pixel_type=None):
    """
    Modified Soil Adjusted Vegetation Index
    MSAVI2 = (1/2)*(2(NIR+1)-sqrt((2*NIR+1)^2-8(NIR-Red)))
    :param raster: the input raster / imagery layer
    :param band_indexes: "NIR Red", e.g., "4 3"
    :param out_pixel_type: output pixel type
    :return: output raster
    """
    return band_arithmetic(raster, band_indexes, out_pixel_type, 4)

def gemi(raster, band_indexes="4 3", out_pixel_type=None):
    """
    Global Environmental Monitoring Index
    GEMI = eta*(1-0.25*eta)-((Red-0.125)/(1-Red))
    where eta = (2*(NIR^2-Red^2)+1.5*NIR+0.5*Red)/(NIR+Red+0.5)

    :param raster: the input raster / imagery layer
    :param band_indexes:"NIR Red", e.g., "4 3"
    :param out_pixel_type: output pixel type
    :return: output raster
    """
    return band_arithmetic(raster, band_indexes, out_pixel_type, 5)

def pvi(raster, band_indexes="4 3 0.3 0.5", out_pixel_type=None):
    """
    Perpendicular Vegetation Index
    PVI = (NIR-a*Red-b)/(sqrt(1+a^2))
    :param raster: the input raster / imagery layer
    :param band_indexes:"NIR Red a b", e.g., "4 3 0.3 0.5"
    :param out_pixel_type: output pixel type
    :return: output raster
    """
    return band_arithmetic(raster, band_indexes, out_pixel_type, 6)

def gvitm(raster, band_indexes= "1 2 3 4 5 6", out_pixel_type=None):
    """
    Green Vegetation Index - Landsat TM
    GVITM = -0.2848*Band1-0.2435*Band2-0.5436*Band3+0.7243*Band4+0.0840*Band5-1.1800*Band7
    :param raster: the input raster / imagery layer
    :param band_indexes:"NIR Red", e.g., "4 3"
    :param out_pixel_type: output pixel type
    :return: output raster
    """
    return band_arithmetic(raster, band_indexes, out_pixel_type, 7)

def sultan(raster, band_indexes="1 2 3 4 5 6", out_pixel_type=None):
    """
    Sultan's Formula (transform to 3 band 8 bit image)
        Band 1 = (Band5 / Band6) x 100
        Band 2 = (Band5 / Band1) x 100
        Band 3 = (Band3 / Band4) x (Band5 / Band4) x 100

    :param raster: the input raster / imagery layer
    :param band_indexes:"Band1 Band2 Band3 Band4 Band5 Band6", e.g., "1 2 3 4 5 6"
    :param out_pixel_type: output pixel type
    :return: output raster
    """
    return band_arithmetic(raster, band_indexes, out_pixel_type, 8)

def expression(raster, expression="(B3 - B1 / B3 + B1)", out_pixel_type=None):
    """
    Use a single-line algebraic formula to create a single-band output. The supported operators are -, +, /, *, and unary -.
    To identify the bands, prepend the band number with a B or b. For example: "BandIndexes":"(B1 + B2) / (B3 * B5)"
    :param raster: the input raster / imagery layer
    :param expression: the algebric formula
    :param out_pixel_type: output pixel type
    :return: output raster
    :return:
    """
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
        "variableName": "Raster"
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
            "Rasters": rasters
        },
        "variableName": "Rasters"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }

def contrast_brightness(raster, contrast_offset=2, brightness_offset=1, out_pixel_type=None):
    """
    The ContrastBrightness function enhances the appearance of raster data (imagery) by modifying the brightness or
    contrast within the image. This function works on 8-bit input raster only.
    :param raster: input raster
    :param contrast_offset: double, -100 to 100
    :param brightness_offset: double, -100 to 100
    :param out_pixel_type: pixel type of result raster
    :return: output raster
    """
    layer, raster = _raster_input(raster)

    template_dict = {
      "rasterFunction" : "ContrastBrightness",
      "rasterFunctionArguments" : {
        "Raster": raster,
        "ContrastOffset" : contrast_offset,
        "BrightnessOffset" : brightness_offset
      },
      "variableName" : "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def convolution(raster, kernel=None, out_pixel_type=None):
    """
    The Convolution function performs filtering on the pixel values in an image, which can be used for sharpening an
    image, blurring an image, detecting edges within an image, or other kernel-based enhancements. For more information,
     see Convolution function at http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/convolution-function.htm

    :param raster: input raster
    :param kernel well known kernel from arcgis.raster.kernels or user defined kernel passed as a list of list
    :param out_pixel_type: pixel type of result raster
    :return: output raster
    """
    layer, raster = _raster_input(raster)

    template_dict = {
      "rasterFunction" : "Convolution",
      "rasterFunctionArguments" : {
        "Raster": raster,
      },
      "variableName" : "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if (isinstance(kernel, int)):
        template_dict["rasterFunctionArguments"]['Type'] = kernel
    elif (isinstance(kernel, list)):
        numrows = len(kernel)
        numcols = len(kernel[0])
        flattened = [item for sublist in kernel for item in sublist]
        template_dict["rasterFunctionArguments"]['Columns'] = numcols
        template_dict["rasterFunctionArguments"]['Rows'] = numrows
        template_dict["rasterFunctionArguments"]['Kernel'] = flattened
    else:
        raise RuntimeError('Invalid kernel type - pass int or list of list: [[][][]...]')

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def curvature(raster, curvature_type='standard', z_factor=1, out_pixel_type=None):
    """
    The Curvature function displays the shape or curvature of the slope. A part of a surface can be concave or convex;
    you can tell that by looking at the curvature value. The curvature is calculated by computing the second derivative
    of the surface. Refer to this conceptual help on how it works.

    http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/curvature-function.htm

    :param raster: input raster
    :param curvature_type: 'standard', 'planform', 'profile'
    :param z_factor: double
    :param out_pixel_type: output pixel type
    :return: the output raster
    """
    layer, raster = _raster_input(raster)


    curv_types = {
        'standard': 0,
        'planform': 1,
        'profile': 2
    }

    in_curv_type = curv_types[curvature_type.lower()]

    template_dict = {
        "rasterFunction": "Curvature",
        "rasterFunctionArguments": {
            "Raster": raster,
            "Type": in_curv_type,
            "ZFactor": z_factor
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer' : layer,
        'function_chain' : template_dict
    }


def NDVI(raster, visible_band=2, ir_band=1, out_pixel_type=None):
    """
    The Normalized Difference Vegetation Index (ndvi) is a standardized index that allows you to generate an image
    displaying greenness (relative biomass). This index takes advantage of the contrast of the characteristics of
    two bands from a multispectral raster dataset—the chlorophyll pigment absorptions in the red band and the
    high reflectivity of plant materials in the near-infrared (NIR) band. For more information, see ndvi function.
    The arguments for the ndvi function are as follows:

    :param raster: input raster
    :param visible_band_id: int (zero-based band id, e.g. 2)
    :param infrared_band_id: int (zero-based band id, e.g. 1)
    :param out_pixel_type: output pixel type
    :return: the output raster
    The following equation is used by the NDVI function to generate a 0–200 range 8 bit result:
    NDVI = ((IR - R)/(IR + R)) * 100 + 100
    If you need the specific pixel values (-1.0 to 1.0), use the lowercase ndvi method.
    """
    layer, raster = _raster_input(raster)

    template_dict = {
      "rasterFunction" : "NDVI",
      "rasterFunctionArguments" : {
        "Raster": raster,
        "VisibleBandID" : visible_band,
        "InfraredBandID" : ir_band
      },
      "variableName" : "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def elevation_void_fill(raster, max_void_width=0, out_pixel_type=None):
    """
    The elevation_void_fill function is used to create pixels where holes exist in your elevation. Refer to
    <a href="http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/elevation-void-fill-function.htm">
    this conceptual help</a> on how it works. The arguments for the elevation_void_fill function are as follows:

    :param raster: input raster
    :param max_void_width: number. Maximum void width to fill. 0: fill all
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "ElevationVoidFill",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if max_void_width is not None:
        template_dict["rasterFunctionArguments"]["MaxVoidWidth"] = max_void_width

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def extract_band(raster, band_ids=None, band_names=None, band_wavelengths=None, missing_band_action=None,
                 wavelength_match_tolerance=None, out_pixel_type=None):
    """
    The extract_band function allows you to extract one or more bands from a raster, or it can reorder the bands in a
     multiband image.This function was added at 10.2.1.The arguments for the extract_band function are as follows:

    :param raster: input raster
    :param band_ids: array of int
    :param band_names: array of string
    :param band_wavelengths: array of double
    :param missing_band_action: int, 0 = esriMissingBandActionFindBestMatch, 1 = esriMissingBandActionFail
    :param wavelength_match_tolerance: double
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "ExtractBand",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if band_ids is not None:
        template_dict["rasterFunctionArguments"]["BandIDs"] = band_ids
    if band_names is not None:
        template_dict["rasterFunctionArguments"]["BandNames"] = band_names
    if band_wavelengths is not None:
        template_dict["rasterFunctionArguments"]["BandWavelengths"] = band_wavelengths
    if missing_band_action is not None:
        template_dict["rasterFunctionArguments"]["MissingBandAction"] = missing_band_action
    if wavelength_match_tolerance is not None:
        template_dict["rasterFunctionArguments"]["WavelengthMatchTolerance"] = wavelength_match_tolerance

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def geometric(raster, geodata_transforms=None, append_geodata_xform=None, z_factor=None, z_offset=None, constant_z=None,
              correct_geoid=None, out_pixel_type=None):
    """
    The geometric function transforms the image (for example, orthorectification) based on a sensor definition and a
    terrain model.This function was added at 10.1.The arguments for the geometric function are as follows:

    :param raster: input raster
    :param geodata_transforms: Please refer to the Geodata Transformations documentation for more details.
    :param append_geodata_xform: boolean
    :param z_factor: double
    :param z_offset: double
    :param constant_z: double
    :param correct_geoid: boolean
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Geometric",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if geodata_transforms is not None:
        template_dict["rasterFunctionArguments"]["GeodataTransforms"] = geodata_transforms
    if append_geodata_xform is not None:
        template_dict["rasterFunctionArguments"]["AppendGeodataXform"] = append_geodata_xform
    if z_factor is not None:
        template_dict["rasterFunctionArguments"]["ZFactor"] = z_factor
    if z_offset is not None:
        template_dict["rasterFunctionArguments"]["ZOffset"] = z_offset
    if constant_z is not None:
        template_dict["rasterFunctionArguments"]["ConstantZ"] = constant_z
    if correct_geoid is not None:
        template_dict["rasterFunctionArguments"]["CorrectGeoid"] = correct_geoid

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def hillshade(dem, azimuth=215.0, altitude=75.0, z_factor=0.3, slope_type=1, ps_power=None, psz_factor=None,
              remove_edge_effect=None, out_pixel_type=None):
    """
    A hillshade is a grayscale 3D model of the surface taking the sun's relative position into account to shade the image.
     For more information, see
     <a href='http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/hillshade-function.htm'>hillshade
     function</a> and <a href="http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/how-hillshade-works.htm">How hillshade works.</a>
     The arguments for the hillshade function are as follows:

    :param dem: input DEM
    :param azimuth: double (e.g. 215.0)
    :param altitude: double (e.g. 75.0)
    :param z_factor: double (e.g. 0.3)
    :param slope_type: new at 10.2. 1=DEGREE, 2=PERCENTRISE, 3=SCALED. default is 1.
    :param ps_power: new at 10.2. double, used together with SCALED slope type
    :param psz_factor: new at 10.2. double, used together with SCALED slope type
    :param remove_edge_effect: new at 10.2. boolean, true of false
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    raster = dem

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Hillshade",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if azimuth is not None:
        template_dict["rasterFunctionArguments"]["Azimuth"] = azimuth
    if altitude is not None:
        template_dict["rasterFunctionArguments"]["Altitude"] = altitude
    if z_factor is not None:
        template_dict["rasterFunctionArguments"]["ZFactor"] = z_factor
    if slope_type is not None:
        template_dict["rasterFunctionArguments"]["SlopeType"] = slope_type
    if ps_power is not None:
        template_dict["rasterFunctionArguments"]["PSPower"] = ps_power
    if psz_factor is not None:
        template_dict["rasterFunctionArguments"]["PSZFactor"] = psz_factor
    if remove_edge_effect is not None:
        template_dict["rasterFunctionArguments"]["RemoveEdgeEffect"] = remove_edge_effect

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def local(rasters, operation, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The local function allows you to perform bitwise, conditional, logical, mathematical, and statistical operations on
    a pixel-by-pixel basis. For more information, see
    <a href="http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/local-function.htm">local function</a>.

    License:At 10.5, you must license your ArcGIS Server as ArcGIS Server 10.5.1 Enterprise Advanced or
     ArcGIS Image Server to use this resource.
     At versions prior to 10.5, the hosting ArcGIS Server needs to have a Spatial Analyst license.

    The local function works on single band or the first band of an image only, and the output is single band.
    The arguments for the local function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param operation: int see reference at http://resources.arcgis.com/en/help/arcobjects-net/componenthelp/index.html#//004000000149000000
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    raster = rasters

    layer, raster = _raster_input(raster)


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
        "rasterFunction": "Local",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if operation is not None:
        template_dict["rasterFunctionArguments"]["Operation"] = operation
    if extent_type is not None:
        template_dict["rasterFunctionArguments"]["ExtentType"] = in_extent_type
    if cellsize_type is not None:
        template_dict["rasterFunctionArguments"]["CellsizeType"] = in_cellsize_type

    return {
        'layer': layer,
        'function_chain': template_dict
    }


###############################################  LOCAL FUNCTIONS  ######################################################

def plus(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The binary Plus (addition,+) operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 1, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def minus(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The binary Minus (subtraction,-) operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 2, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def times(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Times (multiplication,*) operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 3, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def sqrt(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Square Root operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 4, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def power(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Power operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 5, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def acos(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The acos operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 6, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def asin(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The asin operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 7, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def atan(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The ATan operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 8, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def atanh(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The ATanH operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 9, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def abs(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Abs operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 10, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def bitwise_and(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BitwiseAnd operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 11, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def bitwise_left_shift(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BitwiseLeftShift operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 12, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def bitwise_not(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BitwiseNot operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 13, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def bitwise_or(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BitwiseOr operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 14, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def bitwise_right_shift(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BitwiseRightShift operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 15, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def bitwise_xor(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BitwiseXOr operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 16, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def boolean_and(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BooleanAnd operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 17, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def boolean_not(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BooleanNot operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 18, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def boolean_or(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BooleanOr operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 19, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def boolean_xor(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The BooleanXOr operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 20, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def cos(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Cos operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 21, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def cosh(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The CosH operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 22, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def divide(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Divide operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 23, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def equal_to(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The EqualTo operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 24, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def exp(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Exp operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 25, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def exp10(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Exp10 operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 26, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def exp2(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Exp2 operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 27, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def greater_than(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The GreaterThan operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 28, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def greater_than_equal(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The GreaterThanEqual operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 29, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def int(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Int operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 30, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def is_null(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The IsNull operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 31, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def float(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Float operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 32, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def less_than(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The LessThan operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 33, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def less_than_equal(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The LessThanEqual operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 34, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def ln(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Ln operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 35, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def log10(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Log10 operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 36, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def log2(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Log2 operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 37, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def majority(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Majority operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 38, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def max(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Max operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 39, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def mean(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Mean operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 40, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def med(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Med operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 41, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def min(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Min operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 42, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def minority(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Minority operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 43, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def mod(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Mod operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 44, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def negate(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Negate operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 45, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def not_equal(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The NotEqual operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 46, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def range(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Range operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 47, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def round_down(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The RoundDown operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 48, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def round_up(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The RoundUp operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 49, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def set_null(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The SetNull operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 50, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def sin(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Sin operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 51, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def sinh(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The SinH operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 52, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def square(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Square operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 53, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def std(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Std operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 54, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def sum(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Sum operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 55, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def tan(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Tan operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 56, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def tanh(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The TanH operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 57, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def variety(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The Variety operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 58, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def acosh(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The ACosH operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 59, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def asinh(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The ASinH operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 60, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def atan2(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The ATan2 operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 61, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def float_divide(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The FloatDivide operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 64, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def floor_divide(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The FloorDivide operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 65, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def majority_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The MajorityIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 66, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def max_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The MaxIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 67, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def mean_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The MeanIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 68, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def med_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The MedIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 69, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def min_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The MinIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 70, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def minority_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The MinorityIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 71, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def range_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The RangeIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 72, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def std_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The StdIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 73, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def sum_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The SumIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 74, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def variety_ignore_no_data(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The VarietyIgnoreNoData operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 75, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)


def con(rasters, extent_type="FirstOf", cellsize_type="FirstOf", out_pixel_type=None):
    """
    The con operation
    This function works on single band or the first band of an image only, and the output is single band.
    The arguments for this function are as follows:

    :param rasters: array of rasters. If a scalar is needed for the operation, the scalar can be a double or string
    :param extent_type: one of "FirstOf", "IntersectionOf", "UnionOf", "LastOf"
    :param cellsize_type: one of "FirstOf", "MinOf", "MaxOf, "MeanOf", "LastOf"
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    return local(rasters, 76, extent_type=extent_type, cellsize_type=cellsize_type, out_pixel_type=out_pixel_type)

###############################################  LOCAL FUNCTIONS  ######################################################


def mask(raster, no_data_values=None, included_ranges=None, no_data_interpretation=None, out_pixel_type=None):
    """
    The mask function changes the image by specifying a certain pixel value or a range of pixel values as no data.
    The arguments for the mask function are as follows:

    :param raster: input raster
    :param no_data_values: array of string ["band0_val","band1_val",...]
    :param included_ranges: array of double [band0_lowerbound,band0_upperbound,band1...],
    :param no_data_interpretation: int 0=MatchAny, 1=MatchAll
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Mask",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if no_data_values is not None:
        template_dict["rasterFunctionArguments"]["NoDataValues"] = no_data_values
    if included_ranges is not None:
        template_dict["rasterFunctionArguments"]["IncludedRanges"] = included_ranges
    if no_data_interpretation is not None:
        template_dict["rasterFunctionArguments"]["NoDataInterpretation"] = no_data_interpretation

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def ml_classify(raster, signature, out_pixel_type=None):
    """
    The ml_classify function allows you to perform a supervised classification using the maximum likelihood classification algorithm. The hosting ArcGIS Server needs to have a Spatial Analyst license.LicenseLicense:At 10.5, you must license your ArcGIS Server as ArcGIS Server 10.5.1 Enterprise Advanced or ArcGIS Image Server to use this resource.At versions prior to 10.5, the hosting ArcGIS Server needs to have a Spatial Analyst license.This function was added at 10.2.1.The arguments for the ml_classify function are as follows:

    :param raster: input raster
    :param signature: string. a signature string returned from computeClassStatistics (GSG)
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "MLClassify",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if signature is not None:
        template_dict["rasterFunctionArguments"]["SignatureFile"] = signature

    return {
        'layer': layer,
        'function_chain': template_dict
    }

# See NDVI() above
# def ndvi(raster, visible_band_id=None, infrared_band_id=None, out_pixel_type=None):
#     """
#     The Normalized Difference Vegetation Index (ndvi) is a standardized index that allows you to generate an image displaying greenness (relative biomass). This index takes advantage of the contrast of the characteristics of two bands from a multispectral raster dataset—the chlorophyll pigment absorptions in the red band and the high reflectivity of plant materials in the near-infrared (NIR) band. For more information, see ndvi function.The arguments for the ndvi function are as follows:
#
#     :param raster: input raster
#     :param visible_band_id: int (zero-based band id, e.g. 2)
#     :param infrared_band_id: int (zero-based band id, e.g. 1)
#     :param out_pixel_type: output pixel type
#     :return: the output raster
#
#     """
#
#     layer, raster = _raster_input(raster)
#
#     template_dict = {
#         "rasterFunction": "NDVI",
#         "rasterFunctionArguments": {
#             "Raster": raster
#         },
#         "variableName": "Raster"
#     }
#
#     if out_pixel_type is not None:
#         template_dict["outputPixelType"] = out_pixel_type
#
#     if visible_band_id is not None:
#         template_dict["rasterFunctionArguments"]["VisibleBandID"] = visible_band_id
#     if infrared_band_id is not None:
#         template_dict["rasterFunctionArguments"]["InfraredBandID"] = infrared_band_id
#
#     return {
#         'layer': layer,
#         'function_chain': template_dict
#     }

# TODO: how does recast work?
# def recast(raster, < _argument_name1 >= None, < _argument_name2 >= None, out_pixel_type=None):
#     """
#     The recast function reassigns argument values in an existing function template.The arguments for the recast function are based on the function it is overwriting.
#
#     :param raster: input raster
#     :param <_argument_name1>: ArgumentName1 will be reassigned with ArgumentValue1
#     :param <_argument_name2>: ArgumentName1 will be reassigned with ArgumentValue2
#     :param out_pixel_type: output pixel type
#     :return: the output raster
#
#     """
#
#     layer, raster = _raster_input(raster)
#
#     template_dict = {
#         "rasterFunction": "Recast",
#         "rasterFunctionArguments": {
#             "Raster": raster
#         },
#         "variableName": "Raster"
#     }
#
#     if out_pixel_type is not None:
#         template_dict["outputPixelType"] = out_pixel_type
#
#     if < _argument_name1 > is not None:
#         template_dict["rasterFunctionArguments"]["<ArgumentName1>"] = < _argument_name1 >
#     if < _argument_name2 > is not None:
#         template_dict["rasterFunctionArguments"]["<ArgumentName2>"] = < _argument_name2 >
#
#     return {
#         'layer': layer,
#         'function_chain': template_dict
#     }


def remap(raster, input_ranges=None, output_values=None, geometry_type=None, geometries=None, no_data_ranges=None,
          allow_unmatched=None, out_pixel_type=None):
    """
    The remap function allows you to change or reclassify the pixel values of the raster data. For more information,
    see <a href="http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/remap-function.htm">remap function</a>.

    The arguments for the remap function are as follows:

    :param raster: input raster
    :param input_ranges: [double, double,...], input ranges are specified in pairs: from (inclusive) and to (exclusive).
    :param output_values: [double, ...], output values of corresponding input ranges
    :param geometry_type: added at 10.3
    :param geometries: added at 10.3
    :param no_data_ranges: [double, double, ...], nodata ranges are specified in pairs: from (inclusive) and to (exclusive).
    :param allow_unmatched: Boolean, specify whether to keep the unmatched values or turn into nodata.
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Remap",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if input_ranges is not None:
        template_dict["rasterFunctionArguments"]["InputRanges"] = input_ranges
    if output_values is not None:
        template_dict["rasterFunctionArguments"]["OutputValues"] = output_values
    if geometry_type is not None:
        template_dict["rasterFunctionArguments"]["GeometryType"] = geometry_type
    if geometries is not None:
        template_dict["rasterFunctionArguments"]["Geometries"] = geometries
    if no_data_ranges is not None:
        template_dict["rasterFunctionArguments"]["NoDataRanges"] = no_data_ranges
    if allow_unmatched is not None:
        template_dict["rasterFunctionArguments"]["AllowUnmatched"] = allow_unmatched

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def resample(raster, resampling_type=None, input_cellsize=None, out_pixel_type=None):
    """
    The resample function resamples pixel values from a given resolution.The arguments for the resample function are as follows:

    :param raster: input raster
    :param resampling_type: one of NearestNeighbor,Bilinear,Cubic,Majority,BilinearInterpolationPlus,BilinearGaussBlur,
            BilinearGaussBlurPlus, Average, Minimum, Maximum,VectorAverage(require two bands)
    :param input_cellsize: point that defines cellsize in source spatial reference
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)
    resample_types = {
        'NearestNeighbor': 0,
        'Bilinear': 1,
        'Cubic': 2,
        'Majority': 3,
        'BilinearInterpolationPlus': 4,
        'BilinearGaussBlur': 5,
        'BilinearGaussBlurPlus': 6,
        'Average': 7,
        'Minimum': 8,
        'Maximum': 9,
        'VectorAverage':10
    }

    if isinstance(resampling_type, str):
        resampling_type = resample_types[resampling_type]

    template_dict = {
        "rasterFunction": "Resample",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if resampling_type is not None:
        template_dict["rasterFunctionArguments"]["ResamplingType"] = resampling_type
    if input_cellsize is not None:
        template_dict["rasterFunctionArguments"]["InputCellsize"] = input_cellsize

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def segment_mean_shift(raster, spectral_detail=None, spatial_detail=None, spectral_radius=None, spatial_radius=None,
                       min_num_pixels_per_segment=None, out_pixel_type=None):
    """
    The segment_mean_shift function produces a segmented output. Pixel values in the output image represent the
    converged RGB colors of the segment. The input raster needs to be a 3-band 8-bit image. If the imagery layer is not
    a 3-band 8-bit unsigned image, you can use the Stretch function before the segment_mean_shift function.

    License:At 10.5, you must license your ArcGIS Server as ArcGIS Server 10.5.1 Enterprise Advanced or
    ArcGIS Image Server to use this resource.
    At versions prior to 10.5, the hosting ArcGIS Server needs to have a Spatial Analyst license.

    When specifying arguments for SegmentMeanShift, use either SpectralDetail,SpatialDetail as a pair, or use
    SpectralRadius, SpatialRadius. They have an inverse relationship. SpectralRadius = 21 - SpectralDetail,
    SpatialRadius = 21 - SpectralRadius

    The arguments for the segment_mean_shift function are as follows:

    :param raster: input raster
    :param spectral_detail: double 0-21. Bigger value is faster and has more segments.
    :param spatial_detail: int 0-21. Bigger value is faster and has more segments.
    :param spectral_radius: double. Bigger value is slower and has less segments.
    :param spatial_radius: int. Bigger value is slower and has less segments.
    :param min_num_pixels_per_segment: int
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "SegmentMeanShift",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if spectral_detail is not None:
        template_dict["rasterFunctionArguments"]["SpectralDetail"] = spectral_detail
    if spatial_detail is not None:
        template_dict["rasterFunctionArguments"]["SpatialDetail"] = spatial_detail
    if spectral_radius is not None:
        template_dict["rasterFunctionArguments"]["SpectralRadius"] = spectral_radius
    if spatial_radius is not None:
        template_dict["rasterFunctionArguments"]["SpatialRadius"] = spatial_radius
    if min_num_pixels_per_segment is not None:
        template_dict["rasterFunctionArguments"]["MinNumPixelsPerSegment"] = min_num_pixels_per_segment

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def shaded_relief(raster, azimuth=None, altitude=None, z_factor=None, colormap=None, slope_type=None, ps_power=None,
                  psz_factor=None, remove_edge_effect=None, out_pixel_type=None):
    """
    Shaded relief is a color 3D model of the terrain, created by merging the images from the Elevation-coded and
    Hillshade methods. For more information, see
    <a href="http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/shaded-relief-function.htm">Shaded relief</a> function.

    The arguments for the shaded_relief function are as follows:

    :param raster: input raster
    :param azimuth: double (e.g. 215.0)
    :param altitude: double (e.g. 75.0)
    :param z_factor: double (e.g. 0.3)
    :param colormap: [[<value1>, <red1>, <green1>, <blue1>], [<value2>, <red2>, <green2>, <blue2>]]
    :param slope_type: 1=DEGREE, 2=PERCENTRISE, 3=SCALED. default is 1.
    :param ps_power: double, used together with SCALED slope type
    :param psz_factor: double, used together with SCALED slope type
    :param remove_edge_effect: boolean, True or False
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "ShadedRelief",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if azimuth is not None:
        template_dict["rasterFunctionArguments"]["Azimuth"] = azimuth
    if altitude is not None:
        template_dict["rasterFunctionArguments"]["Altitude"] = altitude
    if z_factor is not None:
        template_dict["rasterFunctionArguments"]["ZFactor"] = z_factor
    if colormap is not None:
        template_dict["rasterFunctionArguments"]["Colormap"] = colormap
    if slope_type is not None:
        template_dict["rasterFunctionArguments"]["SlopeType"] = slope_type
    if ps_power is not None:
        template_dict["rasterFunctionArguments"]["PSPower"] = ps_power
    if psz_factor is not None:
        template_dict["rasterFunctionArguments"]["PSZFactor"] = psz_factor
    if remove_edge_effect is not None:
        template_dict["rasterFunctionArguments"]["RemoveEdgeEffect"] = remove_edge_effect

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def slope(dem, z_factor=None, slope_type=None, ps_power=None, psz_factor=None, remove_edge_effect=None,
          out_pixel_type=None):
    """
    slope represents the rate of change of elevation for each pixel. For more information, see
    <a href="http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/slope-function.htm">slope function</a>
    and <a href="http://desktop.arcgis.com/en/arcmap/latest/tools/spatial-analyst-toolbox/how-slope-works.htm">How slope works</a>.
    The arguments for the slope function are as follows:

    :param dem: input DEM
    :param z_factor: double (e.g. 0.3)
    :param slope_type: new at 10.2. 1=DEGREE, 2=PERCENTRISE, 3=SCALED. default is 1.
    :param ps_power: new at 10.2. double, used together with SCALED slope type
    :param psz_factor: new at 10.2. double, used together with SCALED slope type
    :param remove_edge_effect: new at 10.2. boolean, true of false
    :param dem: optional, default is the image service
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    raster = dem

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Slope",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if z_factor is not None:
        template_dict["rasterFunctionArguments"]["ZFactor"] = z_factor
    if slope_type is not None:
        template_dict["rasterFunctionArguments"]["SlopeType"] = slope_type
    if ps_power is not None:
        template_dict["rasterFunctionArguments"]["PSPower"] = ps_power
    if psz_factor is not None:
        template_dict["rasterFunctionArguments"]["PSZFactor"] = psz_factor
    if remove_edge_effect is not None:
        template_dict["rasterFunctionArguments"]["RemoveEdgeEffect"] = remove_edge_effect
    if dem is not None:
        template_dict["rasterFunctionArguments"]["DEM"] = dem

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def statistics(raster, kernel_columns=None, kernel_rows=None, stat_type=None, columns=None, rows=None,
               fill_no_data_only=None, out_pixel_type=None):
    """
    The statistics function calculates focal statistics for each pixel of an image based on a defined focal neighborhood.
    For more information, see
    <a href="http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/statistics-function.htm">statistics function</a>.
    The arguments for the statistics function are as follows:

    :param raster: input raster
    :param kernel_columns: int (e.g. 3)
    :param kernel_rows: int (e.g. 3)
    :param stat_type: int 1=Min, 2=Max, 3=Mean, 4=StandardDeviation
    :param columns: int (e.g. 3)
    :param rows: int (e.g. 3)
    :param fill_no_data_only: bool
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Statistics",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if kernel_columns is not None:
        template_dict["rasterFunctionArguments"]["KernelColumns"] = kernel_columns
    if kernel_rows is not None:
        template_dict["rasterFunctionArguments"]["KernelRows"] = kernel_rows
    if stat_type is not None:
        template_dict["rasterFunctionArguments"]["Type"] = stat_type
    if columns is not None:
        template_dict["rasterFunctionArguments"]["Columns"] = columns
    if rows is not None:
        template_dict["rasterFunctionArguments"]["Rows"] = rows
    if fill_no_data_only is not None:
        template_dict["rasterFunctionArguments"]["FillNoDataOnly"] = fill_no_data_only

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def stretch(raster, stretch_type=0, min=None, max=None, number_of_standard_deviations=None, statistics=None,
            dra=None, min_percent=None, max_percent=None, gamma=None, compute_gamma=None, sigmoid_strength_level=None,
            out_pixel_type=None):
    """
    The stretch function enhances an image through multiple stretch types. For more information, see
    <a href="http://desktop.arcgis.com/en/arcmap/latest/manage-data/raster-and-images/stretch-function.htm">stretch function</a>.

    Gamma stretch works with all stretch types. The Gamma parameter is needed when UseGamma is set to true. Min and Max
    can be used to define output minimum and maximum. DRA is used to get statistics from the extent in the export_image request.
    ComputeGamma will automatically calculate best gamma value to render exported image based on empirical model.

    Stretch type 0 (None) does not require other parameters.
    Stretch type 3 (StandardDeviation) requires NumberOfStandardDeviations, Statistics, or DRA (true).
    Stretch type 4 (Histogram Equalization) requires the source dataset to have histograms or additional DRA (true).
    Stretch type 5 (MinMax) requires Statistics or DRA (true).
    Stretch type 6 (PercentClip) requires MinPercent, MaxPercent, and DRA (true), or histograms from the source dataset.
    Stretch type 9 (sigmoid) does not require other parameters.

    Optionally, set the SigmoidStrengthLevel (1 to 6) to adjust the curvature of Sigmoid curve used in color stretch.


    The arguments for the stretch function are as follows:

    :param raster: input raster
    :param stretch_type: int (0 = None, 3 = StandardDeviation, 4 = Histogram Equalization, 5 = MinMax, 6 = PercentClip, 9 = Sigmoid)
    :param min: double
    :param max: double
    :param number_of_standard_deviations: double (e.g. 2.5)
    :param statistics: double (e.g. 2.5)[<min1>, <max1>, <mean1>, <standardDeviation1>], //[double, double, double, double][<min2>, <max2>, <mean2>, <standardDeviation2>]],
    :param dra: boolean. derive statistics from current request, Statistics parameter is ignored when DRA is true
    :param min_percent: double (e.g. 0.25), applicable to PercentClip
    :param max_percent: double (e.g. 0.5), applicable to PercentClip
    :param gamma: array of doubles
    :param compute_gamma: optional, applicable to any stretch type when "UseGamma" is "true"
    :param sigmoid_strength_level: int (1~6), applicable to Sigmoid
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Stretch",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if stretch_type is not None:
        template_dict["rasterFunctionArguments"]["StretchType"] = stretch_type
    if min is not None:
        template_dict["rasterFunctionArguments"]["Min"] = min
    if max is not None:
        template_dict["rasterFunctionArguments"]["Max"] = max
    if number_of_standard_deviations is not None:
        template_dict["rasterFunctionArguments"]["NumberOfStandardDeviations"] = number_of_standard_deviations
    if statistics is not None:
        template_dict["rasterFunctionArguments"]["Statistics"] = statistics
    if dra is not None:
        template_dict["rasterFunctionArguments"]["DRA"] = dra
    if min_percent is not None:
        template_dict["rasterFunctionArguments"]["MinPercent"] = min_percent
    if max_percent is not None:
        template_dict["rasterFunctionArguments"]["MaxPercent"] = max_percent
    if gamma is not None:
        template_dict["rasterFunctionArguments"]["Gamma"] = gamma
    if compute_gamma is not None:
        template_dict["rasterFunctionArguments"]["ComputeGamma"] = compute_gamma
    if sigmoid_strength_level is not None:
        template_dict["rasterFunctionArguments"]["SigmoidStrengthLevel"] = sigmoid_strength_level

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def threshold(raster, out_pixel_type=None):
    """
    The binary threshold function produces the binary image. It uses the Otsu method and assumes the input image to have
     a bi-modal histogram. The arguments for the threshold function are as follows:

    :param raster: input raster
    :param out_pixel_type: output pixel type
    :return: the output raster

    """
    threshold_type = 1
    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "Threshold",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if threshold_type is not None:
        template_dict["rasterFunctionArguments"]["ThresholdType"] = threshold_type

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def transpose_bits(raster, input_bit_positions=None, output_bit_positions=None, constant_fill_check=None,
                   constant_fill_value=None, fill_raster=None, out_pixel_type=None):
    """
    The transpose_bits function performs a bit operation. It extracts bit values from the source data and assigns them
    to new bits in the output data.The arguments for the transpose_bits function are as follows:

    If constant_fill_check is False, it assumes there is an input fill_raster. If an input fill_raster is not given,
    it falls back constant_fill_check to True and looks for constant_fill_value.
    Filling is used to initialize pixel values of the output raster.
    Landsat 8 has a quality assessment band. The following are the example input and output bit positions to extract
    confidence levels by mapping them to 0-3:
    Landsat 8 Water: {"input_bit_positions":[4,5],"output_bit_positions":[0,1]}
    Landsat 8 Cloud Shadow: {"input_bit_positions":[6,7],"output_bit_positions":[0,1]}
    Landsat 8 Vegetation: {"input_bit_positions":[8,9],"output_bit_positions":[0,1]}
    Landsat 8 Snow/Ice: {"input_bit_positions":[10,11],"output_bit_positions":[0,1]}
    Landsat 8 Cirrus: {"input_bit_positions":[12,13],"output_bit_positions":[0,1]}
    Landsat 8 Cloud: {"input_bit_positions":[14,15],"output_bit_positions":[0,1]}
    Landsat 8 Designated Fill: {"input_bit_positions":[0],"output_bit_positions":[0]}
    Landsat 8 Dropped Frame: {"input_bit_positions":[1],"output_bit_positions":[0]}
    Landsat 8 Terrain Occlusion: {"input_bit_positions":[2],"output_bit_positions":[0]}

    :param raster: input raster
    :param input_bit_positions: array of long, required
    :param output_bit_positions: array of long, required
    :param constant_fill_check: bool, optional
    :param constant_fill_value: int, required
    :param fill_raster: optional, the fill raster
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "TransposeBits",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if input_bit_positions is not None:
        template_dict["rasterFunctionArguments"]["InputBitPositions"] = input_bit_positions
    if output_bit_positions is not None:
        template_dict["rasterFunctionArguments"]["OutputBitPositions"] = output_bit_positions
    if constant_fill_check is not None:
        template_dict["rasterFunctionArguments"]["ConstantFillCheck"] = constant_fill_check
    if constant_fill_value is not None:
        template_dict["rasterFunctionArguments"]["ConstantFillValue"] = constant_fill_value
    if fill_raster is not None:
        template_dict["rasterFunctionArguments"]["FillRaster"] = fill_raster

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def unit_conversion(raster, from_unit=None, to_unit=None, out_pixel_type=None):
    """
    The unit_conversion function performs unit conversions.The arguments for the unit_conversion function are as follows:
    FromUnit and ToUnit take the following:
    Speed Units: 100=MetersPerSecond, 101=KilometersPerHour, 102 =Knots, 103 =FeetPerSecond, 104=MilesPerHour
    Temperature Units: 200=Celsius,201=Fahrenheit,202=Kelvin
    Distance Units: 1=Inches, 2=Points, 3=Feet,4=Yards,5=Miles, 6=NauticalMiles,7=Millimeters,8=Centimeters,9=Meters,
    10=Kilometers,11=DecimalDegrees,12=Decimeters

    :param raster: input raster
    :param from_unit: units constant listed below (int)
    :param to_unit: units constant listed below (int)
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "UnitConversion",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if from_unit is not None:
        template_dict["rasterFunctionArguments"]["FromUnit"] = from_unit
    if to_unit is not None:
        template_dict["rasterFunctionArguments"]["ToUnit"] = to_unit

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def vector_field_renderer(raster, is_uv_components=None, reference_system=None, mass_flow_angle_representation=None,
                          calculation_method="Vector Average", symbology_name="Single Arrow", out_pixel_type=None):
    """
    The vector_field_renderer function symbolizes a U-V or Magnitude-Direction raster.The arguments for the vector_field_renderer function are as follows:

    :param raster: input raster
    :param is_uv_components: bool
    :param reference_system: int 1=Arithmetic, 2=Angular
    :param mass_flow_angle_representation: int 0=from 1=to
    :param calculation_method: string, "Vector Average" |
    :param symbology_name: string, "Single Arrow" |
    :param out_pixel_type: output pixel type
    :return: the output raster

    """

    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": "VectorFieldRenderer",
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    if out_pixel_type is not None:
        template_dict["outputPixelType"] = out_pixel_type

    if is_uv_components is not None:
        template_dict["rasterFunctionArguments"]["IsUVComponents"] = is_uv_components
    if reference_system is not None:
        template_dict["rasterFunctionArguments"]["ReferenceSystem"] = reference_system
    if mass_flow_angle_representation is not None:
        template_dict["rasterFunctionArguments"]["MassFlowAngleRepresentation"] = mass_flow_angle_representation
    if calculation_method is not None:
        template_dict["rasterFunctionArguments"]["CalculationMethod"] = calculation_method
    if symbology_name is not None:
        template_dict["rasterFunctionArguments"]["SymbologyName"] = symbology_name

    return {
        'layer': layer,
        'function_chain': template_dict
    }


def apply(raster, fn_name, **kwargs):
    """
    Applies a server side raster function template defined by the imagery layer (image service)
    The name of the raster function template is available in the imagery layer properties.rasterFunctionInfos.

    Function arguments are optional; argument names and default values are created by the author of the raster function
    template and are not known through the API. A client can simply provide the name of the raster function template
    only or, optionally, provide arguments to overwrite the default values.
    For more information about authoring server-side raster function templates, see
    <a href="http://server.arcgis.com/en/server/latest/publish-services/windows/server-side-raster-functions.htm">Server-side raster functions</a>.

    :param raster: the input raster, or imagery layer
    :param fn_name: name of the server side raster function template, See imagery layer properties.rasterFunctionInfos
    :param kwargs: keyword arguments to override the default values of the raster function template
    :return: the output raster
    """
    layer, raster = _raster_input(raster)

    template_dict = {
        "rasterFunction": fn_name,
        "rasterFunctionArguments": {
            "Raster": raster
        },
        "variableName": "Raster"
    }

    for key, value in kwargs.iteritems():
        template_dict["rasterFunctionArguments"][key] = value

    return {
        'layer': layer,
        'function_chain': template_dict
    }

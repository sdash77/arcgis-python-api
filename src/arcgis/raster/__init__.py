"""
The arcgis.raster module containing classes and raster analysis functions for working with raster data and
imagery layers.

Raster data is made up of a grid of cells, where each cell or pixel can have a value. Raster data is useful
for storing data that varies continuously, as in a satellite image, a surface of chemical concentrations, or
an elevation surface.

Use arcgis.raster.is_analysis_supported(gis) to check if raster analysis is supported in your GIS.
"""

from .layer import ImageryLayer
from .analysis import generate_raster, rasterize, interpolate, copy_raster, summarize_raster_within, \
                       density, classify, segment_mean_shift, train_classifier, convert_raster_to_feature

__all__ = ['ImageryLayer', 'generate_raster', 'rasterize', 'interpolate', 'copy_raster', 'summarize_raster_within',
           'density', 'classify', 'segment_mean_shift', 'train_classifier', 'convert_raster_to_feature']

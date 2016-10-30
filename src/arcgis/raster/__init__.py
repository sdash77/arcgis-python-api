"""
Module containing classes for working with rasters and image layers and functions for raster analysis.

Use arcgis.raster.is_analysis_supported(gis) to check if raster analysis is supported in your GIS.
"""

from .layer import ImageLayer
from .analysis import generate_raster, rasterize, interpolate, copy_raster, summarize_raster_within, \
                       density, classify, segment_mean_shift, train_classifier, convert_raster_to_feature

__all__ = ['ImageLayer', 'generate_raster', 'rasterize', 'interpolate', 'copy_raster', 'summarize_raster_within',
           'density', 'classify', 'segment_mean_shift', 'train_classifier', 'convert_raster_to_feature']

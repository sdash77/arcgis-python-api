"""
Module for working with rasters and image layers
"""

from .layer import ImageLayer
from .analytics import generate_raster, rasterize, interpolate, copy_raster, summarize_raster_within, \
                       density, classify, segment_mean_shift, train_classifier, convert_raster_to_feature

__all__ = ['ImageLayer', 'generate_raster', 'rasterize', 'interpolate', 'copy_raster', 'summarize_raster_within',
           'density', 'classify', 'segment_mean_shift', 'train_classifier', 'convert_raster_to_feature']

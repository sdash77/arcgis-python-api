import os
import math
import numpy as np
import torch
from fastai.vision.data import ObjectItemList
from .common import ArcGISMSImage
from ..models._ssd_utils import SSDObjectCategoryList
from matplotlib import pyplot as plt
from matplotlib import patheffects

    
class SSDObjectMSItemList(ObjectItemList):
    "`ItemList` suitable for object detection on Multispectral Data."
    _label_cls,_square_show_res = SSDObjectCategoryList,False
    def open(self, fn):
        return ArcGISMSImage.open_gdal(fn)

def show_batch_pascal_voc_rectangles(self, rows=3, alpha=1, **kwargs): # parameters adjusted in kwargs 
    nrows = rows
    ncols = kwargs.get('ncols', nrows)
    #start_index = kwargs.get('start_index', 0) # Does not work with dataloader
    
    n_items = kwargs.get('n_items', nrows*ncols)
    n_items = min(n_items, len(self.x))
    nrows = math.ceil(n_items/ncols)

    type_data_loader = kwargs.get('data_loader', 'training') # options : traininig, validation, testing
    if type_data_loader == 'training':
        data_loader = self.train_dl
    elif type_data_loader == 'validation':
        data_loader = self.valid_dl
    elif type_data_loader == 'testing':
        data_loader = self.test_dl
    else:
        e = Exception(f'could not find {type_data_loader} in data.')
        raise(e)

    rgb_bands = kwargs.get('rgb_bands', self._symbology_rgb_bands)
    nodata = kwargs.get('nodata', 0)
    imsize = kwargs.get('imsize', 5)
    statistics_type = kwargs.get('statistics_type', 'dataset') # Accepted Values `dataset`, `DRA`
    label_font_size = kwargs.get('label_font_size', 16)

    e = Exception('`rgb_bands` should be a valid band_order, list or tuple of length 3 or 1.')
    symbology_bands = []
    if not ( len(rgb_bands) == 3 or len(rgb_bands) == 1 ):
        raise(e)
    for b in rgb_bands:
        if type(b) == str:
            b_index = self._bands.index(b)
        elif type(b) == int:
            self._bands[b] # To check if the band index specified by the user really exists.
            b_index = b
        else:
            raise(e)
        b_index = self._extract_bands.index(b_index)
        symbology_bands.append(b_index)

    # Get Batch
    x_batch, y_batch = [], []
    i = 0
    dl_iterater = iter(data_loader)
    while i < n_items:
        x, y = next(dl_iterater)
        x_batch.append(x)
        y_batch.append(y)
        i+=self.batch_size
    x_batch = torch.cat(x_batch)
    # Denormalize X
    x_batch = (self._scaled_std_values[self._extract_bands].view(1, -1, 1, 1).to(x_batch) * x_batch ) + self._scaled_mean_values[self._extract_bands].view(1, -1, 1, 1).to(x_batch)
    y_bboxes = []
    y_classes = []
    for yb in y_batch:
        y_bboxes.extend(yb[0])
        y_classes.extend(yb[1])
    #return y_bboxes, y_classes, x_batch

    # Extract RGB Bands
    symbology_x_batch = x_batch[:, symbology_bands]
    if statistics_type == 'DRA':
        shp = symbology_x_batch.shape
        min_vals = symbology_x_batch.view(shp[0], shp[1], -1).min(dim=2)[0]
        max_vals = symbology_x_batch.view(shp[0], shp[1], -1).max(dim=2)[0]
        symbology_x_batch = symbology_x_batch / ( max_vals.view(shp[0], shp[1], 1, 1) - min_vals.view(shp[0], shp[1], 1, 1) + .001 )

    # Channel first to channel last and clamp float values to range 0 - 1 for plotting
    symbology_x_batch = symbology_x_batch.permute(0, 2, 3, 1)
    # Clamp float values to range 0 - 1
    if symbology_x_batch.mean() < 1:
        symbology_x_batch = symbology_x_batch.clamp(0, 1)

    # Squeeze channels if single channel (1, 224, 224) -> (224, 224)
    if symbology_x_batch.shape[-1] == 1:
        symbology_x_batch = symbology_x_batch.squeeze()

    # Get color Array
    color_array = self._multispectral_color_array
    color_array[1:, 3] = alpha

    # Size for plotting
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*imsize, nrows*imsize))
    idx = 0
    for r in range(nrows):
        for c in range(ncols):
            if idx < symbology_x_batch.shape[0]:
                axi  = ax[r][c]
                axi.imshow(symbology_x_batch[idx])
                classes = y_classes[idx][y_classes[idx] > 0]
                bboxes = y_bboxes[idx][y_classes[idx] > 0]
                bboxes = (bboxes+1)*.5
                bboxes = bboxes.clamp(0, 1)*(x_batch.shape[-1]-1)
                for i, bbox in enumerate(bboxes):
                    xs = bbox[[1, 1, 3, 3, 1]]
                    ys = bbox[[0, 2, 2, 0, 0]]
                    color = self._multispectral_color_array[classes[i]]
                    axi.plot(xs, ys, color=color, linewidth=2)
                    axi.text(xs[0]+1, ys[0]+1+(label_font_size*(x_batch.shape[-1]-1)/256), self.classes[classes[i]], size=label_font_size, color=color, path_effects=[patheffects.Stroke(linewidth=.5, foreground='gray')])
                axi.axis('off')
            else:
                ax[r][c].axis('off')
            idx+=1

from fastai.vision import ImageSegment, Image
from fastai.vision.image import open_image, show_image, pil2tensor
from fastai.vision.data import SegmentationProcessor, ImageList
from fastai.layers import CrossEntropyFlat
from fastai.basic_train import LearnerCallback
import torch
import warnings
import PIL
import numpy as np
import os
import math

def _class_array_to_rbg(ca : 'classified_array', cm : 'color_mapping', nodata=0):
    im = np.expand_dims(ca, axis=2).repeat(3, axis=2)
    white_mask = im[im == nodata]
    for x in (np.unique(im)):
        if not x == nodata:
            for i in range(3):
                im[:,:,i][im[:,:,i] == x] = cm[x][i]
    im[white_mask] = 255
    return im

#def _show_batch_unet_multispectral(self, nrows=3, ncols=3, n_items=None, index=0, rgb_bands=None, nodata=0, alpha=0.7, imsize=5): # Proposed Parameters 
def _show_batch_unet_multispectral(self, rows=3, alpha=0.7, **kwargs): # parameters adjusted in kwargs
    import matplotlib.pyplot as plt
    from .._data import _tensor_scaler
   
    nrows = rows
    ncols = 3
    if kwargs.get('ncols', None) is not None:
        ncols = kwargs.get('ncols')
    
    n_items = None
    if kwargs.get('n_items', None) is not None:
        n_items = kwargs.get('n_items')

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

    rgb_bands = self._symbology_rgb_bands
    if kwargs.get('rgb_bands', None) is not None:
        rgb_bands = kwargs.get('rgb_bands')

    nodata = 0
    if kwargs.get('nodata', None) is not None:
        nodata = kwargs.get('nodata')

    index = 0
    if kwargs.get('index', None) is not None:
        index = kwargs.get('index')

    imsize = 5
    if kwargs.get('imsize', None) is not None:
        imsize = kwargs.get('imsize')

    statistics_type = kwargs.get('statistics_type', 'dataset') # Accepted Values `dataset`, `DRA`

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
    if n_items is None:
        n_items = nrows*ncols
    else:
        nrows = math.ceil(n_items/ncols)
    n_items = min(n_items, len(self.x))

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
    y_batch = torch.cat(y_batch)

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
                y_rgb = color_array[y_batch[idx][0]]#.cpu().numpy()
                #y_rgb = _class_array_to_rbg(y_batch[idx][0], self._multispectral_color_mapping, nodata)
                axi.imshow(y_rgb, alpha=alpha)
                axi.axis('off')
            else:
                ax[r][c].axis('off')
            idx+=1

class ArcGISImageSegment(Image):
    "Support applying transforms to segmentation masks data in `px`."
    def __init__(self, x, color_mapping=None):
        super(ArcGISImageSegment, self).__init__(x)
        self.color_mapping = color_mapping

    def lighting(self, func, *args, **kwargs):
        return self

    def refresh(self):
        self.sample_kwargs['mode'] = 'nearest'
        return super().refresh()

    @property
    def data(self):
        "Return this image pixels as a `LongTensor`."
        return self.px.long()

    def show(self, ax=None, figsize:tuple=(3,3), title=None, hide_axis:bool=True,
        cmap=None, alpha:float=0.5, **kwargs):
        "Show the `ImageSegment` on `ax`."
        if is_no_color(self.color_mapping):
            ## This condition will not be true.
            ax = show_image(self, ax=ax, hide_axis=hide_axis, cmap="tab20", figsize=figsize,
                        interpolation='nearest', alpha=alpha, vmin=0, **kwargs)
        else:     
            color_mapping = torch.tensor(list(self.color_mapping.values()))
            color_mapping = torch.cat((color_mapping.float()/255, torch.tensor([float(alpha)] * len(color_mapping)).view(-1, 1)), dim=1)
            color_mapping = torch.cat((torch.tensor([0., 0., 0., 0.]).view(1, -1), color_mapping), dim=0)
            ax = show_image(color_mapping[self.data[0]].permute(2, 0, 1), ax=ax, hide_axis=hide_axis, cmap=cmap, figsize=figsize,
                            interpolation='nearest', alpha=alpha, vmin=0, **kwargs)
        if title: ax.set_title(title)

class ArcGISMultispectralImageSegment():
    def __init__(self, tensor):
        self.data = tensor
        self.size = tensor.shape
        self.shape = tensor.shape

def is_no_color(color_mapping):
    if isinstance(color_mapping, dict):
        color_mapping = list(color_mapping.values())
    return (np.array(color_mapping) == [-1., -1., -1.]).any()

def is_contigous(class_values):
    flag = True
    for i in range(len(class_values) - 1):
        if class_values[i] + 1 != class_values[i+1]:
            flag = False
    return flag

def map_to_contigous(tensor, mapping):
    modified_tensor = torch.zeros_like(tensor)
    for i, value in enumerate(mapping):
        modified_tensor[tensor == value] = i
    return modified_tensor

class ArcGISSegmentationLabelList(ImageList):
    "`ItemList` for segmentation masks."
    _processor = SegmentationProcessor
    def __init__(self, items, classes=None, class_mapping=None, color_mapping=None, **kwargs):
        super().__init__(items, **kwargs)
        self.class_mapping = class_mapping
        self.color_mapping = color_mapping
        self.copy_new.append('classes')
        self.classes, self.loss_func = classes, CrossEntropyFlat(axis=1)
        self.is_contigous = is_contigous([0] + list(self.class_mapping.keys()))
        if not self.is_contigous:
            self.pixel_mapping = [0] + list(self.class_mapping.keys())

    def open(self, fn):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning) # EXIF warning from TiffPlugin
            x = PIL.Image.open(fn)
            if x.palette is not None:
                x = x.convert('P')
            else:
                x = x.convert('L')
            x = pil2tensor(x, np.float32)

        if not self.is_contigous:
            x = map_to_contigous(x, self.pixel_mapping)
        return ArcGISImageSegment(x, color_mapping=self.color_mapping)

    def analyze_pred(self, pred, thresh:float=0.5): 
        return pred.argmax(dim=0)[None]

    def reconstruct(self, t): 
        return ArcGISImageSegment(t, color_mapping=self.color_mapping)

class ArcGISSegmentationItemList(ImageList):
    "`ItemList` suitable for segmentation tasks."
    _label_cls, _square_show_res = ArcGISSegmentationLabelList, False

class ArcGISSegmentationMSLabelList(ArcGISSegmentationLabelList):
    def open(self, fn):
        import gdal
        path = str(os.path.abspath(fn))
        x = gdal.Open(path).ReadAsArray()
        x = torch.tensor(x.astype(np.long))[None]
        return ArcGISImageSegment(x, color_mapping=self.color_mapping)

class ArcGISSegmentationMSItemList(ImageList):
    "`ItemList` suitable for segmentation tasks."
    _label_cls, _square_show_res = ArcGISSegmentationMSLabelList, False
    def open(self, fn):
        import gdal
        path = str(os.path.abspath(fn))
        x = gdal.Open(path).ReadAsArray()
        #x = ArcGISImageMSSegment(x.astype(np.float32))
        x = torch.tensor(x.astype(np.float32))
        #x = ArcGISImageSegment( x[:3, ] )
        x = ArcGISMultispectralImageSegment(x)
        return x

class LabelCallback(LearnerCallback):
    def __init__(self, learn):
        super().__init__(learn)
        import pdb
        self.label_mapping = {value:(idx+1) for idx, value in enumerate(learn.data.class_mapping.keys())}
        
    def on_batch_begin(self, last_input, last_target, **kwargs):
        modified_target = torch.zeros_like(last_target)
        for label, idx in self.label_mapping.items():
            modified_target[last_target==label] = idx
        return {'last_input':last_input, 'last_target':modified_target}
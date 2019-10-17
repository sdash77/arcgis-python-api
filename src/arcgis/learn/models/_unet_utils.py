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

    ds = self.train_ds
    if kwargs.get('type_ds', None) is not None:
        type_ds = kwargs.get('type_ds')
        if getattr(self, type_ds, None) is not None:
            ds = getattr(self, type_ds)
        else:
            e = Exception(f'could not find {str(type_ds)} in data.')
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
        symbology_bands.append(b_index)

    # Get Batch
    if n_items is None:
        n_items = nrows*ncols
    else:
        nrows = math.ceil(n_items/ncols)
    n_items = min(n_items, len(self.x))

    x_batch, y_batch = [], []
    for i in range(index, index+n_items):
        x_batch.append(ds.x[i].data)
        y_batch.append(ds.y[i].data[0])
    x_batch = self._min_max_scaler(torch.stack(x_batch))
    symbology_x_batch = x_batch[:, symbology_bands].cpu().numpy()

    # Channel first to channel last for plotting
    symbology_x_batch = np.rollaxis(symbology_x_batch, 1, 4)
    if symbology_x_batch.max() < 1.5:
        symbology_x_batch = symbology_x_batch.clip(0, 1)

    # Size for plotting
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*imsize, nrows*imsize))
    idx = 0
    for r in range(nrows):
        for c in range(ncols):
            if idx < symbology_x_batch.shape[0]:
                axi  = ax[r][c]
                axi.imshow(symbology_x_batch[idx])
                y_rgb = _class_array_to_rbg(y_batch[idx], self._multispectral_color_mapping, nodata)
                axi.imshow(y_rgb, alpha=alpha)
                axi.axis('off')
            else:
                ax[r][c].axis('off')
            idx+=1

class ArcGISImageSegment(Image):
    "Support applying transforms to segmentation masks data in `px`."
    def __init__(self, x, cmap=None, norm=None):
        super(ArcGISImageSegment, self).__init__(x)
        self.cmap = cmap
        self.mplnorm = norm

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
        cmap='tab20', alpha:float=0.5, **kwargs):
        "Show the `ImageSegment` on `ax`."
        ax = show_image(self, ax=ax, hide_axis=hide_axis, cmap=self.cmap, figsize=figsize,
                        interpolation='nearest', alpha=alpha, vmin=0, norm=self.mplnorm, **kwargs)
        if title: ax.set_title(title)

class ArcGISMultispectralImageSegment():
    def __init__(self, tensor):
        self.data = tensor
        self.size = tensor.shape

def is_no_color(color_mapping):
    if isinstance(color_mapping, dict):
        color_mapping = list(color_mapping.values())
    return (np.array(color_mapping) == [-1., -1., -1.]).any()

class ArcGISSegmentationLabelList(ImageList):
    "`ItemList` for segmentation masks."
    _processor = SegmentationProcessor
    def __init__(self, items, classes=None, class_mapping=None, color_mapping=None, **kwargs):
        super().__init__(items, **kwargs)
        self.class_mapping = class_mapping
        self.color_mapping = color_mapping
        self.copy_new.append('classes')
        self.classes, self.loss_func = classes, CrossEntropyFlat(axis=1)

        if is_no_color(list(color_mapping.values())):
            self.cmap = 'tab20'  ## compute cmap from palette
            import matplotlib as mpl
            bounds = list(color_mapping.keys())
            if len(bounds) < 3: # Two handle two classes i am adding one number to the classes which is not already in bounds
                bounds = bounds + [max(bounds)+1]
            self.mplnorm = mpl.colors.BoundaryNorm(bounds, len(bounds))
        else:
            import matplotlib as mpl
            bounds = list(color_mapping.keys())
            if len(bounds) < 3: # Two handle two classes i am adding one number to the classes which is not already in bounds
                bounds = bounds + [max(bounds)+1]
            self.cmap = mpl.colors.ListedColormap(np.array(list(color_mapping.values()))/255)
            self.mplnorm = mpl.colors.BoundaryNorm(bounds, self.cmap.N)

        if len(color_mapping.keys()) == 1:
            self.cmap = 'tab20'
            self.mplnorm = None
        

    def open(self, fn):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning) # EXIF warning from TiffPlugin
            x = PIL.Image.open(fn)
            if x.palette is not None:
                x = x.convert('P')
            else:
                x = x.convert('L')
            x = pil2tensor(x, np.float32)

        return ArcGISImageSegment(x, cmap=self.cmap, norm=self.mplnorm)

    def analyze_pred(self, pred, thresh:float=0.5): 
        label_mapping = {(idx + 1):value for idx, value in enumerate(self.class_mapping.keys())}
        out = pred.argmax(dim=0)[None]
        predictions = torch.zeros_like(out)
        for key, value in label_mapping.items():
            predictions[out==key] = value
        return predictions

    def reconstruct(self, t): 
        return ArcGISImageSegment(t, cmap=self.cmap, norm=self.mplnorm)

class ArcGISSegmentationItemList(ImageList):
    "`ItemList` suitable for segmentation tasks."
    _label_cls, _square_show_res = ArcGISSegmentationLabelList, False

class ArcGISSegmentationMSLabelList(ArcGISSegmentationLabelList):
    def open(self, fn):
        import gdal
        path = str(os.path.abspath(fn))
        x = gdal.Open(path).ReadAsArray()
        x = torch.tensor(x.astype(np.long))[None]
        return ArcGISImageSegment(x, cmap=self.cmap, norm=self.mplnorm)

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
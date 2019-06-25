from fastai.vision import ImageSegment, Image
from fastai.vision.image import open_image, show_image, pil2tensor
from fastai.vision.data import SegmentationProcessor, ImageItemList
from fastai.layers import CrossEntropyFlat
from fastai.basic_train import LearnerCallback
import matplotlib.pyplot as plt
import torch
import warnings
import PIL
import numpy as np

class ArcGISImageSegment(Image):
    "Support applying transforms to segmentation masks data in `px`."
    def __init__(self, x, color_mapping=None, pixel_mapping=None):
        super(ArcGISImageSegment, self).__init__(x)
        self.color_mapping = color_mapping
        self.pixel_mapping = pixel_mapping

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
        arr = self.data.numpy()[0] # 1x224x224
        out_arr = np.zeros_like(self.data.numpy()[0])

        for c, p in self.pixel_mapping.items():
            out_arr[arr == p] = c       
        rgb_im = mask_to_rbg(out_arr, self.color_mapping)
        ax.imshow(rgb_im, alpha=alpha, interpolation='nearest', vmin=0)
        if hide_axis: ax.axis('off')
        if title: ax.set_title(title)

def is_no_color(color_mapping):
    if isinstance(color_mapping, dict):
        color_mapping = list(color_mapping.values())
    return (np.array(color_mapping) == [-1., -1., -1.]).any()


def mask_to_rbg(ca : 'mask_array', cm : 'color_mapping'):
    im = np.expand_dims(ca, axis=2).repeat(3, axis=2)
    vals = np.unique(ca)
    vals.sort()
    for x in vals:
        for i in range(3):
            im[:,:,i][im[:,:,i] == x] = cm[x][i]            
    return im    


class ArcGISSegmentationLabelList(ImageItemList):
    "`ItemList` for segmentation masks."
    _processor = SegmentationProcessor
    def __init__(self, items, classes=None, class_mapping=None, color_mapping=None, pixel_mapping=None, **kwargs):
        super().__init__(items, **kwargs)
        self.class_mapping = class_mapping
        self.color_mapping = color_mapping
        self.pixel_mapping = pixel_mapping
        self.copy_new.append('classes')
        self.classes, self.loss_func = classes, CrossEntropyFlat(axis=1)

    def open(self, fn):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning) # EXIF warning from TiffPlugin
            x = PIL.Image.open(fn)
            if x.palette is not None:
                x = x.convert('P')
            else:
                x = x.convert('L')
            x = pil2tensor(x, np.float32)

        return ArcGISImageSegment(x, color_mapping=self.color_mapping, pixel_mapping=self.pixel_mapping)

    def analyze_pred(self, pred, thresh:float=0.5): 
        # label_mapping = {(idx + 1):value for idx, value in enumerate(self.class_mapping.keys())}
        out = pred.argmax(dim=0)[None]
        predictions = torch.zeros_like(out)       
        for key, value in self.pixel_mapping.items():
            predictions[out==key] = int(value)
        return predictions

    def reconstruct(self, t): 
        return ArcGISImageSegment(t, color_mapping=self.color_mapping, pixel_mapping=self.pixel_mapping)

class ArcGISSegmentationItemList(ImageItemList):
    "`ItemList` suitable for segmentation tasks."
    _label_cls, _square_show_res = ArcGISSegmentationLabelList, False

class LabelCallback(LearnerCallback):
    def __init__(self, learn):
        super().__init__(learn)
        self.label_mapping = {value:(idx+1) for idx, value in enumerate(learn.data.class_mapping.keys())}
        
    def on_batch_begin(self, last_input, last_target, **kwargs):
        modified_target = torch.zeros_like(last_target)
        for idx, label in self.label_mapping.items():
            modified_target[last_target==label] = idx
        return last_input, modified_target
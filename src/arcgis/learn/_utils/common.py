from fastai.vision.data import ImageList
from fastai.vision import Image
import os
import torch
import numpy as np
from matplotlib import pyplot as plt

class ArcGISMSImage(Image):

    def show(self, ax=None, rgb_bands=None):
        if rgb_bands is None:
            rgb_bands = getattr(self, 'rgb_bands', [0, 1, 2])
        symbology_data = self.data[rgb_bands]
        im_shape = symbology_data.shape
        min_vals = symbology_data.view(im_shape[0], -1).min(dim=1)[0]
        max_vals = symbology_data.view(im_shape[0], -1).max(dim=1)[0]
        strechted_data = ( symbology_data - min_vals.view(im_shape[0], 1, 1) ) / ( max_vals.view(im_shape[0], 1, 1) - min_vals.view(im_shape[0], 1, 1) + .001 )
        data_to_plot = strechted_data.permute(1, 2, 0)
        if ax is not None:
            return ax.imshow(data_to_plot)
        else:
            return plt.imshow(data_to_plot)

    def print_method(self):
        return self.show()

    def _repr_png_(self):
        return self.show()
    
    def _repr_jpeg_(self): 
        return self.show()

    @classmethod
    def open_gdal(cls, path):
        import gdal
        path = str(os.path.abspath(path))
        x = gdal.Open(path).ReadAsArray()
        x = torch.tensor(x.astype(np.float32))
        if len(x.shape)==2:
            x = x.unsqueeze(0)
        return cls(x)

class ArcGISMSImageList(ImageList):
    "`ImageList` suitable for classification tasks."
    _square_show_res = False
    def open(self, fn):
        return ArcGISMSImage.open_gdal(fn)

def get_multispectral_data_params_from_emd(data, emd):
    data._is_multispectral = emd.get('IsMultispectral', False)
    if data._is_multispectral:
        data._bands = emd.get('Bands')
        data._imagery_type = emd.get("ImageryType")
        data._extract_bands = emd.get("ExtractBands")
        data._train_tail = False # Hardcoded because we are never going to train a model with empty data
        normalization_stats = dict(emd.get("NormalizationStats")) # Copy the normalization stats so that self._data.emd has no tensors other wise it will raise error while creating emd
        for _stat in normalization_stats:
            if normalization_stats[_stat] is not None:
                normalization_stats[_stat] = torch.tensor(normalization_stats[_stat])
            setattr(data, ('_'+_stat), normalization_stats[_stat])
        data._do_normalize = emd.get("DoNormalize")
    return data

def _get_post_processed_model(arcgis_model, input_normalization=True):
    from .object_detection import get_TFOD_post_processed_model
    from .image_classification import get_TFIC_post_processed_model
    if arcgis_model._backend == 'tensorflow':
        from .fastai_tf_fit import _pytorch_to_tf
        if arcgis_model.__class__.__name__ == 'SingleShotDetector':
            return get_TFOD_post_processed_model(arcgis_model, input_normalization=input_normalization)
        if arcgis_model.__class__.__name__ == 'FeatureClassifier':
            return get_TFIC_post_processed_model(arcgis_model, input_normalization=input_normalization)
    pass
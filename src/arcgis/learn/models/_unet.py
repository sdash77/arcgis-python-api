import json
from pathlib import Path
from ._codetemplate import image_classifier_prf
from ._arcgis_model import _EmptyData
from functools import partial
import math

try:
    from ._arcgis_model import ArcGISModel, SaveModelCallback, _set_multigpu_callback
    import torch
    from torchvision import models
    from fastai.vision.learner import unet_learner, cnn_config
    import numpy as np
    from ._unet_utils import is_no_color, LabelCallback, _class_array_to_rbg
    from fastai.callbacks import EarlyStoppingCallback
    from torch.nn import Module as NnModule
    HAS_FASTAI = True
except Exception as e:
    class NnModule():
        pass
    HAS_FASTAI = False


def accuracy(input, target, void_code=0, class_mapping=None):  
    target = target.squeeze(1)
    mask = target != void_code
    return (input.argmax(dim=1)[mask] == target[mask]).float().mean()


class UnetClassifier(ArcGISModel):
    """
    Creates a Unet like classifier based on given pretrained encoder.

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Required fastai Databunch. Returned data object from
                            `prepare_data` function.
    ---------------------   -------------------------------------------
    backbone                Optional function. Backbone CNN model to be used for
                            creating the base of the `UnetClassifier`, which
                            is `resnet34` by default.
    ---------------------   -------------------------------------------
    pretrained_path         Optional string. Path where pre-trained model is
                            saved.
    =====================   ===========================================

    :returns: `UnetClassifier` Object
    """

    def __init__(self, data, backbone=None, pretrained_path=None):

        super().__init__(data, backbone)

        self._code = image_classifier_prf

        backbone_cut = None
        backbone_split = None

        _backbone = self._backbone
        if hasattr(self, '_backbone_'):
            _backbone = self._backbone_
            
        if not (self._check_backbone_support(_backbone)):
            raise Exception(f"Enter only compatible backbones from {', '.join(self.supported_backbones)}")

        if hasattr(self, '_backbone_'):
            _backbone_meta = cnn_config(self._backbone_)
            backbone_cut = _backbone_meta['cut']
            backbone_split = _backbone_meta['split']

        acc_metric = partial(accuracy, void_code=0, class_mapping=data.class_mapping) 
        self.learn = unet_learner(data, arch=self._backbone, metrics=acc_metric, wd=1e-2, bottle=True, last_cross=True, cut=backbone_cut, split_on=backbone_split)
        self._arcgis_init_callback() # make first conv weights learnable
        self.learn.callbacks.append(LabelCallback(self.learn))  #appending label callback

        self.learn.model = self.learn.model.to(self._device)

        # _set_multigpu_callback(self) # MultiGPU doesn't work for U-Net. (Fastai-Forums)
        if pretrained_path is not None:
            self.load(pretrained_path)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%s>' % (type(self).__name__)

    @property
    def supported_backbones(self):
        return [*self._resnet_family]

    @classmethod
    def from_model(cls, emd_path, data=None):
        """
        Creates a Unet like classifier from an Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Esri Model Definition
                                file.
        ---------------------   -------------------------------------------
        data                    Required fastai Databunch or None. Returned data
                                object from `prepare_data` function or None for
                                inferencing.
        =====================   ===========================================
        
        :returns: `UnetClassifier` Object
        """
        return cls.from_emd(data, emd_path)

    @classmethod
    def from_emd(cls, data, emd_path):
        """
        Creates a Unet like classifier from an Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        data                    Required fastai Databunch or None. Returned data
                                object from `prepare_data` function or None for
                                inferencing.
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Esri Model Definition
                                file.
        =====================   ===========================================
        
        :returns: `UnetClassifier` Object
        """
        emd_path = Path(emd_path)
        with open(emd_path) as f:
            emd = json.load(f)

        model_file = Path(emd['ModelFile'])

        if not model_file.is_absolute():
            model_file = emd_path.parent / model_file

        model_params = emd['ModelParameters']

        try:
            class_mapping = {i['Value']: i['Name'] for i in emd['Classes']}
            color_mapping = {i['Value']: i['Color'] for i in emd['Classes']}
        except KeyError:
            class_mapping = {i['ClassValue']: i['ClassName'] for i in emd['Classes']}
            color_mapping = {i['ClassValue']: i['Color'] for i in emd['Classes']}

        resize_to = emd.get('resize_to')

        if data is None:
            data = _EmptyData(path=emd_path.parent.parent, loss_func=None, c=len(class_mapping) + 1,
                              chip_size=emd['ImageHeight'])
            data.class_mapping = class_mapping
            data.color_mapping = color_mapping
            data._is_multispectral = emd.get('IsMultispectral', False)
            if data._is_multispectral:
                data._bands = emd.get('Bands')
                data._imagery_type = emd.get("ImageryType")
                data._extract_bands = emd.get("ExtractBands")
                data._train_tail = False # Hardcoded because we are never going to train a model with empty data
                normalization_stats = emd.get("NormalizationStats")
                for _stat in normalization_stats:
                    if normalization_stats[_stat] is not None:
                        normalization_stats[_stat] = torch.tensor(normalization_stats[_stat])
                    setattr(data, ('_'+_stat), normalization_stats[_stat])
                data._do_normalize = emd.get("DoNormalize")
            data.emd_path = emd_path
            data.emd = emd

        data.resize_to = resize_to        

        return cls(data, **model_params, pretrained_path=str(model_file))

    @property
    def _model_metrics(self):
        return {'accuracy': self._get_model_metrics()}

    def _get_emd_params(self):
        import random
        _emd_template = {}
        _emd_template["Framework"] = "arcgis.learn.models._inferencing"
        _emd_template["ModelConfiguration"] = "_unet"
        _emd_template["InferenceFunction"] = "ArcGISImageClassifier.py"
        _emd_template["ExtractBands"] = [0, 1, 2]

        _emd_template['Classes'] = []
        class_data = {}
        for i, class_name in enumerate(self._data.classes[1:]):  # 0th index is background
            inverse_class_mapping = {v: k for k, v in self._data.class_mapping.items()}
            class_data["Value"] = inverse_class_mapping[class_name]
            class_data["Name"] = class_name
            color = [random.choice(range(256)) for i in range(3)] if is_no_color(self._data.color_mapping) else \
                self._data.color_mapping[inverse_class_mapping[class_name]]
            class_data["Color"] = color
            _emd_template['Classes'].append(class_data.copy())

        _emd_template["IsMultispectral"] = getattr(self, '_is_multispectral', False)
        if _emd_template["IsMultispectral"]:
            _emd_template["Bands"] = self._data._bands
            _emd_template["ImageryType"] = self._data._imagery_type
            _emd_template["ExtractBands"] = self._data._extract_bands
            _emd_template["NormalizationStats"] = {
                "band_min_values": self._data._band_min_values,
                "band_max_values": self._data._band_max_values,
                "band_mean_values": self._data._band_mean_values,
                "band_std_values": self._data._band_std_values,
                "scaled_min_values": self._data._scaled_min_values,
                "scaled_max_values": self._data._scaled_max_values,
                "scaled_mean_values": self._data._scaled_mean_values,
                "scaled_std_values": self._data._scaled_std_values
            }
            for _stat in _emd_template["NormalizationStats"]:
                if _emd_template["NormalizationStats"][_stat] is not None:
                    _emd_template["NormalizationStats"][_stat] = _emd_template["NormalizationStats"][
                        _stat].tolist()
            _emd_template["DoNormalize"] = self._data._do_normalize

        return _emd_template

    def _predict_batch(self, imagetensor_batch):
        predictions = self.learn.model.eval()(imagetensor_batch.to(self._device).float()).detach().cpu()
        return predictions.max(dim=1)[1]

    #def _show_results_multispectral(self, nrows=3, index=0, type_ds='valid', rgb_bands=None, nodata=0, alpha=0.7, imsize=5, top=0.97): # Proposed Parameters 
    def _show_results_multispectral(self, rows=5, alpha=0.7, **kwargs): # parameters adjusted in kwargs
        import matplotlib.pyplot as plt
        from .._data import _tensor_scaler

        # Get Number of items
        nrows = rows
        ncols=2

        type_data_loader = kwargs.get('data_loader', 'validation') # options : traininig, validation, testing
        if type_data_loader == 'training':
            data_loader = self._data.train_dl
        elif type_data_loader == 'validation':
            data_loader = self._data.valid_dl
        elif type_data_loader == 'testing':
            data_loader = self._data.test_dl
        else:
            e = Exception(f'could not find {type_data_loader} in data.')
            raise(e)

        rgb_bands = self._data._symbology_rgb_bands
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

        title_font_size = 16
        if kwargs.get('top', None) is not None:
            top = kwargs.get('top')
        else:
            top = 1 - (math.sqrt(title_font_size)/math.sqrt(100*nrows*imsize))

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
            b_index = self._data._extract_bands.index(b_index)
            symbology_bands.append(b_index)

        # Get Batch
        x_batch, y_batch = [], []
        i = 0
        dl_iterater = iter(data_loader)
        while i < nrows:
            x, y = next(dl_iterater)
            x_batch.append(x)
            y_batch.append(y)
            i+=self._data.batch_size
        x_batch = torch.cat(x_batch)
        # Denormalize X
        y_batch = torch.cat(y_batch)

        # Get Predictions
        predictions = []
        for i in range(0, x_batch.shape[0], self._data.batch_size):
            predictions.append(self._predict_batch(x_batch[i:i+self._data.batch_size]))
        predictions = torch.cat(predictions)

        # Denormalize X
        x_batch = (self._data._scaled_std_values[self._data._extract_bands].view(1, -1, 1, 1).to(x_batch) * x_batch ) + self._data._scaled_mean_values[self._data._extract_bands].view(1, -1, 1, 1).to(x_batch)
        
        # Extract RGB Bands
        symbology_x_batch = x_batch[:, symbology_bands]
        if statistics_type == 'DRA':
            shp = symbology_x_batch.shape
            min_vals = symbology_x_batch.view(shp[0], shp[1], -1).min(dim=2)[0]
            max_vals = symbology_x_batch.view(shp[0], shp[1], -1).max(dim=2)[0]
            symbology_x_batch = symbology_x_batch / ( max_vals.view(shp[0], shp[1], 1, 1) - min_vals.view(shp[0], shp[1], 1, 1) + .001 )
        
        # Channel first to channel last for plotting
        symbology_x_batch = symbology_x_batch.permute(0, 2, 3, 1)
        # Clamp float values to range 0 - 1
        if symbology_x_batch.mean() < 1:
            symbology_x_batch = symbology_x_batch.clamp(0, 1)

        # Get color Array
        color_array = self._data._multispectral_color_array
        color_array[1:, 3] = alpha

        # Size for plotting
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*imsize, nrows*imsize))
        fig.suptitle('Ground Truth / Predictions', fontsize=title_font_size)
        for r in range(nrows):
            ax[r][0].imshow(symbology_x_batch[r])
            y_rgb = color_array[y_batch[r][0]]
            ax[r][0].imshow(y_rgb, alpha=alpha)
            ax[r][0].axis('off')
            ax[r][1].imshow(symbology_x_batch[r])
            p_rgb = color_array[predictions[r]]
            ax[r][1].imshow(p_rgb, alpha=alpha)
            ax[r][1].axis('off')
            plt.subplots_adjust(top=top)

    def show_results(self, rows=5, **kwargs):
        """
        Displays the results of a trained model on a part of the validation set.
        """
        self._check_requisites()
        self.learn.callbacks = [x for x in self.learn.callbacks if not isinstance(x, LabelCallback)]
        if rows > len(self._data.valid_ds):
            rows = len(self._data.valid_ds)
        self.learn.show_results(rows=rows, **kwargs)

    def _get_model_metrics(self, **kwargs):
        checkpoint = kwargs.get('checkpoint', True)
        model_accuracy = self.learn.recorder.metrics[-1][0]
        if checkpoint:
            model_accuracy = np.min(self.learn.recorder.metrics)

        return float(model_accuracy)

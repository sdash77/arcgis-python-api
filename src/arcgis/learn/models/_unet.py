import json, tempfile
from pathlib import Path
from ._codetemplate import image_classifier_prf
from ._ssd import _EmptyData
from functools import partial

try:
    from ._arcgis_model import ArcGISModel, SaveModelCallback, _set_multigpu_callback
    import torch
    from torchvision import models
    from fastai.vision.learner import unet_learner
    import numpy as np
    from ._unet_utils import is_no_color, LabelCallback, _class_array_to_rbg
    from fastai.callbacks import EarlyStoppingCallback
    from torch.nn import Module as NnModule
    HAS_FASTAI = True
except Exception as e:
    class NnModule():
        pass
    HAS_FASTAI = False


def _mobilenet_split(m:NnModule): return m[0][0][0], m[1]

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

        if self._backbone == models.mobilenet_v2:
            backbone_cut = -1
            backbone_split = _mobilenet_split

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

    @classmethod
    def from_model(cls, emd_path, data=None):
        return cls.from_emd(data, emd_path)

    @classmethod
    def from_emd(cls, data, emd_path):
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
            data = _EmptyData(path=tempfile.TemporaryDirectory().name, loss_func=None, c=len(class_mapping) + 1,
                              chip_size=emd['ImageHeight'])
            data.class_mapping = class_mapping
            data.color_mapping = color_mapping

        data.resize_to = resize_to

        return cls(data, **model_params, pretrained_path=str(model_file))

    @property
    def _model_metrics(self):
        return {'accuracy': self._get_model_metrics()}
    
    def _create_emd(self, path):
        import random
        super()._create_emd(path)

        self._emd_template["Framework"] = "arcgis.learn.models._inferencing"
        self._emd_template["ModelConfiguration"] = "_unet"
        self._emd_template["InferenceFunction"] = "ArcGISImageClassifier.py"
        self._emd_template["ExtractBands"] = [0, 1, 2]

        self._emd_template['Classes'] = []
        class_data = {}
        for i, class_name in enumerate(self._data.classes[1:]):  # 0th index is background
            inverse_class_mapping = {v: k for k, v in self._data.class_mapping.items()}
            class_data["Value"] = inverse_class_mapping[class_name]
            class_data["Name"] = class_name
            color = [random.choice(range(256)) for i in range(3)] if is_no_color(self._data.color_mapping) else \
            self._data.color_mapping[inverse_class_mapping[class_name]]
            class_data["Color"] = color
            self._emd_template['Classes'].append(class_data.copy())

        json.dump(self._emd_template, open(path.with_suffix('.emd'), 'w'), indent=4)
        return path.stem

    def _predict_batch(self, imagetensor_batch):
        predictions = self.learn.model.eval()(imagetensor_batch.to(self._device)).detach().cpu()
        return  predictions.max(dim=1)[1]

    #def _show_results_multispectral(self, nrows=3, index=0, type_ds='valid', rgb_bands=None, nodata=0, alpha=0.7, imsize=5, top=0.97): # Proposed Parameters 
    def _show_results_multispectral(self, rows=5, alpha=0.7, **kwargs): # parameters adjusted in kwargs
        import matplotlib.pyplot as plt
        from .._data import _tensor_scaler

        # Get Number of items
        nrows = rows
        ncols=2

        ds = self._data.train_ds
        if kwargs.get('type_ds', None) is not None:
            type_ds = kwargs.get('type_ds')
            if getattr(self, type_ds, None) is not None:
                ds = getattr(self, type_ds)
            else:
                e = Exception(f'could not find {str(type_ds)} in data.')
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
            
        top = 0.97
        if kwargs.get('top', None) is not None:
            imsize = kwargs.get('top')

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
        x_batch, y_batch = [], []
        for i in range(index, index+nrows):
            x_batch.append(ds.x[i].data)
            y_batch.append(ds.y[i].data[0])
        x_batch = self._data._min_max_scaler(torch.stack(x_batch))
        symbology_x_batch = x_batch[:, symbology_bands].cpu().numpy()

        # Get Predictions
        predictions = []
        for i in range(0, x_batch.shape[0], self._data.batch_size):
            predictions.append(self._predict_batch(x_batch[i:i+self._data.batch_size]))

        # Channel first to channel last for plotting
        symbology_x_batch = np.rollaxis(symbology_x_batch, 1, 4)
        y_batch = torch.stack(y_batch).cpu().numpy()
        predictions = torch.cat(predictions).cpu().numpy()

        #return x_batch, y_batch, predictions

        # Size for plotting
        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*imsize, nrows*imsize))
        for r in range(nrows):
            ax[r][0].imshow(symbology_x_batch[r])
            y_rgb = _class_array_to_rbg(y_batch[r], self._data._multispectral_color_mapping, nodata)
            ax[r][0].imshow(y_rgb, alpha=alpha)
            ax[r][0].axis('off')
            ax[r][1].imshow(symbology_x_batch[r])
            p_rgb = _class_array_to_rbg(predictions[r], self._data._multispectral_color_mapping, nodata)
            ax[r][1].imshow(p_rgb, alpha=alpha)
            ax[r][1].axis('off')
            plt.subplots_adjust(top=top)

    def show_results(self, rows=5, **kwargs):
        """
        Displays the results of a trained model on a part of the validation set.
        """
        self.learn.callbacks = [x for x in self.learn.callbacks if not isinstance(x, LabelCallback)]
        if rows > self._data.batch_size:
            rows = self._data.batch_size
        self.learn.show_results(rows=rows, **kwargs)

    def _get_model_metrics(self, **kwargs):
        checkpoint = kwargs.get('checkpoint', True)
        model_accuracy = self.learn.recorder.metrics[-1][0]
        if checkpoint:
            model_accuracy = np.min(self.learn.recorder.metrics)

        return float(model_accuracy)

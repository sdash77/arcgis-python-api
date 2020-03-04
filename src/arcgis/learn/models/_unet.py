import json
from pathlib import Path
from ._codetemplate import image_classifier_prf
from ._arcgis_model import _EmptyData
from functools import partial
import math
from .._data import _raise_fastai_import_error  
import traceback    

try:
    from ._arcgis_model import ArcGISModel, SaveModelCallback, _set_multigpu_callback, _resnet_family
    import torch
    from torchvision import models
    from fastai.vision.learner import unet_learner, cnn_config
    import numpy as np
    from ._unet_utils import is_no_color, LabelCallback, _class_array_to_rbg, predict_batch, show_results_multispectral
    from fastai.callbacks import EarlyStoppingCallback
    from torch.nn import Module as NnModule
    from .._utils.common import get_multispectral_data_params_from_emd
    from ._psp_utils import accuracy
    from ._deeplab_utils import compute_miou
    HAS_FASTAI = True
except Exception as e:
    import_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
    class NnModule():
        pass
    HAS_FASTAI = False


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
        if hasattr(self, '_orig_backbone'):
            _backbone = self._orig_backbone
            
        if not (self._check_backbone_support(_backbone)):
            raise Exception(f"Enter only compatible backbones from {', '.join(self.supported_backbones)}")

        if hasattr(self, '_orig_backbone'):
            _backbone_meta = cnn_config(self._orig_backbone)
            backbone_cut = _backbone_meta['cut']
            backbone_split = _backbone_meta['split']

        self.learn = unet_learner(data, arch=self._backbone, metrics=accuracy, wd=1e-2, bottle=True, last_cross=True, cut=backbone_cut, split_on=backbone_split)
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
        """
        Supported torchvision backbones for this model.
        """        
        return UnetClassifier._supported_backbones()

    @staticmethod
    def _supported_backbones():
        return [*_resnet_family]

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
        if not HAS_FASTAI:
            _raise_fastai_import_error(import_exception=import_exception)
            
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
            data = get_multispectral_data_params_from_emd(data, emd)
                
            data.emd_path = emd_path
            data.emd = emd

        data.resize_to = resize_to        

        return cls(data, **model_params, pretrained_path=str(model_file))

    @property
    def _model_metrics(self):
        return {'accuracy': '{0:1.4e}'.format(self._get_model_metrics())}
        
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

        return _emd_template

    def _predict_batch(self, imagetensor_batch):
        return predict_batch(self, imagetensor_batch)

    def _show_results_multispectral(self, rows=5, alpha=0.7, **kwargs): # parameters adjusted in kwargs
        ax = show_results_multispectral(
            self, 
            nrows=rows, 
            alpha=alpha, 
            **kwargs
        )

    def show_results(self, rows=5, **kwargs):
        """
        Displays the results of a trained model on a part of the validation set.
        """
        self._check_requisites()
        self.learn.callbacks = [x for x in self.learn.callbacks if not isinstance(x, LabelCallback)]
        if rows > len(self._data.valid_ds):
            rows = len(self._data.valid_ds)
        self.learn.show_results(rows=rows, **kwargs)

    def accuracy(self):
        return self.learn.validate()[-1].tolist()     

    def _get_model_metrics(self, **kwargs):
        checkpoint = kwargs.get('checkpoint', True)
        if not hasattr(self.learn, 'recorder'):
            return 0.0

        try:
            model_accuracy = self.learn.recorder.metrics[-1][0]
            if checkpoint:
                model_accuracy = np.max(self.learn.recorder.metrics)
        except:
            model_accuracy = 0.0

        return float(model_accuracy)

    def mIOU(self, mean=False, show_progress=True):

        """
        Computes mean IOU on the validation set for each class.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        mean                    Optional bool. If False returns class-wise
                                mean IOU, otherwise returns mean iou of all
                                classes combined.   
        ---------------------   -------------------------------------------
        show_progress           Optional bool. Displays the prgress bar if
                                True.                     
        =====================   ===========================================
        
        :returns: `dict` if mean is False otherwise `float`
        """
        num_classes = torch.arange(self._data.c)
        miou = compute_miou(self, self._data.valid_dl, mean, num_classes, show_progress)
        if mean:
            return np.mean(miou)
        return dict(zip(['0'] + self._data.classes[1:], miou))
        
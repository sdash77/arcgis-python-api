import os, json, tempfile
from pathlib import Path
from ._codetemplate import image_classifier_prf
from ._arcgis_model import _raise_fastai_import_error
from functools import partial
from ._arcgis_model import ArcGISModel

try:
    from fastai.basic_train import Learner
    from ._arcgis_model import SaveModelCallback, _resnet_family, _vgg_family, _densenet_family
    from ._unet_utils import is_no_color, predict_batch, show_results_multispectral
    import torch
    from torch import nn
    import torch.nn.functional as F
    from torchvision import models
    from ._unet_utils import LabelCallback
    from ._arcgis_model import _EmptyData, _change_tail
    from fastai.vision import to_device
    import numpy as np
    from fastai.callbacks import EarlyStoppingCallback
    from fastai.torch_core import split_model_idx
    from fastai.vision import flatten_model
    from torchvision.models.segmentation.segmentation import _segm_resnet
    from torchvision.models.segmentation.deeplabv3 import DeepLabHead, DeepLabV3
    from torchvision.models.segmentation.fcn import FCNHead
    from ._deeplab_utils import Deeplab, compute_miou
    from .._utils.common import get_multispectral_data_params_from_emd
    HAS_FASTAI = True
except Exception as e:
    class DeepLabV3():
        pass
    HAS_FASTAI = False

class _DeepLabOverride(DeepLabV3):
    '''
    class to override the DeepLabV3 class such that after forwrd pass we can 
    take output as a tuple instead of dictionary in parent class.
    '''
    def __init__(self, backbone, classifier, aux_classifier=None):
        super().__init__(backbone, classifier, aux_classifier)

    def forward(self, x):
        result = super().forward(x)
        if self.training:
            return result['out'], result['aux']
        else:
            return result['out']

def _create_deeplab(num_class, pretrained=True, **kwargs):
    '''
    Create default torchvision pretrained model with resnet101.
    '''
    model = models.segmentation.deeplabv3_resnet101(pretrained=True, progress=True, **kwargs)
    model = _DeepLabOverride(model.backbone, model.classifier, model.aux_classifier)
    model.classifier = DeepLabHead(2048, num_class)
    model.aux_classifier = FCNHead(1024, num_class)

    return model

class DeepLab(ArcGISModel):
    """
    Creates a ``DeepLab`` Semantic segmentation object

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Required fastai Databunch. Returned data object from
                            ``prepare_data`` function.
    ---------------------   -------------------------------------------
    backbone                Optional function. Backbone CNN model to be used for
                            creating the base of the `DeepLab`, which
                            is `resnet101` by default since it is pretrained in
                            torchvision. It supports the ResNet,
                            DenseNet, and VGG families.
    ---------------------   -------------------------------------------
    pretrained_path         Optional string. Path where pre-trained model is
                            saved.
    =====================   ===========================================

    :returns: ``DeepLab`` Object
    """
    def __init__(self, data, backbone=None, pretrained_path=None):
        # Set default backbone to be 'resnet101'
        if backbone is None:
            backbone = models.resnet101

        super().__init__(data, backbone)
        
        _backbone = self._backbone
        if hasattr(self, '_orig_backbone'):
            _backbone = self._orig_backbone
    
        if not self._check_backbone_support(_backbone):
            raise Exception (f"Enter only compatible backbones from {', '.join(self.supported_backbones)}")

        self._code = image_classifier_prf
        if self._backbone.__name__ is 'resnet101':
            model = _create_deeplab(data.c)
            if self._is_multispectral:
                model = _change_tail(model, data)
        else:
            model = Deeplab(data.c, self._backbone, data.chip_size)

        self.learn = Learner(data, model, metrics=self._accuracy)
        self.learn.loss_func = self._deeplab_loss
        self.learn.model = self.learn.model.to(self._device)
        self._freeze()
        self._arcgis_init_callback() # make first conv weights learnable
        if pretrained_path is not None:
            self.load(pretrained_path)
    
    @property
    def supported_backbones(self):
        return DeepLab._supported_backbones()

    @staticmethod
    def _supported_backbones():
        return [*_resnet_family, *_densenet_family, *_vgg_family]

    @classmethod
    def from_model(cls, emd_path, data=None):
        """
        Creates a ``DeepLab`` semantic segmentation object from an Esri Model Definition (EMD) file.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        emd_path                Required string. Path to Esri Model Definition
                                file.
        ---------------------   -------------------------------------------
        data                    Required fastai Databunch or None. Returned data
                                object from ``prepare_data`` function or None for
                                inferencing.

        =====================   ===========================================

        :returns: `DeepLab` Object
        """

        emd_path = Path(emd_path)
        with open(emd_path) as f:
            emd = json.load(f)
            
        model_file = Path(emd['ModelFile'])
        
        if not model_file.is_absolute():
            model_file = emd_path.parent / model_file
            
        model_params = emd['ModelParameters']

        try:
            class_mapping = {i['Value'] : i['Name'] for i in emd['Classes']}
            color_mapping = {i['Value'] : i['Color'] for i in emd['Classes']}
        except KeyError:
            class_mapping = {i['ClassValue'] : i['ClassName'] for i in emd['Classes']} 
            color_mapping = {i['ClassValue'] : i['Color'] for i in emd['Classes']}                
        
        if data is None:
            empty_data = _EmptyData(path=emd_path.parent.parent, loss_func=None, c=len(class_mapping) + 1, chip_size=emd['ImageHeight'])
            empty_data.class_mapping = class_mapping
            empty_data.color_mapping = color_mapping
            empty_data = get_multispectral_data_params_from_emd(empty_data, emd)
            empty_data.emd_path = emd_path
            empty_data.emd = emd
            return cls(empty_data, **model_params, pretrained_path=str(model_file))
        else:
            return cls(data, **model_params, pretrained_path=str(model_file))

    def _get_emd_params(self):
        import random
        _emd_template = {}
        _emd_template["Framework"] = "arcgis.learn.models._inferencing"
        _emd_template["ModelConfiguration"] = "_deeplab_infrencing"
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

    def accuracy(self):
        return self.learn.validate()[-1].tolist()

    @property
    def _model_metrics(self):
        return {'accuracy': '{0:1.4e}'.format(self._get_model_metrics())}

    def _get_model_metrics(self, **kwargs):
        checkpoint = kwargs.get('checkpoint', True)
        if not hasattr(self.learn, 'recorder'):
            return 0.0

        model_accuracy = self.learn.recorder.metrics[-1][0]
        if checkpoint:
            model_accuracy = np.max(self.learn.recorder.metrics)             
        return float(model_accuracy)

    def _deeplab_loss(self, outputs, targets):
        targets = targets.squeeze(1).detach()
        criterion = nn.CrossEntropyLoss().to(self._device)
        if self.learn.model.training:
            out = outputs[0]
            aux = outputs[1]
        else: # validation
            out = outputs
        main_loss = criterion(out, targets)

        if self.learn.model.training:
            aux_loss = criterion(aux, targets)
            total_loss = main_loss + 0.4 * aux_loss
            return total_loss
        else:
            return main_loss

    def _freeze(self):
        "Freezes the pretrained backbone."
        for idx, i in enumerate(flatten_model(self.learn.model)):
            if isinstance(i, (nn.BatchNorm2d)):
                continue
            if hasattr(i, 'dilation'):
                dilation = i.dilation
                dilation = dilation[0] if isinstance(dilation, tuple) else dilation
                if dilation > 1:
                    break        
            for p in i.parameters():
                p.requires_grad = False

        self.learn.layer_groups = split_model_idx(self.learn.model, [idx])  ## Could also call self.learn.freeze after this line because layer groups are now present.
        self.learn.create_opt(lr=3e-3)

    def unfreeze(self):
        for _, param in self.learn.model.named_parameters():
            param.requires_grad = True

    def show_results(self, rows=5, **kwargs):
        """
        Displays the results of a trained model on a part of the validation set.
        """
        self._check_requisites()
        if rows > len(self._data.valid_ds):
            rows = len(self._data.valid_ds)
        self.learn.show_results(rows=rows, **kwargs) 

    def _show_results_multispectral(self, rows=5, alpha=0.7, **kwargs): # parameters adjusted in kwargs
        ax = show_results_multispectral(
            self, 
            nrows=rows, 
            alpha=alpha, 
            **kwargs
        )

    def _accuracy(self, input, target, void_code=0, class_mapping=None): 
        if self.learn.model.training: # while training
            input = input[0]

        target = target.squeeze(1)
        return (input.argmax(dim=1) == target).float().mean()

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

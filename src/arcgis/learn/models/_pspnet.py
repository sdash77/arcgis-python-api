import os, json, tempfile
from pathlib import Path
from ._codetemplate import image_classifier_prf
from ._arcgis_model import _raise_fastai_import_error
from functools import partial
from ._arcgis_model import ArcGISModel

try:
    from fastai.basic_train import Learner
    from ._arcgis_model import SaveModelCallback
    from ._unet_utils import is_no_color
    import torch
    from torch import nn
    import torch.nn.functional as F
    from torchvision import models
    from ._unet_utils import LabelCallback
    from ._arcgis_model import _EmptyData
    from fastai.vision import to_device
    from ._psp_utils import PSPNet, _pspnet_unet
    from fastai.vision.models import unet
    import numpy as np
    from fastai.callbacks import EarlyStoppingCallback
    from fastai.torch_core import split_model_idx
    from fastai.vision import flatten_model
    HAS_FASTAI = True
except Exception as e:
    HAS_FASTAI = False

def _pspnet_learner(data,  backbone, chip_size=224, pyramid_sizes=(1, 2, 3, 6), pretrained=True, **kwargs):
    "Build psp_net learner from `data` and `arch`."
    model = to_device(PSPNet(data.c, backbone, chip_size, pyramid_sizes, pretrained), data.device)
    learn = Learner(data, model, **kwargs)
    return learn

def _pspnet_learner_with_unet(data,  backbone, chip_size=224, pyramid_sizes=(1, 2, 3, 6), pretrained=True, **kwargs):
    "Build psp_net learner from `data` and `arch`."
    model = unet.DynamicUnet(encoder=_pspnet_unet(data.c, backbone, chip_size, pyramid_sizes, pretrained), n_classes=data.c, last_cross=False)
    learn = Learner(data, model, **kwargs)
    return learn


class PSPNetClassifier(ArcGISModel):

    """
    Model architecture from https://arxiv.org/abs/1612.01105.
    Creates a PSPNet Image Segmentation/ Pixel Classification model. 

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Required fastai Databunch. Returned data object from
                            `prepare_data` function.
    ---------------------   -------------------------------------------
    backbone                Optional function. Backbone CNN model to be used for
                            creating the base of the `PSPNetClassifier`, which
                            is `resnet50` by default. It supports the ResNet,
                            DenseNet, and VGG families.
    ---------------------   -------------------------------------------
    use_unet                Optional Bool. Specify whether to use Unet-Decoder or not,
                            Default True.                          
    ---------------------   -------------------------------------------
    pyramid_sizes           Optional List. The sizes at which the feature map is pooled at.
                            Currently set to the best set reported in the paper,
                            i.e, (1, 2, 3, 6)
    ---------------------   -------------------------------------------
    pretrained              Optional Bool. If True, use the pretrained backbone                                                                                 
    ---------------------   -------------------------------------------
    pretrained_path         Optional string. Path where pre-trained PSPNet model is
                            saved.
    =====================   ===========================================

    :returns: `PSPNetClassifier` Object
    """

    def __init__(self, data, backbone=None, use_unet=True, pyramid_sizes=[1, 2, 3, 6], pretrained_path=None):
        # Set default backbone to be 'resnet50'
        if backbone is None: 
            backbone = models.resnet50
      
        super().__init__(data, backbone)     

        # Check if a backbone provided is compatible, use resnet50 as default
        if not self._check_backbone_support(backbone):
            raise Exception (f"Enter only compatible backbones from {', '.join(self.supported_backbones)}")              

        self._code = image_classifier_prf
        self.pyramid_sizes = pyramid_sizes
        self._use_unet = use_unet
        if use_unet:
            self.learn = _pspnet_learner_with_unet(data, backbone=self._backbone, chip_size=self._data.chip_size, pyramid_sizes=pyramid_sizes, pretrained=True, metrics=self.accuracy)
        else:
            self.learn = _pspnet_learner(data, backbone=self._backbone, chip_size=self._data.chip_size, pyramid_sizes=pyramid_sizes, pretrained=True, metrics=self.accuracy)
            self.learn.loss_func = self._psp_loss
        self.learn.callbacks.append(LabelCallback(self.learn))  #appending label callback 

        if pretrained_path is not None:
            self.load(pretrained_path)
        
        self.freeze()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%s>' % (type(self).__name__)

    # Return a list of supported backbones names
    @property
    def supported_backbones(self):
        return [*self._resnet_family, *self._densenet_family, *self._vgg_family]

    @classmethod
    def from_model(cls, emd_path, data=None):
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
            empty_data = _EmptyData(path=tempfile.TemporaryDirectory().name, loss_func=None, c=len(class_mapping) + 1, chip_size=emd['ImageHeight'])
            empty_data.class_mapping = class_mapping
            empty_data.color_mapping = color_mapping
            return cls(empty_data, **model_params, pretrained_path=str(model_file))
        else:
            return cls(data, **model_params, pretrained_path=str(model_file)) 


    def accuracy(self, input, target, void_code=0, class_mapping=None): 
        if self.learn.model.training: # while training
            input = input[0]

        target = target.squeeze(1)
        mask = target != void_code
        return (input.argmax(dim=1)[mask] == target[mask]).float().mean()

    def _psp_loss(self, outputs, targets):
        targets = targets.squeeze().detach()
        criterion = nn.CrossEntropyLoss().cuda()

        if self.learn.model.training: # returns a tuple of aux_logits and main_logits while training
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

    def freeze(self):
        "Freezes the pretrained backbone."
        for idx, i in enumerate(flatten_model(self.learn.model)):
            if hasattr(i, 'dilation'):
                dilation = i.dilation
                dilation = dilation[0] if isinstance(dilation, tuple) else dilation
                if dilation > 1:
                    break        
            for p in i.parameters():
                p.requires_grad = False

        self.learn.layer_groups = split_model_idx(self.learn.model, [idx])  ## Could also call self.learn.freeze after this line because layer groups are now present.      
  
    def unfreeze(self):
        for _, param in self.learn.model.named_parameters():
            param.requires_grad = True
        
    def _create_emd(self, path):
        import random
        super()._create_emd(path)
        
        self._emd_template["ModelParameters"]["pyramid_sizes"] = self.pyramid_sizes
        self._emd_template["ModelParameters"]["use_unet"] = self._use_unet
        self._emd_template["Framework"] = "arcgis.learn.models._inferencing"
        self._emd_template["ModelConfiguration"] = "_psp"
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

    def show_results(self, rows=5, **kwargs):
        """
        Displays the results of a trained model on a part of the validation set.
        """
        if rows > self._data.batch_size:
            rows = self._data.batch_size
        self.learn.show_results(rows=rows, **kwargs)   

    @property
    def _model_metrics(self):
        return {'accuracy': self._get_model_metrics()}

    def _get_model_metrics(self, **kwargs):
        checkpoint = kwargs.get('checkpoint', True)
        model_accuracy = self.learn.recorder.metrics[-1][0]
        if checkpoint:
            model_accuracy = np.min(self.learn.recorder.metrics)             
        return float(model_accuracy)
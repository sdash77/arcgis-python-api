# MIT License

# Copyright (c) 2019 Hengshuang Zhao

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Based on https://github.com/hszhao/semseg

import torch
import warnings
import numpy as np
import torch.nn.functional as F
import torch.nn as nn
import torch
from torchvision import models
import math
from fastai.callbacks.hooks import hook_output
from fastai.vision.learner import create_body
from fastai.callbacks.hooks import model_sizes
from torchvision.models.segmentation.segmentation import _segm_resnet
from torchvision.models.segmentation.deeplabv3 import DeepLabHead, DeepLabV3
from torchvision.models.segmentation.fcn import FCNHead
from ._arcgis_model import _get_backbone_meta

class Deeplab(nn.Module):
    def __init__(self, num_classes, backbone_fn, chip_size=224):
        super().__init__()        
        if getattr(backbone_fn, '_is_multispectral', False):
            self.backbone = create_body(backbone_fn, pretrained=True, cut=_get_backbone_meta(backbone_fn.__name__)['cut'])
        else:
            self.backbone = create_body(backbone_fn, pretrained=True)
        
        backbone_name = backbone_fn.__name__

        ## Support for different backbones
        if "densenet" in backbone_name or "vgg" in backbone_name:
            hookable_modules = list(self.backbone.children())[0]
        else:
            hookable_modules = list(self.backbone.children())
        
        if "vgg" in backbone_name:
            modify_dilation_index = -5
        else:
            modify_dilation_index = -2
            
        if backbone_name == 'resnet18' or backbone_name == 'resnet34':
            module_to_check = 'conv' 
        else:
            module_to_check = 'conv2'
        
        ## Hook at the index where we need to get the auxillary logits out
        self.hook = hook_output(hookable_modules[modify_dilation_index])
        
        custom_idx = 0
        for i, module in enumerate(hookable_modules[modify_dilation_index:]): 
            dilation = 2 * (i + 1)
            padding = 2 * (i + 1)
            for n, m in module.named_modules():
                if module_to_check in n:
                    m.dilation, m.padding, m.stride = (dilation, dilation), (padding, padding), (1, 1)
                elif 'downsample.0' in n:
                    m.stride = (1, 1)                    
                    
            if "vgg" in backbone_fn.__name__:
                if isinstance(module, nn.Conv2d):
                    dilation = 2 * (custom_idx + 1)
                    padding = 2 * (custom_idx + 1)
                    module.dilation, module.padding, module.stride = (dilation, dilation), (padding, padding), (1, 1)
                    custom_idx += 1
        
        ## returns the size of various activations
        feature_sizes = model_sizes(self.backbone, size=(chip_size, chip_size))
        ## Geting the number of channel persent in stored activation inside of the hook
        num_channels_aux_classifier = self.hook.stored.shape[1]
        ## Get number of channels in the last layer
        num_channels_classifier = feature_sizes[-1][1]

        self.classifier = DeepLabHead(num_channels_classifier, num_classes)
        self.aux_classifier = FCNHead(num_channels_aux_classifier, num_classes)

    def forward(self, x):
        x_size = x.size()
        x = self.backbone(x)
        if self.training:
            aux_l = self.aux_classifier(self.hook.stored)
        
        ## Remove hook to free up memory.
        self.hook.remove()
        x = self.classifier(x)
        result = F.interpolate(x, x_size[2:], mode='bilinear', align_corners=False)
        if self.training:
            x = F.interpolate(aux_l, x_size[2:], mode='bilinear', align_corners=False)
            return result, x
        else:
            return F.interpolate(x, x_size[2:], mode='bilinear', align_corners=False) 
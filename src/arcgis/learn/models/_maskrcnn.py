from ._arcgis_model import ArcGISModel
import tempfile
from pathlib import Path
import json
from ._codetemplate import code
from ._arcgis_model import _EmptyData
import logging
from ._codetemplate import instance_detector_prf

try:
    import torch
    from fastai.vision.learner import cnn_learner
    from fastai.callbacks.hooks import model_sizes
    from fastai.vision.learner import create_body
    from fastai.vision.image import open_image
    from torchvision.models import resnet34
    from torchvision import models
    import numpy as np
    from .._data import prepare_data, _raise_fastai_import_error
    from fastai.callbacks import EarlyStoppingCallback
    from ._arcgis_model import SaveModelCallback, _set_multigpu_callback
    import torchvision
    from torchvision import models
    from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
    from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
    from fastai.basic_train import Learner
    from ._maskrcnn_utils import is_no_color, mask_rcnn_loss, train_callback
    from fastai.torch_core import split_model_idx
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    HAS_FASTAI = True
except Exception as e:
    #raise Exception(e)
    HAS_FASTAI = False


class MaskRCNN(ArcGISModel):
    """
    Creates a ``MaskRCNN`` Instance segmentation object

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Required fastai Databunch. Returned data object from
                            ``prepare_data`` function.
    ---------------------   -------------------------------------------
    backbone                Optional function. Backbone CNN model to be used for
                            creating the base of the `MaskRCNN`, which
                            is `resnet50` by default. 
                            Compatible backbones: 'resnet50'
    ---------------------   -------------------------------------------
    pretrained_path         Optional string. Path where pre-trained model is
                            saved.
    =====================   ===========================================

    :returns: ``MaskRCNN`` Object
    """
    def __init__(self, data, backbone=None, pretrained_path=None):

        super().__init__(data, backbone)
    
        self._backbone = models.resnet50

        #if not self._check_backbone_support(self._backbone):
        #    raise Exception (f"Enter only compatible backbones from {', '.join(self.supported_backbones)}")

        self._code = instance_detector_prf

        model = models.detection.maskrcnn_resnet50_fpn(pretrained=True, min_size = data.chip_size)
        in_features = model.roi_heads.box_predictor.cls_score.in_features
        model.roi_heads.box_predictor = FastRCNNPredictor(in_features, data.c)
        in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
        hidden_layer = 256
        model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,
                                                       hidden_layer,
                                                       data.c)

        self.learn = Learner(data, model, loss_func = mask_rcnn_loss)
        self.learn.callbacks.append(train_callback(self.learn))
        self.learn.model = self.learn.model.to(self._device)

        # fixes for zero division error when slice is passed
        self.learn.layer_groups = split_model_idx(self.learn.model, [28])
        self.learn.create_opt(lr=3e-3)

        if pretrained_path is not None:
            self.load(pretrained_path)           

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%s>' % (type(self).__name__)

    @property
    def supported_backbones(self):
        return [models.detection.maskrcnn_resnet50_fpn.__name__]

    @classmethod
    def from_model(cls, emd_path, data=None):
        """
        Creates a ``MaskRCNN`` Instance segmentation object from an Esri Model Definition (EMD) file.

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

        :returns: `MaskRCNN` Object
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
            empty_data = _EmptyData(path=tempfile.TemporaryDirectory().name, loss_func=None, c=len(class_mapping) + 1, chip_size=emd['ImageHeight'])
            empty_data.class_mapping = class_mapping
            empty_data.color_mapping = color_mapping
            return cls(empty_data, **model_params, pretrained_path=str(model_file))
        else:
            return cls(data, **model_params, pretrained_path=str(model_file))        

    def _create_emd(self, path):
        import random
        super()._create_emd(path)
        self._emd_template["Framework"] = "arcgis.learn.models._inferencing"
        self._emd_template["ModelConfiguration"] = "_maskrcnn_inferencing"
        self._emd_template["InferenceFunction"] = "ArcGISInstanceDetector.py"

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

    @property
    def _model_metrics(self):
        return {}

    def _predict_results(self, xb):

        self.learn.model.eval()
        predictions = self.learn.model(xb.cuda())
        predictionsf =[]
        for i in range(len(predictions)):
            predictionsf.append({})
            predictionsf[i]['masks'] = predictions[i]['masks'].detach().cpu().numpy()
            predictionsf[i]['boxes'] = predictions[i]['boxes'].detach().cpu().numpy()
            predictionsf[i]['labels'] = predictions[i]['labels'].detach().cpu().numpy()
            predictionsf[i]['scores'] = predictions[i]['scores'].detach().cpu().numpy()
            del predictions[i]['masks']
            del predictions[i]['boxes']
            del predictions[i]['labels']
            del predictions[i]['scores']
        del xb
        torch.cuda.empty_cache()      

        return predictionsf

    def _predict_postprocess(self, predictions, threshold=0.5, box_threshold = 0.5):

        pred_mask = []
        pred_box = []

        for i in range(len(predictions)):
            out = predictions[i]['masks'].squeeze()
            pred_box.append([])

            if out.shape[0] != 0:  # handle for prediction with n masks
                if len(out.shape) == 2: # for out dimension hxw (in case of only one predicted mask)
                    out = out[None]
                ymask = np.where(out[0]> threshold, 1, 0)
                #if torch.max(out[0]) > threshold:
                if predictions[i]['scores'][0] > box_threshold:
                    pred_box[i].append(predictions[i]['boxes'][0])
                for j in range(1,out.shape[0]):
                    ym1 = np.where(out[j]> threshold, j+1, 0)
                    ymask += ym1
                    #if torch.max(out[j]) > threshold:
                    if predictions[i]['scores'][j] > box_threshold:
                        pred_box[i].append(predictions[i]['boxes'][j])
            else:
                ymask = np.zeros((self._data.chip_size, self._data.chip_size)) # handle for not predicted masks
            pred_mask.append(ymask)
        return pred_mask, pred_box

    def show_results(self, mode='mask', mask_threshold=0.5, box_threshold=0.7, nrows=None, imsize=5, index=0, alpha=0.5, cmap='tab20'):
        """
        Displays the results of a trained model on a part of the validation set.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        mode                    Required arguments within ['bbox', 'mask', 'bbox_mask'].
                                    * ``bbox`` - For visualizing only boundig boxes.
                                    * ``mask`` - For visualizing only mask
                                    * ``bbox_mask`` - For visualizing both mask and bounding boxes.
        ---------------------   -------------------------------------------
        mask_threshold          Optional float. The probabilty above which
                                a pixel will be considered mask.
        ---------------------   -------------------------------------------
        box_threshold           Optional float. The pobabilty above which
                                a detection will be considered valid.
        ---------------------   -------------------------------------------
        nrows                   Optional int. Number of rows of results
                                to be displayed.
        =====================   ===========================================
        """ 

        if mode not in ['bbox', 'mask', 'bbox_mask']:
            raise Exception("mode can be only ['bbox', 'mask', 'bbox_mask']")

        # Get Number of items
        if nrows is None:
            nrows = self._data.batch_size
        ncols=2
    
        # Get Batch
        xb,yb = self._data.one_batch('DatasetType.Valid')
        
        predictions = self._predict_results(xb)

        pred_mask, pred_box = self._predict_postprocess(predictions, mask_threshold, box_threshold)

        fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*imsize, nrows*imsize))
        fig.suptitle('Ground Truth / Predictions', fontsize=20)

        for i in range(nrows):
            ax[i][0].imshow(xb[i].numpy().transpose(1,2,0))
            ax[i][0].axis('off')
            if mode in ['mask', 'bbox_mask']:
                yb_mask = yb[i][0].numpy()
                for j in range(1, yb[i].shape[0]):
                    max_unique = np.max(np.unique(yb_mask))
                    yb_j = np.where(yb[i][j]>0, yb[i][j] + max_unique, yb[i][j])
                    yb_mask += yb_j
                ax[i][0].imshow(yb_mask, cmap = cmap, alpha = alpha)
            ax[i][0].axis('off')
            ax[i][1].imshow(xb[i].numpy().transpose(1,2,0))
            ax[i][1].axis('off')
            if mode in ['mask', 'bbox_mask']:
                ax[i][1].imshow(pred_mask[i], cmap=cmap, alpha = alpha)
            if mode in ['bbox','bbox']:
                if pred_box[i] != []:
                    for num_boxes in pred_box[i]:
                        rect = patches.Rectangle((num_boxes[0], num_boxes[1]), num_boxes[2]-num_boxes[0], num_boxes[3]-num_boxes[1], linewidth=1, edgecolor='r', facecolor='none')
                        ax[i][1].add_patch(rect)
            ax[i][1].axis('off')
        plt.subplots_adjust(top=0.95)
        torch.cuda.empty_cache()

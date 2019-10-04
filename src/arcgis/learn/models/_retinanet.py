from ._arcgis_model import ArcGISModel
import tempfile
from pathlib import Path
import json
from ._codetemplate import code
import random
import statistics

# Try to import the necessary modules
# Exception will turn the HAS_FASTAI flag to false so that relevant exception can be raised
try:
    import torch
    import numpy as np
    import pandas as pd
    from fastai.vision.learner import create_body
    from fastai.vision.image import open_image
    from fastai.core import ifnone
    from torchvision import models
    from ._retinanet_utils import RetinaNetModel, RetinaNetFocalLoss, compute_class_AP
    from .._data import prepare_data
    from fastai.callbacks import EarlyStoppingCallback
    from fastai.basic_train import Learner
    from .._data import _raise_fastai_import_error
    from ._arcgis_model import SaveModelCallback
    HAS_FASTAI = True
except:
    HAS_FASTAI = False

class _EmptyData():
    def __init__(self, path, classes, c, loss_func, chip_size):
        self.path = path
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.classes = classes
        self.c = c
        self.loss_func = loss_func
        self.chip_size = chip_size


class RetinaNet(ArcGISModel):
    """
    Creates a RetinaNet Object Detector with the specified zoom scales
    and aspect ratios. 
    Based on the Fast.ai notebook at https://github.com/fastai/fastai_dev/blob/master/dev_nb/102a_coco.ipynb

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Required fastai Databunch. Returned data object from
                            `prepare_data` function.
    ---------------------   -------------------------------------------
    scales                  Optional list of float values. Zoom scales of anchor boxes.
    ---------------------   -------------------------------------------
    ratios                  Optional list of float values. Aspect ratios of anchor
                            boxes.
    ---------------------   -------------------------------------------
    backbone                Optional function. Backbone CNN model to be used for
                            creating the base of the `RetinaNet`, which
                            is `resnet50` by default. 
                            Compatible backbones: 'resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152'
    ---------------------   -------------------------------------------
    pretrained_path         Optional string. Path where pre-trained model is
                            saved.
    =====================   ===========================================

    :returns: `RetinaNet` Object
    """

    def __init__(self, data, scales=None, ratios=None, backbone=None, pretrained_path=None):

        # Set default backbone to be 'resnet50'
        if backbone is None: 
            backbone = models.resnet50

        super().__init__(data, backbone)

        # Check if a backbone provided is compatible, use resnet50 as default
        if not self._check_backbone_support(backbone):
            raise Exception (f"Enter only compatible backbones from {', '.join(self.supported_backbones)}")

        self.name = RetinaNet
        self._code = code

        self.scales = ifnone(scales, [1,2**(-1/3), 2**(-2/3)])
        self.ratios = ifnone(ratios, [1/2,1,2])
        self._n_anchors = len(self.scales) * len(self.ratios)

        self._data = data
        self._chip_size = (data.chip_size,data.chip_size)

        # Cut-off the backbone before the penultimate layer
        self._encoder = create_body(self._backbone, -2)

        # Initialize the model, loss function and the Learner object        
        self._model = RetinaNetModel(self._encoder, n_classes=data.c-1, final_bias=-4, chip_size=self._chip_size, n_anchors=self._n_anchors)
        self._loss_f = RetinaNetFocalLoss(sizes=self._model.sizes, scales=self.scales, ratios=self.ratios)
        self.learn = Learner(data, self._model, loss_func=self._loss_f)
        self.learn.split([self._model.encoder[6], self._model.c5top5])
        self.learn.freeze()
        if pretrained_path is not None:
            self.load(str(pretrained_path))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%s>' % (type(self).__name__)

    # Return a list of supported backbones names
    @property
    def supported_backbones(self):
        return [*self._resnet_family]

    def _create_emd(self, path):
        """
        Creates an Esri Model Definition (EMD) file with the parameters and 
        other information about the model.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        path                    Required string. Path where the created 
                                Esri Model Definition file will be saved.
        =====================   ===========================================

        :returns: path of the saved EMD file
        """

        super()._create_emd(path)
        
        self._emd_template["Framework"] = "arcgis.learn.models._inferencing"
        self._emd_template["InferenceFunction"] = "ArcGISObjectDetector.py"
        self._emd_template["ModelConfiguration"] = "_RetinaNet_Inference"
        self._emd_template["ModelType"] = "ObjectDetection"
        self._emd_template["ExtractBands"] = [0, 1, 2]
        self._emd_template['ModelParameters']['Scales'] = self._loss_f.scales #Scales and Ratios are attributes of RetinaNetFocalLoss object _loss_f
        self._emd_template['ModelParameters']['Ratios'] = self._loss_f.ratios
        self._emd_template['Classes'] = []

        class_data = {}
        for i, class_name in enumerate(self._data.classes[1:]): # 0th index is background
            inverse_class_mapping = {v: k for k, v in self._data.class_mapping.items()}
            class_data["Value"] = inverse_class_mapping[class_name]
            class_data["Name"] = class_name
            color = [random.choice(range(256)) for i in range(3)]
            class_data["Color"] = color
            self._emd_template['Classes'].append(class_data.copy())

        json.dump(self._emd_template, open(path.with_suffix('.emd'), 'w'), indent=4)
        return path.stem

    @property
    def _model_metrics(self):
        return {'accuracy': self.average_precision_score(show_progress=False)}

    @classmethod
    def from_model(cls, emd_path, data=None):
        """
        Creates a RetinaNet Object Detector from an Esri Model Definition (EMD) file.

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

        :returns: `RetinaNet` Object
        """

        emd_path = Path(emd_path)
        emd = json.load(open(emd_path))
        model_file = Path(emd['ModelFile'])
        backbone = emd.get('backbone', 'resnet50')

        if not model_file.is_absolute():
            model_file = emd_path.parent / model_file

        class_mapping = {i['Value'] : i['Name'] for i in emd['Classes']}

        if data is None:
            data = _EmptyData(path=tempfile.TemporaryDirectory().name, loss_func=None, classes=class_mapping.values(), c=len(class_mapping) + 1, chip_size=emd['ImageHeight'])
        
        resize_to = emd.get('resize_to')
        data.resize_to = resize_to
        
        return cls(data, backbone=backbone, pretrained_path=model_file)

    def show_results(self, rows=5, thresh=0.5, nms_overlap=0.1):
        """
        Displays the results of a trained model on a part of the validation set.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        rows                    Optional int. Number of rows of results
                                to be displayed.
        ---------------------   -------------------------------------------
        thresh                  Optional float. The probabilty above which
                                a detection will be considered valid.
        ---------------------   -------------------------------------------
        nms_overlap             Optional float. The intersection over union
                                threshold with other predicted bounding 
                                boxes, above which the box with the highest
                                score will be considered a true positive.
        =====================   ===========================================
        """ 

        if rows > self._data.batch_size:
            rows = self._data.batch_size      
        self.learn.show_results(rows=rows, thresh=thresh, nms_overlap=nms_overlap, ssd=self)
        

    def predict(self, image_path, threshold=0.5, nms_overlap=0.1, return_scores=True, visualize=False):
        """
        Predicts and displays the results of a trained model on a single image.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        image_path              Path to the image to predict on.
        ---------------------   -------------------------------------------
        thresh                  Optional float. The probabilty above which
                                a detection will be considered valid.
        ---------------------   -------------------------------------------
        nms_overlap             Optional float. The intersection over union
                                threshold with other predicted bounding 
                                boxes, above which the box with the highest
                                score will be considered a true positive.
        ---------------------   -------------------------------------------
        return_scores           Optional boolean.
                                Will return the probability scores of the 
                                bounding box predictions if True.
        ---------------------   -------------------------------------------
        visualize               Optional boolean. Displays the image with 
                                predicted bounding boxes if True.
        =====================   ===========================================
        
        :returns: 'List' of coordinates of predicted bounding boxes on the given image
        """ 

        if isinstance(image_path, str) or isinstance(image_path, Path):  ### Handling for inference
            image = open_image(image_path).apply_tfms(self._data.valid_ds.tfms)
        else:
            image = image_path

        if self._data.resize_to is not None:
            image = image.resize(size=self._data.resize_to)

        bbox = self.learn.predict(image, thresh=threshold, nms_overlap=nms_overlap, ret_scores=return_scores, ssd=self)[0] ## ssd because 'data' is an SSD Object

        if visualize:
            image.show(y=bbox)

        return None if bbox is None else (bbox.data, bbox.scores)

    def average_precision_score(self, detect_thresh=0.5, iou_thresh=0.1, mean=False, show_progress=True):
        """
        Computes average precision on the validation set for each class.

        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        detect_thresh           Optional float. The probabilty above which
                                a detection will be considered for computing
                                average precision.
        ---------------------   -------------------------------------------
        iou_thresh              Optional float. The intersection over union
                                threshold with the ground truth labels, above
                                which a predicted bounding box will be
                                considered a true positive.
        ---------------------   -------------------------------------------
        mean                    Optional bool. If False returns class-wise
                                average precision otherwise returns mean
                                average precision.                        
        =====================   ===========================================

        :returns: `dict` if mean is False otherwise `float`
        """

        aps = compute_class_AP(self, self._data.valid_dl, self._data.c - 1, show_progress, detect_thresh=detect_thresh, iou_thresh=iou_thresh)
        if mean:
            return statistics.mean(aps)
        else:
            return dict(zip(self._data.classes[1:], aps))


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
    from ._unet_utils import is_no_color, LabelCallback
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

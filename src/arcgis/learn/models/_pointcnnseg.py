from .._data import _raise_fastai_import_error

try:
    from ._arcgis_model import ArcGISModel, SaveModelCallback, _set_multigpu_callback
    from ._pointcnn_utils import PointCNNSeg, SamplePointsCallback, CrossEntropyPC, accuracy, accuracy_non_zero
    from .._utils.pointcloud_data import get_device, inference_las, show_results
    from ._unet_utils import is_no_color
    from fastai.basic_train import Learner
    import torch
    import numpy as np
    from fastai.callbacks import EarlyStoppingCallback
    from functools import partial
    HAS_FASTAI = True
except Exception as e:
    HAS_FASTAI = False

class PointCNN(ArcGISModel):
    """
    kwargs: {encoder_params, dropout, sample_point_num}
    ADD DOC HERE
    """
    def __init__(self, data, pretrained_path=None, **kwargs):
        super().__init__(data, None)
        
        self._backbone = None
        self.sample_point_num = kwargs.get('sample_point_num', data.max_point)
        self.learn = Learner(data,
                PointCNNSeg(self.sample_point_num, data.c, data.extra_dim, kwargs.get('encoder_params', None), kwargs.get('dropout', None)),
                loss_func=CrossEntropyPC(data.c),
                metrics=[accuracy, accuracy_non_zero],
                callback_fns=[partial(SamplePointsCallback, sample_point_num=self.sample_point_num)])
        self.encoder_params = self.learn.model.encoder_params

        self.learn.model = self.learn.model.to(self._device)

        if pretrained_path is not None:
            self.load(pretrained_path)

    @property
    def _model_metrics(self):
        return {'accuracy': self._get_model_metrics()}            

    def _get_model_metrics(self, **kwargs):
        checkpoint = kwargs.get('checkpoint', True)
        if not hasattr(self.learn, 'recorder'):
            return 0.0

        model_accuracy = self.learn.recorder.metrics[-1][0]
        if checkpoint:
            model_accuracy = np.max(self.learn.recorder.metrics)

        return float(model_accuracy)

    def _get_emd_params(self):
        import random
        _emd_template = {"ModelParameters" : {}}
        _emd_template["Framework"] = "N/A"
        _emd_template["ModelConfiguration"] = "N/A"
        # _emd_template["InferenceFunction"] = "N/A"
        _emd_template["ExtractBands"] = "N/A"
        _emd_template["ModelParameters"]["encoder_params"] = self.encoder_params
        _emd_template["ModelParameters"]["sample_point_num"] = self.sample_point_num

        _emd_template['Classes'] = []
        class_data = {}
        for i, class_name in enumerate(self._data.classes):  # 0th index is background
            inverse_class_mapping = {v: k for k, v in self._data.class_mapping.items()}
            class_data["Value"] = inverse_class_mapping[class_name]
            class_data["Name"] = class_name
            color = [random.choice(range(256)) for i in range(3)] if is_no_color(self._data.color_mapping) else \
                self._data.color_mapping[inverse_class_mapping[class_name]]
            class_data["Color"] = (255 * color).astype(int).tolist()
            _emd_template['Classes'].append(class_data.copy())

        return _emd_template
        
    def show_results(self, rows=2, **kwargs):
        return show_results(self, rows, **kwargs)

    def predict_las(self, path, output_path=None, publish=False, **kwargs):
        return inference_las(path, self, output_path)
        

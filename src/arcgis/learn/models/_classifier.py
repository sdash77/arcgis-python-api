try:
    from ._arcgis_model import ArcGISModel
    import tempfile
    import numpy as np
    import json
    import os
    import warnings
    from pathlib import Path
    from ._ssd import _raise_fastai_import_error, _EmptyData
    from functools import partial
    from ._unet_utils import is_no_color
    from ._codetemplate import feature_classifier_prf
    import torch
    from torchvision import models
    from fastai.metrics import accuracy
    from fastai.vision.image import open_image
    from fastai.vision.data import ImageDataBunch
    from fastai.vision import imagenet_stats
    from fastai.vision.learner import create_cnn, ClassificationInterpretation
    from fastai.vision.transform import crop, rotate, dihedral_affine, brightness, contrast, skew, rand_zoom, get_transforms
    import tempfile
    HAS_FASTAI = True
except Exception as e:
    HAS_FASTAI = False

_EMD_TEMPLATE = {
    "Framework":"arcgis.learn.models._inferencing",
    "ModelConfiguration":"_classifier",
    "ModelFile":"",
    "InferenceFunction": "ArcGISFeatureClassifier.py",
    "ExtractBands":[0,1,2],
    "ImageWidth":400,
    "ImageHeight":400,
    "Classes" : []
}

_CLASS_TEMPLATE =     {
      "Value" : 1,
      "Name" : "1",
      "Color" : []
    }

class FeatureClassifier(ArcGISModel):
    """
    Creates an image classifier to classify the area occupied by a
    geographical feature based on the imagery it overlaps with.

    =====================   ===========================================
    **Argument**            **Description**
    ---------------------   -------------------------------------------
    data                    Required fastai Databunch. Returned data object from
                            `prepare_data` function.
    ---------------------   -------------------------------------------
    backbone                Optional torchvision model. Backbone CNN model to be used for
                            creating the base of the `FeatureClassifier`, which
                            is `resnet34` by default.
    ---------------------   -------------------------------------------
    pretrained_path         Optional string. Path where pre-trained model is
                            saved.
    =====================   ===========================================

    :returns: `FeatureClassifier` Object
    """

    def __init__(self, data, backbone=None, pretrained_path=None):
        super().__init__()

        self._device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

        if not HAS_FASTAI:
            _raise_fastai_import_error()

        if backbone is None:
            self._backbone = models.resnet34
        elif type(backbone) is str:
            self._backbone = getattr(models, backbone)
        else:
            self._backbone = backbone

        self._emd_template = _EMD_TEMPLATE

        self._code = feature_classifier_prf

        self._data = data
        self.learn = create_cnn(data, self._backbone, metrics=accuracy)
        self.learn.model = self.learn.model.to(self._device)

        if pretrained_path is not None:
            self.load(pretrained_path)


    def show_results(self, rows=5, **kwargs):
        """
        Displays the results of a trained model on a part of the validation set.
        """
        if rows > self._data.batch_size:
            rows = self._data.batch_size
        self.learn.show_results(rows=rows, **kwargs)

    def predict(self, img_path):
        img = open_image(img_path)
        return self.learn.predict(img)

    def _create_emd(self, path):
        import random
        _EMD_TEMPLATE['ModelFile'] = path.name
        _EMD_TEMPLATE['ImageHeight'] = self._data.chip_size
        _EMD_TEMPLATE['ImageWidth'] = self._data.chip_size
        _EMD_TEMPLATE['ModelParameters'] = {
                                            'backbone': self._backbone.__name__
                                           }
        _EMD_TEMPLATE['Classes'] = []
        for i, class_name in enumerate(self._data.classes):
            inverse_class_mapping = {v: k for k, v in self._data.class_mapping.items()}
            _CLASS_TEMPLATE["Value"] = inverse_class_mapping[class_name]
            _CLASS_TEMPLATE["Name"] = class_name
            color = [random.choice(range(256)) for i in range(3)] if is_no_color(self._data.color_mapping) else self._data.color_mapping[inverse_class_mapping[class_name]]
            _CLASS_TEMPLATE["Color"] = color
            _EMD_TEMPLATE['Classes'].append(_CLASS_TEMPLATE.copy())

        json.dump(_EMD_TEMPLATE, open(path.with_suffix('.emd'), 'w'), indent=4)
        return path.stem

    @classmethod
    def from_model(cls, emd_path, data=None):
        emd_path = Path(emd_path)
        with open(emd_path) as f:
            emd = json.load(f)

        model_file = Path(emd['ModelFile'])

        if not model_file.is_absolute():
            model_file = emd_path.parent / model_file

        model_params = emd['ModelParameters']
        chip_size = emd["ImageWidth"]

        try:
            class_mapping = {i['Value'] : i['Name'] for i in emd['Classes']}
            color_mapping = {i['Value'] : i['Color'] for i in emd['Classes']}
        except KeyError:
            class_mapping = {i['ClassValue'] : i['ClassName'] for i in emd['Classes']}
            color_mapping = {i['ClassValue'] : i['Color'] for i in emd['Classes']}


        if data is None:
            ranges = (0, 1)
            train_tfms = [rotate(degrees=30, p=0.5),
                crop(size=chip_size, p=1., row_pct=ranges, col_pct=ranges),
                dihedral_affine(), brightness(change=(0.4, 0.6)), contrast(scale=(0.75, 1.5)),
                # rand_zoom(scale=(0.75, 1.5))
                ]
            val_tfms = [crop(size=chip_size, p=1.0, row_pct=0.5, col_pct=0.5)]
            transforms = (train_tfms, val_tfms)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)

                tempdata = ImageDataBunch.single_from_classes(
                    tempfile.TemporaryDirectory().name, sorted(list(class_mapping.values())),
                    tfms=transforms, size=chip_size).normalize(imagenet_stats)
                tempdata.chip_size = chip_size
                return cls(tempdata, **model_params, pretrained_path=str(model_file))
        else:
            return cls(data, **model_params, pretrained_path=str(model_file))

    def plot_confusion_matrix(self):
        """
        Plots a confusion matrix of the model predictions to evaluate accuracy
        """
        interp = ClassificationInterpretation.from_learner(self.learn)
        interp.plot_confusion_matrix()

    def classify_features(self, input_features, imagery,
                   class_value_field=None,
                   confidence_score_field=None,
                   context=None):

        """
        Classifies the area occupied by geographical features based on the imagery they overlaps with.

        ====================================     ====================================================================
        **Argument**                             **Description**
        ------------------------------------     --------------------------------------------------------------------
        input_features                           Required. Spatially enabled DataFrame containing features to be classified
        ------------------------------------     --------------------------------------------------------------------
        imagery                                  Required. MapImageLayer or ImageryLayer with imagery
        ------------------------------------     --------------------------------------------------------------------
        class_value_field                        Optional string. The column in the returned dataframe that contains the class value
        ------------------------------------     --------------------------------------------------------------------
        confidence_score_field                   Optional string. The column in the returned dataframe that contains the confidence scores as output by the image detection model
        ------------------------------------     --------------------------------------------------------------------
        context                                  Optional dictionary. Context contains additional settings that affect task execution.
                                                Dictionary can contain value for following keys:

                                                - cellSize - Set the output raster cell size, or resolution
        ====================================     ====================================================================

        :return:
            The spatially enabled dataframe with colmns for the inferred class value and confidence scores

        """
        sdf = input_features.copy()
        cellsize = 1.0

        if context is not None:
            try:
                cellsize = context['cellSize']
            except:
                pass

        chipsize = self._data.chip_size

        w = cellsize * chipsize
        with tempfile.TemporaryDirectory() as tmpdir:
            for index, row in input_features.iterrows():
                g = row['SHAPE']
                x, y = g.centroid
                ext = (x - w/2, y - w/2, x + w/2, y + w/2)

                filename = imagery.export_map(ext, size='{0},{1}'.format(chipsize, chipsize), f='image', format='jpg',save_folder=tmpdir, save_file='test.jpg')
                prediction = self.predict(filename)
                sdf[class_value_field] = self._data.classes[int(prediction[1])]
                sdf[confidence_score_field] = float(prediction[2][prediction[1]]*100)

        return sdf
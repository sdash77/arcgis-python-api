import arcgis as _arcgis 
from ._arcgis_model import ArcGISModel, _set_multigpu_callback
import random
try:
    import pandas
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
    from fastai.vision.learner import cnn_learner, ClassificationInterpretation
    from ._arcgis_model import _set_multigpu_callback
    from fastai.vision.transform import crop, rotate, dihedral_affine, brightness, contrast, skew, rand_zoom, get_transforms
    import torch.nn.functional as functional
    from .._data import _check_esri_files
    import tempfile
    import glob
    import time
    import xml.etree.ElementTree as ElementTree
    import PIL.Image
    import PIL.ExifTags
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

_CLASS_TEMPLATE = {
      "Value" : 1,
      "Name" : "1",
      "Color" : []
}


def _prediction_function(predictions):
    classes = {}
    max_prediction_value = 0
    max_prediction_class = None
    for prediction in predictions:
        if not classes.get(prediction[0]):
            classes[prediction[0]] = prediction[1]
        else:
            classes[prediction[0]] = classes[prediction[0]] + prediction[1]
        if max_prediction_value < classes[prediction[0]]:
            max_prediction_value = classes[prediction[0]]
            max_prediction_class = prediction[0]

    return max_prediction_class, max_prediction_value


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
        self.learn = cnn_learner(data, self._backbone, metrics=accuracy)
        self.learn.model = self.learn.model.to(self._device)

        _set_multigpu_callback(self)
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
        _EMD_TEMPLATE['ModelFile'] = path.name
        _EMD_TEMPLATE['ImageHeight'] = self._data.chip_size
        _EMD_TEMPLATE['ImageWidth'] = self._data.chip_size
        _EMD_TEMPLATE['ModelParameters'] = {'backbone': self._backbone.__name__}
        _EMD_TEMPLATE['Classes'] = []

        for i, class_name in enumerate(self._data.classes):
            inverse_class_mapping = {v: k for k, v in self._data.class_mapping.items()}
            _CLASS_TEMPLATE["Value"] = inverse_class_mapping[class_name]
            _CLASS_TEMPLATE["Name"] = class_name
            color = [random.choice(range(256)) for i in range(3)]
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
                    ds_tfms=transforms, size=chip_size).normalize(imagenet_stats)
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

    def plot_hard_examples(self, num_examples):
        """
        Plots the hard examples with their heatmaps.
        
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        num_examples            Number of hard examples to plot
                                `prepare_data` function.
        """
        interp = ClassificationInterpretation.from_learner(self.learn)
        interp.plot_top_losses(num_examples, figsize=(15,15), heatmap=True)        

    def _get_model_metrics(self, **kwargs):

        interp = ClassificationInterpretation.from_learner(self.learn)
        cm = interp.confusion_matrix(slice_size=1)

        message = ""
        for value in self.learn.data.classes:
            message = message + \
                      "\t" + f"predicted_{(self.learn.data.class_mapping.get(value) or self.learn.data.class_mapping.get(int(value)))}"

        message = message + "\n"
        for i in range(len(self.learn.data.classes)):
            message = message + (self.learn.data.class_mapping.get(self.learn.data.classes[i]) or self.learn.data.class_mapping.get(
                int(self.learn.data.classes[i]))) + "\t"
            for val in cm[i]:
                message = message + "\t" + str(val) + "\t"
            message = message + "\n"

        return message

    @staticmethod
    def convert_to_degrees(value, reference):
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        degrees = d + (m / 60.0) + (s / 3600.0)

        if reference == "S" or reference == "W":
            degrees = 0 - degrees
        
        return degrees

    def predict_folder_and_create_layer(self, folder, feature_layer_name, gis=None, prediction_field='predict', confidence_field='confidence'):
        """
        Predicts on images present in the given folder and creates a feature layer.
        
        =====================   ===========================================
        **Argument**            **Description**
        ---------------------   -------------------------------------------
        folder                  Required String. Folder to inference on.
        ---------------------   -------------------------------------------
        feature_layer_name      Required String. The name of the feature layer used to publish.   
        ---------------------   -------------------------------------------
        gis                     Optional GIS Object, the GIS on which this tool runs. If not specified,
                                the active GIS is used.      
        ---------------------   -------------------------------------------
        prediction_field        Optional String. The field name to use to add predictions.             
        ---------------------   -------------------------------------------
        confidence_field        Optional String. The field name to use to add confidence.                                                                               
        =====================   ===========================================

        :returns: `FeatureCollection` Object                              
        """        
        return self._create_feature_layer(
            self._extract_images_geo_data(folder),
            _arcgis.env.active_gis if gis is None else gis,
            feature_layer_name,
            prediction_field,
            confidence_field
        )

    def _extract_images_geo_data(self, folder):
        ALLOWED_FILE_FORMATS = ['tif', 'jpg', 'png']

        files = []

        for ext in ALLOWED_FILE_FORMATS:
            files.extend(glob.glob(os.path.join(folder, '*.' + ext)))
        
        images_data = []

        for file in files:
            img = PIL.Image.open(file)
            exif = {
                PIL.ExifTags.TAGS[k]: v
                for k, v in img._getexif().items()
                if k in PIL.ExifTags.TAGS
            }

            images_data.append(
                {
                    'image_path': file,
                    'y': FeatureClassifier.convert_to_degrees(exif['GPSInfo'][2], exif['GPSInfo'][1]),
                    'x': FeatureClassifier.convert_to_degrees(exif['GPSInfo'][4], exif['GPSInfo'][3])
                }
            )
        
        return images_data

    def _create_feature_layer(self, images_data, gis_user, feature_layer_name, prediction_field, confidence_field):
        data = []
        images = {}
        for image_data in images_data:
            prediction = self.predict(image_data['image_path'])
            images[os.path.basename(image_data['image_path'])] = image_data['image_path']
            data.append(
                [   
                    os.path.basename(image_data['image_path']),
                    prediction[0].obj,
                    prediction[2].data.max().tolist(),
                    image_data['x'],
                    image_data['y']
                ]
            )
        
        dataframe = pandas.DataFrame(data, columns=['Image_Name', prediction_field, confidence_field, 'X', 'Y'])
        spatial_dataframe = dataframe.spatial.from_xy(df=dataframe, sr=4326, x_column='X', y_column='Y')

        feature_collection = gis_user.content.import_data(spatial_dataframe, title=feature_layer_name)

        feature_layer = feature_collection.layers[0]
        feature_layer.manager.add_to_definition({"hasAttachments":True})

        df = feature_layer.query(as_df=True)
        object_field = feature_layer.properties['objectIdField']

        for image_name, image_path in images.items():
            object_id = df[object_field].where(df['Image_Name'] == image_name).values[0]  #assuming image_name is unique
            if np.isnan(object_id):
                continue #skipping those values which are not present.
            feature_layer.attachments.add(
                object_id,
                image_path
            )

        return feature_collection

    @staticmethod
    def _update_predictions_layer(feature_layer, features_to_update, output_label_field, confidence_field=None):
        field_template = {
            "name": output_label_field,
            "type": "esriFieldTypeString",
            "alias": output_label_field,
            "sqlType": "sqlTypeOther",
            "length": 256,
            "nullable": True,
            "editable": True,
            "visible": True,
            "domain": None,
            "defaultValue": ''
        }

        confidence_field_template = {
            "name": confidence_field,
            "type": "esriFieldTypeString",
            "alias": confidence_field,
            "sqlType": "sqlTypeOther",
            "length": 256,
            "nullable": True,
            "editable": True,
            "visible": True,
            "domain": None,
            "defaultValue": ''
        }

        feature_layer.manager.add_to_definition({'fields': [field_template]})

        if confidence_field:
            feature_layer.manager.add_to_definition({'fields': [confidence_field_template]})

        try:
            start = 0
            stop = 100
            count = 100

            features_updated = features_to_update[start:stop]
            response = feature_layer.edit_features(updates=features_updated)

            for resp in response.get('updateResults', []):
                if resp.get('success', False):
                    continue
                warnings.warn(f"Something went wrong for data {resp}")

            time.sleep(2)
            while count == len(features_updated):
                start = stop
                stop = stop + 100
                features_updated = features_to_update[start:stop]
                response = feature_layer.edit_features(updates=features_updated)
                for resp in response.get('updateResults', []):
                    if resp.get('success', False):
                        continue
                    warnings.warn(f"Something went wrong for data {resp}")
                time.sleep(2)
        except Exception:
            feature_layer.manager.delete_from_definition({'fields': [field_template]})
            if confidence_field:
                feature_layer.manager.delete_from_definition({'fields': [confidence_field_template]})

            return False

        return True

    def _classify_attachments(
            self,
            feature_layer,
            data_folder,
            feature_attachments_mapping,
            input_label_field,
            output_label_field,
            confidence_field=None,
            predict_function=_prediction_function
    ):

        features = feature_layer.query().features
        features_to_update = []

        for feature in features:
            feature_attachments = (feature_attachments_mapping.get(str(feature.attributes[input_label_field])) or \
                                   feature_attachments_mapping.get(int(feature.attributes[input_label_field])))
            if not feature_attachments:
                continue

            predictions = []
            for attachment in feature_attachments:
                prediction = self.predict(os.path.join(data_folder, attachment))
                predictions.append((prediction[0].obj, prediction[2].data.max().tolist()))

            final_prediction = predict_function(predictions)

            feature.attributes[output_label_field] = final_prediction[0]
            if confidence_field:
                feature.attributes[confidence_field] = final_prediction[1]

            features_to_update.append(feature)

        return features_to_update

    def _classify_labeled_tiles(
            self,
            feature_layer,
            labeled_tiles_directory,
            input_label_field,
            output_label_field,
            confidence_field=None
    ):
        ALLOWED_FILE_FORMATS = ['tif', 'jpg', 'png']
        IMAGES_FOLDER = 'images/'
        LABELS_FOLDER = 'labels/'

        files = []

        for ext in ALLOWED_FILE_FORMATS:
            files.extend(glob.glob(os.path.join(labeled_tiles_directory, IMAGES_FOLDER + '*.' + ext)))

        predictions = {}
        for file in files:
            xml_path = os.path.join(os.path.dirname(os.path.dirname(file)),
                                    os.path.join(LABELS_FOLDER, os.path.basename(file).split('.')[0] + '.xml'))

            if not os.path.exists(xml_path):
                continue

            tree = ElementTree.parse(xml_path)
            root = tree.getroot()

            name_field = root.findall('object/name')
            if len(name_field) != 1:
                continue

            file_prediction = self.predict(file)

            predictions[name_field[0].text] = {
                'prediction': file_prediction[0].obj,
                'score': str(file_prediction[2].data.max().tolist())
            }

        features = feature_layer.query(output_fields=[input_label_field]).features
        features_to_update = []
        for feature in features:
            if predictions.get(str(feature.attributes[input_label_field])):
                feature.attributes[output_label_field] = predictions.get(str(feature.attributes[input_label_field]))[
                    'prediction']
                if confidence_field:
                    feature.attributes[confidence_field] = predictions.get(str(feature.attributes[input_label_field]))[
                        'score']

                features_to_update.append(feature)

        return features_to_update

    def classify_features(
        self,
        feature_layer,
        labeled_tiles_directory,
        input_label_field,
        output_label_field,
        confidence_field=None,
        predict_function=None
    ):

        """
        Classifies the exported images and updates the feature layer with the prediction results in the output_label_field.

        ====================================     ====================================================================
        **Argument**                             **Description**
        ------------------------------------     --------------------------------------------------------------------
        feature_layer                            Required. Feature Layer for classification.
        ------------------------------------     --------------------------------------------------------------------
        labeled_tiles_directory                  Required. Folder structure containing images and labels folder. The
                                                 chips should have been generated using the export training data tool in
                                                 the Labeled Tiles format, and the labels should contain the OBJECTIDs
                                                 of the features to be classified.
        ------------------------------------     --------------------------------------------------------------------
        input_label_field                        Required. Value field name which created the labeled tiles. This field
                                                 should contain the OBJECTIDs of the features to be classified. In case of
                                                 attachments this field is not used.
        ------------------------------------     --------------------------------------------------------------------
        output_label_field                       Required. Output column name to be added in the layer which contains predictions.
        ------------------------------------     --------------------------------------------------------------------
        confidence_field                         Optional. Output column name to be added in the layer which contains the confidence score.
        ------------------------------------     --------------------------------------------------------------------
        predict_function                         Optional. Used for calculation of final prediction result when each feature
                                                 has more than one attachment. The predict_function takes as input a list of tuples.
                                                 Each tuple has first element as the class predicted and second element is the confidence score.
                                                 The function should return the final tuple classifying the feature and its confidence
        ====================================     ====================================================================

        :return:
            Boolean : True/False if operation is sucessful

        """

        if predict_function is None:
            predict_function = _prediction_function

        if input_label_field and _check_esri_files(Path(labeled_tiles_directory)):
            features_to_update = self._classify_labeled_tiles(
                feature_layer,
                labeled_tiles_directory,
                input_label_field,
                output_label_field,
                confidence_field
            )
        elif os.path.exists(os.path.join(labeled_tiles_directory, 'mapping.txt')):
            json_file = os.path.join(labeled_tiles_directory, 'mapping.txt')
            with open(json_file) as file:
                feature_attachments_mapping = json.load(file)

            features_to_update = self._classify_attachments(
                feature_layer,
                labeled_tiles_directory,
                feature_attachments_mapping,
                feature_layer.properties['objectIdField'],
                output_label_field,
                confidence_field,
                predict_function
            )
        else:
            return False

        return FeatureClassifier._update_predictions_layer(
            feature_layer,
            features_to_update,
            output_label_field,
            confidence_field
        )

    def categorize_features(
        self,
        feature_layer,
        input_raster=None,
        output_label_field='Prediction',
        confidence_field='Confidence',
        cell_size=1,
        predict_function=None
    ):

        """
        Categorizes each feature by classifying it's attachments or an image of its geographical area (using the provided Imagery Layer)
        and updates the feature layer with the prediction results in the output_label_field.

        ====================================     ====================================================================
        **Argument**                             **Description**
        ------------------------------------     --------------------------------------------------------------------
        feature_layer                            Required. Feature Layer for classification with read, write, edit permissions.
        ------------------------------------     --------------------------------------------------------------------
        input_raster                             Optional. ImageryLayer to be used for exporting image chips. (Requires arcpy)
        ------------------------------------     --------------------------------------------------------------------
        output_label_field                       Required. Output field to be added in the layer, containing predictions.
        ------------------------------------     --------------------------------------------------------------------
        cell_size                                Optional. Cell size to be used for exporting the image chips.
        ------------------------------------     --------------------------------------------------------------------
        confidence_field                         Optional. Output column name to be added in the layer which contains the confidence score.
        ------------------------------------     --------------------------------------------------------------------
        predict_function                         Optional. Used for calculation of final prediction result when each feature
                                                 has more than one attachment. The predict_function takes as input a list of tuples.
                                                 Each tuple has first element as the class predicted and second element is the confidence score.
                                                 The function should return the final tuple classifying the feature and its confidence.
        ====================================     ====================================================================

        :return:
            Boolean : True if operation is successful, False otherwise

        """

        out_folder = tempfile.TemporaryDirectory().name
        class_value_field = None

        if isinstance(feature_layer, str):
            from arcgis.features import FeatureLayer
            feature_layer = FeatureLayer(feature_layer)

        if input_raster is not None:
            if isinstance(input_raster, str):
                from arcgis.raster import ImageryLayer
                input_raster = ImageryLayer(input_raster)

            import arcpy

            feature_layer_url = f"{feature_layer.url}"
            input_raster_url = f"{input_raster.url}"

            if feature_layer._token is not None:
                feature_layer_url = feature_layer_url + f"?token={feature_layer._token}"

            if input_raster._token is not None:
                input_raster_url = input_raster_url + f"?token={input_raster._token}"

            class_value_field = feature_layer.properties['objectIdField']

            copy_field_name = ''.join([chr(ord('a') + round(random.random() * 100 % 25)) for i in range(5)])
            arcpy.AddField_management(feature_layer_url, copy_field_name, "LONG", field_length="20")
            arcpy.CalculateField_management(
                feature_layer.url,
                copy_field_name,
                class_value_field,
                "SQL"
            )

            arcpy.env.cellSize = cell_size
            arcpy.ia.ExportTrainingDataForDeepLearning(
                input_raster_url,
                out_folder,
                in_class_data=feature_layer_url,
                image_chip_format="TIFF",
                tile_size_x=self._data.chip_size,
                tile_size_y=self._data.chip_size,
                metadata_format="Labeled_Tiles",
                class_value_field=copy_field_name
            )
            arcpy.DeleteField_management(feature_layer_url, [copy_field_name])
        else:
            os.mkdir(out_folder)
            feature_layer.export_attachments(out_folder)

        return self.classify_features(
            feature_layer,
            out_folder,
            class_value_field,
            output_label_field,
            confidence_field=confidence_field,
            predict_function=predict_function
        )

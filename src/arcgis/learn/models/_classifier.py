import arcgis as _arcgis 
from ._arcgis_model import ArcGISModel
import random
try:
    import pandas
    import tempfile
    import numpy as np
    import json
    import os
    import io
    import shutil
    import warnings
    from pathlib import Path
    from functools import partial
    from ._unet_utils import is_no_color
    from ._codetemplate import feature_classifier_prf
    import torch
    from torchvision import models
    from fastai.metrics import accuracy
    from fastai.vision.image import open_image
    from fastai.vision.data import ImageDataBunch, ImageList
    from fastai.vision import imagenet_stats, normalize
    from fastai.vision.learner import cnn_learner, ClassificationInterpretation
    from ._arcgis_model import _set_multigpu_callback
    from fastai.vision.transform import crop, rotate, dihedral_affine, brightness, contrast, skew, rand_zoom, get_transforms
    import torch.nn.functional as functional
    from .._data import _check_esri_files
    import glob
    import time
    import xml.etree.ElementTree as ElementTree
    import PIL.Image
    import PIL.ExifTags
    from torch.nn import Module as NnModule
    HAS_FASTAI = True
except Exception as e:
    class NnModule():
        pass
    HAS_FASTAI = False


def _mobilenet_split(m:NnModule): return m[0][0][0], m[1]


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
                            creating the base of the ``FeatureClassifier``, which
                            is ``resnet34`` by default.
    ---------------------   -------------------------------------------
    pretrained_path         Optional string. Path where pre-trained model is
                            saved.
    =====================   ===========================================

    :returns: `FeatureClassifier` Object
    """

    def __init__(self, data, backbone=None, pretrained_path=None):
        
        super().__init__(data, backbone)

        backbone_cut = None
        backbone_split = None
        if self._backbone == models.mobilenet_v2:
            backbone_cut = -1
            backbone_split = _mobilenet_split

        if not self._check_backbone_support(self._backbone):
            raise Exception (f"Enter only compatible backbones from {', '.join(self.supported_backbones)}")

        self._code = feature_classifier_prf
        self.learn = cnn_learner(data, self._backbone, metrics=accuracy, cut=backbone_cut, split_on=backbone_split)

        self.learn.model = self.learn.model.to(self._device)

        _set_multigpu_callback(self)
        if pretrained_path is not None:
            self.load(pretrained_path)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%s>' % (type(self).__name__)

    @property
    def supported_backbones(self):
        return [*self._resnet_family, models.mobilenet_v2.__name__]

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

    def _predict_batch(self, imagetensor_batch):
        predictions = self.learn.model.eval()(imagetensor_batch.to(self._device)).detach().cpu()
        predictions_conf,  predicted_classes = torch.max(predictions, dim=-1)
        predicted_classes = predicted_classes.tolist()
        predictions_conf = (predictions_conf*100).tolist()
        return predicted_classes, predictions_conf

    def _save_confusion_matrix(self, path):
        from matplotlib import pyplot as plt
        import fastai
        import fastprogress
        fastprogress.fastprogress.NO_BAR = True
        fastai.basic_train.master_bar, fastai.basic_train.progress_bar = fastprogress.force_console_behavior()
        self.plot_confusion_matrix()
        fastai.basic_train.master_bar, fastai.basic_train.progress_bar = fastprogress.master_bar, fastprogress.progress_bar
        plt.savefig(os.path.join(path, 'confusion_matrix.png'))
        plt.close()

    @property
    def _model_metrics(self):
        return {}
    
    def _create_emd(self, path):
        super()._create_emd(path)
        self._emd_template["Framework"] = "PyTorch"
        self._emd_template["ModelConfiguration"] = "FeatureClassifier"
        self._emd_template["ModelType"] = "ObjectClassification"
        self._emd_template["ExtractBands"] = [0, 1, 2]
        self._emd_template['CropSizeFixed'] = 1  # hardcoded
        self._emd_template['BlackenAroundFeature'] = 0 #hardcoded
        self._emd_template['ImageSpaceUsed'] = "MAP_SPACE"
        self._emd_template['Classes'] = []
        class_data = {}
        for i, class_name in enumerate(self._data.classes):
            inverse_class_mapping = {v: k for k, v in self._data.class_mapping.items()}
            class_data["Value"] = inverse_class_mapping[class_name]
            class_data["Name"] = class_name
            color = [random.choice(range(256)) for i in range(3)]
            class_data["Color"] = color
            self._emd_template['Classes'].append(class_data.copy())

        json.dump(self._emd_template, open(path.with_suffix('.emd'), 'w'), indent=4)

        return path.stem

    def _create_tf_emd(self, saved_path, onnx_path):
        import random
        super()._create_tf_emd(saved_path, onnx_path)

        self._emd_template["Framework"] = "arcgis.learn.models._inferencing"
        self._emd_template["InferenceFunction"] = "ArcGISObjectDetector.py"
        self._emd_template["ModelConfiguration"] = "_classifier"
        self._emd_template["ExtractBands"] = [0, 1, 2]
        self._emd_template['Classes'] = []

        class_data = {}
        for i, class_name in enumerate(self._data.classes):
            inverse_class_mapping = {v: k for k, v in self._data.class_mapping.items()}
            class_data["Value"] = inverse_class_mapping[class_name]
            class_data["Name"] = class_name
            color = [random.choice(range(256)) for i in range(3)]
            class_data["Color"] = color
            self._emd_template['Classes'].append(class_data.copy())

        json.dump(self._emd_template, open(saved_path.with_suffix('.emd'), 'w'), indent=4)

        return saved_path.stem

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
            class_mapping = {i['Value']: i['Name'] for i in emd['Classes']}
            color_mapping = {i['Value']: i['Color'] for i in emd['Classes']}
        except KeyError:
            class_mapping = {i['ClassValue']: i['ClassName'] for i in emd['Classes']}
            color_mapping = {i['ClassValue']: i['Color'] for i in emd['Classes']}

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
                tempdata.class_mapping = class_mapping
                tempdata.classes = list(class_mapping.keys())
                data = tempdata

        resize_to = emd.get('resize_to')
        data.resize_to = resize_to

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
                                ``prepare_data`` function.
        =====================   ===========================================
        """
        interp = ClassificationInterpretation.from_learner(self.learn)
        interp.plot_top_losses(num_examples, figsize=(15,15), heatmap=True)

    @staticmethod
    def _convert_to_degrees(value, reference):
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
                    'y': FeatureClassifier._convert_to_degrees(exif['GPSInfo'][2], exif['GPSInfo'][1]),
                    'x': FeatureClassifier._convert_to_degrees(exif['GPSInfo'][4], exif['GPSInfo'][3])
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
        Classifies the exported images and updates the feature layer with the prediction results in the ``output_label_field``.

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
                                                 has more than one attachment. The ``predict_function`` takes as input a list of tuples.
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

    def _categorize_feature_layer(
        self,
        feature_layer,
        raster,
        class_value_field,
        class_name_field,
        confidence_field,
        cell_size,
        coordinate_system,
        predict_function,
        batch_size,
        overwrite
    ):  
        #
        norm_mean = torch.tensor(imagenet_stats[0])
        norm_std = torch.tensor(imagenet_stats[1])

        # Check and create Fields 
        class_name_field_template = {
            "name": class_name_field.lower(),
            "type": "esriFieldTypeString",
            "alias": class_name_field,
            "sqlType": "sqlTypeOther",
            "length": 256,
            "nullable": True,
            "editable": True,
            "visible": True,
            "domain": None,
            "defaultValue": ''
        }

        class_value_field_template = {
            "name": class_value_field.lower(),
            "type": "esriFieldTypeInteger",
            "alias": class_value_field,
            "sqlType": "sqlTypeOther",
            "nullable": True,
            "editable": True,
            "visible": True,
            "domain": None,
            "defaultValue": -999
        }

        to_delete = []
        to_create = []

        feature_layer_fields = { f['name'].lower():f for f in feature_layer.properties["fields"] }
        oid_field = feature_layer.properties['objectIdField']

        if class_value_field_template['name'] in feature_layer_fields:
            if overwrite:
                to_delete.append(feature_layer_fields[class_value_field_template['name']])
            else:
                e = Exception(f"The specified class_value_field '{class_value_field}' already exists, please specify a different name or set `overwrite=True`")
                raise(e)
        to_create.append(class_value_field_template)

        if class_name_field_template['name'] in feature_layer_fields:
            if overwrite:
                to_delete.append(feature_layer_fields[class_name_field_template['name']])
            else:
                e = Exception(f"The specified class_name_field '{class_name_field}' already exists, please specify a different name or set `overwrite=True`")
                raise(e)
        to_create.append(class_name_field_template)
        
        if confidence_field is not None:
            confidence_field_template = {
                "name": confidence_field.lower(),
                "type": "esriFieldTypeDouble",
                "alias": confidence_field,
                "sqlType": "sqlTypeDouble",
                "nullable": True,
                "editable": True,
                "visible": True,
                "domain": None,
                "defaultValue": -999
            }
            if confidence_field_template['name'] in feature_layer_fields:
                if overwrite:
                    to_delete.append(feature_layer_fields[confidence_field_template['name']])
                else:
                    e = Exception(f"The specified confidence_field '{confidence_field}' already exists, please specify a different name or set `overwrite=True`")
                    raise(e)
            to_create.append(confidence_field_template)

        feature_layer.manager.delete_from_definition({'fields': to_delete})
        feature_layer.manager.add_to_definition({'fields': to_create})

        # Get features for updation
        fields_to_update = [oid_field, class_value_field, class_name_field]
        if confidence_field is not None:
            fields_to_update.append(confidence_field)
        feature_layer_features = feature_layer.query(out_fields=",".join(fields_to_update), return_geometry=False).features
        update_store = {}

        if raster is not None:
            import arcpy

            #Arcpy Environment to export data
            arcpy.env.cellSize = cell_size
            arcpy.env.outputCoordinateSystem = coordinate_system
            arcpy.env.cartographicCoordinateSystem = coordinate_system

            feature_layer_url = feature_layer.url

            if feature_layer._token is not None:
                feature_layer_url = feature_layer_url + f"?token={feature_layer._token}"

            
            
            # Create Temporary ID field
            tempid_field = _tempid_field = 'f_fcuid'
            i = 1
            while tempid_field in feature_layer_fields:
                tempid_field = _tempid_field + str(i)
                i+=1
            arcpy.AddField_management(feature_layer_url, tempid_field, "LONG")
            #feature_layer.manager.add_to_definition({'fields': [tempid_field_template]})
            arcpy.CalculateField_management(feature_layer_url, tempid_field, f"{oid_field}", "SQL")

            temp_folder = arcpy.env.scratchFolder
            temp_datafldr = os.path.join(temp_folder, 'categorize_features_'+str(int(time.time())))
            result = arcpy.ia.ExportTrainingDataForDeepLearning(
                in_raster=raster,
                out_folder=temp_datafldr,
                in_class_data=feature_layer_url,
                image_chip_format="TIFF",
                tile_size_x=self._data.chip_size,
                tile_size_y=self._data.chip_size,
                stride_x=0,
                stride_y=0,
                output_nofeature_tiles="ALL_TILES",
                metadata_format="Labeled_Tiles",
                start_index=0,
                class_value_field=tempid_field,
                buffer_radius=0,
                in_mask_polygons=None,
                rotation_angle=0
            )
            # cleanup
            arcpy.DeleteField_management(feature_layer_url, [ tempid_field ])

            image_list = ImageList.from_folder(os.path.join(temp_datafldr, 'images'))
            def get_id(imagepath):
                with open(os.path.join(temp_datafldr, 'labels', os.path.basename(imagepath)[:-3]+'xml')) as f:
                    return(int(f.read().split('<name>')[1].split('<')[0]))

            for i in range(0, len(image_list), batch_size):
                # Get Temporary Ids
                tempids = [ get_id(f) for f in image_list.items[i:i+batch_size] ]
                
                # Get Image batch
                image_batch = torch.stack([ im.data for im in image_list[i:i+batch_size] ])
                image_batch = normalize(image_batch, mean=norm_mean, std=norm_std)
                
                # Get Predications
                predicted_classes, predictions_conf = self._predict_batch(image_batch)
                
                # push prediction to store
                for ui, oid in enumerate(tempids):
                    classvalue = self._data.classes[predicted_classes[ui]]
                    update_store[oid] = {
                        oid_field: oid,
                        class_value_field: classvalue,
                        class_name_field:  self._data.class_mapping[classvalue]
                    } 
                    if confidence_field is not None:
                        update_store[oid][confidence_field] = predictions_conf[ui]

            # Cleanup
            arcpy.Delete_management(temp_datafldr)
            shutil.rmtree(temp_datafldr, ignore_errors=True)

        else:
            out_folder = tempfile.TemporaryDirectory().name
            os.mkdir(out_folder)
            feature_layer.export_attachments(out_folder)
            with open(os.path.join(out_folder, 'mapping.txt')) as file:
                feature_attachments_mapping = json.load(file)
                images_store = []
                for oid in feature_attachments_mapping:
                    for im in feature_attachments_mapping[oid]:
                        images_store.append({
                            'oid': oid,
                            'im': os.path.join(out_folder,im)
                        })
            update_store_scratch = {}
            for i in range(0, len(images_store), batch_size):
                rel_objectids = []
                image_batch = []
                for r in images_store[i:i+batch_size]:
                    im = open_image(r['im']) # Read Bytes
                    im = im.resize(self._data.chip_size) # Resize
                    image_batch.append(im.data) # Convert to tensor
                    rel_objectids.append(int(r['oid']))
                image_batch = torch.stack(image_batch)
                image_batch = normalize(image_batch, mean=norm_mean, std=norm_std)
                # Get Predictions and save to scratch
                predicted_classes, predictions_conf = self._predict_batch(image_batch)
                for ai, oid in enumerate(rel_objectids):
                    if update_store_scratch.get(oid) is None:
                        update_store_scratch[oid] = []
                    update_store_scratch[oid].append([predicted_classes[ai], predictions_conf[ai]])
            # Prepare final updated features
            for oid in update_store_scratch:
                max_prediction_class, max_prediction_value = predict_function(update_store_scratch[oid])
                if max_prediction_class is not None:
                    classvalue = self._data.classes[max_prediction_class]
                    classname = self._data.class_mapping[classvalue]
                else:
                    classvalue = None
                    classname = None                
                update_store[oid] = {
                    oid_field: oid,
                    class_value_field: classvalue,
                    class_name_field:  classname
                } 
                if confidence_field is not None:
                    update_store[oid][confidence_field] = max_prediction_value

        # Update Features
        features_to_update = []
        for feat in feature_layer_features:
            if update_store.get(feat.attributes[oid_field]) is not None:
                updated_attributes = update_store[feat.attributes[oid_field]]
                for f in fields_to_update:
                    feat.attributes[f] = updated_attributes[f]
                features_to_update.append(feat)
        step = 100
        for si in range(0, len(features_to_update), step):
            feature_batch = features_to_update[si:si+step]
            response = feature_layer.edit_features(updates=feature_batch)
            for resp in response.get('updateResults', []):
                if resp.get('success', False):
                    continue
                warnings.warn(f"Something went wrong for data {resp}")
            time.sleep(2)


    def _categorize_feature_class(
        self,
        feature_class,
        raster,
        class_value_field,
        class_name_field,
        confidence_field,
        cell_size,
        coordinate_system,
        predict_function,
        batch_size,
        overwrite
    ):
        import arcpy
        arcpy.env.overwriteOutput = overwrite

        if batch_size is None:
            batch_size  = self._data.batch_size

        if predict_function is None:
            predict_function = _prediction_function
        
        norm_mean = torch.tensor(imagenet_stats[0])
        norm_std = torch.tensor(imagenet_stats[1])
        
        fcdesc = arcpy.Describe(feature_class)
        oid_field = fcdesc.OIDFieldName
        if not (fcdesc.dataType == 'FeatureClass' and fcdesc.shapeType == 'Polygon'):
            e = Exception(f"The specified FeatureClass at '{feature_class}' is not valid, it should be Polygon FeatureClass")
            raise(e)
        fields = arcpy.ListFields(feature_class)
        field_names = [f.name for f in fields]
        if class_value_field in field_names:
            if not overwrite:
                e = Exception(f"The specified class_value_field '{class_value_field}' already exists in the target FeatureClass, please specify a different name or set `overwrite=True`")
                raise(e)
        arcpy.DeleteField_management(feature_class, 
                                [ class_value_field ])
        arcpy.AddField_management(feature_class, class_value_field, "LONG")
            
        if class_name_field in field_names:
            if not overwrite:
                e = Exception(f"The specified class_name_field '{class_name_field}' already exists in the target FeatureClass, please specify a different name or set `overwrite=True`")
                raise(e)
        arcpy.DeleteField_management(feature_class, 
                                [ class_name_field ])
        arcpy.AddField_management(feature_class, class_name_field, "TEXT")

        if confidence_field is not None:
            if confidence_field in field_names:
                if not overwrite:
                    e = Exception(f"The specified confidence_field '{confidence_field}' already exists in the target FeatureClass, please specify a different name or set `overwrite=True`")
                    raise(e)
            arcpy.DeleteField_management(feature_class, 
                                    [ confidence_field ])
            arcpy.AddField_management(feature_class, confidence_field, "DOUBLE")

        if raster is not None:
            #Arcpy Environment to export data
            arcpy.env.cellSize = cell_size
            arcpy.env.outputCoordinateSystem = coordinate_system
            arcpy.env.cartographicCoordinateSystem = coordinate_system

            tempid_field = _tempid_field = 'f_fcuid'
            i = 1
            while tempid_field in field_names:
                tempid_field = _tempid_field + str(i)
                i+=1
            arcpy.AddField_management(feature_class, tempid_field, "LONG")
            arcpy.CalculateField_management(feature_class, tempid_field, f"!{oid_field}!")

            temp_folder = arcpy.env.scratchFolder
            temp_datafldr = os.path.join(temp_folder, 'categorize_features_'+str(int(time.time())))
            result = arcpy.ia.ExportTrainingDataForDeepLearning(
                in_raster=raster,
                out_folder=temp_datafldr,
                in_class_data=feature_class,
                image_chip_format="TIFF",
                tile_size_x=self._data.chip_size,
                tile_size_y=self._data.chip_size,
                stride_x=0,
                stride_y=0,
                output_nofeature_tiles="ALL_TILES",
                metadata_format="Labeled_Tiles",
                start_index=0,
                class_value_field=tempid_field,
                buffer_radius=0,
                in_mask_polygons=None,
                rotation_angle=0
            )
            # cleanup
            arcpy.DeleteField_management(feature_class, [ tempid_field ])
            image_list = ImageList.from_folder(os.path.join(temp_datafldr, 'images'))
            def get_id(imagepath):
                with open(os.path.join(temp_datafldr, 'labels', os.path.basename(imagepath)[:-3]+'xml')) as f:
                    return(int(f.read().split('<name>')[1].split('<')[0]))

            for i in range(0, len(image_list), batch_size):
                # Get Temporary Ids
                tempids =[ get_id(f) for f in image_list.items[i:i+batch_size] ]
                
                # Get Image batch
                image_batch = torch.stack([ im.data for im in image_list[i:i+batch_size] ])
                image_batch = normalize(image_batch, mean=norm_mean, std=norm_std)
                
                # Get Predications
                predicted_classes, predictions_conf = self._predict_batch(image_batch)
                
                # Update Feature Class
                where_clause = f"{oid_field} IN ({','.join(str(e) for e in tempids)})"
                update_cursor = arcpy.UpdateCursor(
                    feature_class,
                    where_clause=where_clause,
                    sort_fields=f"{oid_field} A"
                )
                for row in update_cursor:
                    row_tempid = row.getValue(oid_field)
                    ui = tempids.index(row_tempid)
                    classvalue = self._data.classes[predicted_classes[ui]]
                    row.setValue(class_value_field, classvalue)
                    row.setValue(class_name_field, self._data.class_mapping[classvalue])
                    if confidence_field is not None:
                        row.setValue(confidence_field, predictions_conf[ui])
                    update_cursor.updateRow(row)

                # Remove Locks
                del row
                del update_cursor

            # Cleanup
            arcpy.Delete_management(temp_datafldr)
            shutil.rmtree(temp_datafldr, ignore_errors=True)

        else:
            feature_class_attach = feature_class+'__ATTACH'
            nrows = arcpy.GetCount_management(feature_class_attach)[0]
            store={}
            for i in range(0, int(nrows), batch_size):
                attachment_ids = []
                rel_objectids = []
                image_batch = []
                
                # Get Image Batch
                with arcpy.da.SearchCursor(feature_class_attach, [ 'ATTACHMENTID', 'REL_OBJECTID', 'DATA' ]) as search_cursor:
                    for c, item in enumerate(search_cursor):
                        if c >= i and c < i+batch_size :
                            attachment_ids.append(item[0])
                            rel_objectids.append(item[1])
                            attachment = item[-1]
                            im = open_image(io.BytesIO(attachment.tobytes())) # Read Bytes
                            im = im.resize(self._data.chip_size) # Resize
                            image_batch.append(im.data) # Convert to tensor
                            del item
                            del attachment
                            #del im
                image_batch = torch.stack(image_batch)
                image_batch = normalize(image_batch, mean=norm_mean, std=norm_std)
                
                # Get Predictions and save to store
                predicted_classes, predictions_conf = self._predict_batch(image_batch)
                for ai in range(len(attachment_ids)):
                    if store.get(rel_objectids[ai]) is None:
                        store[rel_objectids[ai]] = []
                    store[rel_objectids[ai]].append([predicted_classes[ai], predictions_conf[ai]])
                
            # Update Feature Class
            update_cursor = arcpy.UpdateCursor(feature_class)
            for row in update_cursor:
                row_oid = row.getValue(oid_field)
                max_prediction_class, max_prediction_value = predict_function(store[row_oid])
                if max_prediction_class is not None:
                    classvalue = self._data.classes[max_prediction_class]
                    classname = self._data.class_mapping[classvalue]
                else:
                    classvalue = None
                    classname = None
                row.setValue(class_value_field, classvalue)
                row.setValue(class_name_field, classname)
                if confidence_field is not None:
                    row.setValue(confidence_field, max_prediction_value)
                update_cursor.updateRow(row)

            # Remove Locks
            del row
            del update_cursor
        return True

    def categorize_features(
        self,
        feature_layer,
        raster=None,
        class_value_field='class_val',
        class_name_field='prediction',
        confidence_field="confidence",
        cell_size=1,
        coordinate_system=3857,
        predict_function=None,
        batch_size=64,
        overwrite=False 
    ):
        """
        Categorizes each feature by classifying its attachments or an image of its geographical area (using the provided Imagery Layer)
        and updates the feature layer with the prediction results in the ``output_label_field``.

        ====================================     ====================================================================
        **Argument**                             **Description**
        ------------------------------------     --------------------------------------------------------------------
        feature_layer                            Required. Feature Layer or path of local feature class for classification with read, write, edit permissions.
        ------------------------------------     --------------------------------------------------------------------
        raster                                   Optional. Imagery layer or path of local raster to be used for exporting image chips. (Requires arcpy)
        ------------------------------------     --------------------------------------------------------------------
        class_value_field                        Required string. Output field to be added in the layer, containing class value of predictions.
        ------------------------------------     --------------------------------------------------------------------
        class_name_field                         Required string. Output field to be added in the layer, containing class name of predictions.
        ------------------------------------     --------------------------------------------------------------------
        confidence_field                         Optional string. Output column name to be added in the layer which contains the confidence score.
        ------------------------------------     --------------------------------------------------------------------
        cell_size                                Optional float. Cell size to be used for exporting the image chips.
        ------------------------------------     --------------------------------------------------------------------
        coordinate_system                        Optional. Cartographic Coordinate System to be used for exporting the image chips.
        ------------------------------------     --------------------------------------------------------------------
        predict_function                         Optional list of tuples. Used for calculation of final prediction result when each feature
                                                 has more than one attachment. The ``predict_function`` takes as input a list of tuples.
                                                 Each tuple has first element as the class predicted and second element is the confidence score.
                                                 The function should return the final tuple classifying the feature and its confidence.
        ------------------------------------     --------------------------------------------------------------------
        batch_size                               Optional integer. The no of images or tiles to process in a single go. 
                                                 
                                                 The default value is 64.
        ------------------------------------     --------------------------------------------------------------------
        overwrite                                Optional boolean. If set to True the output fields will be overwritten by new values. 

                                                 The default value is False.
        ====================================     ====================================================================

        :return:
            Boolean : True if operation is successful, False otherwise

        """        

        import arcgis
        from arcgis.features import FeatureLayer
        from arcgis.raster import ImageryLayer
        from arcgis.gis import Item
        
        if predict_function is None:
            predict_function = _prediction_function

        if isinstance(raster, str):
            if 'http' in raster:
                raster = ImageryLayer(raster, gis=arcgis.env.active_gis)
        if isinstance(raster, ImageryLayer):
            raster_url = raster.url
            if raster._token is not None:
                raster_url = raster_url + f"?token={raster._token}" 
            raster = raster_url
        elif isinstance(raster, Item):  # handles Mapserver
            raster_url = raster.url
            if raster.layers[0]._token is not None:
                raster_url = raster_url + f"?token={raster.layers[0]._token}" 
            raster = raster_url

        if isinstance(feature_layer, str):
            if 'http' in feature_layer:
                feature_layer = FeatureLayer(feature_layer, gis=arcgis.env.active_gis)
            else:
                return self._categorize_feature_class(
                    feature_class=feature_layer,
                    raster=raster,
                    class_value_field=class_value_field,
                    class_name_field=class_name_field,
                    confidence_field=confidence_field,
                    cell_size=cell_size,
                    coordinate_system=coordinate_system,
                    predict_function=predict_function,
                    batch_size=batch_size,
                    overwrite=overwrite
                )

        if isinstance(feature_layer, FeatureLayer):
            return self._categorize_feature_layer(
                feature_layer=feature_layer,
                raster=raster,
                class_value_field=class_value_field,
                class_name_field=class_name_field,
                confidence_field=confidence_field,
                cell_size=cell_size,
                coordinate_system=coordinate_system,
                predict_function=predict_function,
                batch_size=batch_size,
                overwrite=overwrite
            )
        else:
            e = Exception("Could not understand layer type")
            raise(e)
            

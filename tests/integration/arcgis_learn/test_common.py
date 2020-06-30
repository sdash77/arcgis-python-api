# -------------------------------------------------------------------------------
# Name:        Common Arcgis Learn Tests.
# Purpose:     Common Tests for arcgis learn to factor same code out.
# -------------------------------------------------------------------------------

import unittest
import os
from integration.arcgis_learn.env import *
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

HAS_DEPS = True
try:
    import fastai
    import torch
    import torchvision
    from torchvision import models
    import pandas as pd
    from datetime import datetime
except Exception:
    HAS_DEPS = False

module_skip = False

if not HAS_DEPS:
    module_skip = True
else:
    from arcgis.learn import SingleShotDetector, UnetClassifier, PSPNetClassifier, FeatureClassifier, RetinaNet, MaskRCNN, prepare_data

####
update_dict = {"attributes":
                {"Date": "",
                "ssd": 0,
                "retinanet": 0,
                "unet": 0,
                "pspnet": 0,
                "maskrcnn": 0,
                "featureclassifier": 0}}
# TestModule
@unittest.skipIf(module_skip, "Precondition check failed. Skipping Common tests")
def setUpModule():
    setupenviron()
    print("Dependencies Installed.")
    if os.environ['nightly_test'] == "1":
        update_dict["attributes"]["Date"] = convertdate(datetime.today())
    
def updateAccuracyResults():
    from arcgis.gis import GIS
    from arcgis.features import FeatureLayerCollection
    gis = GIS("https://deldev.maps.arcgis.com", "demos_deldev", "DelDevs12")
    item = gis.content.get('30ca1ab53255408dbb1aea9fa6cb8c14')
    data = item.tables[0]
    data.edit_features(adds=[update_dict])

def convertdate(dates):
    day = dates.day
    month = dates.month
    year = dates.year
    dstr = str(str(month)+'/'+str(day)+'/'+str(year))
    return dstr

def common_test(test_object, model_type, output_name, data_path, old_models, **prepare_data_kwargs):
    # Prepare Data bunch.
    data = prepare_data(data_path, **prepare_data_kwargs)

    # Default backbone model
    model_object = model_type(data)

    #Show results without training.
    model_object.show_results()

    # Save object without training.
    model_object.save(f"pre_fit_{output_name}")

    # Fit for 5 epochs without LR.
    model_object.fit(5)

    # Fit for 10 epochs if nightly tests are run.
    if os.environ['nightly_test'] == "1":
        model_object.fit(15)

    # Fit for 5 epochs with LR.
    model_object.fit(1, lr=0.001)

    # Save after training.
    model_object.save(f'post_fit_{output_name}')

    # Show results after training.
    model_object.show_results()

    # Test for accuracy if nightly_test is run
    if os.environ['nightly_test'] == "1":
        score = 0
        if output_name in ['retinanet', 'ssd', 'maskrcnn']:
            score = model_object.average_precision_score(mean=True)
            # updatecsv(output_name, score)
        elif output_name in ['unet', 'pspnet']:
            score = model_object.mIOU(mean=True)
        # TO-DO
        elif output_name in ['featureclassifier']:
            score = 0
        update_dict["attributes"][output_name] = score

    # Load from saved model.
    model_object.load(f'post_fit_{output_name}')

    # Check all supported backbones.
    supported_backbones = model_type.supported_backbones

    if os.environ['run_backbones'] == "1":
        for backbone in supported_backbones:
            model_object = model_type(data, backbone=backbone)
            model_object.fit(1, lr=0.1)

    # From model with and without data bunch.
    model_object = model_type.from_model(os.path.join(data_path, f'models/post_fit_{output_name}/post_fit_{output_name}.emd'))
    model_object = model_type.from_model(os.path.join(data_path, f'models/post_fit_{output_name}/post_fit_{output_name}.emd'), data)

    # Load old models.
    for old_model in old_models:
        model_object = model_type.from_model(old_model)

    #For object detection inferencing.

def object_detection_inferencing(in_model_definition, in_raster, out_detected_objects, model_args):
    import arcpy
    arcpy.env.processorType = "GPU"
    arcpy.CheckOutExtension("ImageAnalyst")

    arcpy.ia.DetectObjectsUsingDeepLearning(
        in_raster,
        out_detected_objects,
        in_model_definition,
        model_args,
        "NO_NMS",
        "Confidence",
        "Class",
        0,
        "PROCESS_AS_MOSAICKED_IMAGE"
    )

def pixel_classification_inferencing(in_model_definition, in_raster):
    import arcpy
    arcpy.env.processorType = "GPU"
    arcpy.CheckOutExtension("ImageAnalyst")

    arcpy.ia.ClassifyPixelsUsingDeepLearning(
        in_raster,
        in_model_definition,
        "padding 56;batch_size 4;predict_background True",
        "PROCESS_AS_MOSAICKED_IMAGE"
    )

    
def classify_features_test(in_model_definition, in_raster, feature_layer, output_path):
    import arcpy
    arcpy.env.processorType = "GPU"
    arcpy.CheckOutExtension("ImageAnalyst")

    arcpy.ia.ClassifyObjectsUsingDeepLearning(
        in_raster,
        output_path,
        in_model_definition,
        in_features=feature_layer,
        class_label_field="ClassLabel",
        processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
        model_arguments="batch_size 4"
    )

@unittest.skipIf(module_skip, "Precondition check failed. Skipping Common tests")
class Test_Common(unittest.TestCase):
    """
    Test to check if Prepare Data works correctly.
    """

    @classmethod
    def setUpClass(cls):
        #Training Data
        cls.obj_detection_data1 = os.environ["object_detection_data1"]
        cls.obj_detection_data2 = os.environ["object_detection_data2"]
        cls.obj_detection_data3 = os.environ["object_detection_data3"]

        cls.pixel_classification_data1 = os.environ['pixel_classification_data1']
        cls.pixel_classification_inferencing_data1 = os.environ['pixel_classification_inferencing_data1']

        cls.feature_classification_data1 = os.environ['feature_classification_data1']
        cls.feature_classification_inferencing_data1 = os.environ['feature_classification_inferencing_data1']
        cls.feature_classification_inferencing_in_raster = os.environ['feature_classification_inferencing_in_raster']

        cls.maskrcnn_data1 = os.environ['maskrcnn_data1']

        # if os.environ['run_inferencing'] == '1':
        #Inferencing Data
        cls.obj_detection_inference_data1 = os.environ["object_detection_inferencing_data1"]
        cls.obj_detection_inference_data2 = os.environ["object_detection_inferencing_data2"]

        #SSD
        cls.model_ssd_162 = os.environ["model_ssd_162"]
        cls.model_ssd_170 = os.environ["model_ssd_170"]

        #Unet
        cls.model_unet_162 = os.environ["model_unet_162"]
        cls.model_unet_170 = os.environ["model_unet_170"]

        #Feature Classification
        cls.model_fc_162 = os.environ["model_fc_162"]
        cls.model_fc_170 = os.environ["model_fc_170"]

        #Retinanet
        cls.model_rn_170 = os.environ["model_rn_170"]

        #PSPNet
        cls.model_pspnet_170 = os.environ['model_pspnet_170']

        #MaskRCNN
        cls.model_maskrcnn_170 = os.environ['model_maskrcnn_170']

    def setUp(self):
        print("Test: " + self._testMethodName)

    def tearDown(self):
        print("Test:" + self._testMethodName + "is completed.\n")
        print("----------------------------------------------\n")

    @classmethod
    def tearDownClass(cls):
        print("\n All Tests have completed")
        print("==================================================================")

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_ssd(self):
        common_test(
            self,
            SingleShotDetector,
            'ssd',
            self.obj_detection_data2,
            [self.model_ssd_162, self.model_ssd_170],
            batch_size=8,
            chip_size=300
        )

        if os.environ['run_inferencing'] == '1':
            object_detection_inferencing(
                os.path.join(self.obj_detection_data2, 'models/post_fit_ssd/post_fit_ssd.emd'),
                self.obj_detection_inference_data1,
                os.environ["object_detection_inferencing_result_ssd"],
                os.environ["object_detection_inferencing_ssd_args"]
            )

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_retinanet(self):
        common_test(
            self,
            RetinaNet,
            'retinanet',
            self.obj_detection_data2,
            [self.model_rn_170],
            batch_size=8,
            chip_size=300
        )
        if os.environ['run_inferencing'] == '1':
            object_detection_inferencing(
                os.path.join(self.obj_detection_data2, 'models/post_fit_retinanet/post_fit_retinanet.emd'),
                self.obj_detection_inference_data1,
                os.environ["object_detection_inferencing_result_rn"],
                os.environ["object_detection_inferencing_rn_args"]
            )

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_unet(self):
        common_test(
            self,
            UnetClassifier,
            'unet',
            self.pixel_classification_data1,
            [self.model_unet_162, self.model_unet_170],
            batch_size=8
        )
        
        if os.environ['run_inferencing'] == '1':
            pixel_classification_inferencing(
                os.path.join(self.pixel_classification_data1, 'models/post_fit_unet/post_fit_unet.emd'),
                self.pixel_classification_inferencing_data1
            )

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_fc(self):
        common_test(
            self,
            FeatureClassifier,
            'featureclassifier',
            self.feature_classification_data1,
            [self.model_fc_162, self.model_fc_170],
            batch_size=8
        )

        if os.environ['run_inferencing'] == '1':
            classify_features_test(
                os.path.join(self.feature_classification_data1, 'models/post_fit_featureclassifier/post_fit_featureclassifier.emd'),
                self.feature_classification_inferencing_in_raster,
                self.feature_classification_inferencing_data1,
                os.environ['inferencing_result_fc']
            )

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_pspnet(self):
        common_test(
            self,
            PSPNetClassifier,
            'pspnet',
            self.pixel_classification_data1,
            [self.model_pspnet_170],
            batch_size=8
        )

        if os.environ['run_inferencing'] == '1':
            pixel_classification_inferencing(
                os.path.join(self.pixel_classification_data1, 'models/post_fit_pspnet/post_fit_pspnet.emd'),
                self.pixel_classification_inferencing_data1
            )

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    def test_maskrcnn(self):
        common_test(
            self,
            MaskRCNN,
            'maskrcnn',
            self.maskrcnn_data1,
            [self.model_maskrcnn_170],
            batch_size=8
        )

        if os.environ['run_inferencing'] == '1':
            object_detection_inferencing(
                os.path.join(self.maskrcnn_data1, 'models/post_fit_maskrcnn/post_fit_maskrcnn.emd'),
                self.obj_detection_inference_data1,
                os.environ["object_detection_inferencing_result_maskrcnn"],
                os.environ["object_detection_inferencing_maskrcnn_args"]
            )


# TestModule
def tearDownModule():
    if os.environ['nightly_test'] == "1":
        print("Updating feature layer for accuracy dashboard\n")
        updateAccuracyResults()
    os.system(f'rm -rf "{os.path.join(os.environ["object_detection_data1"], "models")}"')
    os.system(f'rm -rf "{os.path.join(os.environ["object_detection_data1"], "images/models")}"')

    os.system(f'rm -rf "{os.path.join(os.environ["object_detection_data2"], "models")}"')
    os.system(f'rm -rf "{os.path.join(os.environ["object_detection_data2"], "images/models")}"')

    os.system(f'rm -rf "{os.path.join(os.environ["object_detection_data3"], "models")}"')
    os.system(f'rm -rf "{os.path.join(os.environ["object_detection_data3"], "images/models")}"')

    os.system(f'rm -rf "{os.path.join(os.environ["pixel_classification_data1"], "models")}"')
    os.system(f'rm -rf "{os.path.join(os.environ["pixel_classification_data1"], "images/models")}"')

    os.system(f'rm -rf "{os.path.join(os.environ["feature_classification_data1"], "models")}"')
    os.system(f'rm -rf "{os.path.join(os.environ["feature_classification_data1"], "images/models")}"')

    os.system(f'rm -rf "{os.path.join(os.environ["maskrcnn_data1"], "models")}"')
    os.system(f'rm -rf "{os.path.join(os.environ["maskrcnn_data1"], "images/models")}"')

    os.system(f'rm -rf "{os.path.join(os.environ["notebook_test"])}"')

    # outputs_to_delete = os.listdir(os.path.dirname(os.environ["object_detection_inferencing_result_ssd"]))
    # for output_files in outputs_to_delete:
    #     os.remove(f'{os.path.join(os.path.dirname(os.environ["object_detection_inferencing_result_ssd"]), output_files)}')

    # outputs_to_delete = os.listdir(os.path.dirname(os.environ["object_detection_inferencing_result_rn"]))
    # for output_files in outputs_to_delete:
    #     os.remove(f'{os.path.join(os.path.dirname(os.environ["object_detection_inferencing_result_rn"]), output_files)}')

    print("**End Common Arcgis Learn module Tests**")




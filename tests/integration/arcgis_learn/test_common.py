# -------------------------------------------------------------------
# Name:        Common Arcgis Learn Tests.
# Purpose:     Common Tests for arcgis learn to factor same code out.
# -------------------------------------------------------------------


import os
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
import unittest
import traceback
from parameterized import parameterized
from fastai.vision.learner import ClassificationInterpretation
import random
import string
import_exception = None

try:
    import fastai
    import torch
    import torchvision
    import pytest
    HAS_DEPS = True
    print(" ================= Modules Imported ==============")
except Exception as e:
    import_exception = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))
    HAS_DEPS = False


module_skip = False
parameter = []
if not HAS_DEPS:
    print("**Environment fails**")
    raise Exception(f"""{import_exception} \n\nThis module requires fastai, PyTorch, torchvision and scikit-image as its dependencies.""")
    module_skip = True
else:
    from integration.arcgis_learn.properties import data,data_folder, setuposenviron
    from arcgis.learn import prepare_data
    from datetime import datetime


accuracy_values = {"attributes":
                {"Date": "",
                "ssd": 0,
                "retinanet": 0,
                "unet": 0,
                "pspnet": 0,
                "maskrcnn": 0,
                "featureclassifier": 0,
                 "fasterrcnn":0,
                 "superres":0,
                 "ner":0,
                 "deeplab":0,
                 "pointcnn":0
                 }}

@unittest.skipIf(module_skip, "Precondition check failed. Skipping Common tests")
def setUpModule():
    setuposenviron()
    data_path = data_folder
    if os.environ['run_nightly'] == "1":
        accuracy_values["attributes"]["Date"] = convertdate(datetime.today())
    print("Setup completed successfully")


def updateAccuracyResults():
    from arcgis.gis import GIS
    from arcgis.features import FeatureLayerCollection
    gis = GIS("https://deldev.maps.arcgis.com", "demos_deldev", "DelDevs12")
    item = gis.content.get('30ca1ab53255408dbb1aea9fa6cb8c14')
    data = item.tables[0]
    global accuracy_values
    data.edit_features(adds=[accuracy_values])



def convertdate(dates):
    day = dates.day
    month = dates.month
    year = dates.year
    dstr = str(str(month)+'/'+str(day)+'/'+str(year))
    return dstr


def commonTestCases(model_type, model_test, data_path, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name):
    data = prepare_data(**preparedata)

    # Check model with all default backbone
    model_object = model_type(data)
    # Fit for 1 epochs without LR.
    model_object.fit(1)
    # Fit for 1 epochs with LR.
    model_object.fit(1, lr=0.001)

    ## Check model with all supported backbones
    if os.environ['run_backbones'] == "1":
        print("Testing for all backbones")
        supported_backbones = model_object.supported_backbones
        for backbone in supported_backbones:
            model_object = model_type(data, backbone=str(backbone))
            model_object.fit(1)
            model_object.save(model_test + '_' + str(backbone))
            torch.cuda.empty_cache()

    if os.environ['run_nightly'] == "1":
        print("Testing for accuracy with default backbone")
        global accuracy_values
        model_object.fit(15)
        if regression_parameter == "average_precision_score":
            score = model_object.average_precision_score()
            score = [v for k, v in sorted(score.items(), key=lambda item: item[1], reverse=True)][0]
        elif regression_parameter == "accuracy":
            score = model_object.accuracy()
        elif regression_parameter == "confusion_matrix":
            array = ClassificationInterpretation.from_learner(model_object.learn).confusion_matrix()
            true_prediction = array.diagonal().sum()
            all_prediction = array.sum()
            score = true_prediction / all_prediction
        elif regression_parameter == "precision_score":
            score = model_object.precision_score()
        elif regression_parameter == "compute_precision_recall":
            score = model_object.compute_precision_recall().accuracy.loc["precision", :].max()
        elif regression_parameter == "psnr_metric":
            score = model_object.psnr_metric()
        else:
            score = 0.0

        accuracy_values["attributes"][model_name] = score

        # assert (accuracy >= regression_test_score),"Model accuracy is lower than the threshold value. Please check."



    ## Inferencing function here.
    if os.environ["run_inference"] == "1":
        from arcpy.ia import DetectObjectsUsingDeepLearning, ClassifyPixelsUsingDeepLearning, ClassifyObjectsUsingDeepLearning

        letters = string.ascii_lowercase
        output_name = ''.join(random.choice(letters) for i in range(9)) + ".shp"

        if inferencing_parameter["model_type"] == "DetectObjectsUsingDeepLearning":
            DetectObjectsUsingDeepLearning(
                    inferencing_parameter["sample_input"],
                os.path.join(inferencing_parameter["path"], output_name),
                inferencing_parameter["model"],
                inferencing_parameter["parameters"]
            )
        elif inferencing_parameter["model_type"] == "ClassifyPixelsUsingDeepLearning":
            ClassifyPixelsUsingDeepLearning(
                inferencing_parameter["sample_input"],
                inferencing_parameter["model"],
                inferencing_parameter["parameters"],
                "PROCESS_AS_MOSAICKED_IMAGE"
            )
        elif inferencing_parameter["model_type"] == "ClassifyObjectsUsingDeepLearning":
            ClassifyObjectsUsingDeepLearning(
                inferencing_parameter["sample_input"],
                inferencing_parameter["path"],
                inferencing_parameter["model"],
                in_features=inferencing_parameter["feature_layer"],
                class_label_field="ClassLabel",
                processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
                model_arguments="batch_size 4"

            )
        else:
            pass

    # save model
    model_object.save(f'{model_test}')
    # Load from saved model.
    model_object.load(f'{model_test}')

    # From model with and without data bunch.
    model_object = model_type.from_model(os.path.join(data_folder,data_path, f'models/{model_test}/{model_test}.emd'))
    model_object = model_type.from_model(os.path.join(data_folder, data_path, f'models/{model_test}/{model_test}.emd'),
                                         data)


def update_parameter():
    for key, val in data.items():
        if val["should_test"]:
            parameter.append([key, val["model_test"], val["model"], val["datapath"], val["prepare_data"], val["regression_parameter"], val["regression_test_score"], val["inferencing_parameter"], val["model_name"]])
    return parameter

class TestTraining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Inside Setup Class!!!")


    def setUp(self):
        print("Test: " + self._testMethodName)

    def tearDown(self):
        print("Test:" + self._testMethodName + "is completed.\n")
        print("------------------------------------------------------------------\n")

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter)
    def test(self,name,model_test, model, datapath, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name):
        commonTestCases(model,model_test, datapath, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name)

    @classmethod
    def tearDownClass(cls):
        print("\n All Tests have completed")
        print("==================================================================")




## Remove all model directories
def tearDownModule():
    if os.environ['run_nightly'] == "1":
        print("Updating feature layer for accuracy dashboard\n")
        updateAccuracyResults()
    for key, val in data.items():
        os.system(f'rm -rf "{os.path.join(data_folder,val["datapath"],"models")}"')

    print("**End Common Arcgis Learn module Training**")





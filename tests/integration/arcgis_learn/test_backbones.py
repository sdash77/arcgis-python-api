# -------------------------------------------------------------------
# Name:        Model Specific Arcgis Learn Tests.
# Purpose:     Backbones and Model Specific Features' Tests for 
#              arcgis learn to make code robust to future changes.
# -------------------------------------------------------------------

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import unittest
from parameterized import parameterized
from properties_backbones import (
    data_folder,
    data_folder_ms,
    data,
)
from fastai.vision.learner import ClassificationInterpretation

accuracy_values = {}
fc_backbones = ["dofa_base", "timm:swin_base_window12", "hf:resnet18_landsat_etm_sr_moco"]


def modelAPIs(model, model_object, num_epochs, data_path, model_test, regression_parameter, data):
    print("Running modelAPIs for", model_test, data_path)
    lr_val = model_object.lr_find(allow_plot=False)
    model_object.fit(num_epochs, lr=lr_val, checkpoint=False)
    # save model
    d_path = os.path.join(data_folder, data_path, "models", model_test)
    model_save_path = model_object.save(f"{d_path}")
    #computing accuracy
    if regression_parameter == "confusion_matrix":
        array = ClassificationInterpretation.from_learner(
                    model_object.learn
                ).confusion_matrix()
        true_prediction = array.diagonal().sum()
        all_prediction = array.sum()
        result = true_prediction / all_prediction
        print("accuracy value for ", model_test, "is: ", result) #add results to dict later
    else:
        pass #add for other models
    print("testing model object load")
    model_object.load(str(model_save_path) + os.sep + f"{model_test}.emd")
    # From model with and without data bunch.
    print("testing model object from model w/o data")
    model_object = model.from_model(
        str(model_save_path) + os.sep + f"{model_test}.emd"
    )
    print("testing model object from model with data")
    model_object = model.from_model(
        str(model_save_path) + os.sep + f"{model_test}.emd", data
    )




def commonTestCases(
    model,
    model_test,
    data_path,
    preparedata,
    regression_parameter,
    regression_test_score,
    model_name,
    num_epochs,
    is_ms,
):
    # Prepare data
    from arcgis.learn import prepare_data
    if False: #to include preparedata for text and tabular data
        pass
    else:
        data = prepare_data(**preparedata)
    
    if model_test == "fc_singleLabel_test" or model_test == "fc_multiLabel_test" or model_test == "fc_singleLabel_test_ms" or model_test == "fc_multiLabel_test_ms":
        for bbone in fc_backbones:
            if bbone == "dofa_base":
                if is_ms:
                    model_object = model(data, backbone=bbone, wavelengths=[0.65, 0.55, 0.45, 0.85])
                    print("The ms model initialized will be", bbone)
                else:
                    model_object = model(data, backbone=bbone, wavelengths=[0.49, 0.56, 0.665])
                    print("The rgb model initialized will be", bbone)
            else:
                model_object = model(data, backbone=bbone)
                print("The model initialized will be", bbone)
            print('Running the test for backbone:', bbone)
            #write model initialiation, fit etc code here
            modelAPIs(model, model_object, num_epochs, data_path, model_test, regression_parameter, data)
    else:
        model_object = model(data)
        modelAPIs(model, model_object, num_epochs, data_path, model_test, regression_parameter, data)
        



def update_parameter():
    is_ms = False
    parameter = []
    for key, val in data.items():
        if val["should_test"] and not val["test_feature_layer"]:
            parameter.append(
                (
                    key,
                    val["model_test"],
                    val["model"],
                    val["datapath"],
                    val["prepare_data"],
                    val["regression_parameter"],
                    val["regression_test_score"],
                    val["model_name"],
                    val["regression_epochs"],
                    is_ms,
                )
            )
    return parameter


def update_parameter_ms():
    is_ms = True
    parameter = []
    for key, val in data.items():
        if (
            val["should_test"]
            and not val["test_feature_layer"]
            and val["prepare_data_ms"] != False
        ):
            parameter.append(
                (
                    key+"_ms",
                    val["model_test"]+"_ms",
                    val["model"],
                    val["datapath_ms"],
                    val["prepare_data_ms"],
                    val["regression_parameter"],
                    val["regression_test_score"],
                    val["model_name"],
                    val["regression_epochs"],
                    is_ms,
                )
            )
    return parameter

class TestBackbonesFeatures(unittest.TestCase):
    @parameterized.expand(update_parameter)
    def test(
        self,
        name,
        model_test,
        model,
        datapath,
        preparedata,
        regression_parameter,
        regression_test_score,
        model_name,
        num_epochs,
        is_ms,
    ):
        commonTestCases(
            model,
            model_test,
            datapath,
            preparedata,
            regression_parameter,
            regression_test_score,
            model_name,
            num_epochs,
            is_ms,
        )


    @parameterized.expand(update_parameter_ms)
    def test_ms(
            self,
            name,
            model_test,
            model,
            datapath,
            preparedata,
            regression_parameter,
            regression_test_score,
            model_name,
            num_epochs,
            is_ms,
    ):
        commonTestCases(
            model,
            model_test,
            datapath,
            preparedata,
            regression_parameter,
            regression_test_score,
            model_name,
            num_epochs,
            is_ms,
        )
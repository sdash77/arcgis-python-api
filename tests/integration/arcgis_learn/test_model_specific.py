# -------------------------------------------------------------------
# Name:        Model Specific Arcgis Learn Tests.
# Purpose:     Backbones and Model Specific Features' Tests for 
#              arcgis learn to make code robust to future changes.
# -------------------------------------------------------------------

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import unittest
from parameterized import parameterized
from properties_model_specific import (
    data_folder,
    data_folder_ms,
    data_folder_tabular,
    data,
)
from fastai.vision.learner import ClassificationInterpretation
import urllib.parse

accuracy_values = {}

def modelAPIs_backbones(model, model_object, num_epochs, data_path, model_test, regression_parameter, data, bbone):
    print("Running backbone modelAPIs for", model_test, data_path)
    lr_val = model_object.lr_find(allow_plot=False)
    model_object.fit(num_epochs, lr=lr_val, checkpoint=False)
    model_object.plot_losses()
    model_object.show_results()
    # save model
    d_path = os.path.join(data_folder, data_path, "models", model_test+"_"+urllib.parse.quote(bbone, safe=""))
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
    model_object.load(str(model_save_path) + os.sep + f"{model_test}_{urllib.parse.quote(bbone, safe='')}.emd")
    # From model with and without data bunch.
    print("testing model object from model w/o data")
    model_object = model.from_model(
        str(model_save_path) + os.sep + f"{model_test}_{urllib.parse.quote(bbone, safe='')}.emd"
    )
    print("testing model object from model with data")
    model_object = model.from_model(
        str(model_save_path) + os.sep + f"{model_test}_{urllib.parse.quote(bbone, safe='')}.emd", data
    )




def backboneTestCases(
    model,
    model_test,
    data_path,
    preparedata,
    regression_parameter,
    regression_test_score,
    model_name,
    num_epochs,
    is_ms,
    bbone,
    wavelengths_dofa,
):
    # Prepare data
    from arcgis.learn import prepare_data
    data = prepare_data(**preparedata)
    data.show_batch()
    if bbone == "dofa_base":
        if is_ms:
            model_object = model(data, backbone = bbone, wavelengths = wavelengths_dofa)
            print("The ms model initialized will be", model_test, bbone, wavelengths_dofa)
        else:
            model_object = model(data, backbone = bbone, wavelengths = wavelengths_dofa)
            print("The rgb model initialized will be", model_test, bbone, wavelengths_dofa)
    else:
        model_object = model(data, backbone=bbone)
        print("The model initialized will be", model_test, bbone, wavelengths_dofa)
    #write model initialiation, fit etc code here
    modelAPIs_backbones(model, model_object, num_epochs, data_path, model_test, regression_parameter, data, bbone)


def fairnessTestCases(
        model,
        model_test,
        datapath,
        preparedata,
        regression_parameter,
        regression_test_score,
        model_name,
        num_epochs,
):
    pass


def update_parameter_backbones():
    is_ms = False
    parameter = []
    for key, val in data.items():
        if val["should_test"] and not val["test_feature_layer"]:
            for bbone in val["backbones"]:
                parameter.append(
                (
                    key+"_"+bbone,
                    val["model_test"],
                    val["model"],
                    val["datapath"],
                    val["prepare_data"],
                    val["regression_parameter"],
                    val["regression_test_score"],
                    val["model_name"],
                    val["regression_epochs"],
                    is_ms,
                    bbone,
                    val["wavelengths_rgb"],
                )
            )
    return parameter


def update_parameter_backbones_ms():
    is_ms = True
    parameter = []
    for key, val in data.items():
        if (
            val["should_test"]
            and not val["test_feature_layer"]
            and val["prepare_data_ms"] != False
        ):
            for bbone in val["backbones"]:
                parameter.append(
                (
                    key+"_ms"+bbone,
                    val["model_test"]+"_ms",
                    val["model"],
                    val["datapath_ms"],
                    val["prepare_data_ms"],
                    val["regression_parameter"],
                    val["regression_test_score"],
                    val["model_name"],
                    val["regression_epochs"],
                    is_ms,
                    bbone,
                    val["wavelengths_ms"],
                )
            )
    return parameter

def update_parameter_fairness():
    parameter = []
    for key, val in data.items():
        if (
            val["should_test"]
            and val["test_feature_layer"]
        ):
            parameter.append(
            (
                key,
                val["model_test"],
                val["model"],
                val["datapath"],
                val["prepare_tabular_data"],
                val["regression_parameter"],
                val["regression_test_score"],
                val["model_name"],
                val["regression_epochs"],
            )
        )
    return parameter

class TestModelSpecificFeatures(unittest.TestCase):
    @parameterized.expand(update_parameter_backbones)
    def test_backbones(
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
        bbone,
        wavelengths_dofa,
    ):
        backboneTestCases(
            model,
            model_test,
            datapath,
            preparedata,
            regression_parameter,
            regression_test_score,
            model_name,
            num_epochs,
            is_ms,
            bbone,
            wavelengths_dofa,
        )


    @parameterized.expand(update_parameter_backbones_ms)
    def test_backbones_ms(
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
            bbone,
            wavelengths_dofa,
    ):
        backboneTestCases(
            model,
            model_test,
            datapath,
            preparedata,
            regression_parameter,
            regression_test_score,
            model_name,
            num_epochs,
            is_ms,
            bbone,
            wavelengths_dofa,
        )


    @parameterized.expand(update_parameter_fairness)
    def test_fairness(
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
    ):
        fairnessTestCases(
            model,
            model_test,
            datapath,
            preparedata,
            regression_parameter,
            regression_test_score,
            model_name,
            num_epochs,
        )
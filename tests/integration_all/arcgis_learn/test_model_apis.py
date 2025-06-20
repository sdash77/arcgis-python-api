# -------------------------------------------------------------------
# Name:        Model Specific Arcgis Learn Tests.
# Purpose:     Backbones and Model Specific Features' Tests for 
#              arcgis learn to make code robust to future changes.
# -------------------------------------------------------------------


import sys
from pathlib import Path
import unittest
import os
import stat
import shutil
import warnings
warnings.filterwarnings("ignore")

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

ARCGIS_FOLDER = os.environ.get('ARCGIS_FOLDER')
if ARCGIS_FOLDER:
    custom_arcgis_path = Path(ARCGIS_FOLDER)
    if str(custom_arcgis_path) not in sys.path:
        sys.path.insert(0, str(custom_arcgis_path))
else:
    print("Warning: ARCGIS_FOLDER environment variable is not set.")

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
from parameterized import parameterized

from properties_model_apis import (
    data_folder,
    data_folder_ms,
    data_folder_tabular,
    data,
)
from fastai.vision.learner import ClassificationInterpretation
import urllib.parse
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from sklearn.model_selection import train_test_split
from arcgis.learn import prepare_tabulardata

import gc, torch

accuracy_values = {}

import arcgis
print("*"*10, arcgis.__file__, "*"*10)

def modelAPIs_backbones(model, model_object, num_epochs, data_path, model_test, regression_parameter, data, bbone):
    print("Running backbone modelAPIs for", model_test, data_path)
    lr_val = model_object.lr_find(allow_plot=False)
    model_object.fit(num_epochs, lr=lr_val, checkpoint=False)
    model_object.plot_losses()
    if bbone == "gradcam":
        model_object.show_results(gradcam = True)
    else:
        model_object.show_results()
    # save model
    d_path = os.path.join(data_folder, data_path, "models", model_test+"_"+urllib.parse.quote(bbone, safe=""))
    if bbone == "gradcam":
        model_save_path = model_object.save(f"{d_path}", gradcam = True)
    else:
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
    elif regression_parameter == "average_precision_score":
        result = model_object.average_precision_score()
        result = [
            v
            for k, v in sorted(
                result.items(), key=lambda item: item[1], reverse=True
            )
        ][0]
        print("accuracy value for ", model_test, "is: ", result)
    elif regression_parameter == "edge_detection":
        result = model_object.compute_precision_recall()["Precision"]
        print("accuracy value for ", model_test, "is: ", result)
    elif regression_parameter == "accuracy":
        result = model_object.accuracy()
        print("accuracy value for ", model_test, "is: ", result)
    print("testing model object load")
    model_object.load(str(model_save_path) + os.sep + f"{model_test}_{urllib.parse.quote(bbone, safe='')}.emd")
    if bbone == "gradcam":
        print("making gradcam prediction on image at path: ", os.path.join(data_folder, data_path, "images", "000000000001.tif"))
        predicted_class = model_object.predict(os.path.join(data_folder, data_path, "images", "000000000001.tif"), visualize=True, gradcam=True)
        print("gradcam prediction made on image ", predicted_class)
    # From model with and without data bunch.
    print("testing model object from model w/o data")
    model_object = model.from_model(
        str(model_save_path) + os.sep + f"{model_test}_{urllib.parse.quote(bbone, safe='')}.emd"
    )
    print("testing model object from model with data")
    model_object = model.from_model(
        str(model_save_path) + os.sep + f"{model_test}_{urllib.parse.quote(bbone, safe='')}.emd", data
    )
    del model_object
    gc.collect()
    torch.cuda.empty_cache()




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
    if bbone == "gradcam":      #for gradcam
        model_object = model(data)
        print("model initialized for gradcam")
    elif bbone == "dofa_base":
        if is_ms:
            if model_test == "deeplab_test_ms":
                model_object = model(data, backbone = bbone)
                print("The ms model initialized with wavelength values from emd file will be", model_test, bbone)
            else:
                model_object = model(data, backbone = bbone, wavelengths = wavelengths_dofa)
                print("The ms model initialized will be", model_test, bbone, wavelengths_dofa)
        else:
            model_object = model(data, backbone = bbone, wavelengths = wavelengths_dofa)
            print("The rgb model initialized with custom wavelength values will be", model_test, bbone, wavelengths_dofa)
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
        model_category,
):
    print("running test case for ", model_name, model_category)
    data_df = pd.read_csv(preparedata["path"])
    if model_test == 'mlmodel_test':
        print('setting training data for ml model')
        test_size = 0.25
        train, test = train_test_split(data_df, test_size = test_size)
        if(model_category == "classification"):
            X = [
                ('Age',True),
                ('Workclass',True),
                ('Education',True),
                'Education-num',
                ('Marital-status',True),
                ('Occupation',True),
                ('Relationship',True),
                ('Race',True),
                ('Gender',True),
                'Capital-gain',
                'Capital-loss',
                'Hours-per-week',
                ('Native-country',True),
            ]
            preprocessors = [('Education-num','Capital-gain', 'Capital-loss', 'Hours-per-week', MinMaxScaler())]
            data = prepare_tabulardata(train, 'Salary', explanatory_variables=X, preprocessors=preprocessors)
            print("preparing model instance for classification")
            model_instance = model(data, "lightgbm.LGBMClassifier", n_estimators=500, random_state=43)
            model_instance.fit()
            model_instance.fairness_score(sensitive_feature ='Race')
            model_instance.fairness_score(sensitive_feature ='Gender')
            print("mitigating bias for classification")
            fairness_args = {
                'sensitive_feature': 'Race',
                'mitigation_type': "threshold_optimizer",
                'mitigation_constraint':'demographic_parity',
            }
            model_instance = model(data, 'sklearn.ensemble.RandomForestClassifier', fairness_args=fairness_args, random_state=43)
            model_instance.fit()
            d_path = os.path.join(data_folder_tabular, datapath, "models", "classification", model_test)
            model_save_path = model_instance.save(f"{d_path}")
        else:
            X = [
                ('Age',True),
                ('Workclass',True),
                ('Education',True),
                'Education-num',
                ('Marital-status',True),
                ('Occupation',True),
                ('Relationship',True),
                ('Race',True),
                ('Gender',True),
                'Capital-gain',
                'Capital-loss',
                'Hours-per-week',
                ('Native-country',True),
            ]
            preprocessors =[('Education-num','Capital-gain', 'Capital-loss', 'Hours-per-week', MinMaxScaler())]
            data = prepare_tabulardata(train, 'annual_salary_$', explanatory_variables=X)
            print("preparing model instance for regression")
            model_instance = model(data, 'sklearn.ensemble.RandomForestRegressor', n_estimators=500, random_state=43)
            model_instance.fit()
            model_instance.fairness_score(sensitive_feature ='Race')
            model_instance.fairness_score(sensitive_feature ='Gender')
            print("mitigating bias for regression")
            fairness_args = {
                'sensitive_feature': 'Gender',
                'mitigation_type': 'grid_search',
                'mitigation_constraint':'ZeroOneLoss',
            }
            model_instance = model(data, 'sklearn.ensemble.RandomForestRegressor', fairness_args=fairness_args, n_estimators=500, random_state=43)
            model_instance.fit()
            d_path = os.path.join(data_folder_tabular, datapath, "models", "regression", model_test)
            model_save_path = model_instance.save(f"{d_path}")
    else:
        print('setting training data for auto ml')
        if(model_category == "classification"):
            X = ['capacity_f', 'wind_speed', 'dayl__s_', 'prcp__mm_d','srad__W_m_',('swe__kg_m_', True),'tmax__deg','tmin__deg','vp__Pa_']
            data = prepare_tabulardata(data_df, 'altitude_class', explanatory_variables=X)
            model_instance = model(data=data, eval_metric='accuracy')
            model_instance.fit()
            model_instance.fairness_score(sensitive_feature ='swe__kg_m_', fairness_metrics="demographic_parity_difference", visualize=True)
            print("mitigating bias for classification")
            model_instance = model(data, sensitive_variables= ['swe__kg_m_'], fairness_metric = 'demographic_parity_ratio')
            model_instance.fit()
            model_instance.report()
            d_path = os.path.join(data_folder_tabular, datapath, "models", "classification", model_test)
            model_save_path = model_instance.save(f"{d_path}")
        else:
            X = [('altitude_m',True), 'wind_speed', 'dayl__s_', 'prcp__mm_d','srad__W_m_',('swe__kg_m_', True),'tmax__deg','tmin__deg','vp__Pa_']
            data = prepare_tabulardata(data_df, 'capacity_f', explanatory_variables=X)
            model_instance = model(data)
            model_instance.fit()
            model_instance.fairness_score(sensitive_feature ='altitude_m', fairness_metrics="RMSE", visualize=True)
            print("mitigating bias for regression")
            model_instance = model(data, sensitive_variables= ['altitude_m'], fairness_metric = 'group_loss_ratio')
            model_instance.fit()
            model_instance.report()
            d_path = os.path.join(data_folder_tabular, datapath, "models", "regression", model_test)
            model_save_path = model_instance.save(f"{d_path}")
    print("common APIs for fairness models: regression and classification begin here")
    data.show_batch()
    print("show results start")
    model_instance.show_results()
    print("show results end")
    result = model_instance.score()
    print("result is ", result)
    if(model_test == 'mlmodel_test'):
        model_instance.load(str(model_save_path) + os.sep + f"{model_test}.emd")
        model_instance = model.from_model(str(model_save_path) + os.sep + f"{model_test}.emd", data)
        model_instance = model.from_model(str(model_save_path) + os.sep + f"{model_test}.emd")
    elif(model_test == 'automl_test'):
        model_instance = model.from_model(str(model_save_path))
    #from_model for automl doesn't work currently due to known issue of saving multiple randomly named .emd files. It also fails or MLmodel without data.
    del model_instance
    gc.collect()
    torch.cuda.empty_cache()


def update_parameter_backbones():
    is_ms = False
    parameter = []
    for key, val in data.items():
        if val["should_test"] and not val["test_feature_layer"]:
            #To add test case for Gradcam
            if key == "fc_singleLabel":
                parameter.append(
                    (
                        key+"_gradcam",
                        val["model_test"],
                        val["model"],
                        val["datapath"],
                        val["prepare_data"],
                        val["regression_parameter"],
                        val["regression_test_score"],
                        val["model_name"],
                        val["regression_epochs"],
                        is_ms,
                        "gradcam", #here, we usually put backbone name, but using gradcam here for gradcam test case. gradcam is NOT a backbone
                        False,
                    )
                )
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
            for model_category in val["model_categories"]:
                parameter.append(
            (
                key+'_'+model_category,
                val["model_test"],
                val["model"],
                val["datapath"],
                val["prepare_tabular_data"],
                val["regression_parameter"],
                val["regression_test_score"],
                val["model_name"],
                val["regression_epochs"],
                model_category,
            )
        )
    return parameter

class TestModelSpecificFeatures(unittest.TestCase):
    @parameterized.expand(update_parameter_backbones, skip_on_empty=True)
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


    @parameterized.expand(update_parameter_backbones_ms, skip_on_empty=True)
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


    @parameterized.expand(update_parameter_fairness, skip_on_empty=True)
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
            model_category,
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
            model_category,
        )


if __name__ == "__main__":
    unittest.main()
 
# -------------------------------------------------------------------
# Name:        Common Arcgis Learn Tests.
# Purpose:     Common Tests for arcgis learn to factor same code out.
# -------------------------------------------------------------------


import os, sys
import glob
import warnings
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

warnings.filterwarnings('ignore')
import sys
import subprocess

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2] / "src"
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


test_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(test_dir))


logging.info("Using arcgis from:")
import arcgis
logging.info("Using arcgis from:", arcgis.__file__)

from properties import (
    data,
    data_folder,
    setuposenviron,
    data_folder_ms,
    data_inference_only,
)





# from utils._common import *
# try:
#     print("Smoke tests are running...")
#     TESTFOLDERPATH = os.environ.get('TESTFOLDERPATH')
#     smoke_test_paths = glob.glob(
#             os.path.join(TESTFOLDERPATH, "smoke", "**", "*.py"), recursive=True
#         )
#     smoke_test_xml_output = os.path.join(TESTFOLDERPATH, "_output", "smoke_test.xml")
#     run_unittest_on(
#         smoke_test_paths, smoke_test_xml_output, max_fail=0, throw_exc_on_fail=True
#     )
#     print("Smoke tests Ends...")

#     import arcgis
#     print("Working arcgis file:", arcgis.__file__)
# except Exception as E:
#     raise Exception(str(E))


os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import unittest
import traceback
from parameterized import parameterized
from fastai.vision.learner import ClassificationInterpretation
import random
import string
import gc
from sys import platform
import pandas as pd

# import arcgis
from arcgis.learn import classify_pixels, detect_objects, classify_objects
from arcgis.learn import prepare_data, prepare_tabulardata, prepare_textdata
from arcgis.learn import AutoDL, ImageryModel


import_exception = None

try:
    import torch

    HAS_DEPS = True
    print(" ================= Modules Imported ==============")
except Exception as e:
    import_exception = "\n".join(
        traceback.format_exception(type(e), e, e.__traceback__)
    )
    HAS_DEPS = False


module_skip = False
parameter = []
parameter_fl = []
parameter_df = []
# parameter_autodl = []
parameter_text = []
parameter_autodl = []
authorization_data = {}
check_ms = False
current_path = ""
success_flag = False
if not HAS_DEPS:
    print("**Environment fails**")
    module_skip = True
    raise Exception(
        f"""{import_exception} \n\nThis module requires fastai, PyTorch, torchvision and scikit-image as its dependencies."""
    )

else:
    from arcgis.gis import GIS
    from arcgis.features import FeatureLayerCollection
    from datetime import datetime

accuracy_values = {
    "attributes": {
        "Date": "",
        "ssd": 0,
        "retinanet": 0,
        "unet": 0,
        "pspnet": 0,
        "maskrcnn": 0,
        "featureclassifier": 0,
        "fasterrcnn": 0,
        "superres": 0,
        "ner": 0,
        "deeplab": 0,
        "pointcnn": 0,
        "yolov3": 0,
        "fullyconnected": 0,
        "pix2pix": 0,
        "cyclegan": 0,
        "hededgedetector": 0,
        "bdcnedgedetector": 0,
        "imagecaptioner": 0,
        "siammask": 0,
        "changedetection": 0,
        "mtre": 0,
        "sequencetosequence": 0,
        "textclassifier": 0,
        "timeseriesmodel": 0,
        "zeroshotclassifier": 0,
        "questionanswering": 0,
        "textsummarizer": 0,
        "texttranslator": 0,
        "textgenerator": 0,
        "fillmask": 0,
        "deepsort": 0,
        "mmsegmentation": 0,
        "mmdetection": 0,
        "mlmodel": 0,
        "automl": 0,
        "maxdeeplab": 0,
        "detreg": 0,
        "samlora": 0,
        "mm3d": 0,
        "sqnseg": 0,
        "randlanet": 0,
        "psetae": 0,
        "wnet_cgan": 0,
        "pix2pixhd": 0,
        "ptv3seg": 0,
        "ptv3det": 0,
        "mmdetection_dino": 0,
        "rtdetrv2": 0,
        "climax": 0,
    }
}

success_stat = {
    "attributes": {
        "Date": "",
        "total": 0,
        "pass": 0,
        "fail": 0,
        "od_total": 7,
        "od": 0,
        "pc_total": 11,
        "pc": 0,
        "co_total": 1,
        "co": 0,
        "text_total": 9,
        "text": 0,
        "others_total": 15,
        "others": 0,
    }
}

failure_models = []
failure_score = []


@unittest.skipIf(module_skip, "Precondition check failed. Skipping Common tests")
def setUpModule():
    global authorization_data
    authorization_data = setuposenviron()
    if os.environ.get("run_nightly") == "1":
        accuracy_values["attributes"]["Date"] = convertdate(datetime.today())
    print("Setup completed successfully")


def updateAccuracyResults():
    gis = GIS(
        "https://deldev.maps.arcgis.com",
        authorization_data["for_update_accuracy_results"]["username"],
        authorization_data["for_update_accuracy_results"]["password"],
    )
    item = gis.content.get("f2d12f9c5d1c4b168c6e40f0056400e5")
    data = item.tables[0]
    global accuracy_values
    data.edit_features(adds=[accuracy_values])


def updateModelStats():
    gis = GIS(
        "https://deldev.maps.arcgis.com",
        authorization_data["for_update_accuracy_results"]["username"],
        authorization_data["for_update_accuracy_results"]["password"],
    )
    item = gis.content.get("a8c6eb0abe534cd9ac69d9839e2f642d")
    data = item.tables[0]
    global success_stat
    ind = list(data.query().sdf["ObjectId"])
    data.edit_features(deletes=ind[:])
    data.edit_features(adds=[success_stat])


def updateFailureModels():
    gis = GIS(
        "https://deldev.maps.arcgis.com",
        authorization_data["for_update_accuracy_results"]["username"],
        authorization_data["for_update_accuracy_results"]["password"],
    )
    item = gis.content.get("cd08c8edfb2f401bb0df1aafa6ce36af")
    data = item.tables[0]
    sdf = pd.DataFrame.spatial.from_layer(data)
    global failure_models, failure_score
    failed_models = list(sdf["ModelName"])

    try:
        ind = list(data.query().sdf["ObjectId"])
        data.edit_features(deletes=ind[:])
    except KeyError:
        pass
    if len(failure_models) > 0:
        for model, accuracy in zip(failure_models, failure_score):
            if model in failed_models:
                failing_since = sdf.loc[sdf["ModelName"] == model]["FailingSince"][0]
            else:
                failing_since = convertdate(datetime.today())
            failed_model_data = {
                "attributes": {
                    "ModelName": model,
                    "Accuracy": accuracy,
                    "FailingSince": failing_since,
                }
            }
            data.edit_features(adds=[failed_model_data])
    else:
        data.edit_features(
            adds=[
                {
                    "attributes": {
                        "ModelName": "No Failure Case",
                        "Accuracy": 0,
                        "FailingSince": convertdate(datetime.today()),
                    }
                }
            ]
        )


def CommonTestUsingDF(
    query,
    model_type,
    prepare_tabular_data,
    regression_parameter,
    regression_test_score,
    model_name,
    data_path,
    model_test,
    data_folder_path,
    self_obj,
):
    from sklearn.preprocessing import MinMaxScaler
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score
    import sklearn.metrics as metrics

    data_df = pd.read_csv(prepare_tabular_data["path"])
    test_size = 0.10
    sdf_train_base, sdf_test_base = train_test_split(
        data_df, test_size=test_size, random_state=42
    )
    result = 0.0

    X = [
        ("Age", True),
        ("Workclass", True),
        ("Education", True),
        "Education_num",
        ("Marital_status", True),
        ("Occupation", True),
        ("Relationship", True),
        ("Race", True),
        ("Gender", True),
        "Capital_gain",
        "Capital_loss",
        "Hours_per_week",
        ("Native_country", True),
    ]

    preprocessors = [
        (
            "Hours_per_week",
            "Capital_gain",
            "Capital_loss",
            "Age",
            "Workclass",
            "Education",
            "Marital_status",
            "Occupation",
            "Relationship",
            "Race",
            "Gender",
            "Native_country",
            "Education_num",
            MinMaxScaler(),
        )
    ]

    data_base_model = prepare_tabulardata(
        sdf_train_base,
        variable_predict="Salary",
        explanatory_variables=X,
        preprocessors=preprocessors,
    )

    if model_name == "mlmodel":
        model_object = model_type(
            data_base_model,
            "sklearn.tree.DecisionTreeClassifier",
            random_state=43,
        )
    else:
        model_object = model_type(data_base_model)

    model_object.fit()
    model_object.save(f"{os.path.join(data_folder_path, data_path, model_test)}")
    # Load from saved model.

    if os.environ.get("run_nightly") == "1":
        print("Testing for accuracy with default backbone")
        global accuracy_values
        if regression_parameter == "automl_score":
            result = model_object.score()
        else:
            result = 0.0

        accuracy_values["attributes"][model_name] = result
        # self_obj.assertGreater(
        #     result, regression_test_score, "Model accuracy is lower than the threshold value. Please check."
        # )
        global failure_score, failure_models
        if result < regression_test_score:
            failure_models.append(model_name)
            failure_score.append(result)

    if model_name == "mlmodel":
        model_object.load(f"{os.path.join(data_folder_path, data_path, model_test)}")

    # From model with and without data bunch.
    model_object = model_type.from_model(
        os.path.join(data_folder_path, data_path, f"{model_test}/{model_test}.emd")
    )

def CommonTestUsingFL(
    query,
    model_type,
    prepare_tabular_data,
    regression_parameter,
    regression_test_score,
    inferencing_parameter,
    model_name,
    data_path,
    model_test,
    current_path,
):
    global success_flag
    success_flag = False
    gis = GIS(
        url="https://geosaurus.maps.arcgis.com",
        username=authorization_data["for_common_test_using_fl"]["username"],
        password=authorization_data["for_common_test_using_fl"]["password"],
    )
    calgary_no_southland_solar = gis.content.search(**query)[0]
    feature_layer = calgary_no_southland_solar.layers[0]

    if "preprocessors" in prepare_tabular_data.keys():
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.compose import make_column_transformer

        numerical_transformer = make_pipeline(MinMaxScaler())
        preprocessors = make_column_transformer(
            (numerical_transformer, prepare_tabular_data["explanatory_variables"])
        )

        data = prepare_tabulardata(
            feature_layer,
            "capacity_f",
            explanatory_variables=prepare_tabular_data["explanatory_variables"],
            preprocessors=preprocessors,
        )
        # Check model with default backbone
        model_object = model_type(
            data,
            "sklearn.ensemble.GradientBoostingRegressor",
            n_estimators=100,
            random_state=43,
        )
        # Fit the model.
        model_object.fit()

    else:
        data = prepare_tabulardata(feature_layer, "capacity_f", **prepare_tabular_data)

        # Check model with default backbone
        model_object = model_type(data)

        # Fit for 1 epochs without LR.
        model_object.fit(1, checkpoint=False)
        # Fit for 1 epochs with LR.
        model_object.fit(1, lr=0.001, checkpoint=False)

        # save model
        model_object.save(f"{os.path.join(current_path, data_path, model_test)}")
        # Load from saved model.
        model_object.load(f"{os.path.join(current_path, data_path, model_test)}")

        # From model with and without data bunch.
        model_object = model_type.from_model(
            os.path.join(current_path, data_path, f"{model_test}/{model_test}.emd")
        )
        model_object = model_type.from_model(
            os.path.join(current_path, data_path, f"{model_test}/{model_test}.emd"),
            data,
        )

    if os.environ.get("run_nightly") == "1":
        print("Testing for accuracy with default backbone")
        global accuracy_values
        if regression_parameter == "score":
            result = model_object.score()
        else:
            result = 0.0

        accuracy_values["attributes"][model_name] = result

    if os.environ.get("run_inference") == "1":
        model_object.predict(feature_layer, output_layer_name="prediction_layer_rf")

    success_flag = True


def convertdate(dates):
    day = dates.day
    month = dates.month
    year = dates.year
    dstr = str(str(month) + "/" + str(day) + "/" + str(year))
    return dstr


def commonTestCases(
    model_type,
    model_test,
    data_path,
    preparedata,
    regression_parameter,
    regression_test_score,
    inferencing_parameter,
    model_name,
    inferencing_image_server,
    ms_flag,
    current_path,
    num_epochs,
    self_obj,
):
    global success_flag
    success_flag = False
    from arcgis.learn import prepare_data

    if model_test == "sequencetosequence_test" or model_test == "textclassifier_test":
        data = prepare_textdata(**preparedata)
    elif model_test == "timeseriesmodel_test":
        from arcgis.learn import prepare_tabulardata
        import pandas as pd
        from sklearn.model_selection import train_test_split

        cali_rainfall_df1 = pd.read_csv(preparedata["path"])
        cali_rainfall_df1_sorted = cali_rainfall_df1.sort_values(by="date")
        test_size = 12
        train, test = train_test_split(
            cali_rainfall_df1_sorted, test_size=test_size, shuffle=False
        )
        data = prepare_tabulardata(
            train, variable_predict="prcp_mm_", index_field="date", seed=42
        )
    else:
        data = prepare_data(**preparedata)
    # data.show_batch()
    # Check model with all default backbone
    if model_test == "timeseriesmodel_test":
        model_object = model_type(data, seq_len=12)
    elif model_test == "mmsegmentation_test" or model_test == "mmdetection_test":
        all_models = model_type.supported_models
        model_object = model_type(data, model=all_models[0])
    elif model_test == "mmdetection_dino_test":
        all_models = model_type.supported_models
        model_object = model_type(data, model="dino")
    elif model_test == "psetae_test":
        model_object = model_type(data, gamma=2, dropout=0.2)
    else:
        model_object = model_type(data)

    # model_object.show_results()
    lr_val = model_object.lr_find(allow_plot=False)

    # Fit for 1 epochs without LR.
    model_object.fit(1, lr=lr_val, checkpoint=False)
    # # Fit for 1 epochs with LR.

    # Test shap feature for textclassifier
    if model_test == "textclassifier_test":
        # testing for single text
        model_object.predict("Thanks for the support", explain=True)
        # testing for list of texts with and without explain_index argument
        txt_list = ["awwww, I never noticed this", "Thanks for the support"]
        model_object.predict(txt_list, explain=True)
        model_object.predict(txt_list, explain=True, explain_index=[1])

    # save model
    d_path = os.path.join(data_folder, data_path, "models", model_test)
    if model_test == "timeseriesmodel_test":
        pass
    else:
        model_save_path = model_object.save(f"{d_path}")

    # Check model with all supported backbones
    if os.environ.get("run_backbones") == "1":
        print("Testing for all backbones")
        supported_backbones = model_object.supported_backbones
        for backbone in supported_backbones:
            model_object = model_type(data, backbone=str(backbone))
            model_object.fit(1, lr=lr_val, checkpoint=False)
            model_object.save(model_test + "_" + str(backbone))
            gc.collect()
            torch.cuda.empty_cache()

    if os.environ.get("run_nightly") == "1":
        if not ms_flag:
            print("Testing for accuracy with default backbone")
            global accuracy_values
            model_object.fit(num_epochs, lr=lr_val, checkpoint=False)
            if regression_parameter == "average_precision_score":
                result = model_object.average_precision_score()
                result = [
                    v
                    for k, v in sorted(
                        result.items(), key=lambda item: item[1], reverse=True
                    )
                ][0]
            elif regression_parameter == "accuracy":
                result = model_object.accuracy()
            elif regression_parameter == "confusion_matrix":
                array = ClassificationInterpretation.from_learner(
                    model_object.learn
                ).confusion_matrix()
                true_prediction = array.diagonal().sum()
                all_prediction = array.sum()
                result = true_prediction / all_prediction
            elif regression_parameter == "precision_score":
                result = model_object.precision_score()
            elif regression_parameter == "compute_precision_recall":
                result = (
                    model_object.compute_precision_recall().loc["precision", :].max()
                )
            elif regression_parameter == "psnr_metric":
                result = float(model_object.compute_metrics()["SSIM"])
            elif regression_parameter == "f1_score":
                result = model_object.f1_score()
            elif regression_parameter == "panoptic_quality":
                result = model_object.panoptic_quality()
            elif regression_parameter == "compute_metrics":
                if model_test == "siammask_test":
                    result = float(model_object.compute_metrics()["mean_IOU"])
                elif model_test == "cyclegan_test":
                    result = float(model_object.compute_metrics()["FID_A"])
                elif model_test == "climax_test":
                    result = float(model_object.compute_metrics()["SSIM_msl"])
                else:
                    result = float(model_object.compute_metrics()["SSIM"])
            elif regression_parameter == "bleu_score":
                result = float(model_object.bleu_score()["bleu-1"])
            elif regression_parameter == "get_model_metrics":
                result = model_object.get_model_metrics()["seq2seq_acc"]
            elif regression_parameter == "mIOU":
                if model_name == "psetae":
                    result = float(model_object.mIOU()["mIOU"])
                else:
                    result = model_object.mIOU()["0"]
            elif regression_parameter == "edge_detection":
                result = model_object.compute_precision_recall()["Precision"]
            elif regression_parameter == "precision_recall_score":
                result = model_object.precision_recall_score()["Change"]["precision"]
            elif regression_parameter == "per_class_metrics":
                result = model_object.per_class_metrics().iloc[0, 0]
            elif regression_parameter == "r2_score":
                sdf_forecasted = model_object.predict(
                    train, prediction_type="dataframe", number_of_predictions=test_size
                )
                sdf_forecasted = sdf_forecasted.tail(test_size)
                sdf_forecasted = sdf_forecasted[["date", "prcp_mm__results"]]
                sdf_forecasted["actual"] = test[test.columns[-1]].values
                sdf_forecasted = sdf_forecasted.set_index(sdf_forecasted.columns[0])
                from sklearn.metrics import r2_score
                import sklearn.metrics as metrics

                result = r2_score(
                    sdf_forecasted["actual"], sdf_forecasted["prcp_mm__results"]
                )
                success_flag = True
            else:
                result = 0.0

            accuracy_values["attributes"][model_name] = result

            # self_obj.assertGreater(
            #     result,regression_test_score, "Model accuracy is lower than the threshold value. Please check."
            # )
            global failure_score, failure_models
            if result < regression_test_score:
                failure_models.append(model_name)
                failure_score.append(result)

    ## Inferencing function here.
    if os.environ.get("run_inference") == "1" and ms_flag == False:
        from arcpy.ia import (
            DetectObjectsUsingDeepLearning,
            ClassifyPixelsUsingDeepLearning,
            ClassifyObjectsUsingDeepLearning,
        )

        # Inferencing from image server
        from arcgis.gis import GIS
        from arcgis.learn import Model, detect_objects

        gis = GIS(
            "https://ndhlnagsb01.esri.com/portal",
            authorization_data["for_inferencing"]["username"],
            authorization_data["for_inferencing"]["password"],
            verify_cert=False,
        )

        letters = string.ascii_lowercase
        output_name = "".join(random.choice(letters) for i in range(9))

        if inferencing_parameter["model_type"] == "DetectObjectsUsingDeepLearning":
            model_path = os.path.join(
                current_path, data_path, f"models/{model_test}/{model_test}.dlpk"
            )

            model_package = gis.content.add(
                item_properties={
                    "type": "Deep Learning Package",
                    "typeKeywords": "Deep Learning",
                    "title": model_test,
                    "tags": "deeplearning, Detect object using deep learning",
                    "overwrite": "True",
                },
                data=model_path,
                folder="model_inference",
            )

            detect_objecmodel_object = Model(model_package)
            detect_objecmodel_object.install()
            input_raster = gis.content.get(inferencing_image_server["input_raster"])

            detect_objects(
                input_raster.url,
                model=detect_objecmodel_object,
                model_arguments=inferencing_image_server["model_arguments"],
                output_name="test_model_" + output_name,
                folder="model_inference",
                context=inferencing_image_server["context"],
                gis=gis,
            )

            if "win" in platform:
                DetectObjectsUsingDeepLearning(
                    inferencing_parameter["sample_input"],
                    os.path.join(inferencing_parameter["path"], output_name + ".shp"),
                    inferencing_parameter["model"],
                    inferencing_parameter["parameters"],
                )

        elif inferencing_parameter["model_type"] == "ClassifyPixelsUsingDeepLearning":
            model_path = os.path.join(
                current_path, data_path, f"models/{model_test}/{model_test}.dlpk"
            )

            model_package = gis.content.add(
                item_properties={
                    "type": "Deep Learning Package",
                    "typeKeywords": "Deep Learning",
                    "title": model_test,
                    "tags": "deeplearning, classify pxel using deeplearning",
                    "overwrite": "True",
                },
                data=model_path,
                folder="model_inference",
            )

            classify_pixel_model = Model(model_package)
            classify_pixel_model.install()
            input_raster = gis.content.get(inferencing_image_server["input_raster"])

            classify_pixels(
                input_raster=input_raster.url,
                model=classify_pixel_model,
                output_name="test_model_" + output_name,
                context=inferencing_image_server["context"],
                model_arguments=inferencing_image_server["model_args"],
                folder="model_inference",
                gis=gis,
            )

            if "win" in platform:
                ClassifyPixelsUsingDeepLearning(
                    inferencing_parameter["sample_input"],
                    inferencing_parameter["model"],
                    inferencing_parameter["parameters"],
                    "PROCESS_AS_MOSAICKED_IMAGE",
                )

        elif inferencing_parameter["model_type"] == "ClassifyObjectsUsingDeepLearning":
            model_path = os.path.join(
                current_path, data_path, f"models/{model_test}/{model_test}.dlpk"
            )

            model_package = gis.content.add(
                item_properties={
                    "type": "Deep Learning Package",
                    "typeKeywords": "Deep Learning",
                    "title": model_test,
                    "tags": "deeplearning, Classify object using deep learning",
                    "overwrite": "True",
                },
                data=model_path,
                folder="model_inference",
            )

            classify_pixel_model = Model(model_package)
            classify_pixel_model.install()
            input_raster = gis.content.get(inferencing_image_server["input_raster"])
            input_feature = gis.content.get(inferencing_image_server["input_features"])
            classify_objects(
                input_raster=input_raster.url,
                model=model_package,
                input_features=input_feature,
                class_value_field="status",
                model_arguments=inferencing_image_server["model_args"],
                output_name="test_model_" + output_name,
                context=inferencing_image_server["context"],
                folder="model_inference",
                gis=gis,
            )

            if "win" in platform:
                ClassifyObjectsUsingDeepLearning(
                    inferencing_parameter["sample_input"],
                    inferencing_parameter["path"],
                    inferencing_parameter["model"],
                    in_features=inferencing_parameter["feature_layer"],
                    class_label_field="ClassLabel",
                    processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
                    model_arguments="batch_size 4",
                )
        elif inferencing_parameter["model_type"] == "extract_entities":
            model_object.extract_entities(inferencing_parameter["sample_input"])
        elif inferencing_parameter["model_type"] == "predict_las":
            model_object.predict_las(
                path=inferencing_parameter["sample_input"],
                output_path=inferencing_parameter["sample_output"],
                print_metrics=False,
            )
        else:
            pass

    if model_test == "timeseriesmodel_test":
        success_flag = True
        return

    # Load from saved model.
    model_object.load(str(model_save_path) + os.sep + f"{model_test}.emd")

    # From model with and without data bunch.
    model_object = model_type.from_model(
        str(model_save_path) + os.sep + f"{model_test}.emd"
    )
    model_object = model_type.from_model(
        str(model_save_path) + os.sep + f"{model_test}.emd", data
    )
    del model_object
    gc.collect()
    torch.cuda.empty_cache()

    success_flag = True


def CommonTestTextModels(model_name, model, data, labels):
    global accuracy_values
    global success_flag
    success_flag = False
    result = 0
    if model_name == "zeroshotclassifier":
        model = model()
        # single label classification
        predictions = model.predict(data[0], labels[0])
        # Multi-Label classification
        predictions = model.predict(data, labels)
        result = predictions[0]["scores"][0]
        # Multi-Lingual Data
        predictions = model.predict(data[-1], labels[-1])

    elif model_name == "questionanswering":
        model = model()
        predictions = model.get_answer(labels, context=data)
        result = predictions[0]["score"]
    elif model_name == "textsummarizer":
        model = model()
        predictions = model.summarize(data, max_length=100)
    elif model_name == "texttranslator":
        model = model(source_language="en", target_language="fr")
        predictions = model.translate([data[1]])
    elif model_name == "textgenerator":
        model = model()
        predictions = model.generate_text(data, num_return_sequences=2, max_length=25)
    elif model_name == "fillmask":
        model = model()
        predictions = model.predict_token(data, num_suggestions=2)
        result = predictions[0][0]["score"]
    else:
        result = 0

    accuracy_values["attributes"][model_name] = result

    success_flag = True


def update_parameter():
    parameter = []
    check_ms = False
    for key, val in data.items():
        if val["should_test"] and not val["test_feature_layer"]:
            parameter.append(
                [
                    key,
                    val["model_test"],
                    val["model"],
                    val["datapath"],
                    val["prepare_data"],
                    val["regression_parameter"],
                    val["regression_test_score"],
                    val["inferencing_parameter"],
                    val["model_name"],
                    val["inferencing_image_server"],
                    check_ms,
                    data_folder,
                    val["regression_epochs"],
                ]
            )
    return parameter


def update_parameter_ms():
    check_ms = True
    parameter = []
    for key, val in data.items():
        if (
            val["should_test"]
            and not val["test_feature_layer"]
            and val["prepare_data_ms"] != False
        ):
            parameter.append(
                [
                    key + "_ms",
                    val["model_test"] + "_ms",
                    val["model"],
                    val["datapath_ms"],
                    val["prepare_data_ms"],
                    val["regression_parameter"],
                    val["regression_test_score"],
                    val["inferencing_parameter"],
                    val["model_name"],
                    val["inferencing_image_server"],
                    check_ms,
                    data_folder_ms,
                    val["regression_epochs"],
                ]
            )
    return parameter


def update_parameter_fl():
    parameter_fl = []
    for key, val in data.items():
        if (
            val["should_test"]
            and val["test_feature_layer"]
            and not val["model_name"] in ["automl", "mlmodel"]
        ):
            parameter_fl.append(
                [
                    key,
                    val["gis_content_search"],
                    val["model"],
                    val["prepare_tabular_data"],
                    val["regression_parameter"],
                    val["regression_test_score"],
                    val["inferencing_parameter"],
                    val["model_name"],
                    val["datapath"],
                    val["model_test"],
                    data_folder,
                ]
            )
    return parameter_fl


def update_parameter_df():
    parameter_df = []
    for key, val in data.items():
        if val["should_test"] and val["model_name"] in ["automl", "mlmodel"]:
            parameter_df.append(
                [
                    key,
                    val["model"],
                    val["prepare_tabular_data"],
                    val["regression_parameter"],
                    val["regression_test_score"],
                    val["model_name"],
                    val["datapath"],
                    val["model_test"],
                    data_folder,
                ]
            )
    return parameter_df


# def efficientnet_main():
#     from integration.arcgis_learn.properties import *


def text_models():
    parameter_text = []
    for key, val in data_inference_only.items():
        parameter_text.append(
            [key, val["model_name"], val["model"], val["data"], val["labels"]]
        )
    return parameter_text


def autodl_main():
    autodl_data = [
        os.path.join(data_folder, "autodl_data", "classified_tiles"),
        os.path.join(data_folder, "autodl_data", "palm_trees"),
    ]
    autodl_pretrained_model = [
        os.path.join(
            data_folder,
            "autodl_data",
            "unet_model",
            "AutoDL_UnetClassifier_resnet34.emd",
        ),
        os.path.join(
            data_folder,
            "autodl_data",
            "ssd_model",
            "AutoDL_SingleShotDetector_resnet34.emd",
        ),
    ]
    autodl_model = ["DeepLab", "SingleShotDetector"]
    for ind in range(0, 2):
        path = autodl_data[ind]
        data = prepare_data(path, batch_size=None)
        dl = AutoDL(
            data,
            total_time_limit=0.25,
            verbose=True,
            network=[autodl_model[ind]],
            mode="basic",
        )
        dl.fit()
        dl.score()
        dl.supported_classification_models()
        dl.supported_detection_models()
        dl.average_precision_score()
        dl.lr_find()
        dl.BestPerformingModel
        dl.mIOU()
        del dl
        gc.collect()
        torch.cuda.empty_cache()
        im = ImageryModel()
        im.load(autodl_pretrained_model[ind], data)
        im.fit(3)
        im.save("test_dl")
        del im
        gc.collect()
        torch.cuda.empty_cache()


class TestTraining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Inside Setup Class!!!")
        # try:
        #     test_folder = Path(os.environ.get("TESTFOLDERPATH", "."))
        #     smoke_tests = list(test_folder.glob("smoke/**/*.py"))
        #     output_file = test_folder / "_output" / "smoke_test.xml"

        #     print("Smoke tests are running...")

        #     cmd = [
        #         sys.executable,
        #         "-m", "pytest", "-v",
        #         *[str(p) for p in smoke_tests],
        #         f"--junitxml={output_file}"
        #     ]
        #     subprocess.run(cmd, check=True)

        #     print("Smoke tests finished successfully.")
        #     import arcgis
        #     print("Working arcgis file:", arcgis.__file__)

        # except subprocess.CalledProcessError as e:
        #     raise RuntimeError(
        #         f"Smoke tests failed with exit code {e.returncode}"
        #     ) from e


    def setUp(self):
        print("Test: " + self._testMethodName)

    def tearDown(self):
        global success_flag
        global success_stat
        success_stat["attributes"]["total"] = success_stat["attributes"]["total"] + 1
        test_name = self._testMethodName.split("_")[-1]

        if success_flag:
            success_stat["attributes"]["pass"] = success_stat["attributes"]["pass"] + 1
            if test_name == "ms":
                pass
            elif test_name in [
                "ssd",
                "rn",
                "fasterrcnn",
                "yolov3",
                "maskrcnn",
                "detreg",
                "rtdetrv2",
            ]:
                success_stat["attributes"]["od"] = success_stat["attributes"]["od"] + 1
            elif test_name in [
                "unet",
                "deeplab",
                "pspnet",
                "superres",
                "pix2pix",
                "pointcnn",
                "hededgedetector",
                "bdcnedgedetector",
                "changedetection",
                "mtre",
                "maxdeeplab",
            ]:
                success_stat["attributes"]["pc"] = success_stat["attributes"]["pc"] + 1
            elif test_name in ["fc"]:
                success_stat["attributes"]["co"] = success_stat["attributes"]["co"] + 1
            elif test_name in [
                "ner",
                "sequencetosequence",
                "textclassifier",
                "zeroshotclassifier",
                "questionanswering",
                "textsummarizer",
                "texttranslator",
                "textgenerator",
                "fillmask",
            ]:
                success_stat["attributes"]["text"] = (
                    success_stat["attributes"]["text"] + 1
                )
            elif test_name in [
                "fcn",
                "ml",
                "imagecaptioner",
                "siammask",
                "timeseriesmodel",
                "deepsort",
                "mmsegmentation",
                "mmdetection",
                "mmdetection_dino",
                "automl",
                "mlmodel",
            ]:
                success_stat["attributes"]["others"] = (
                    success_stat["attributes"]["others"] + 1
                )
            print("Method is successful")
            print(self._testMethodName)
        else:
            success_stat["attributes"]["fail"] = success_stat["attributes"]["fail"] + 1
            print("Method is a failure")
            print(self._testMethodName)
        gc.collect()
        torch.cuda.empty_cache()
        for key, val in data.items():
            os.system(
                f'rm -rf "{os.path.join(data_folder, val["datapath"], "models")}"'
            )
            if "datapath_ms" in val.keys():
                os.system(
                    f'rm -rf "{os.path.join(data_folder_ms, val["datapath_ms"], "models")}"'
                )
        print("Test:" + self._testMethodName + "is completed.\n")
        print("------------------------------------------------------------------\n")

    def test_smoke(skip_on_empty=True):
        test_folder = Path(os.environ.get("TESTFOLDERPATH", "."))
        smoke_tests = list(test_folder.glob("smoke/**/*.py"))
        output_file = test_folder / "_output" / "smoke_test.xml"

        print("Smoke tests are running...")

        cmd = [
            sys.executable,
            "-m", "pytest", "-v",
            *[str(p) for p in smoke_tests],
            f"--junitxml={output_file}"
        ]
        subprocess.run(cmd, check=True)

        print("Smoke tests finished successfully.")

    
    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter, skip_on_empty=True)
    def test(
        self,
        name,
        model_test,
        model,
        datapath,
        preparedata,
        regression_parameter,
        regression_test_score,
        inferencing_parameter,
        model_name,
        inferencing_image_server,
        ms_flag,
        data_folder_path,
        num_epochs,
    ):
        commonTestCases(
            model,
            model_test,
            datapath,
            preparedata,
            regression_parameter,
            regression_test_score,
            inferencing_parameter,
            model_name,
            inferencing_image_server,
            ms_flag,
            data_folder_path,
            num_epochs,
            self,
        )

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter_ms, skip_on_empty=True)
    def test_ms(
        self,
        name,
        model_test,
        model,
        datapath,
        preparedata,
        regression_parameter,
        regression_test_score,
        inferencing_parameter,
        model_name,
        inferencing_image_server,
        ms_flag,
        data_folder_path,
        num_epochs,
    ):
        if os.environ.get("run_nightly") != "1":
            commonTestCases(
                model,
                model_test,
                datapath,
                preparedata,
                regression_parameter,
                regression_test_score,
                inferencing_parameter,
                model_name,
                inferencing_image_server,
                ms_flag,
                data_folder_path,
                num_epochs,
                self,
            )
        else:
            print("ignoring nightly training for ms data")
            pass

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter_fl, skip_on_empty=True)
    def test_fl(
        self,
        name,
        query,
        model_type,
        prepare_tabular_data,
        regression_parameter,
        regression_test_score,
        inferencing_parameter,
        model_name,
        data_path,
        model_test,
        data_folder_path,
    ):
        CommonTestUsingFL(
            query,
            model_type,
            prepare_tabular_data,
            regression_parameter,
            regression_test_score,
            inferencing_parameter,
            model_name,
            data_path,
            model_test,
            data_folder_path,
        )

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(text_models, skip_on_empty=True)
    def test_text_models(self, key, model_name, model, data, labels):
        CommonTestTextModels(model_name, model, data, labels)

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter_df, skip_on_empty=True)
    def test_automl(
        self,
        query,
        model_type,
        prepare_tabular_data,
        regression_parameter,
        regression_test_score,
        model_name,
        data_path,
        model_test,
        data_folder_path,
    ):
        CommonTestUsingDF(
            query,
            model_type,
            prepare_tabular_data,
            regression_parameter,
            regression_test_score,
            model_name,
            data_path,
            model_test,
            data_folder_path,
            self,
        )

    def test_autodl(self):
        if os.environ.get("run_nightly") != "1":
            autodl_main()
        else:
            pass

    @classmethod
    def tearDownClass(cls):
        gc.collect()
        torch.cuda.empty_cache()
        for key, val in data.items():
            try:
                os.system(
                    f'rm -rf "{os.path.join(data_folder, val["datapath"], "models")}"'
                )
                if "datapath_ms" in val.keys():
                    os.system(
                        f'rm -rf "{os.path.join(data_folder_ms, val["datapath_ms"], "models")}"'
                    )
            except:
                continue
        print("\n All Tests have completed.")
        print("==================================================================")


## Remove all model directories
def tearDownModule():
    gc.collect()
    torch.cuda.empty_cache()
    if os.environ.get("run_nightly") == "1":
        print("Updating feature layer for accuracy dashboard\n")
        updateAccuracyResults()
        updateModelStats()
        # updateFailureModels()
    for key, val in data.items():
        try:
            os.system(f'rm -rf "{os.path.join(data_folder,val["datapath"],"models")}"')
            if "datapath_ms" in val.keys():
                os.system(
                    f'rm -rf "{os.path.join(data_folder_ms, val["datapath_ms"], "models")}"'
                )
        except:
            continue

    print("**End Common Arcgis Learn module Training**")



if __name__ == "__main__":
    unittest.main()
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
from sys import platform
from arcgis.learn import classify_pixels, detect_objects, classify_objects
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
parameter_fl = []
authorization_data = {}
if not HAS_DEPS:
    print("**Environment fails**")
    raise Exception(f"""{import_exception} \n\nThis module requires fastai, PyTorch, torchvision and scikit-image as its dependencies.""")
    module_skip = True
else:
    from arcgis.gis import GIS
    from arcgis.features import FeatureLayerCollection
    from integration.arcgis_learn.properties import data,data_folder, setuposenviron
    from arcgis.learn import prepare_data, prepare_tabulardata
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
                 "pointcnn":0,
                 "yolov3":0,
                 "fullyconnected":0,
                 "machine_learning":0
                 }}

@unittest.skipIf(module_skip, "Precondition check failed. Skipping Common tests")
def setUpModule():
    global authorization_data
    authorization_data = setuposenviron()
    data_path = data_folder
    if os.environ['run_nightly'] == "1":
        accuracy_values["attributes"]["Date"] = convertdate(datetime.today())
    print("Setup completed successfully")


def updateAccuracyResults():
    gis = GIS("https://deldev.maps.arcgis.com", authorization_data["for_update_accuracy_results"]["username"], authorization_data["for_update_accuracy_results"]["password"])
    item = gis.content.get('ea43a502dac5457598458562d6172af2')
    data = item.tables[0]
    global accuracy_values
    data.edit_features(adds=[accuracy_values])


def CommonTestUsingFL(query, model_type, prepare_tabular_data, regression_parameter, regression_test_score, inferencing_parameter, model_name, data_path, model_test):
    gis = GIS(url="https://geosaurus.maps.arcgis.com",username= authorization_data["for_common_test_using_fl"]["username"], password= authorization_data["for_common_test_using_fl"]["password"])
    calgary_no_southland_solar = gis.content.search(**query)[
        0]
    feature_layer = calgary_no_southland_solar.layers[0]

    if "preprocessors" in prepare_tabular_data.keys():
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.compose import make_column_transformer

        numerical_transformer = make_pipeline(MinMaxScaler())
        preprocessors = make_column_transformer((numerical_transformer, prepare_tabular_data["explanatory_variables"]))

        data = prepare_tabulardata(feature_layer,
                                   'capacity_f',
                                   explanatory_variables=prepare_tabular_data["explanatory_variables"],
                                   preprocessors=preprocessors)
        # Check model with default backbone
        model_object = model_type(data, 'sklearn.ensemble.GradientBoostingRegressor', n_estimators = 100, random_state = 43)
        # Fit the model.
        model_object.fit()

    else:
        data = prepare_tabulardata(feature_layer,
                               'capacity_f',
                               **prepare_tabular_data)

        # Check model with default backbone
        model_object = model_type(data)

        # Fit for 1 epochs without LR.
        model_object.fit(1,checkpoint=False)
        # Fit for 1 epochs with LR.
        model_object.fit(1, lr=0.001, checkpoint=False)

        # save model
        model_object.save(f'{os.path.join(data_folder, data_path, model_test)}')
        # Load from saved model.
        model_object.load(f'{os.path.join(data_folder, data_path, model_test)}')

        # From model with and without data bunch.
        model_object = model_type.from_model(
            os.path.join(data_folder, data_path, f'{model_test}/{model_test}.emd'))
        model_object = model_type.from_model(
            os.path.join(data_folder, data_path, f'{model_test}/{model_test}.emd'),
            data)



    if os.environ['run_nightly'] == "1":
        print("Testing for accuracy with default backbone")
        global accuracy_values
        if regression_parameter == "score":
            result = model_object.score()
        else:
            result = 0.0

        accuracy_values["attributes"][model_name] = result




def convertdate(dates):
    day = dates.day
    month = dates.month
    year = dates.year
    dstr = str(str(month)+'/'+str(day)+'/'+str(year))
    return dstr


def commonTestCases(model_type, model_test, data_path, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name, inferencing_image_server):
    data = prepare_data(**preparedata)

    # Check model with all default backbone
    model_object = model_type(data)
    # Fit for 1 epochs without LR.
    model_object.fit(1)
    # Fit for 1 epochs with LR.
    model_object.fit(1, lr=0.001)

    # save model
    model_object.save(f'{model_test}')

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
            result = model_object.average_precision_score()
            result = [v for k, v in sorted(result.items(), key=lambda item: item[1], reverse=True)][0]
        elif regression_parameter == "accuracy":
            result = model_object.accuracy()
        elif regression_parameter == "confusion_matrix":
            array = ClassificationInterpretation.from_learner(model_object.learn).confusion_matrix()
            true_prediction = array.diagonal().sum()
            all_prediction = array.sum()
            result = true_prediction / all_prediction
        elif regression_parameter == "precision_score":
            result = model_object.precision_score()
        elif regression_parameter == "compute_precision_recall":
            result = model_object.compute_precision_recall().loc["precision", :].max()
        elif regression_parameter == "psnr_metric":
            result = model_object.show_metrics()[-1]
        else:
            result = 0.0

        accuracy_values["attributes"][model_name] = result

        assert (result >= regression_test_score),"Model accuracy is lower than the threshold value. Please check."



    ## Inferencing function here.
    if os.environ["run_inference"] == "1":
        from arcpy.ia import DetectObjectsUsingDeepLearning, ClassifyPixelsUsingDeepLearning, ClassifyObjectsUsingDeepLearning
        # Inferencing from image server
        from arcgis.gis import GIS
        from arcgis.learn import Model, detect_objects
        gis = GIS('https://ndhlnagsb01.esri.com/portal', authorization_data["for_inferencing"]["username"],authorization_data["for_inferencing"]["password"], verify_cert=False)

        letters = string.ascii_lowercase
        output_name = ''.join(random.choice(letters) for i in range(9))

        if inferencing_parameter["model_type"] == "DetectObjectsUsingDeepLearning":
            model_path = os.path.join(data_folder, data_path, f'models/{model_test}/{model_test}.dlpk')

            model_package = gis.content.add(
                item_properties={"type": "Deep Learning Package", "typeKeywords": "Deep Learning",
                                 "title": model_test,
                                 "tags": "deeplearning, Detect object using deep learning", 'overwrite': 'True'}, data=model_path,
                folder="model_inference")

            detect_objects_model = Model(model_package)
            detect_objects_model.install()
            input_raster = gis.content.get(inferencing_image_server["input_raster"])

            detect_objects(input_raster.url,
                           model=detect_objects_model,
                           model_arguments=inferencing_image_server["model_arguments"],
                           output_name='test_model_'+output_name,
                           folder="model_inference",
                           context=inferencing_image_server["context"],
                           gis=gis)

            if "win" in platform:
                DetectObjectsUsingDeepLearning(
                        inferencing_parameter["sample_input"],
                    os.path.join(inferencing_parameter["path"], output_name+ ".shp"),
                    inferencing_parameter["model"],
                    inferencing_parameter["parameters"]

                )



        elif inferencing_parameter["model_type"] == "ClassifyPixelsUsingDeepLearning":

            model_path = os.path.join(data_folder, data_path, f'models/{model_test}/{model_test}.dlpk')

            model_package = gis.content.add(
                item_properties={"type": "Deep Learning Package", "typeKeywords": "Deep Learning",
                                 "title": model_test,
                                 "tags": "deeplearning, classify pxel using deeplearning", 'overwrite': 'True'}, data=model_path,
                folder="model_inference")

            classify_pixel_model = Model(model_package)
            classify_pixel_model.install()
            input_raster = gis.content.get(inferencing_image_server["input_raster"])

            classify_pixels(input_raster=input_raster.url,
                            model=classify_pixel_model,
                            output_name='test_model_'+output_name,
                            context=inferencing_image_server["context"],
                            model_arguments=inferencing_image_server["model_args"],
                            folder="model_inference",
                            gis=gis)

            if "win" in platform:
                ClassifyPixelsUsingDeepLearning(
                    inferencing_parameter["sample_input"],
                    inferencing_parameter["model"],
                    inferencing_parameter["parameters"],
                    "PROCESS_AS_MOSAICKED_IMAGE"
                )


        elif inferencing_parameter["model_type"] == "ClassifyObjectsUsingDeepLearning":

            model_path = os.path.join(data_folder, data_path, f'models/{model_test}/{model_test}.dlpk')

            model_package = gis.content.add(
                item_properties={"type": "Deep Learning Package", "typeKeywords": "Deep Learning",
                                 "title": model_test,
                                 "tags": "deeplearning, Classify object using deep learning", 'overwrite': 'True'},
                data=model_path,
                folder="model_inference")

            classify_pixel_model = Model(model_package)
            classify_pixel_model.install()
            input_raster = gis.content.get(inferencing_image_server["input_raster"])
            input_feature = gis.content.get(inferencing_image_server["input_features"])
            classify_objects(input_raster=input_raster.url,
                             model=model_package,
                             input_features=input_feature,
                             class_value_field='status',
                             model_arguments=inferencing_image_server["model_args"],
                             output_name='test_model_'+output_name,
                             context=inferencing_image_server["context"],
                            folder="model_inference",
                            gis=gis)

            if "win" in platform:
                ClassifyObjectsUsingDeepLearning(
                    inferencing_parameter["sample_input"],
                    inferencing_parameter["path"],
                    inferencing_parameter["model"],
                    in_features=inferencing_parameter["feature_layer"],
                    class_label_field="ClassLabel",
                    processing_mode="PROCESS_AS_MOSAICKED_IMAGE",
                    model_arguments="batch_size 4"

                )
        elif inferencing_parameter["model_type"] == "extract_entities":
            model_object.extract_entities(inferencing_parameter["sample_input"])
        elif inferencing_parameter["model_type"] == "predict_las":
            model_object.predict_las(
                path = inferencing_parameter["sample_input"],
                output_path = inferencing_parameter["sample_output"],
                print_metrics = False
            )
        else:
            pass


    # Load from saved model.
    model_object.load(f'{model_test}')

    # From model with and without data bunch.
    model_object = model_type.from_model(os.path.join(data_folder,data_path, f'models/{model_test}/{model_test}.emd'))
    model_object = model_type.from_model(os.path.join(data_folder, data_path, f'models/{model_test}/{model_test}.emd'),
                                         data)


def update_parameter():
    for key, val in data.items():
        if val["should_test"] and not val["test_feature_layer"]:
            parameter.append([key, val["model_test"], val["model"], val["datapath"], val["prepare_data"], val["regression_parameter"], val["regression_test_score"], val["inferencing_parameter"], val["model_name"], val["inferencing_image_server"]])
    return parameter

def update_parameter_fl():
    for key, val in data.items():
        if val["should_test"] and val["test_feature_layer"]:
            parameter_fl.append([key, val["gis_content_search"], val["model"], val["prepare_tabular_data"], val["regression_parameter"], val["regression_test_score"], val["inferencing_parameter"], val["model_name"], val["datapath"],val["model_test"]])
    return parameter_fl

class TestTraining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Inside Setup Class!!!")


    def setUp(self):
        print("Test: " + self._testMethodName)

    def tearDown(self):
        torch.cuda.empty_cache()
        # for key, val in data.items():
        #     os.system(f'rm -rf "{os.path.join(data_folder, val["datapath"], "models")}"')
        print("Test:" + self._testMethodName + "is completed.\n")
        print("------------------------------------------------------------------\n")

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter, skip_on_empty=True)
    def test(self,name,model_test, model, datapath, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name,inferencing_image_server):
        commonTestCases(model,model_test, datapath, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name,inferencing_image_server)

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter_fl, skip_on_empty=True)
    def test_fl(self, name,query, model_type, prepare_tabular_data, regression_parameter, regression_test_score, inferencing_parameter, model_name, data_path, model_test):
        CommonTestUsingFL(query, model_type, prepare_tabular_data, regression_parameter, regression_test_score, inferencing_parameter, model_name, data_path, model_test)

    @classmethod
    def tearDownClass(cls):
        torch.cuda.empty_cache()
        # for key, val in data.items():
        #     os.system(f'rm -rf "{os.path.join(data_folder, val["datapath"], "models")}"')
        print("\n All Tests have completed.")
        print("==================================================================")




## Remove all model directories
def tearDownModule():
    torch.cuda.empty_cache()
    if os.environ['run_nightly'] == "1":
        print("Updating feature layer for accuracy dashboard\n")
        updateAccuracyResults()
    # for key, val in data.items():
    #     os.system(f'rm -rf "{os.path.join(data_folder,val["datapath"],"models")}"')

    print("**End Common Arcgis Learn module Training**")





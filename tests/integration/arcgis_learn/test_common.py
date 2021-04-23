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
parameter_text = []
authorization_data = {}
check_ms = False
current_path = ""
if not HAS_DEPS:
    print("**Environment fails**")
    raise Exception(f"""{import_exception} \n\nThis module requires fastai, PyTorch, torchvision and scikit-image as its dependencies.""")
    module_skip = True
else:
    from arcgis.gis import GIS
    from arcgis.features import FeatureLayerCollection
    from integration.arcgis_learn.properties import data,data_folder, setuposenviron, data_folder_ms, data_inference_only
    from arcgis.learn import prepare_data, prepare_tabulardata, prepare_textdata
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
    if os.environ['run_nightly'] == "1":
        accuracy_values["attributes"]["Date"] = convertdate(datetime.today())
    print("Setup completed successfully")


def updateAccuracyResults():
    gis = GIS("https://deldev.maps.arcgis.com", authorization_data["for_update_accuracy_results"]["username"], authorization_data["for_update_accuracy_results"]["password"])
    item = gis.content.get('ea43a502dac5457598458562d6172af2')
    data = item.tables[0]
    global accuracy_values
    data.edit_features(adds=[accuracy_values])


def CommonTestUsingFL(query, model_type, prepare_tabular_data, regression_parameter, regression_test_score, inferencing_parameter, model_name, data_path, model_test, current_path):
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
        model_object.save(f'{os.path.join(current_path, data_path, model_test)}')
        # Load from saved model.
        model_object.load(f'{os.path.join(current_path, data_path, model_test)}')

        # From model with and without data bunch.
        model_object = model_type.from_model(
            os.path.join(current_path, data_path, f'{model_test}/{model_test}.emd'))
        model_object = model_type.from_model(
            os.path.join(current_path, data_path, f'{model_test}/{model_test}.emd'),
            data)



    if os.environ['run_nightly'] == "1":
        print("Testing for accuracy with default backbone")
        global accuracy_values
        if regression_parameter == "score":
            result = model_object.score()
        else:
            result = 0.0

        accuracy_values["attributes"][model_name] = result

    if os.environ["run_inference"] == "1":
        model_object.predict(feature_layer, output_layer_name='prediction_layer_rf')




def convertdate(dates):
    day = dates.day
    month = dates.month
    year = dates.year
    dstr = str(str(month)+'/'+str(day)+'/'+str(year))
    return dstr


def commonTestCases(model_type, model_test, data_path, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name, inferencing_image_server, ms_flag, current_path, num_epochs):
    if model_test == "sequencetosequence_test":
        data = prepare_textdata(**preparedata)
    elif model_test == "timeseriesmodel_test":
        from arcgis.learn import prepare_tabulardata
        import pandas as pd
        from sklearn.model_selection import train_test_split
        cali_rainfall_df1 = pd.read_csv(preparedata["path"])
        cali_rainfall_df1_sorted = cali_rainfall_df1.sort_values(by='date')
        test_size = 12
        train, test = train_test_split(cali_rainfall_df1_sorted, test_size = test_size, shuffle=False)
        data = prepare_tabulardata(train, variable_predict='prcp_mm_', index_field='date', seed=42)
    else:
        data = prepare_data(**preparedata)
    # data.show_batch()
    # Check model with all default backbone
    if model_test == "timeseriesmodel_test":
        model_object = model_type(data, seq_len=12)
    else:   
        model_object = model_type(data)


    # model_object.show_results()
    # model_object.lr_find(allow_plot=False)

    # Fit for 1 epochs without LR.
    model_object.fit(1)
    # # Fit for 1 epochs with LR.
    model_object.fit(1, lr=0.001)

    # save model
    if model_test == "sequencetosequence_test":
        d_path = os.path.join(data_folder, "sequencetosequence_data", "models", "sequencetosequence_test")
        model_save_path = model_object.save(d_path)
    elif model_test == "timeseriesmodel_test":
        pass
    else:
        model_save_path = model_object.save(f'{model_test}')

    # Check model with all supported backbones
    if os.environ['run_backbones'] == "1":
        print("Testing for all backbones")
        supported_backbones = model_object.supported_backbones
        for backbone in supported_backbones:
            model_object = model_type(data, backbone=str(backbone))
            model_object.fit(1)
            model_object.save(model_test + '_' + str(backbone))
            torch.cuda.empty_cache()

    if os.environ['run_nightly'] == "1":
        if not ms_flag:
            print("Testing for accuracy with default backbone")
            global accuracy_values
            model_object.fit(num_epochs)
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
                result = model_object.compute_metrics()[-1]
            elif regression_parameter == "f1_score":
                result = model_object.f1_score()
            elif regression_parameter == "compute_metrics":
                if model_test == "siammask_test":
                    result = float(model_object.compute_metrics()["mIOU"])
                else:
                    result = float(model_object.compute_metrics()["PSNR"])
            elif regression_parameter == "bleu_score":
                result = float(model_object.bleu_score()["bleu_score"])
            elif regression_parameter == "get_model_metrics":
                result = model_object.get_model_metrics()["seq2seq_acc"]
            elif regression_parameter == "mIOU":
                result = model_object.get_model_metrics()["0"]
            elif regression_parameter == "r2_score":
                sdf_forecasted = ts_model.predict(train, prediction_type='dataframe', number_of_predictions=test_size)
                sdf_forecasted = sdf_forecasted.tail(test_size)
                sdf_forecasted = sdf_forecasted[['date','prcp_mm__results']]
                sdf_forecasted['actual'] = test[test.columns[-1]].values
                sdf_forecasted = sdf_forecasted.set_index(sdf_forecasted.columns[0]) 
                from sklearn.metrics import r2_score
                import sklearn.metrics as metrics
                result = r2_score(sdf_forecasted['actual'],sdf_forecasted['prcp_mm__results'])
                return
            else:
                result = 0.0

            accuracy_values["attributes"][model_name] = result

            assert (result >= regression_test_score),"Model accuracy is lower than the threshold value. Please check."



    ## Inferencing function here.
    if os.environ["run_inference"] == "1" and ms_flag == False:
        from arcpy.ia import DetectObjectsUsingDeepLearning, ClassifyPixelsUsingDeepLearning, ClassifyObjectsUsingDeepLearning
        # Inferencing from image server
        from arcgis.gis import GIS
        from arcgis.learn import Model, detect_objects
        gis = GIS('https://ndhlnagsb01.esri.com/portal', authorization_data["for_inferencing"]["username"],authorization_data["for_inferencing"]["password"], verify_cert=False)

        letters = string.ascii_lowercase
        output_name = ''.join(random.choice(letters) for i in range(9))

        if inferencing_parameter["model_type"] == "DetectObjectsUsingDeepLearning":
            model_path = os.path.join(current_path, data_path, f'models/{model_test}/{model_test}.dlpk')

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

            model_path = os.path.join(current_path, data_path, f'models/{model_test}/{model_test}.dlpk')

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

            model_path = os.path.join(current_path, data_path, f'models/{model_test}/{model_test}.dlpk')

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

    if model_test == "timeseriesmodel_test":
        return

    # Load from saved model.
    model_object.load(str(model_save_path)+ os.sep + f"{model_test}.emd")

    # From model with and without data bunch.
    model_object = model_type.from_model(str(model_save_path)+ os.sep + f"{model_test}.emd")
    model_object = model_type.from_model(str(model_save_path)+ os.sep + f"{model_test}.emd",
                                         data)

def CommonTestTextModels(model_name, model, data, labels):
    if model_name == "zeroshotclassifier":
        model = model()
        # single label classification
        predictions = model.predict(data[0], labels[0])
        # Multi-Label classification
        predictions = model.predict(data, labels)
        # Multi-Lingual Data
        predictions = model.predict(data[-1], labels[-1])
    elif model_name == "questionanswering":
        model = model()
        predictions = model.get_answer(labels, context=data)
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
        model = model(backbone="roberta-base")
        predictions = model.predict_token(data, num_suggestions=4)

def update_parameter():
    check_ms = False
    for key, val in data.items():
        if val["should_test"] and not val["test_feature_layer"]:
            parameter.append([key, val["model_test"], val["model"], val["datapath"], val["prepare_data"], val["regression_parameter"], val["regression_test_score"], val["inferencing_parameter"], val["model_name"], val["inferencing_image_server"], check_ms, data_folder, val["regression_epochs"]])
    return parameter

def update_parameter_ms():
    check_ms = True
    for key, val in data.items():
        if val["should_test"] and not val["test_feature_layer"] and val["prepare_data_ms"] != False:
            parameter.append([key+"_ms", val["model_test"]+"_ms", val["model"], val["datapath_ms"], val["prepare_data_ms"], val["regression_parameter"], val["regression_test_score"], val["inferencing_parameter"], val["model_name"], val["inferencing_image_server"], check_ms, data_folder_ms, val["regression_epochs"]])
    return parameter

def update_parameter_fl():
    for key, val in data.items():
        if val["should_test"] and val["test_feature_layer"]:
            parameter_fl.append([key, val["gis_content_search"], val["model"], val["prepare_tabular_data"], val["regression_parameter"], val["regression_test_score"], val["inferencing_parameter"], val["model_name"], val["datapath"],val["model_test"], data_folder])
    return parameter_fl

def text_models():
    for key, val in data_inference_only.items():
        parameter_text.append([key, val["model_name"], val["model"], val["data"], val["labels"]])
    return parameter_text


class TestTraining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Inside Setup Class!!!")


    def setUp(self):
        print("Test: " + self._testMethodName)

    def tearDown(self):
        torch.cuda.empty_cache()
        for key, val in data.items():
            os.system(f'rm -rf "{os.path.join(data_folder, val["datapath"], "models")}"')
            if "datapath_ms" in val.keys():
                os.system(f'rm -rf "{os.path.join(data_folder_ms, val["datapath_ms"], "models")}"')
        print("Test:" + self._testMethodName + "is completed.\n")
        print("------------------------------------------------------------------\n")

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter, skip_on_empty=True)
    def test(self,name,model_test, model, datapath, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name,inferencing_image_server,ms_flag, data_folder_path, num_epochs):
        commonTestCases(model,model_test, datapath, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name,inferencing_image_server, ms_flag, data_folder_path, num_epochs)

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter_ms, skip_on_empty=True)
    def test(self, name, model_test, model, datapath, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name, inferencing_image_server, ms_flag, data_folder_path, num_epochs):
        commonTestCases(model, model_test, datapath, preparedata, regression_parameter, regression_test_score, inferencing_parameter, model_name, inferencing_image_server, ms_flag, data_folder_path, num_epochs)

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(update_parameter_fl, skip_on_empty=True)
    def test_fl(self, name,query, model_type, prepare_tabular_data, regression_parameter, regression_test_score, inferencing_parameter, model_name, data_path, model_test, data_folder_path):
        CommonTestUsingFL(query, model_type, prepare_tabular_data, regression_parameter, regression_test_score, inferencing_parameter, model_name, data_path, model_test, data_folder_path)

    @unittest.skipIf(module_skip, "Preconditions not met, skipping test")
    @parameterized.expand(text_models, skip_on_empty=True)
    def test_text_models(self,key, model_name, model, data, labels):
        CommonTestTextModels(model_name, model, data, labels)
    
    @classmethod
    def tearDownClass(cls):
        torch.cuda.empty_cache()
        for key, val in data.items():
            try:
                os.system(f'rm -rf "{os.path.join(data_folder, val["datapath"], "models")}"')
                if "datapath_ms" in val.keys():
                    os.system(f'rm -rf "{os.path.join(data_folder_ms, val["datapath_ms"], "models")}"')
            except:
                continue
        print("\n All Tests have completed.")
        print("==================================================================")




## Remove all model directories
def tearDownModule():
    torch.cuda.empty_cache()
    if os.environ['run_nightly'] == "1":
        print("Updating feature layer for accuracy dashboard\n")
        updateAccuracyResults()
    for key, val in data.items():
        try:
            os.system(f'rm -rf "{os.path.join(data_folder,val["datapath"],"models")}"')
            if "datapath_ms" in val.keys():
                os.system(f'rm -rf "{os.path.join(data_folder_ms, val["datapath_ms"], "models")}"')
        except:
            continue

    print("**End Common Arcgis Learn module Training**")





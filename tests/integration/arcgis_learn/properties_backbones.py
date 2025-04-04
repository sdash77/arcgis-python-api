import os
import warnings
warnings.filterwarnings('ignore')
from arcgis.learn import FeatureClassifier

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
data_folder = r"C:\files_sanoj\backbone_testing_data\rgb"
data_folder_ms = r"/root/test_automation/data/test_train_model/train_model_ms"
# authorization_path = (
#     r"/root/test_automation/data/test_train_model/properties/properties.json"
# )

data = {
    "fc": {
        "model_name": "featureclassifier",
        "datapath": "featureClassifier",
        "datapath_ms": "fc_data",
        "model": FeatureClassifier,
        "model_test": "fc_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "featureClassifier"),
            "batch_size": None,
            "dataset_type": "Imagenet",
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "fc_data"),
            "batch_size": None,
            "imagery_type": "multispectral",
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "confusion_matrix",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "ClassifyObjectsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyObjectsUsingDeepLearning",
                "fc",
                "world_imagery.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyObjectsUsingDeepLearning",
                "fc",
                "fc_test.emd",
            ),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "feature_layer": os.path.join(
                data_folder_inference,
                "ClassifyObjectsUsingDeepLearning",
                "fc",
                "test_data.tif",
            ),
            "path": os.path.join(
                data_folder_inference, "ClassifyObjectsUsingDeepLearning", "fc"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "ab399b847323487dba26809bf11ea91a",
            "input_features": "6ba16b390c4641a29fbc9e216080985d",
            "context": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -19518742.602406844,
                        "ymin": -2403911.9216141663,
                        "xmax": -19518595.699993156,
                        "ymax": -2403852.205185837,
                    },
                }
            },
            "model_args": {"batch_size": 4},
        },
    }
}
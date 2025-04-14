import os
import warnings
warnings.filterwarnings('ignore')
from arcgis.learn import FeatureClassifier

data_folder = r"C:\files_sanoj\backbone_testing_data\rgb"
data_folder_ms = r"C:\files_sanoj\backbone_testing_data\ms"

data = {
    "fc_singleLabel": {
        "model_name": "featureclassifier_singleLabel",
        "datapath": "fc_singleLabel",
        "datapath_ms": "fc_singleLabel",
        "model": FeatureClassifier,
        "model_test": "fc_singleLabel_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "fc_singleLabel"),
            "batch_size": None,
            "dataset_type": "Imagenet",
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "fc_singleLabel"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "confusion_matrix",
        "regression_test_score": 0.40,
        "regression_epochs": 1,
    },
    "fc_multiLabel": {
        "model_name": "featureclassifier_multiLabel",
        "datapath": "fc_multiLabel",
        "datapath_ms": "fc_multiLabel",
        "model": FeatureClassifier,
        "model_test": "fc_multiLabel_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "fc_multiLabel"),
            "batch_size": None,
            "dataset_type": "Imagenet",
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "fc_multiLabel"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "confusion_matrix",
        "regression_test_score": 0.40,
        "regression_epochs": 1,
    }
}
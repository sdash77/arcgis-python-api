import os
import warnings
warnings.filterwarnings('ignore')
from arcgis.learn import (
    FeatureClassifier,
    MLModel,
)

data_folder = r"D:\files_sanoj\bacbone_data\rgb"
data_folder_ms = r"D:\files_sanoj\bacbone_data\ms"
data_folder_tabular = r"D:\files_sanoj\tabular_data"

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
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "fc_singleLabel"),
            "batch_size": None,
        },
        "backbones": ["dofa_base", "timm:swin_base_window12", "hf:resnet18_landsat_etm_sr_moco"],
        "wavelengths_ms": [0.65, 0.55, 0.45, 0.85],
        "wavelengths_rgb": [0.49, 0.56, 0.665],
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
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "fc_multiLabel"),
            "batch_size": None,
        },
        "backbones": ["dofa_base", "timm:swin_base_window12", "hf:resnet18_landsat_etm_sr_moco"],
        "wavelengths_ms": [0.65, 0.55, 0.45, 0.85],
        "wavelengths_rgb": [0.49, 0.56, 0.665],
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "confusion_matrix",
        "regression_test_score": 0.40,
        "regression_epochs": 1,
    },
    "mlmodel_fairness": {
        "model_name": "mlmodel_fairness",
        "datapath": "mlmodel_data",
        "datapath_ms": False,
        "model": MLModel,
        "model_test": "mlmodel_test",
        "prepare_tabular_data": {
            "path": os.path.join(data_folder_tabular, "mlmodel_fairness", "salary.csv")
        },
        "prepare_data_ms": False,
        "backbones": False,
        "wavelengths_ms": False,
        "wavelengths_rgb": False,
        "should_test": True,
        "test_feature_layer": True,
        "regression_parameter": "automl_score",
        "regression_test_score": 0.4,
        "regression_epochs": 1,
    },
}
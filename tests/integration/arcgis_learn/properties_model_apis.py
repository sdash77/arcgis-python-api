import os
import warnings
warnings.filterwarnings('ignore')
import sys
from pathlib import Path
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
from arcgis.learn import (
    FeatureClassifier,
    MLModel,
    MaskRCNN,
    HEDEdgeDetector,
    DeepLab,
    FasterRCNN,
    RetinaNet,
    SingleShotDetector,
    AutoML,
)
DATA_FOLDER = os.environ.get('DATA_FOLDER')
data_path = Path(DATA_FOLDER)
 
 
data_folder = str(os.path.join(data_path, "bacbone_data", "rgb"))
data_folder_ms = str(os.path.join(data_path, "bacbone_data", "ms"))
data_folder_tabular = str(os.path.join(data_path, "tabular_data"))

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
    "maskrcnn": {
        "model_name": "maskrcnn",
        "datapath": "maskrcnn",
        "datapath_ms": "maskrcnn",
        "model": MaskRCNN,
        "model_test": "maskrcnn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "maskrcnn"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "maskrcnn"),
            "batch_size": None,
        },
        "backbones": ["dofa_base"],
        "wavelengths_ms": [0.665, 0.56, 0.49, 0.85],
        "wavelengths_rgb": [0.665, 0.56, 0.49],
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "regression_epochs": 1,
    },
    "hedEdge": {
        "model_name": "hedEdge",
        "datapath": "hedEdge",
        "datapath_ms": "hedEdge",
        "model": HEDEdgeDetector,
        "model_test": "hedEdge_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "hedEdge"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "hedEdge"),
            "batch_size": None,
        },
        "backbones": ["dofa_base"],
        "wavelengths_ms": [0.665, 0.56, 0.49, 0.85],
        "wavelengths_rgb": [0.665, 0.56, 0.49],
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "edge_detection",
        "regression_test_score": 0.40,
        "regression_epochs": 1,
    },
    "deeplab": {
        "model_name": "deeplab",
        "datapath": "deeplab",
        "datapath_ms": "deeplab",
        "model": DeepLab,
        "model_test": "deeplab_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "deeplab"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "deeplab"),
            "batch_size": None,
        },
        "backbones": ["dofa_base"],
        "wavelengths_ms": [0.665, 0.56, 0.49, 0.85],
        "wavelengths_rgb": [0.665, 0.56, 0.49],
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "accuracy",
        "regression_test_score": 0.40,
        "regression_epochs": 1,
    },
    "frcnn": {
        "model_name": "frcnn",
        "datapath": "frcnn_retina_ssd",
        "datapath_ms": "frcnn_retina_ssd",
        "model": FasterRCNN,
        "model_test": "frcnn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "frcnn_retina_ssd"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "frcnn_retina_ssd"),
            "batch_size": None,
        },
        "backbones": ["dofa_base"],
        "wavelengths_ms": [0.65, 0.55, 0.45, 0.85],
        "wavelengths_rgb": [0.65, 0.55, 0.45],
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "regression_epochs": 1,
    },
    "retina_net": {
        "model_name": "retina_net",
        "datapath": "frcnn_retina_ssd",
        "datapath_ms": "frcnn_retina_ssd",
        "model": RetinaNet,
        "model_test": "retina_net_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "frcnn_retina_ssd"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "frcnn_retina_ssd"),
            "batch_size": None,
        },
        "backbones": ["dofa_base"],
        "wavelengths_ms": [0.65, 0.55, 0.45, 0.85],
        "wavelengths_rgb": [0.65, 0.55, 0.45],
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "regression_epochs": 1,
    },
    "ssd": {
        "model_name": "ssd",
        "datapath": "frcnn_retina_ssd",
        "datapath_ms": "frcnn_retina_ssd",
        "model": SingleShotDetector,
        "model_test": "ssd_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "frcnn_retina_ssd"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "frcnn_retina_ssd"),
            "batch_size": None,
        },
        "backbones": ["dofa_base"],
        "wavelengths_ms": [0.65, 0.55, 0.45, 0.85],
        "wavelengths_rgb": [0.65, 0.55, 0.45],
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
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
        "model_categories": ["classification", "regression"],
    },
    "automl_fairness": {
        "model_name": "automl_fairness",
        "datapath": "automl_data",
        "datapath_ms": False,
        "model": AutoML,
        "model_test": "automl_test",
        "prepare_tabular_data": {
            "path": os.path.join(data_folder_tabular, "automl_data", "solar_power_train.csv")
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
        "model_categories": ["classification", "regression"],
    },
}
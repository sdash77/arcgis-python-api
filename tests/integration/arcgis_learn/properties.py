import os
import warnings

warnings.filterwarnings("ignore")
import json
from fastai.vision.transform import rotate, brightness, contrast
from arcgis.learn import (
    MLModel,
    FasterRCNN,
    SuperResolution,
    PointCNN,
    SingleShotDetector,
    UnetClassifier,
    PSPNetClassifier,
    FeatureClassifier,
    RetinaNet,
    MaskRCNN,
    DeepLab,
    YOLOv3,
    FullyConnectedNetwork,
    Pix2Pix,
    CycleGAN,
    BDCNEdgeDetector,
    HEDEdgeDetector,
    ImageCaptioner,
    SiamMask,
    ChangeDetector,
    MultiTaskRoadExtractor,
    TimeSeriesModel,
    DeepSort,
    MMSegmentation,
    MMDetection,
    AutoML,
    MaXDeepLab,
    DETReg,
    PSETAE,
    RandLANet,
    SQNSeg,
    MMDetection3D,
    SamLoRA,
    RTDetrV2,
    ClimaX,
    WNet_cGAN,
    Pix2PixHD,
    PTv3Seg,
    PTv3Det,
)
from arcgis.learn.text import (
    ZeroShotClassifier,
    QuestionAnswering,
    TextGenerator,
    TextSummarizer,
    TextTranslator,
    FillMask,
    EntityRecognizer,
    SequenceToSequence,
    TextClassifier,
)

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
if os.environ.get("run_nightly") == "1":
    data_folder = r"/root/test_automation/data/test_train_model/train_model_regression"
else:
    data_folder = r"/root/test_automation/data/test_train_model/train_model"
data_folder_inference = r"/root/test_automation/data/test_train_model/train_inference"
data_folder_ms = r"/root/test_automation/data/test_train_model/train_model_ms"
authorization_path = (
    r"/root/test_automation/data/test_train_model/properties/properties.json"
)

colormap = {
    "0": [0, 0, 0],
    "1": [0, 255, 0],
    "2": [0, 255, 100],
    "3": [0, 0, 255],
    "4": [0, 255, 100],
    "5": [255, 0, 0],
    "6": [0, 150, 100],
    "7": [0, 150, 100],
    "8": [0, 150, 100],
    "9": [0, 150, 100],
    "10": [0, 150, 100],
}

X = [
    "altitude_m",
    "wind_speed",
    "dayl__s_",
    "prcp__mm_d",
    "srad__W_m_",
    "swe__kg_m_",
    "tmax__deg",
    "tmin__deg",
    "vp__Pa_",
]

class_mapping_psetae = {
    204: "Pistachios",
    2: "Cotton",
    176: "Grassland/Pasture",
    195: "Herbaceous Wetlands",
    225: "Dbl Crop WinWht/Corn",
    24: "Winter Wheat",
    61: "Fallow/Idle Cropland",
    75: "Almonds",
    54: "Tomatoes",
    36: "Alfalfa",
    37: "Other Hay/Non Alfalfa",
    69: "Grapes",
    67: "Peaches",
    121: "Developed",
}


def setuposenviron():
    with open(authorization_path) as f:
        authorization_data = json.load(f)
    return authorization_data


data = {
    "ssd": {
        "model_name": "ssd",
        "datapath": "100_cracks_data",
        "datapath_ms": "ssd_retina_yolo_fasterrcnn_data",
        "model": SingleShotDetector,
        "model_test": "ssd_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "100_cracks_data"),
            "batch_size": None,
            "dataset_type": "PASCAL_VOC_rectangles",
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "ssd_retina_yolo_fasterrcnn_data"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "regression_epochs": 20,
        "inferencing_parameter": {
            "model_type": "DetectObjectsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "ssd",
                "Kolovai Palms.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "ssd",
                "ssd_test.emd",
            ),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True",
            "path": os.path.join(
                data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "163a78a453c243db964b5d7ee05a3fdb",
            "context": {
                "cellSize": 1,
                "processorType": "GPU",
                "extent": {
                    "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                    "xmin": -19518789.277457245,
                    "ymin": -2403355.53258688,
                    "xmax": -19518642.375043556,
                    "ymax": -2403295.816158551,
                },
                "parallelProcessingFactor": "2",
            },
            "model_arguments": {
                "padding": "56",
                "threshold": "0.5",
                "nms_overlap": "0.1",
                "batch_size": "4",
                "exclude_pad_detections": "True",
            },
        },
    },
    "rn": {
        "model_name": "retinanet",
        "datapath": "yolo_data",
        "datapath_ms": "ssd_retina_yolo_fasterrcnn_data",
        "model": RetinaNet,
        "model_test": "rn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "yolo_data"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "ssd_retina_yolo_fasterrcnn_data"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "regression_epochs": 20,
        "inferencing_parameter": {
            "model_type": "DetectObjectsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "rn",
                "Kolovai Palms.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "rn",
                "rn_test.emd",
            ),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True",
            "path": os.path.join(
                data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "163a78a453c243db964b5d7ee05a3fdb",
            "context": {
                "cellSize": 1,
                "processorType": "GPU",
                "extent": {
                    "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                    "xmin": -19518789.277457245,
                    "ymin": -2403355.53258688,
                    "xmax": -19518642.375043556,
                    "ymax": -2403295.816158551,
                },
                "parallelProcessingFactor": "2",
            },
            "model_arguments": {
                "padding": "56",
                "threshold": "0.5",
                "nms_overlap": "0.1",
                "batch_size": "4",
                "exclude_pad_detections": "True",
            },
        },
    },
    "unet": {
        "model_name": "unet",
        "datapath": "unet_psp_deep_data",
        "datapath_ms": "unet_psp_deeplab_superres_data",
        "model": UnetClassifier,
        "model_test": "unet_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "unet_psp_deep_data"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "unet_psp_deeplab_superres_data"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "accuracy",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "unet",
                "test_data.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "unet",
                "unet_test.emd",
            ),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "path": os.path.join(
                data_folder_inference, "ClassifyPixelsUsingDeepLearning", "unet"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "ab399b847323487dba26809bf11ea91a",
            "context": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -13046171.4852458,
                        "ymin": 4033856.50520854,
                        "xmax": -13045909.5350487,
                        "ymax": 4034115.48833226,
                    },
                    "batch_size": 1,
                }
            },
            "model_args": {"batch_size": 4, "padding": 56},
        },
    },
    "deeplab": {
        "model_name": "deeplab",
        "datapath": "unet_psp_deep_data",
        "datapath_ms": "unet_psp_deeplab_superres_data",
        "model": DeepLab,
        "model_test": "deeplab_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "unet_psp_deep_data"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "unet_psp_deeplab_superres_data"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "accuracy",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "deeplab",
                "test_data.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "deeplab",
                "deeplab_test.emd",
            ),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "path": os.path.join(
                data_folder_inference, "ClassifyPixelsUsingDeepLearning", "deeplab"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "ab399b847323487dba26809bf11ea91a",
            "context": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -13046171.4852458,
                        "ymin": 4033856.50520854,
                        "xmax": -13045909.5350487,
                        "ymax": 4034115.48833226,
                    },
                    "batch_size": 1,
                }
            },
            "model_args": {"batch_size": 4, "padding": 56},
        },
    },
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
    },
    "pspnet": {
        "model_name": "pspnet",
        "datapath": "unet_psp_deep_data",
        "datapath_ms": "unet_psp_deeplab_superres_data",
        "model": PSPNetClassifier,
        "model_test": "pspnet_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "unet_psp_deep_data"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "unet_psp_deeplab_superres_data"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "accuracy",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "pspnet",
                "test_data.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "pspnet",
                "pspnet_test.emd",
            ),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "path": os.path.join(
                data_folder_inference, "ClassifyPixelsUsingDeepLearning", "pspnet"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "ab399b847323487dba26809bf11ea91a",
            "context": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -13046171.4852458,
                        "ymin": 4033856.50520854,
                        "xmax": -13045909.5350487,
                        "ymax": 4034115.48833226,
                    },
                    "batch_size": 1,
                }
            },
            "model_args": {"batch_size": 1, "padding": 56},
        },
    },
    "maskrcnn": {
        "model_name": "maskrcnn",
        "datapath": "maskrcnn_data",
        "datapath_ms": "maskrcnn_data",
        "model": MaskRCNN,
        "model_test": "maskrcnn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "maskrcnn_data"),
            "batch_size": None,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "maskrcnn_data"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.30,
        "regression_epochs": 15,
        "inferencing_parameter": {
            "model_type": "DetectObjectsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "maskrcnn",
                "input_image.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "ssd",
                "maskrcnn_test.emd",
            ),
            "parameters": "padding 56;batch_size 64;threshold 0.5;return_bboxes True",
            "path": os.path.join(
                data_folder_inference, "DetectObjectsUsingDeepLearning", "maskrcnn"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "d9dcf0415d23462da80a8f47783fe9e8",
            "context": {
                "cellSize": 1,
                "processorType": "GPU",
                "extent": {
                    "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                    "xmin": -13042106.3685066,
                    "ymin": -13042016.2777014,
                    "xmax": 4033862.48706524,
                    "ymax": 4033930.88199369,
                },
                "parallelProcessingFactor": "2",
            },
            "model_arguments": {
                "padding": "56",
                "threshold": "0.5",
                "nms_overlap": "0.1",
                "batch_size": "4",
                "exclude_pad_detections": "True",
            },
        },
    },
    "ner": {
        "model_name": "ner",
        "datapath": "ner_data",
        "model": EntityRecognizer,
        "model_test": "ner_model_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "ner_data", "updated_labelled.json"),
            "batch_size": 8,
            "dataset_type": "ner_json",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "f1_score",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "extract_entities",
            "sample_input": os.path.join(
                data_folder_inference, "Others", "ner", "Reports"
            ),
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "pointcnn": {
        "model_name": "pointcnn",
        "datapath": os.path.join("pointcnn_data", "input"),
        "model": PointCNN,
        "model_test": "pointcnn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "pointcnn_data", "input"),
            "batch_size": None,
            "dataset_type": "PointCloud",
            "transforms": None,
            "color_mapping": colormap,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_precision_recall",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "predict_las",
            "sample_input": os.path.join(
                data_folder_inference, "Others", "pointcnn", "sample_input"
            ),
            "sample_output": os.path.join(
                data_folder_inference, "Others", "pointcnn", "sample_output"
            ),
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "superres": {
        "model_name": "superres",
        "datapath": "superres_data",
        "datapath_ms": "unet_psp_deeplab_superres_data",
        "model": SuperResolution,
        "model_test": "superres_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "superres_data"),
            "batch_size": 2,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "psnr_metric",
        "regression_test_score": 0.4,
        "regression_epochs": 20,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "superres",
                "input_image.jpg",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "superres",
                "superres_test.emd",
            ),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "path": os.path.join(
                data_folder_inference, "ClassifyPixelsUsingDeepLearning", "superres"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "ab399b847323487dba26809bf11ea91a",
            "context": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -13046171.4852458,
                        "ymin": 4033856.50520854,
                        "xmax": -13045909.5350487,
                        "ymax": 4034115.48833226,
                    },
                    "batch_size": 1,
                }
            },
            "model_args": {"batch_size": 1, "padding": 56},
        },
    },
    "fasterrcnn": {
        "model_name": "fasterrcnn",
        "datapath": "fasterrcnn_data",
        "datapath_ms": "ssd_retina_yolo_fasterrcnn_data",
        "model": FasterRCNN,
        "model_test": "fasterrcnn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "fasterrcnn_data"),
            "batch_size": 4,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "ssd_retina_yolo_fasterrcnn_data"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.4,
        "regression_epochs": 15,
        "inferencing_parameter": {
            "model_type": "DetectObjectsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "fasterrcnn",
                "input_image.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "fasterrcnn",
                "fasterrcnn.emd",
            ),
            "parameters": "padding 56;batch_size 64;threshold 0.5;return_bboxes True",
            "path": os.path.join(
                data_folder_inference, "DetectObjectsUsingDeepLearning", "fasterrcnn"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "d9dcf0415d23462da80a8f47783fe9e8",
            "context": {
                "cellSize": 1,
                "processorType": "GPU",
                "extent": {
                    "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                    "xmin": -13042106.3685066,
                    "ymin": -13042016.2777014,
                    "xmax": 4033862.48706524,
                    "ymax": 4033930.88199369,
                },
                "parallelProcessingFactor": "2",
            },
            "model_arguments": {
                "padding": "56",
                "threshold": "0.5",
                "nms_overlap": "0.1",
                "batch_size": "4",
                "exclude_pad_detections": "True",
            },
        },
    },
    "yolov3": {
        "model_name": "yolov3",
        "datapath": "yolo_data",
        "datapath_ms": "ssd_retina_yolo_fasterrcnn_data",
        "model": YOLOv3,
        "model_test": "yolov3_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "yolo_data"),
            "batch_size": 4,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "ssd_retina_yolo_fasterrcnn_data"),
            "batch_size": None,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "DetectObjectsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "yolo",
                "input_image.jpg",
            ),
            "model": os.path.join(
                data_folder_inference,
                "DetectObjectsUsingDeepLearning",
                "yolo",
                "yolov3_test.emd",
            ),
            "parameters": "padding 56;batch_size 64;threshold 0.5;return_bboxes True",
            "path": os.path.join(
                data_folder_inference, "DetectObjectsUsingDeepLearning", "yolo"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "d9dcf0415d23462da80a8f47783fe9e8",
            "context": {
                "cellSize": 1,
                "processorType": "GPU",
                "extent": {
                    "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                    "xmin": -13042106.3685066,
                    "ymin": -13042016.2777014,
                    "xmax": 4033862.48706524,
                    "ymax": 4033930.88199369,
                },
                "parallelProcessingFactor": "2",
            },
            "model_arguments": {
                "padding": "56",
                "threshold": "0.5",
                "nms_overlap": "0.1",
                "batch_size": "4",
                "exclude_pad_detections": "True",
            },
        },
    },
    "fcn": {
        "model_name": "fullyconnected",
        "model": FullyConnectedNetwork,
        "datapath": "fcn_data",
        "model_test": "fcn_test",
        "prepare_tabular_data": {"explanatory_variables": X},
        "gis_content_search": {
            "query": "calgary_no_southland_solar owner:api_data_owner",
            "item_type": "feature layer",
        },
        "should_test": True,
        "test_feature_layer": True,
        "regression_parameter": "score",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {"model_type": "prediction_layer"},
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "pix2pix": {
        "model_name": "pix2pix",
        "datapath": "pix2pix_data",
        "datapath_ms": "pix2pix_data_ms",
        "model": Pix2Pix,
        "model_test": "pix2pix_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "pix2pix_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_metrics",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "pix2pix",
                "images",
                "000000000.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "pix2pix",
                "pix2pix_test.emd",
            ),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True",
            "path": os.path.join(
                data_folder_inference, "ClassifyPixelsUsingDeepLearning", "pix2pix"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "pass",
            "model_package": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -13046171.4852458,
                        "ymin": 4033856.50520854,
                        "xmax": -13045909.5350487,
                        "ymax": 4034115.48833226,
                    },
                    "batch_size": 1,
                }
            },
            "model_args": {"batch_size": 1, "padding": 56},
        },
    },
    "cyclegan": {
        "model_name": "cyclegan",
        "datapath": "cyclegan_data",
        "datapath_ms": "cyclegan_data_ms",
        "model": CycleGAN,
        "model_test": "cyclegan_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "cyclegan_data"),
            "batch_size": None,
            "dataset_type": "CycleGAN",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_metrics",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "cyclegan",
                "images",
                "000000000.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "cyclegan",
                "cyclegan_test.emd",
            ),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True",
            "path": os.path.join(
                data_folder_inference, "ClassifyPixelsUsingDeepLearning", "cyclegan"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "ab399b847323487dba26809bf11ea91a",
            "context": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -13046171.4852458,
                        "ymin": 4033856.50520854,
                        "xmax": -13045909.5350487,
                        "ymax": 4034115.48833226,
                    },
                    "batch_size": 1,
                }
            },
            "model_args": {"batch_size": 1, "padding": 56},
        },
    },
    "hededgedetector": {
        "model_name": "hededgedetector",
        "datapath": "hededgedetector_data",
        "datapath_ms": "hededgedetector_data_ms",
        "model": HEDEdgeDetector,
        "model_test": "hededgedetector_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "hededgedetector_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "edge_detection",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "cyclegan",
                "images",
                "000000000.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "cyclegan",
                "cyclegan_test.emd",
            ),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True",
            "path": os.path.join(
                data_folder_inference, "ClassifyPixelsUsingDeepLearning", "cyclegan"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "ab399b847323487dba26809bf11ea91a",
            "context": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -13046171.4852458,
                        "ymin": 4033856.50520854,
                        "xmax": -13045909.5350487,
                        "ymax": 4034115.48833226,
                    },
                    "batch_size": 1,
                }
            },
            "model_args": {"batch_size": 1, "padding": 56},
        },
    },
    "bdcnedgedetector": {
        "model_name": "bdcnedgedetector",
        "datapath": "hededgedetector_data",
        "datapath_ms": "hededgedetector_data_ms",
        "model": BDCNEdgeDetector,
        "model_test": "bdcnedgedetector_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "hededgedetector_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "edge_detection",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "cyclegan",
                "images",
                "000000000.tif",
            ),
            "model": os.path.join(
                data_folder_inference,
                "ClassifyPixelsUsingDeepLearning",
                "cyclegan",
                "cyclegan_test.emd",
            ),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True",
            "path": os.path.join(
                data_folder_inference, "ClassifyPixelsUsingDeepLearning", "cyclegan"
            ),
        },
        "inferencing_image_server": {
            "input_raster": "ab399b847323487dba26809bf11ea91a",
            "context": {
                "extent": {
                    "cellSize": 0.3,
                    "processorType": "GPU",
                    "extent": {
                        "spatialReference": {"latestWkid": 3857, "wkid": 102100},
                        "xmin": -13046171.4852458,
                        "ymin": 4033856.50520854,
                        "xmax": -13045909.5350487,
                        "ymax": 4034115.48833226,
                    },
                    "batch_size": 1,
                }
            },
            "model_args": {"batch_size": 1, "padding": 56},
        },
    },
    "maxdeeplab": {
        "model_name": "maxdeeplab",
        "datapath": "panoptic_rgb",
        "datapath_ms": "panoptic_ms",
        "model": MaXDeepLab,
        "model_test": "maxdeeplab_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "panoptic_rgb"),
            "batch_size": None,
            "n_masks": 38,
            "resize_to": 256,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "panoptic_ms"),
            "batch_size": None,
            "n_masks": 38,
            "resize_to": 256,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "panoptic_quality",
        "regression_test_score": 0.10,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "detreg": {
        "model_name": "detreg",
        "datapath": "panoptic_rgb",
        "datapath_ms": "panoptic_ms",
        "model": DETReg,
        "model_test": "detreg_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "rgb_small"),
            "batch_size": None,
            "chip_size": 256,
        },
        "prepare_data_ms": {
            "path": os.path.join(data_folder_ms, "ms_small"),
            "batch_size": None,
            "chip_size": 256,
        },
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "imagecaptioner": {
        "model_name": "imagecaptioner",
        "datapath": "imagecaptioner_data",
        "datapath_ms": "imagecaptioner_data_ms",
        "model": ImageCaptioner,
        "model_test": "imagecaptioner_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "imagecaptioner_data"),
            "batch_size": None,
            "transforms": False,
            "dataset_type": "ImageCaptioning",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "bleu_score",
        "regression_test_score": 0.3,
        "regression_epochs": 30,
        "inferencing_parameter": {"model_type": "bleu_score"},
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "siammask": {
        "model_name": "siammask",
        "datapath": "siammask_data",
        "datapath_ms": "siammask_data_ms",
        "model": SiamMask,
        "model_test": "siammask_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "siammask_data"),
            "batch_size": 64,
            "dataset_type": "ObjectTracking",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_metrics",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {"model_type": "siammask_iou"},
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "changedetection": {
        "model_name": "changedetection",
        "datapath": "changedetection_data",
        "datapath_ms": "changedetection_data_ms",
        "model": ChangeDetector,
        "model_test": "changedetection_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "changedetection_data"),
            "chip_size": 256,
            "dataset_type": "ChangeDetection",
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "precision_recall_score",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {"model_type": "pass"},
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "mtre": {
        "model_name": "mtre",
        "datapath": "mtre_data",
        "datapath_ms": "mtre_data_ms",
        "model": MultiTaskRoadExtractor,
        "model_test": "mtre_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "mtre_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "mIOU",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "sequencetosequence": {
        "model_name": "sequencetosequence",
        "datapath": "sequencetosequence_data",
        "model": SequenceToSequence,
        "model_test": "sequencetosequence_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "sequencetosequence_data"),
            "batch_size": 4,
            "task": "sequence_translation",
            "text_columns": "input",
            "label_columns": "target",
            "train_file": "address_crapified_mini.csv",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "get_model_metrics",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": os.path.join(
                data_folder_inference, "Others", "sequencetosequence", "Reports"
            ),
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "timeseriesmodel": {
        "model_name": "timeseriesmodel",
        "datapath": "timeseriesmodel_data",
        "datapath_ms": "timeseriesmodel_data_ms",
        "model": TimeSeriesModel,
        "model_test": "timeseriesmodel_test",
        "prepare_data": {
            "path": os.path.join(
                data_folder, "timeseriesmodel_data", "california_rainfall.csv"
            )
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "r2_score",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "deepsort": {
        "model_name": "deepsort",
        "datapath": "deepsort_data",
        "datapath_ms": "deepsort_data_ms",
        "model": DeepSort,
        "model_test": "deepsort_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "deepsort_data"),
            "batch_size": 10,
            "transforms": (
                [
                    rotate(degrees=30, p=0.5),
                    brightness(change=(0.4, 0.6)),
                    contrast(scale=(0.75, 1.5)),
                ],
                [],
            ),
            "resize_to": (128, 64),
            "dataset_type": "Imagenet",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "confusion_matrix",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "mmsegmentation": {
        "model_name": "mmsegmentation",
        "datapath": "mmsegmentation_data",
        "datapath_ms": "mmsegmentation_data_ms",
        "model": MMSegmentation,
        "model_test": "mmsegmentation_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "mmsegmentation_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "per_class_metrics",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "mmdetection": {
        "model_name": "mmdetection",
        "datapath": "mmdetection_data",
        "datapath_ms": "mmdetection_data_ms",
        "model": MMDetection,
        "model_test": "mmdetection_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "mmdetection_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.4,
        "regression_epochs": 20,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "mlmodel": {
        "model_name": "mlmodel",
        "datapath": "mlmodel_data",
        "datapath_ms": "automl_data_ms",
        "model": MLModel,
        "model_test": "automl_test",
        "prepare_tabular_data": {
            "path": os.path.join(data_folder, "mlmodel_data", "salary_data.csv")
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": True,
        "regression_parameter": "automl_score",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "automl": {
        "model_name": "automl",
        "datapath": "automl_data",
        "datapath_ms": "automl_data_ms",
        "model": AutoML,
        "model_test": "automl_test",
        "prepare_tabular_data": {
            "path": os.path.join(data_folder, "automl_data", "automl_data.csv")
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": True,
        "regression_parameter": "automl_score",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "psetae": {
        "model_name": "psetae",
        "datapath": "psetae_data",
        "datapath_ms": "psetae_data_ms",
        "model": PSETAE,
        "model_test": "psetae_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "psetae_data"),
            "batch_size": 64,
            "dataset_type": "PSETAE",
            "class_mapping": class_mapping_psetae,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "mIOU",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "textclassifier": {
        "model_name": "textclassifier",
        "datapath": "textclassifier_data",
        "model": TextClassifier,
        "model_test": "textclassifier_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "textclassifier_data"),
            "batch_size": 8,
            "task": "classification",
            "train_file": "textclassifier_data_file.csv",
            "text_columns": "text",
            "label_columns": "sentiment",
            "remove_html_tags": True,
            "remove_urls": True,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "accuracy",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "randlanet": {
        "model_name": "randlanet",
        "datapath": "randlanet_data",
        "model": RandLANet,
        "model_test": "randlanet_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "randlanet_data", "GCS_plain.pctd"),
            "batch_size": None,
            "min_points": 100,
            "classes_of_interest": [5],
            "remap_classes": {},
            "extra_features": ["intensity", "numberOfReturns", "returnNumber"],
            "class_mapping": {},
            "dataset_type": "PointCloud",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_precision_recall",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "sqnseg": {
        "model_name": "sqnseg",
        "datapath": "sqnseg_data",
        "model": SQNSeg,
        "model_test": "sqnseg_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "randlanet_data", "GCS_plain.pctd"),
            "batch_size": None,
            "min_points": 100,
            "classes_of_interest": [5],
            "remap_classes": {},
            "extra_features": ["intensity", "numberOfReturns", "returnNumber"],
            "class_mapping": {},
            "dataset_type": "PointCloud",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_precision_recall",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "mm3d": {
        "model_name": "mm3d",
        "datapath": "mm3d_data",
        "model": MMDetection3D,
        "model_test": "mm3d_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "mm3d_data", "Chairs001.pctd"),
            "batch_size": 64,
            "dataset_type": "PointCloudOD",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "regression_epochs": 6,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "samlora": {
        "model_name": "samlora",
        "datapath": "samlora_data",
        "model": SamLoRA,
        "model_test": "samlora_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "samlora_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "accuracy",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "rtdetrv2": {
        "model_name": "rtdetrv2",
        "datapath": "fasterrcnn_data",
        "model": RTDetrV2,
        "model_test": "rtdetrv2_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "fasterrcnn_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "climax": {
        "model_name": "climax",
        "datapath": "climax_data",
        "model": ClimaX,
        "model_test": "climax_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "climax_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_metrics",
        "regression_test_score": 0.40,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "mmdetection_dino": {
        "model_name": "mmdetection_dino",
        "datapath": "mmdetection_data",
        "datapath_ms": "mmdetection_data_ms",
        "model": MMDetection,
        "model_test": "mmdetection_dino_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "mmdetection_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.4,
        "regression_epochs": 10,
        "inferencing_parameter": {
            "model_type": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "context": "pass"},
    },
    "wnet_cgan": {
        "model_name": "wnet_cgan",
        "datapath": "wnet_data",
        "model": WNet_cGAN,
        "model_test": "wnet_cgan_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "wnet_data"),
            "batch_size": None,
            "dataset_type": "WNet_cGAN",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_metrics",
        "regression_test_score": 0.40,
        "regression_epochs": 4,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "pix2pixhd": {
        "model_name": "pix2pixhd",
        "datapath": "pix2pix_data",
        "model": Pix2PixHD,
        "model_test": "pix2pixhd_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "pix2pix_data"),
            "batch_size": None,
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_metrics",
        "regression_test_score": 0.40,
        "regression_epochs": 20,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "ptv3seg": {
        "model_name": "ptv3seg",
        "datapath": "randlanet_data",
        "model": PTv3Seg,
        "model_test": "ptv3seg_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "randlanet_data", "GCS_plain.pctd"),
            "batch_size": None,
            "dataset_type": "PointCloud",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "compute_precision_recall",
        "regression_test_score": 0.40,
        "regression_epochs": 4,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
    "ptv3det": {
        "model_name": "ptv3det",
        "datapath": "mm3d_data",
        "model": PTv3Det,
        "model_test": "ptv3det_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "mm3d_data", "Chairs001.pctd"),
            "batch_size": 64,
            "dataset_type": "PointCloudOD",
        },
        "prepare_data_ms": False,
        "should_test": True,
        "test_feature_layer": False,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "regression_epochs": 4,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": "pass",
        },
        "inferencing_image_server": {"input_raster": "pass", "model_package": "pass"},
    },
}


data_inference_only = {
    "zeroshotclassifier": {
        "model_name": "zeroshotclassifier",
        "model": ZeroShotClassifier,
        "data": [
            (
                "Dude what are you doing? Publishing my project and data without my permission?"
                "You try to make it look like you did this work?"
                "TAKE THIS MAP DOWN! YOU DO NOT OWN THIS MAP PROJECT OR DATA!"
            ),
            "This imagery was great but is not available now",
            "¿A quién vas a votar en 2020?",
        ],
        "labels": [
            "toxic",
            "severe_toxic",
            "obscene",
            "threat",
            "insult",
            "identity_hate",
            "Europa",
        ],
    },
    "questionanswering": {
        "model_name": "questionanswering",
        "model": QuestionAnswering,
        "data": r"""
                    The arcgis.learn module includes PointCNN model to efficiently classify and segment points from a point cloud dataset. 
                    Point cloud datasets are typically collected using Lidar sensors ( light detection and ranging ) – an optical 
                    remote-sensing technique that uses laser light to densely sample the surface of the earth, producing highly 
                    accurate x, y, and z measurements. These Lidar sensor produced points, once post-processed and spatially 
                    organized are referred to as a 'Point cloud' and are typically collected using terrestrial (both mobile or static) 
                    and airborne Lidar.
                """,
        "labels": [
            "What is PointCNN?",
            "How is Point cloud dataset collected?",
            "What is Lidar?",
        ],
    },
    "textsummarizer": {
        "model_name": "textsummarizer",
        "model": TextSummarizer,
        "data": r"""
                    This deep learning model is used to extract building footprints from high resolution (30-50 cm) satellite imagery. 
                    Building footprint layers are useful in preparing base maps and analysis workflows for urban planning and development, 
                    insurance, taxation, change detection, infrastructure planning and a variety of other applications.
                    Digitizing building footprints from imagery is a time consuming task and is commonly done by digitizing features 
                    manually. Deep learning models have a high capacity to learn these complex workflow semantics and can produce 
                    superior results. Use this deep learning model to automate this process and reduce the time and effort required 
                    for acquiring building footprints.
                """,
        "labels": [None],
    },
    "texttranslator": {
        "model_name": "texttranslator",
        "model": TextTranslator,
        "data": [
            """El martes, Jack y Laura Dangermond serán honrados por uno de los legados perdurables de Esri""",
            """On Tuesday, Jack and Laura Dangermond will be honored by one of Esri's enduring legacies""",
            """El martes, Jack y Laura Dangermond serán honrados por uno de los legados perdurables de Esri""",
        ],
        "labels": [None],
    },
    "textgenerator": {
        "model_name": "textgenerator",
        "model": TextGenerator,
        "data": [
            "Hundreds of thousands of organizations in virtually every field are using GIS to make maps that"
        ],
        "labels": [None],
    },
    "fillmask": {
        "model_name": "fillmask",
        "model": FillMask,
        "data": [
            "On Tuesday, Jack and Laura Dangermond are being honored for one of Esri’s __ legacies."
        ],
        "labels": [None],
    },
}

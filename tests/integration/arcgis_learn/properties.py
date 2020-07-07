import os
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
from arcgis.learn import FasterRCNN, SuperResolution, EntityRecognizer, PointCNN, SingleShotDetector, UnetClassifier, \
    PSPNetClassifier, FeatureClassifier, RetinaNet, MaskRCNN, prepare_data, DeepLab


data_folder = r"/home/administrator/Raster/Test_Data/data_for_testing/train_model"
data_folder_inference = r"/home/administrator/Raster/Test_Data/data_for_testing/train_inference"

colormap = {'0': [0, 0, 0], '1': [0, 255, 0], '2': [0, 255, 100], '3': [0, 0, 255], '4': [0, 255, 100],
            '5': [255, 0, 0],
            '6': [0, 150, 100], '7': [0, 150, 100], '8': [0, 150, 100], '9': [0, 150, 100], '10': [0, 150, 100]}


def setuposenviron():
    os.environ['run_backbones'] = "0"
    os.environ["run_nightly"] = "0"
    os.environ["run_inference"] = "0"
    os.environ["run_weekly"] = "0"




data = {
    "ssd": {
        "model_name":"ssd",
        "datapath": "ssd_retina_data",
        "model": SingleShotDetector,
        "model_test": "ssd_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "ssd_retina_data"),
            "batch_size": 2
        },
        "should_test": True,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.10,
        "inferencing_parameter": {
            "model_type": "DetectObjectsUsingDeepLearning",
            "sample_input": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd",
                                         "Kolovai Palms.tif"),
            "model": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd", "ssd_test.emd"),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True",
            "path": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd")
        }
    },
    "rn": {
        "model_name":"ratinanet",
        "datapath": "ssd_retina_data",
        "model": RetinaNet,
        "model_test": "rn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "ssd_retina_data"),
             "batch_size": 2
        },
        "should_test": True,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "DetectObjectsUsingDeepLearning",
            "sample_input": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "rn",
                                         "Kolovai Palms.tif"),
            "model": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "rn", "rn_test.emd"),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True",
            "path": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd")
        }
    },
    "unet": {
        "model_name":"unet",
        "datapath": "unet_psp_deep_data",
        "model": UnetClassifier,
        "model_test": "unet_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "unet_psp_deep_data"),
             "batch_size": 2
        },
        "should_test": True,
        "regression_parameter": "accuracy",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "unet",
                                         "test_data.tif"),
            "model": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "unet", "unet_test.emd"),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "path": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "unet")
        }
    },
    "deeplab": {
        "model_name":"deeplab",
        "datapath": "unet_psp_deep_data",
        "model": DeepLab,
        "model_test": "deeplab_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "unet_psp_deep_data"),
            "batch_size": 2
        },
        "should_test": True,
        "regression_parameter":"accuracy",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "deeplab",
                                         "test_data.tif"),
            "model": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "deeplab",
                                  "deeplab_test.emd"),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "path": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "deeplab")
        }
    },
    "fc": {
        "model_name":"featureclassifier",
        "datapath": "fc_data",
        "model": FeatureClassifier,
        "model_test": "fc_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "fc_data"),
            "batch_size": 2
        },
        "should_test": True,
        "regression_parameter":"confusion_matrix",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "ClassifyObjectsUsingDeepLearning",
            "sample_input": os.path.join(data_folder_inference, "ClassifyObjectsUsingDeepLearning", "fc",
                                         "world_imagery.tif"),
            "model": os.path.join(data_folder_inference, "ClassifyObjectsUsingDeepLearning", "fc", "fc_test.emd"),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "feature_layer": os.path.join(data_folder_inference, "ClassifyObjectsUsingDeepLearning", "fc",
                                          "test_data.tif"),
            "path": os.path.join(data_folder_inference, "ClassifyObjectsUsingDeepLearning", "fc")
        }
    },
    "pspnet": {
        "model_name":"pspnet",
        "datapath": "unet_psp_deep_data",
        "model": PSPNetClassifier,
        "model_test": "pspnet_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "unet_psp_deep_data"),
             "batch_size": 2
        },
        "should_test": True,
        "regression_parameter": "accuracy",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "ClassifyPixelsUsingDeepLearning",
            "sample_input": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "pspnet",
                                         "test_data.tif"),
            "model": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "pspnet",
                                  "pspnet_test.emd"),
            "parameters": "padding 56;batch_size 4;predict_background True",
            "path": os.path.join(data_folder_inference, "ClassifyPixelsUsingDeepLearning", "pspnet")
        }
    },
    "maskrcnn": {
        "model_name":"maskrcnn",
        "datapath": "maskrcnn_data",
        "model": MaskRCNN,
        "model_test": "maskrcnn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "maskrcnn_data"),
            "batch_size": 2
        },
        "should_test": True,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "Pass",
            "sample_input": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "maskrcnn",
                                         "input_image.tif"),
            "model": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd", "maskrcnn_test.emd"),
            "parameters": "padding 56;batch_size 64;threshold 0.5;return_bboxes True",
            "path": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "maskrcnn")
        }
    },
    "ner": {
        "model_name":"ner",
        "datapath": "ner_data",
        "model": EntityRecognizer,
        "model_test": "ner_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "ner_data", "updated_labelled.json"),
            "batch_size": 8,
            "dataset_type": 'ner_json'
        },
        "should_test": True,
        "regression_parameter": "precision_score",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd",
                                         "Kolovai Palms.tif"),
            "model": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd",
                                  "palms_houses_e200.emd"),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True"
        }
    },
    "pointcnn": {
        "model_name":"pointcnn",
        "datapath": "pointcnn_data",
        "model": PointCNN,
        "model_test": "pointcnn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "pointcnn_data", "input"),
             "batch_size": 2,
             "dataset_type": "PointCloud",
             "transforms": None, "color_mapping": colormap
         },
        "should_test": True,
        "regression_parameter":"compute_precision_recall",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd",
                                         "Kolovai Palms.tif"),
            "model": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd",
                                  "palms_houses_e200.emd"),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True"
        }
    },
    "superres": {
        "model_name":"superres",
        "datapath": "superres_data",
        "model": SuperResolution,
        "model_test": "superres_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "superres_data"),
             "batch_size": 4,
             "dataset_type": "superres",
             "downsample_factor": 8
         },
        "should_test": True,
        "regression_parameter": "psnr_metric",
        "regression_test_score": 0.40,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd",
                                         "Kolovai Palms.tif"),
            "model": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd",
                                  "palms_houses_e200.emd"),
            "parameters": "padding 56;threshold 0.5;nms_overlap 0.1;batch_size 4;exclude_pad_detections True"
        }
    },
    "fasterrcnn": {
        "model_name":"fasterrcnn",
        "datapath": "fasterrcnn_data",
        "model": FasterRCNN,
        "model_test": "fasterrcnn_test",
        "prepare_data": {
            "path": os.path.join(data_folder, "fasterrcnn_data"),
            "batch_size": 4
        },
        "should_test": True,
        "regression_parameter": "average_precision_score",
        "regression_test_score": 0.10,
        "inferencing_parameter": {
            "model_type": "pass",
            "sample_input": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "fasterrcnn",
                                         "input_image.tif"),
            "model": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "ssd", "fasterrcnn.emd"),
            "parameters": "padding 56;batch_size 64;threshold 0.5;return_bboxes True",
            "path": os.path.join(data_folder_inference, "DetectObjectsUsingDeepLearning", "fasterrcnn")
        }
    }

}

import os

input_data_path_ms = r"D:\files_sanoj\inferencing_test_resources\input_data\ms"
input_data_path_rgb = r"D:\files_sanoj\inferencing_test_resources\input_data\rgb"
output_gdb_folder = r"D:\files_sanoj\inferencing_test_resources"
saved_models_path = r"D:\files_sanoj\inferencing_test_resources\models"
output_gdb = "outputs_latest.gdb"

data_inferencing = {
    'mtre_hourglass': {
        "name": "mtre_hourglass",
        "inference_function": "ClassifyPixelsUsingDeepLearning",
        "input_path_rgb": os.path.join(input_data_path_rgb, "mtre.tif"),
        "input_path_ms": os.path.join(input_data_path_ms, "mtre.tif"),
        "model_path_rgb": os.path.join(saved_models_path, "rgb_hourglass.dlpk"),
        "model_path_ms": os.path.join(saved_models_path, "ms_hourglass.dlpk"),
        "output_filename_rgb": "segmentation_rgb_mtre_hourglass",
        "output_filename_ms": "segmentation_ms_mtre_hourglass",
        "should_test": True,
        "padding": 32,
        "batch_size": 4,
        "threshold": 0.5,
    },
    'mtre_linknet': {
        "name": "mtre_linknet",
        "inference_function": "ClassifyPixelsUsingDeepLearning",
        "input_path_rgb": os.path.join(input_data_path_rgb, "mtre.tif"),
        "input_path_ms": os.path.join(input_data_path_ms, "mtre.tif"),
        "model_path_rgb": os.path.join(saved_models_path, "rgb_linknet.dlpk"),
        "model_path_ms": os.path.join(saved_models_path, "ms_linknet.dlpk"),
        "output_filename_rgb": "segmentation_rgb_mtre_linknet",
        "output_filename_ms": "segmentation_ms_mtre_linknet",
        "should_test": True,
        "padding": 32,
        "batch_size": 4,
        "threshold": 0.5,
    },
}